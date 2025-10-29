"""
TEST ONLINE VOICE PIPELINE
Tests: Microphone → Groq Whisper (STT) → Qwen (Brain) → Edge TTS Arjun
"""

import os
import sys
import wave
import pyaudio
import time
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment from backend/.env
load_dotenv('backend/.env')

from backend.core import stt_online, brain, tts_manager, mongo_manager

print("=" * 70)
print("🌐 JARVIS ONLINE VOICE PIPELINE TEST")
print("=" * 70)

# Initialize MongoDB
print("\n🗄️  Initializing MongoDB...")
try:
    mongo_manager.initialize()
    print("   ✅ MongoDB connected")
except Exception as e:
    print(f"   ⚠️  MongoDB failed: {e}")
    print("   ℹ️  Continuing without database")

# Test 1: Check internet and APIs
print("\n📡 Step 1: Checking online services...")
print("-" * 70)

# Check Groq API
groq_status = stt_online.test_connection()
print(f"   STT (Groq): {groq_status}")

if "✗" in groq_status:
    print("\n❌ Cannot proceed without Groq API!")
    exit(1)

# Check TTS
tts_status = tts_manager.get_status()
print(f"   TTS: {tts_status['recommended_engine']}")
print(f"   Internet: {'✅' if tts_status['internet'] else '❌'}")

if not tts_status['internet']:
    print("\n❌ No internet connection!")
    exit(1)

# Test 2: Record voice
print("\n🎤 Step 2: Recording your voice...")
print("-" * 70)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
OUTPUT_FILE = "test_online_audio.wav"

audio = pyaudio.PyAudio()

print("\n   You can test these skills:")
print("   • 'What time is it?'")
print("   • 'What's the date today?'")
print("   • 'Set an alarm for 5 minutes'")
print("   • 'Open Chrome'")
print("   • 'Hello Jarvis'")
print("   • 'Thank you'")

input("\n   Press ENTER when ready to speak...")

print("\n   Countdown:")
for i in range(3, 0, -1):
    print(f"   {i}...")
    time.sleep(1)

print(f"\n🔴 SPEAK NOW! ({RECORD_SECONDS} seconds)")
print("   Recording...\n")

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
            bars = "█" * (percent // 5)
            print(f"   [{bars:<20}] {percent}%", end='\r')
    
    print(f"\n   [{'█' * 20}] 100%")
    print("\n✅ Recording complete!")
    
    stream.stop_stream()
    stream.close()
    
    # Save
    wf = wave.open(OUTPUT_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    # Test 3: STT (Groq Whisper)
    print("\n📝 Step 3: Transcribing with Groq Whisper...")
    print("-" * 70)
    
    start_time = time.time()
    text = stt_online.transcribe_online(OUTPUT_FILE)
    stt_time = time.time() - start_time
    
    print(f"\n   YOU SAID: \"{text}\"")
    print(f"   ⏱️  STT Time: {stt_time:.2f}s")
    
    if not text or "[" in text:
        print("\n❌ Transcription failed!")
        exit(1)
    
    # Test 4: Brain Processing (Qwen)
    print("\n🧠 Step 4: Processing with Qwen AI...")
    print("-" * 70)
    
    start_time = time.time()
    result = brain.process_command(text)
    brain_time = time.time() - start_time
    
    # Handle response (could be dict or string)
    if isinstance(result, dict):
        response = result.get('response', str(result))
        intent = result.get('intent', 'unknown')
        method = result.get('method', 'llm')
    else:
        response = result
        intent = 'unknown'
        method = 'direct'
    
    print(f"\n   JARVIS: \"{response}\"")
    print(f"   Intent: {intent}")
    print(f"   Method: {method}")
    print(f"   ⏱️  Brain Time: {brain_time:.2f}s")
    
    # Test 5: TTS (Edge TTS Arjun)
    print("\n🔊 Step 5: Speaking with Edge TTS (Arjun)...")
    print("-" * 70)
    
    start_time = time.time()
    audio_path, engine = tts_manager.speak(response, lang='en', prefer_offline=False)
    tts_time = time.time() - start_time
    
    print(f"   Engine: {engine}")
    print(f"   ⏱️  TTS Time: {tts_time:.2f}s")
    
    if audio_path:
        print(f"   Audio: {audio_path}")
        
        # Play audio
        print("\n   🔊 Playing audio...")
        if audio_path.endswith('.mp3'):
            from pygame import mixer
            mixer.init()
            mixer.music.load(audio_path)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(0.1)
        elif audio_path.endswith('.wav'):
            import winsound
            winsound.PlaySound(audio_path, winsound.SND_FILENAME)
    
    # Test 6: MongoDB save
    print("\n💾 Step 6: Saving to MongoDB...")
    print("-" * 70)
    
    try:
        mongo_manager.save_conversation(text, response, intent)
        print("   ✅ Conversation saved")
    except Exception as e:
        print(f"   ⚠️  Save failed: {e}")
    
    # Clean up
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    # Summary
    total_time = stt_time + brain_time + tts_time
    
    print("\n" + "=" * 70)
    print("✅ ONLINE VOICE PIPELINE TEST COMPLETE!")
    print("=" * 70)
    
    print("\n📊 Performance Summary:")
    print(f"   STT (Groq Whisper):  {stt_time:.2f}s")
    print(f"   Brain (Qwen):        {brain_time:.2f}s")
    print(f"   TTS (Edge Arjun):    {tts_time:.2f}s")
    print(f"   {'─' * 40}")
    print(f"   Total Processing:    {total_time:.2f}s")
    
    print("\n✅ All online components working!")
    print("🎯 Next: Run test_offline_voice.py for offline testing")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    audio.terminate()
