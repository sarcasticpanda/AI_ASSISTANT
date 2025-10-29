"""
COMPLETE VOICE TEST - Using Backend Modules
Step 1: Record voice
Step 2: STT (Speech to Text) with Groq
Step 3: Send to Qwen AI
Step 4: TTS (Text to Speech) with Arjun
"""

import os
import sys
import wave
import pyaudio
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment from backend/.env
load_dotenv('backend/.env')

from backend.core import stt_online, brain, tts_manager

print("=" * 70)
print("🎤 JARVIS COMPLETE VOICE TEST")
print("=" * 70)

# Test 1: Check STT connection
print("\n📡 Step 1: Testing Groq API connection...")
status = stt_online.test_connection()
print(f"   {status}")

if "✗" in status:
    print("\n❌ Cannot proceed without Groq API access!")
    exit(1)

# Test 2: Record audio
print("\n🎤 Step 2: Recording your voice...")
print("   Preparing to record for 5 seconds...")

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
OUTPUT_FILE = "voice_input.wav"

audio = pyaudio.PyAudio()

input("\n   Press ENTER when ready to speak...")

print("\n   3...")
import time
time.sleep(1)
print("   2...")
time.sleep(1)
print("   1...")
time.sleep(1)
print(f"\n🔴 SPEAK NOW! ({RECORD_SECONDS} seconds)")
print("   Try: 'What is the weather in New York?'\n")

try:
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    total = int(RATE / CHUNK * RECORD_SECONDS)
    
    for i in range(total):
        data = stream.read(CHUNK)
        frames.append(data)
        if i % 10 == 0:
            percent = int((i / total) * 100)
            print(f"   Recording... {percent}%", end='\r')
    
    print("\n\n✅ Recording complete!")
    
    stream.stop_stream()
    stream.close()
    
    # Save
    wf = wave.open(OUTPUT_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    # Test 3: Transcribe (STT)
    print("\n📝 Step 3: Transcribing with Groq Whisper...")
    
    text = stt_online.transcribe_online(OUTPUT_FILE)
    
    print("\n" + "=" * 70)
    print("YOU SAID:")
    print(f'   "{text}"')
    print("=" * 70)
    
    if not text or "[" in text:
        print("\n❌ Transcription failed!")
        exit(1)
    
    # Test 4: Process with Qwen AI
    print("\n🧠 Step 4: Sending to Qwen AI...")
    
    response = brain.process_command(text)
    
    print("\n" + "=" * 70)
    print("JARVIS RESPONSE:")
    print(f'   "{response}"')
    print("=" * 70)
    
    # Test 5: Speak response (TTS)
    print("\n🔊 Step 5: Speaking response with TTS...")
    
    audio_path, engine = tts_manager.speak(response, lang='en')
    
    if audio_path:
        print(f"\n✅ Audio generated: {audio_path}")
        print(f"   Engine: {engine}")
        
        # Play audio (Windows)
        import winsound
        if audio_path.endswith('.mp3'):
            print("\n   Playing audio...")
            from pygame import mixer
            mixer.init()
            mixer.music.load(audio_path)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.1)
        elif audio_path.endswith('.wav'):
            winsound.PlaySound(audio_path, winsound.SND_FILENAME)
    
    # Clean up
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE VOICE TEST SUCCESSFUL!")
    print("=" * 70)
    print("\n📊 Summary:")
    print(f"   ✅ Voice recorded: {RECORD_SECONDS}s")
    print(f"   ✅ Transcribed: {len(text)} characters")
    print(f"   ✅ AI response: {len(response)} characters")
    print(f"   ✅ TTS played: {engine}")
    print("\n🎉 All systems working!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    audio.terminate()
