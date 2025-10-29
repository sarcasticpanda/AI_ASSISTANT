"""
STEP 1: Simple STT Test
Record your voice → Send to Groq Whisper → Get text back
"""

import os
import time
import wave
import pyaudio
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

print("=" * 70)
print("🎤 STEP 1: Testing Speech-to-Text")
print("=" * 70)

# Check API key
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    print("\n❌ ERROR: GROQ_API_KEY not found!")
    print("   Add it to your .env file")
    exit(1)

print(f"\n✅ Groq API Key found")
client = Groq(api_key=groq_key)

# Recording settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
OUTPUT_FILE = "voice_test.wav"

print(f"\n📝 Settings: {RECORD_SECONDS}s recording, 16kHz, Mono")

# Initialize microphone
audio = pyaudio.PyAudio()

# Show available microphones
print("\n📋 Available Microphones:")
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"   [{i}] {info['name']}")

# Countdown
print("\n" + "=" * 70)
print("🔴 GET READY TO SPEAK!")
print("=" * 70)
for i in [3, 2, 1]:
    print(f"\n{i}...")
    time.sleep(1)

print(f"\n🎤 RECORDING NOW! ({RECORD_SECONDS} seconds)")
print("   Say: 'Hello Jarvis, what's the weather today?'")
print()

try:
    # Open stream
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    total_chunks = int(RATE / CHUNK * RECORD_SECONDS)
    
    # Record
    for i in range(total_chunks):
        data = stream.read(CHUNK)
        frames.append(data)
        
        # Progress bar
        if i % 5 == 0:
            percent = int((i / total_chunks) * 100)
            bar = "█" * (percent // 5) + "░" * (20 - percent // 5)
            print(f"   [{bar}] {percent}%", end='\r')
    
    print(f"\n\n✅ Recording complete!")
    
    # Stop stream
    stream.stop_stream()
    stream.close()
    
    # Save to file
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    wf = wave.open(OUTPUT_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"✅ Saved!")
    
    # Transcribe with Groq
    print(f"\n🔄 Sending to Groq Whisper API...")
    
    with open(OUTPUT_FILE, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=(OUTPUT_FILE, f.read()),
            model="whisper-large-v3-turbo",
            language="en",
            response_format="json"
        )
    
    # Show result
    print("\n" + "=" * 70)
    print("✅ TRANSCRIPTION SUCCESS!")
    print("=" * 70)
    print(f"\nYou said:\n\n   \"{transcription.text}\"\n")
    print("=" * 70)
    
    # Clean up
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    print("\n✅ STEP 1 COMPLETE: STT is working!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    audio.terminate()
