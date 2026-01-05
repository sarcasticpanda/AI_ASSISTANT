"""
PHASE 1 - PROFESSIONAL VOICE ASSISTANT (ChatGPT Recommended)

Implements:
✅ WebRTC VAD (Voice Activity Detection)
✅ Noise suppression (noisereduce)
✅ Audio normalization (pydub)
✅ Mono 16kHz (STT optimal)
✅ Proper start/stop detection
✅ Clean audio pipeline → Groq STT → Qwen → Edge TTS
"""

import os
import sys
import wave
import numpy as np
import time
import struct
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv('backend/.env')

from backend.core import stt_online, brain, tts_manager, tts_online, mongo_manager

# Check required packages
try:
    import webrtcvad
    print("✅ webrtcvad available")
except ImportError:
    print("❌ webrtcvad not found!")
    print("   Install: pip install webrtcvad")
    sys.exit(1)

try:
    import noisereduce as nr
    print("✅ noisereduce available")
except ImportError:
    print("⚠️  noisereduce not found - audio won't be denoised")
    print("   Install: pip install noisereduce")
    nr = None

try:
    from pydub import AudioSegment, effects
    print("✅ pydub available")
except ImportError:
    print("⚠️  pydub not found - audio won't be normalized")
    print("   Install: pip install pydub")
    AudioSegment = None

import pyaudio

# Audio configuration (ChatGPT recommended)
RATE = 16000  # 16kHz for STT models
CHANNELS = 1  # Mono (stereo adds confusion)
CHUNK_DURATION_MS = 30  # 30ms chunks for WebRTC VAD
CHUNK = int(RATE * CHUNK_DURATION_MS / 1000)  # 480 samples
FORMAT = pyaudio.paInt16

# VAD settings
VAD_MODE = 3  # 0-3, 3=most aggressive (best for noisy environments)
SPEECH_CONSECUTIVE_CHUNKS = 10  # Need 10 chunks (300ms) of speech to START
SILENCE_CONSECUTIVE_CHUNKS = 20  # Need 20 chunks (600ms) of silence to STOP
MAX_RECORDING_SECONDS = 10  # Auto-stop after 10 seconds


# ============================================================================
# WEBRTC VAD RECORDING
# ============================================================================

def record_with_vad():
    """
    Record using WebRTC VAD (Voice Activity Detection).
    This is the PROFESSIONAL way used by Google Meet, Zoom, etc.
    
    Returns:
        audio_file: Path to recorded WAV file
    """
    print("\n🔴 Press ENTER when ready to speak...")
    input()
    
    print("\n🎙️  LISTENING... Speak clearly!")
    print("   Will auto-start when you speak")
    print("   Will auto-stop after 600ms silence\n")
    
    # Beep to indicate ready
    import winsound
    winsound.Beep(1000, 100)
    
    # Initialize WebRTC VAD
    vad = webrtcvad.Vad(VAD_MODE)
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    recording = False
    speech_chunks = 0
    silence_chunks = 0
    total_chunks = 0
    
    print("   ⏳ Waiting for speech...\n")
    
    try:
        while True:
            # Read audio chunk
            data = stream.read(CHUNK, exception_on_overflow=False)
            total_chunks += 1
            
            # WebRTC VAD detection (True = speech, False = silence)
            is_speech = vad.is_speech(data, RATE)
            
            # Visual feedback
            if is_speech:
                print(f"\r   🎤 SPEECH detected! Recording... [{len(frames)} chunks]", end="", flush=True)
                speech_chunks += 1
                silence_chunks = 0
            else:
                if recording:
                    print(f"\r   ⏸️  Silence... [{silence_chunks}/{SILENCE_CONSECUTIVE_CHUNKS}]     ", end="", flush=True)
                else:
                    print(f"\r   ⏳ Waiting... [{speech_chunks}/{SPEECH_CONSECUTIVE_CHUNKS}]     ", end="", flush=True)
                silence_chunks += 1
                speech_chunks = 0
            
            # Start recording after sustained speech
            if not recording and speech_chunks >= SPEECH_CONSECUTIVE_CHUNKS:
                print(f"\n\n   ✅ Speech started! Recording...\n")
                recording = True
                frames = []  # Clear any pre-speech buffer
            
            # Add frame if recording
            if recording:
                frames.append(data)
            
            # Stop recording after sustained silence
            if recording and silence_chunks >= SILENCE_CONSECUTIVE_CHUNKS:
                print(f"\n\n   🔇 Silence detected - stopping...\n")
                break
            
            # Safety: stop after max duration
            if total_chunks > (RATE / CHUNK) * MAX_RECORDING_SECONDS:
                print(f"\n\n   ⏱️  Max recording time ({MAX_RECORDING_SECONDS}s) reached - stopping...\n")
                break
    
    except KeyboardInterrupt:
        print("\n\n   ⚠️  Recording cancelled\n")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        return None
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Check if we got any audio
    if not frames:
        print("   ❌ No speech detected!")
        return None
    
    print(f"   ✅ Recorded {len(frames)} chunks ({len(frames) * CHUNK_DURATION_MS / 1000:.1f}s)")
    
    # Save raw audio
    temp_file = "temp_raw_audio.wav"
    wf = wave.open(temp_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return temp_file


# ============================================================================
# AUDIO CLEANING
# ============================================================================

def clean_audio(input_file):
    """
    Clean audio using noise reduction and normalization.
    This is what makes STT work reliably!
    
    Args:
        input_file: Path to raw audio file
        
    Returns:
        clean_file: Path to cleaned audio file
    """
    print("\n🧹 Cleaning audio...")
    
    # Read audio file
    wf = wave.open(input_file, 'rb')
    audio_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    wf.close()
    
    cleaned_data = audio_data
    
    # Step 1: Noise reduction (if available)
    if nr is not None:
        print("   🔇 Removing background noise...")
        cleaned_data = nr.reduce_noise(
            y=cleaned_data,
            sr=RATE,
            stationary=True,  # Fan noise is stationary
            prop_decrease=0.8  # Reduce noise by 80%
        )
        print("   ✅ Noise reduced")
    
    # Step 2: Normalize volume (if available)
    if AudioSegment is not None:
        print("   🔊 Normalizing volume...")
        
        # Save temp file for pydub
        temp_np = "temp_np.wav"
        wf = wave.open(temp_np, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(RATE)
        wf.writeframes(cleaned_data.astype(np.int16).tobytes())
        wf.close()
        
        # Normalize
        sound = AudioSegment.from_file(temp_np)
        normalized = effects.normalize(sound)
        
        clean_file = "temp_clean_audio.wav"
        normalized.export(clean_file, format="wav")
        
        os.remove(temp_np)
        print("   ✅ Volume normalized")
    else:
        # Save without normalization
        clean_file = "temp_clean_audio.wav"
        wf = wave.open(clean_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(cleaned_data.astype(np.int16).tobytes())
        wf.close()
    
    print("   ✅ Audio cleaned!\n")
    return clean_file


# ============================================================================
# POST-PROCESSING
# ============================================================================

def correct_transcription(text):
    """
    Fix common STT mistakes with keyword correction.
    ChatGPT recommended this for "jarvis" → "service" issues.
    """
    corrections = {
        "service": "jarvis",
        "jarvis": "jarvis",  # Ensure correct
        "garbage": "jarvis",
        "survice": "jarvis",
    }
    
    text_lower = text.lower()
    for wrong, right in corrections.items():
        text_lower = text_lower.replace(wrong, right)
    
    return text_lower


# ============================================================================
# MAIN LOOP
# ============================================================================

def main():
    """Main voice assistant loop with professional audio pipeline"""
    
    print("\n" + "="*70)
    print("🎙️  JARVIS PHASE 1 - PROFESSIONAL (ChatGPT Recommended)")
    print("="*70)
    print("\n📋 FEATURES:")
    print("  ✅ WebRTC VAD (Google Meet level)")
    print("  ✅ Noise reduction (removes fan/AC noise)")
    print("  ✅ Audio normalization (consistent volume)")
    print("  ✅ Mono 16kHz (STT optimized)")
    print("  ✅ Auto start/stop (300ms speech, 600ms silence)")
    print("  ✅ Groq STT → Qwen Brain → Edge TTS")
    print("\n" + "="*70)
    
    # Check internet
    print("\n📡 Checking internet connection...")
    if not tts_manager.is_online():
        print("❌ No internet! Online mode requires internet.")
        return
    print("✅ Online - Ready to start!\n")
    
    # Initialize MongoDB
    print("🗄️  Connecting to MongoDB...")
    try:
        mongo_manager.initialize()
        print("✅ MongoDB connected\n")
    except Exception as e:
        print(f"⚠️  MongoDB failed: {e}")
        print("   Continuing without conversation history...\n")
    
    print("🎯 Ready! Let's talk!")
    print("\n💡 TIPS:")
    print("   • Speak clearly and at normal volume")
    print("   • System will auto-start when you speak")
    print("   • System will auto-stop after 600ms silence")
    print("   • Press Ctrl+C to exit\n")
    
    conversation_count = 0
    
    try:
        while True:
            conversation_count += 1
            print("─" * 70)
            print(f"💬 CONVERSATION #{conversation_count}")
            print("─" * 70)
            
            # 1. RECORD with WebRTC VAD
            raw_audio_file = record_with_vad()
            if not raw_audio_file:
                continue
            
            # 2. CLEAN audio (denoise + normalize)
            clean_audio_file = clean_audio(raw_audio_file)
            
            # 3. STT
            print("🎧 Transcribing...")
            start_time = time.time()
            stt_result = stt_online.transcribe_online(clean_audio_file)
            stt_time = time.time() - start_time
            
            # Cleanup temp files
            os.remove(raw_audio_file)
            os.remove(clean_audio_file)
            
            # Handle STT result (dict or error string)
            if isinstance(stt_result, dict):
                text = stt_result.get("text", "")
            else:
                text = str(stt_result)
            
            if not text or text.strip() == "":
                print("❌ No speech detected. Try speaking louder!\n")
                continue
            
            # 4. POST-PROCESS (fix common mistakes)
            text = correct_transcription(text)
            
            print(f"   📝 You: {text}")
            print(f"   ⏱️  STT: {stt_time:.2f}s\n")
            
            # 5. BRAIN
            print("🧠 Processing...")
            start_time = time.time()
            result = brain.process_command(text)
            brain_time = time.time() - start_time
            
            response = result.get('response', 'Sorry, I could not process that.')
            print(f"   🤖 Jarvis: {response}")
            print(f"   ⏱️  Brain: {brain_time:.2f}s\n")
            
            # 6. TTS
            print("🔊 Speaking...")
            start_time = time.time()
            audio_path, engine = tts_manager.speak(response, lang='en', prefer_offline=False)
            tts_time = time.time() - start_time
            
            if audio_path and os.path.exists(audio_path):
                tts_online.play_audio(audio_path)
                os.remove(audio_path)
                print(f"   ⏱️  TTS: {tts_time:.2f}s")
            
            # 7. Check for follow-up
            if result.get('expects_followup'):
                print(f"\n💬 Jarvis expects a follow-up (timeout: {result.get('followup_timeout', 10)}s)")
                # TODO: Implement follow-up handling
            
            print("\n✅ Complete!\n")
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("👋 GOODBYE!")
        print("="*70)
        print(f"\n📊 Session Summary:")
        print(f"   Conversations: {conversation_count}")
        print("\n✅ Thank you for using Jarvis!\n")


if __name__ == "__main__":
    main()
