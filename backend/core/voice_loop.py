"""
Voice Loop - Parallel Voice Assistant with Interruption Support
Handles continuous listening, processing, and playback in separate threads.

Features:
- 3 threads: Listening, Processing, Playback
- Voice Activity Detection (VAD) for continuous listening
- Interrupt playback when user speaks
- Follow-up question detection with timeout
- Offline STT (faster-whisper) for low latency
"""

import os
import logging
import threading
import queue
import time
import wave
import pyaudio
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import core modules
from backend.core import stt_local, brain, tts_manager, mongo_manager

# ============================================================================
# CONFIGURATION
# ============================================================================

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# VAD settings
SILENCE_THRESHOLD = 500      # Amplitude threshold for silence
SILENCE_DURATION = 1.5       # Seconds of silence to stop recording
MIN_RECORDING_TIME = 0.5     # Minimum recording duration (avoid false triggers)
MAX_RECORDING_TIME = 10      # Maximum recording duration

# Follow-up settings
FOLLOWUP_DEFAULT_TIMEOUT = 8  # Seconds to wait for follow-up response


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AudioChunk:
    """Represents recorded audio data"""
    frames: list
    rate: int
    channels: int
    format: int


@dataclass
class ProcessingTask:
    """Task for processing queue"""
    audio: AudioChunk
    timestamp: float
    is_followup: bool = False


# ============================================================================
# VOICE ACTIVITY DETECTION (VAD)
# ============================================================================

class VoiceActivityDetector:
    """Simple energy-based Voice Activity Detection"""
    
    def __init__(self, threshold: int = SILENCE_THRESHOLD):
        self.threshold = threshold
    
    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Detect if audio chunk contains speech.
        
        Args:
            audio_chunk: Raw audio data
        
        Returns:
            True if speech detected, False if silence
        """
        import audioop
        
        # Calculate RMS (root mean square) energy
        energy = audioop.rms(audio_chunk, 2)  # 2 bytes per sample for paInt16
        
        return energy > self.threshold
    
    def calibrate(self, audio_stream, duration: float = 2.0):
        """
        Auto-calibrate threshold based on ambient noise.
        
        Args:
            audio_stream: PyAudio stream
            duration: Calibration duration in seconds
        """
        import audioop
        
        logger.info(f"Calibrating VAD (please stay quiet for {duration}s)...")
        
        samples = int(RATE / CHUNK * duration)
        energies = []
        
        for _ in range(samples):
            data = audio_stream.read(CHUNK, exception_on_overflow=False)
            energy = audioop.rms(data, 2)
            energies.append(energy)
        
        # Set threshold as 2x the average ambient noise
        avg_noise = sum(energies) / len(energies)
        self.threshold = int(avg_noise * 2.5)
        
        logger.info(f"✓ VAD calibrated - threshold: {self.threshold}")


# ============================================================================
# VOICE LOOP THREADS
# ============================================================================

class VoiceLoop:
    """Main voice loop controller"""
    
    def __init__(self, use_offline_stt: bool = True):
        """
        Initialize voice loop.
        
        Args:
            use_offline_stt: Use faster-whisper (True) or Groq (False)
        """
        self.use_offline_stt = use_offline_stt
        
        # Threading
        self.processing_queue = queue.Queue()
        self.playback_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.interrupt_event = threading.Event()
        
        # Threads
        self.listen_thread: Optional[threading.Thread] = None
        self.process_thread: Optional[threading.Thread] = None
        self.playback_thread: Optional[threading.Thread] = None
        
        # Audio
        self.audio = pyaudio.PyAudio()
        self.vad = VoiceActivityDetector()
        
        # State
        self.is_listening = False
        self.is_processing = False
        self.is_playing = False
        self.waiting_for_followup = False
        self.followup_timeout = 0
        
        logger.info(f"Voice loop initialized (STT: {'offline' if use_offline_stt else 'online'})")
    
    # ========================================================================
    # THREAD 1: CONTINUOUS LISTENING
    # ========================================================================
    
    def _listen_thread_func(self):
        """Continuous listening with VAD"""
        logger.info("🎤 Listening thread started")
        
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Calibrate VAD
        self.vad.calibrate(stream, duration=2.0)
        
        logger.info("🎤 Ready - listening for voice...")
        
        while not self.stop_event.is_set():
            try:
                # Read audio chunk
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Check for speech
                if self.vad.is_speech(data):
                    # Speech detected - start recording
                    self._record_utterance(stream)
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
            
            except Exception as e:
                logger.error(f"Listen thread error: {e}")
                time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        logger.info("🎤 Listening thread stopped")
    
    def _record_utterance(self, stream):
        """
        Record a complete utterance (speech until silence).
        
        Args:
            stream: PyAudio stream
        """
        logger.info("🔴 Recording...")
        
        # If playing audio, interrupt it
        if self.is_playing:
            logger.info("⚠️  Interrupting playback")
            self.interrupt_event.set()
        
        frames = []
        start_time = time.time()
        silence_start = None
        
        while not self.stop_event.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            # Check recording duration
            elapsed = time.time() - start_time
            
            if elapsed > MAX_RECORDING_TIME:
                logger.warning("Max recording time reached")
                break
            
            # Check for silence
            if self.vad.is_speech(data):
                # Speech detected - reset silence timer
                silence_start = None
            else:
                # Silence detected
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_DURATION:
                    # Silence long enough - stop recording
                    if elapsed > MIN_RECORDING_TIME:
                        logger.info(f"✓ Recording complete ({elapsed:.1f}s)")
                        break
        
        # Create audio chunk
        if frames:
            audio_chunk = AudioChunk(
                frames=frames,
                rate=RATE,
                channels=CHANNELS,
                format=FORMAT
            )
            
            # Add to processing queue
            task = ProcessingTask(
                audio=audio_chunk,
                timestamp=time.time(),
                is_followup=self.waiting_for_followup
            )
            
            self.processing_queue.put(task)
            logger.info("📤 Audio sent for processing")
    
    # ========================================================================
    # THREAD 2: PROCESSING (STT → BRAIN → TTS)
    # ========================================================================
    
    def _process_thread_func(self):
        """Process audio: STT → Brain → TTS"""
        logger.info("🧠 Processing thread started")
        
        while not self.stop_event.is_set():
            try:
                # Wait for task (with timeout to check stop_event)
                try:
                    task = self.processing_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                self.is_processing = True
                logger.info("🧠 Processing audio...")
                
                # Step 1: STT (Speech to Text)
                logger.info("📝 Transcribing...")
                start_stt = time.time()
                
                # Save audio to temp file
                temp_audio = "temp_audio.wav"
                wf = wave.open(temp_audio, 'wb')
                wf.setnchannels(task.audio.channels)
                wf.setsampwidth(self.audio.get_sample_size(task.audio.format))
                wf.setframerate(task.audio.rate)
                wf.writeframes(b''.join(task.audio.frames))
                wf.close()
                
                # Transcribe
                if self.use_offline_stt:
                    text = stt_local.transcribe_file(temp_audio, method="whisper")
                else:
                    from backend.core import stt_online
                    text = stt_online.transcribe_online(temp_audio)
                
                stt_time = time.time() - start_stt
                logger.info(f"   YOU: \"{text}\" ({stt_time:.2f}s)")
                
                # Clean up
                if os.path.exists(temp_audio):
                    os.remove(temp_audio)
                
                # Skip if empty or error
                if not text or "[" in text:
                    logger.warning("Transcription failed or empty")
                    self.is_processing = False
                    continue
                
                # Step 2: BRAIN (Process command)
                logger.info("🧠 Processing with brain...")
                start_brain = time.time()
                
                result = brain.process_command(text)
                
                brain_time = time.time() - start_brain
                
                if isinstance(result, dict):
                    response = result.get('response', str(result))
                    expects_followup = result.get('expects_followup', False)
                    followup_timeout = result.get('followup_timeout', FOLLOWUP_DEFAULT_TIMEOUT)
                else:
                    response = result
                    expects_followup = False
                    followup_timeout = 0
                
                logger.info(f"   JARVIS: \"{response[:50]}...\" ({brain_time:.2f}s)")
                
                # Step 3: TTS (Text to Speech)
                logger.info("🔊 Generating speech...")
                start_tts = time.time()
                
                audio_path, engine = tts_manager.speak(
                    response,
                    lang='en',
                    prefer_offline=self.use_offline_stt  # Match STT mode
                )
                
                tts_time = time.time() - start_tts
                logger.info(f"   TTS: {engine} ({tts_time:.2f}s)")
                
                # Add to playback queue
                self.playback_queue.put({
                    "audio_path": audio_path,
                    "engine": engine,
                    "expects_followup": expects_followup,
                    "followup_timeout": followup_timeout
                })
                
                self.is_processing = False
                logger.info(f"✓ Processing complete (Total: {stt_time + brain_time + tts_time:.2f}s)")
            
            except Exception as e:
                logger.error(f"Processing error: {e}")
                import traceback
                traceback.print_exc()
                self.is_processing = False
        
        logger.info("🧠 Processing thread stopped")
    
    # ========================================================================
    # THREAD 3: PLAYBACK (Interruptible)
    # ========================================================================
    
    def _playback_thread_func(self):
        """Play TTS audio (can be interrupted)"""
        logger.info("🔊 Playback thread started")
        
        while not self.stop_event.is_set():
            try:
                # Wait for audio to play
                try:
                    item = self.playback_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                audio_path = item["audio_path"]
                expects_followup = item["expects_followup"]
                followup_timeout = item["followup_timeout"]
                
                self.is_playing = True
                self.interrupt_event.clear()
                
                logger.info("🔊 Playing audio...")
                
                # Play audio (interruptible)
                if audio_path and audio_path != "pyttsx3_direct":
                    if audio_path.endswith('.mp3'):
                        from pygame import mixer
                        mixer.init()
                        mixer.music.load(audio_path)
                        mixer.music.play()
                        
                        # Wait for playback (check for interruption)
                        while mixer.music.get_busy():
                            if self.interrupt_event.is_set():
                                mixer.music.stop()
                                logger.info("⚠️  Playback interrupted")
                                break
                            time.sleep(0.1)
                    
                    elif audio_path.endswith('.wav'):
                        import winsound
                        # Note: winsound.PlaySound is blocking and can't be interrupted easily
                        # For interruptible playback, we'd need pygame or another library
                        winsound.PlaySound(audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                
                self.is_playing = False
                
                # Handle follow-up if needed
                if expects_followup and not self.interrupt_event.is_set():
                    logger.info(f"⏳ Waiting {followup_timeout}s for follow-up...")
                    self.waiting_for_followup = True
                    self.followup_timeout = followup_timeout
                    
                    # Wait for timeout or user input
                    time.sleep(followup_timeout)
                    
                    # If no input received, say goodbye
                    if self.waiting_for_followup:
                        logger.info("⏱️  Follow-up timeout - no input received")
                        tts_manager.speak("Let me know if you need anything else.", prefer_offline=True)
                        self.waiting_for_followup = False
                
            except Exception as e:
                logger.error(f"Playback error: {e}")
                self.is_playing = False
        
        logger.info("🔊 Playback thread stopped")
    
    # ========================================================================
    # MAIN CONTROLS
    # ========================================================================
    
    def start(self):
        """Start all threads"""
        logger.info("🚀 Starting voice loop...")
        
        # Initialize MongoDB
        try:
            mongo_manager.initialize()
            logger.info("✓ MongoDB connected")
        except Exception as e:
            logger.warning(f"MongoDB unavailable: {e}")
        
        # Start threads
        self.listen_thread = threading.Thread(target=self._listen_thread_func, daemon=True)
        self.process_thread = threading.Thread(target=self._process_thread_func, daemon=True)
        self.playback_thread = threading.Thread(target=self._playback_thread_func, daemon=True)
        
        self.listen_thread.start()
        self.process_thread.start()
        self.playback_thread.start()
        
        logger.info("✓ Voice loop started - all threads running")
    
    def stop(self):
        """Stop all threads"""
        logger.info("🛑 Stopping voice loop...")
        
        self.stop_event.set()
        
        # Wait for threads to finish
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        if self.process_thread:
            self.process_thread.join(timeout=2)
        if self.playback_thread:
            self.playback_thread.join(timeout=2)
        
        # Cleanup
        self.audio.terminate()
        
        logger.info("✓ Voice loop stopped")
    
    def run_forever(self):
        """Run voice loop until Ctrl+C"""
        try:
            self.start()
            
            print("\n" + "=" * 70)
            print("🎤 JARVIS VOICE LOOP - RUNNING")
            print("=" * 70)
            print("\nFeatures:")
            print("  ✅ Continuous listening with VAD")
            print("  ✅ Interrupt playback by speaking")
            print("  ✅ Follow-up question detection")
            print(f"  ✅ STT: {'Offline (faster-whisper)' if self.use_offline_stt else 'Online (Groq)'}")
            print("\nPress Ctrl+C to stop\n")
            
            # Keep main thread alive
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping...")
            self.stop()
            print("✓ Stopped")


# ============================================================================
# STANDALONE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Parse arguments
    use_offline = "--offline" in sys.argv or "-o" in sys.argv
    
    # Run voice loop
    loop = VoiceLoop(use_offline_stt=use_offline)
    loop.run_forever()
