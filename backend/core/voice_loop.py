"""
Voice Loop - Parallel Voice Processing with Interruption Support
Handles continuous listening, processing, and speech with ability to interrupt.

Architecture:
- Thread 1 (Listener): Continuously records audio in chunks, detects voice activity
- Thread 2 (Processor): STT → Brain → TTS pipeline
- Thread 3 (Player): Plays audio, can be interrupted by new input
- Queue-based communication between threads
"""

import logging
import threading
import queue
import time
import wave
import pyaudio
import os
import struct
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import core modules
from backend.core import stt_local, brain, tts_manager, mongo_manager

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


class VoiceLoop:
    """
    Parallel voice processing loop with interruption support.
    
    Features:
    - Continuous listening with Voice Activity Detection (VAD)
    - Parallel processing (can listen while speaking)
    - Interrupt playback when user starts speaking
    - Follow-up question detection and waiting
    """
    
    def __init__(self, use_offline: bool = True):
        """
        Initialize voice loop.
        
        Args:
            use_offline: Use offline STT/TTS (True) or online (False)
        """
        self.use_offline = use_offline
        
        # Thread control
        self.running = False
        self.listening = False
        self.speaking = False
        
        # Queues for inter-thread communication
        self.audio_queue = queue.Queue()      # Raw audio chunks
        self.process_queue = queue.Queue()    # Audio files to process
        self.response_queue = queue.Queue()   # Responses to speak
        
        # Threads
        self.listener_thread = None
        self.processor_thread = None
        self.player_thread = None
        
        # PyAudio
        self.audio = None
        self.stream = None
        
        # Statistics
        self.stats = {
            "commands_processed": 0,
            "interruptions": 0,
            "followups_detected": 0,
            "avg_processing_time": 0.0
        }
        
        logger.info(f"VoiceLoop initialized (offline={use_offline})")
    
    
    def start(self):
        """Start the voice loop (all threads)"""
        if self.running:
            logger.warning("Voice loop already running")
            return
        
        logger.info("🎙️ Starting voice loop...")
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Set flags
        self.running = True
        self.listening = True
        
        # Start threads
        self.listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
        self.processor_thread = threading.Thread(target=self._processor_loop, daemon=True)
        self.player_thread = threading.Thread(target=self._player_loop, daemon=True)
        
        self.listener_thread.start()
        self.processor_thread.start()
        self.player_thread.start()
        
        logger.info("✅ Voice loop started")
        logger.info("   - Listener: Running")
        logger.info("   - Processor: Running")
        logger.info("   - Player: Running")
    
    
    def stop(self):
        """Stop the voice loop"""
        if not self.running:
            return
        
        logger.info("🛑 Stopping voice loop...")
        
        # Set flag to stop threads
        self.running = False
        self.listening = False
        
        # Wait for threads to finish
        if self.listener_thread:
            self.listener_thread.join(timeout=2.0)
        if self.processor_thread:
            self.processor_thread.join(timeout=2.0)
        if self.player_thread:
            self.player_thread.join(timeout=2.0)
        
        # Close audio stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        logger.info("✅ Voice loop stopped")
        self._print_stats()
    
    
    def _listener_loop(self):
        """
        Thread 1: Continuous audio recording with VAD.
        Detects when user is speaking and captures audio.
        """
        logger.info("👂 Listener thread started")
        
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            frames = []
            silence_threshold = 1500  # Higher threshold to ignore background noise (was 500)
            speech_threshold = 2000   # Strong speech detection threshold
            silence_chunks = 0
            max_silence_chunks = 25  # ~1.6 seconds of silence (was 20)
            min_speech_chunks = 5     # Must have at least 5 chunks of strong speech
            recording = False
            speech_chunks_count = 0
            
            logger.info("🎧 Listening for speech... (Speak clearly and loudly)")
            
            while self.running and self.listening:
                # Read audio chunk
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                except Exception as e:
                    logger.error(f"Audio read error: {e}")
                    continue
                
                # Calculate RMS energy (proper audio energy calculation)
                # Convert bytes to 16-bit integers
                audio_samples = struct.unpack(f"{len(data)//2}h", data)
                # Calculate RMS (Root Mean Square)
                energy = int((sum(sample**2 for sample in audio_samples) / len(audio_samples))**0.5)
                
                # Detect speech start (must exceed speech threshold, not just silence threshold)
                if energy > speech_threshold and not recording:
                    logger.info(f"🎤 Speech detected (energy: {energy}) - recording started")
                    recording = True
                    frames = [data]
                    silence_chunks = 0
                    speech_chunks_count = 1
                    
                    # If currently speaking, interrupt
                    if self.speaking:
                        logger.info("⚠️ Interruption detected!")
                        self.stats["interruptions"] += 1
                
                # Continue recording
                elif recording:
                    frames.append(data)
                    
                    # Track strong speech chunks
                    if energy > speech_threshold:
                        speech_chunks_count += 1
                    
                    # Count silence
                    if energy < silence_threshold:
                        silence_chunks += 1
                    else:
                        silence_chunks = 0
                    
                    # Stop recording after silence
                    if silence_chunks >= max_silence_chunks:
                        logger.info(f"🔇 Silence detected (energy: {energy}) - recording stopped")
                        recording = False
                        
                        # Only process if we had enough strong speech
                        # This filters out background noise and fan sounds
                        if len(frames) > 10 and speech_chunks_count >= min_speech_chunks:
                            logger.info(f"✅ Valid speech recording ({speech_chunks_count} speech chunks)")
                            self._save_and_queue_audio(frames)
                        else:
                            logger.debug(f"⚠️ Recording rejected (too weak: {speech_chunks_count} speech chunks, need {min_speech_chunks})")
                        
                        frames = []
                        silence_chunks = 0
                        speech_chunks_count = 0
        
        except Exception as e:
            logger.error(f"Listener thread error: {e}")
        
        finally:
            logger.info("👂 Listener thread stopped")
    
    
    def _save_and_queue_audio(self, frames):
        """Save recorded frames to WAV file and queue for processing"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"voice_input_{timestamp}.wav"
        
        try:
            # Save to WAV
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            logger.info(f"💾 Saved audio: {filename}")
            
            # Queue for processing
            self.process_queue.put(filename)
        
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
    
    
    def _processor_loop(self):
        """
        Thread 2: Process audio files (STT → Brain → TTS).
        Waits for audio files in queue, processes them, queues responses.
        """
        logger.info("🧠 Processor thread started")
        
        while self.running:
            try:
                # Wait for audio file (with timeout to check running flag)
                try:
                    audio_file = self.process_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                logger.info(f"⚙️ Processing: {audio_file}")
                start_time = time.time()
                
                # Step 1: STT (Speech to Text)
                stt_start = time.time()
                if self.use_offline:
                    text = stt_local.transcribe_file(audio_file, method="whisper")
                else:
                    from backend.core import stt_online
                    text = stt_online.transcribe_online(audio_file)
                stt_time = time.time() - stt_start
                
                logger.info(f"📝 STT ({stt_time:.2f}s): '{text}'")
                
                # Clean up audio file
                try:
                    if os.path.exists(audio_file):
                        os.remove(audio_file)
                except:
                    pass
                
                if not text or "[" in text:
                    logger.warning("STT failed - skipping")
                    continue
                
                # Step 2: Brain (Process command)
                brain_start = time.time()
                result = brain.process_command(text)
                brain_time = time.time() - brain_start
                
                response = result.get("response", "")
                expects_followup = result.get("expects_followup", False)
                followup_timeout = result.get("followup_timeout", 0)
                
                logger.info(f"🧠 Brain ({brain_time:.2f}s): '{response[:50]}...'")
                if expects_followup:
                    logger.info(f"❓ Follow-up expected (timeout: {followup_timeout}s)")
                    self.stats["followups_detected"] += 1
                
                # Queue response for speaking
                self.response_queue.put({
                    "response": response,
                    "expects_followup": expects_followup,
                    "followup_timeout": followup_timeout,
                    "processing_time": time.time() - start_time
                })
                
                # Update stats
                self.stats["commands_processed"] += 1
                total_time = time.time() - start_time
                self.stats["avg_processing_time"] = (
                    (self.stats["avg_processing_time"] * (self.stats["commands_processed"] - 1) + total_time) 
                    / self.stats["commands_processed"]
                )
            
            except Exception as e:
                logger.error(f"Processor thread error: {e}")
                import traceback
                traceback.print_exc()
        
        logger.info("🧠 Processor thread stopped")
    
    
    def _player_loop(self):
        """
        Thread 3: Play TTS responses.
        Can be interrupted if new audio is being processed.
        """
        logger.info("🔊 Player thread started")
        
        while self.running:
            try:
                # Wait for response (with timeout)
                try:
                    response_data = self.response_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                response = response_data["response"]
                expects_followup = response_data["expects_followup"]
                followup_timeout = response_data["followup_timeout"]
                
                logger.info(f"🔊 Speaking: '{response[:50]}...'")
                
                # Mark as speaking
                self.speaking = True
                
                # Generate and play TTS
                tts_start = time.time()
                audio_path, engine = tts_manager.speak(
                    response, 
                    lang='en', 
                    prefer_offline=self.use_offline
                )
                tts_time = time.time() - tts_start
                
                logger.info(f"🔊 TTS ({tts_time:.2f}s) using {engine}")
                
                # Play audio (handled by tts_manager)
                if audio_path and audio_path != "pyttsx3_direct":
                    # Audio already played by tts_manager
                    pass
                
                self.speaking = False
                
                # Handle follow-up waiting
                if expects_followup and followup_timeout > 0:
                    logger.info(f"⏳ Waiting {followup_timeout}s for follow-up...")
                    
                    # Temporarily disable automatic listening
                    wait_start = time.time()
                    had_followup = False
                    
                    while time.time() - wait_start < followup_timeout:
                        # Check if user started speaking (queue has new audio)
                        if not self.process_queue.empty():
                            logger.info("✅ Follow-up detected!")
                            had_followup = True
                            break
                        time.sleep(0.5)
                    
                    # If no follow-up, say closing message
                    if not had_followup:
                        logger.info("⏱️ Follow-up timeout - closing")
                        closing_msg = "Let me know if you need anything else."
                        tts_manager.speak(closing_msg, lang='en', prefer_offline=self.use_offline)
            
            except Exception as e:
                logger.error(f"Player thread error: {e}")
                import traceback
                traceback.print_exc()
                self.speaking = False
        
        logger.info("🔊 Player thread stopped")
    
    
    def _print_stats(self):
        """Print loop statistics"""
        print("\n" + "=" * 70)
        print("📊 VOICE LOOP STATISTICS")
        print("=" * 70)
        print(f"Commands processed:    {self.stats['commands_processed']}")
        print(f"Interruptions:         {self.stats['interruptions']}")
        print(f"Follow-ups detected:   {self.stats['followups_detected']}")
        print(f"Avg processing time:   {self.stats['avg_processing_time']:.2f}s")
        print("=" * 70)
    
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        return self.stats.copy()


# ============================================================================
# UTILITIES
# ============================================================================

def run_voice_loop(use_offline: bool = True, duration: Optional[int] = None):
    """
    Run voice loop for specified duration or until interrupted.
    
    Args:
        use_offline: Use offline STT/TTS (True) or online (False)
        duration: Duration in seconds (None = run until Ctrl+C)
    
    Example:
        # Run for 60 seconds with offline mode
        run_voice_loop(use_offline=True, duration=60)
        
        # Run indefinitely with online mode
        run_voice_loop(use_offline=False, duration=None)
    """
    loop = VoiceLoop(use_offline=use_offline)
    
    try:
        loop.start()
        
        if duration:
            logger.info(f"⏱️ Running for {duration} seconds...")
            time.sleep(duration)
        else:
            logger.info("⏱️ Running until Ctrl+C...")
            while True:
                time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\n⌨️ Ctrl+C detected")
    
    finally:
        loop.stop()
