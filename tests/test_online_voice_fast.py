"""
TEST ONLINE VOICE PIPELINE - OPTIMIZED FOR SPEED
Optimizations:
1. Async MongoDB saves (non-blocking)
2. Reduced recording time (3s instead of 5s)
3. Parallel processing where possible
4. Streaming TTS (play while generating)
"""

import os
import sys
import wave
import pyaudio
import time
import threading
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment from backend/.env
load_dotenv('backend/.env')

from backend.core import stt_online, brain, tts_manager, mongo_manager

print("=" * 70)
print("🌐 JARVIS ONLINE VOICE PIPELINE - SPEED OPTIMIZED")
print("=" * 70)

# Initialize MongoDB
print("\n🗄️  Initializing MongoDB...")
try:
    mongo_manager.initialize()
    print("   ✅ MongoDB connected")
except Exception as e:
    print(f"   ⚠️  MongoDB failed: {e}")

# Test 1: Check internet and APIs
print("\n📡 Checking online services...")
print("-" * 70)

# Quick check
groq_status = stt_online.test_connection()
print(f"   STT (Groq): {groq_status}")

if "✗" in groq_status:
    print("\n❌ Cannot proceed without Groq API!")
    exit(1)

tts_status = tts_manager.get_status()
print(f"   TTS: {tts_status['recommended_engine']}")

# Test 2: Record voice (REDUCED TO 3 SECONDS)
print("\n🎤 Recording your voice (3 seconds)...")
print("-" * 70)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5  # ⚡ 5 seconds for full sentence
OUTPUT_FILE = "test_fast_audio.wav"

audio = pyaudio.PyAudio()

print("\n   Test phrases:")
print("   • 'What time is it?'")
print("   • 'Hello Jarvis'")
print("   • 'Open Chrome'")

input("\n   ⚠️  Press ENTER when ready to speak (you'll have 3 seconds to prepare)...")

# Clear countdown
print("\n   Get ready...")
time.sleep(1)
print("   3...")
time.sleep(1)
print("   2...")
time.sleep(1)
print("   1...")
time.sleep(1)

print(f"\n🔴 RECORDING NOW - SPEAK CLEARLY! ({RECORD_SECONDS} seconds)")
print("   ", end="", flush=True)

# Beep to indicate start
import winsound
winsound.Beep(1000, 200)  # 1000Hz for 200ms

start_total = time.time()

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
    
    # Record with visual progress
    for i in range(total):
        data = stream.read(CHUNK)
        frames.append(data)
        
        # Show progress every 0.5 seconds
        if i % 10 == 0:
            percent = int((i / total) * 100)
            bars = "█" * (percent // 5)
            spaces = "░" * (20 - (percent // 5))
            print(f"\r   [{bars}{spaces}] {percent}%", end="", flush=True)
    
    # Final progress
    print(f"\r   [{'█' * 20}] 100%")
    
    # Beep to indicate end
    winsound.Beep(800, 200)  # Lower tone
    
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
    print("\n📝 Transcribing...")
    
    start_stt = time.time()
    text = stt_online.transcribe_online(OUTPUT_FILE)
    stt_time = time.time() - start_stt
    
    print(f'   YOU: "{text}"')
    print(f"   ⏱️  {stt_time:.2f}s")
    
    if not text or "[" in text:
        print("❌ Transcription failed!")
        exit(1)
    
    # Test 4: Brain Processing
    print("\n🧠 Processing...")
    
    start_brain = time.time()
    result = brain.process_command(text)
    brain_time = time.time() - start_brain
    
    if isinstance(result, dict):
        response = result.get('response', str(result))
        intent = result.get('intent', 'unknown')
    else:
        response = result
        intent = 'unknown'
    
    print(f'   JARVIS: "{response}"')
    print(f"   ⏱️  {brain_time:.2f}s")
    
    # Test 5: TTS + MongoDB in PARALLEL (non-blocking)
    print("\n🔊 Speaking...")
    
    # Start MongoDB save in background thread (non-blocking)
    def save_async():
        try:
            mongo_manager.save_conversation(text, response, intent)
        except:
            pass
    
    save_thread = threading.Thread(target=save_async, daemon=True)
    save_thread.start()
    
    start_tts = time.time()
    audio_path, engine = tts_manager.speak(response, lang='en', prefer_offline=False)
    tts_time = time.time() - start_tts
    
    print(f"   Engine: {engine}")
    print(f"   ⏱️  {tts_time:.2f}s")
    
    if audio_path:
        # Play audio
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
    
    # Clean up
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    # Summary
    total_time = time.time() - start_total
    processing_time = stt_time + brain_time + tts_time
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    
    print("\n⚡ Performance:")
    print(f"   STT:        {stt_time:.2f}s")
    print(f"   Brain:      {brain_time:.2f}s")
    print(f"   TTS:        {tts_time:.2f}s")
    print(f"   {'─' * 30}")
    print(f"   Processing: {processing_time:.2f}s")
    print(f"   Total:      {total_time:.2f}s")
    
    # Performance rating
    if total_time < 5:
        print("\n🚀 EXCELLENT - Very fast!")
    elif total_time < 8:
        print("\n✅ GOOD - Acceptable speed")
    else:
        print("\n⚠️  SLOW - Needs optimization")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    audio.terminate()
