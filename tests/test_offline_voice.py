""""""

TEST OFFLINE VOICE PIPELINETest offline TTS voice

Tests: Microphone → faster-whisper (STT) → Qwen (Brain) → pyttsx3 David"""

"""import sys

import os

import ossys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import sys

import wavefrom colorama import init, Fore, Style

import pyaudioinit(autoreset=True)

import time

from dotenv import load_dotenvfrom core import tts_offline

import subprocess

# Add backend to path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))print("\n" + "="*70)

print("  OFFLINE VOICE TEST")

# Load environment from backend/.envprint("="*70 + "\n")

load_dotenv('backend/.env')

# Show config

from backend.core import stt_local, brain, tts_manager, mongo_managerprint(f"{Fore.GREEN}Voice Configuration:{Style.RESET_ALL}")

config = tts_offline.get_voice_info()

print("=" * 70)for key, value in config.items():

print("📵 JARVIS OFFLINE VOICE PIPELINE TEST")    print(f"  {key}: {value}")

print("=" * 70)print()



# Initialize MongoDB# Test sentences

print("\n🗄️  Initializing MongoDB...")test_cases = [

try:    "Good morning, sir. All systems are operational.",

    mongo_manager.initialize()    "My pleasure, sir. How may I assist you?",

    print("   ✅ MongoDB connected")    "Certainly, sir. Opening Chrome browser now.",

except Exception as e:    "I am Jarvis, your offline assistant."

    print(f"   ⚠️  MongoDB failed: {e}")]

    print("   ℹ️  Continuing without database")

for i, text in enumerate(test_cases, 1):

# Test 1: Check offline components    print(f"\n{Fore.CYAN}Test {i}:{Style.RESET_ALL}")

print("\n🔌 Step 1: Checking offline components...")    print(f"  Text: '{text}'")

print("-" * 70)    

    # Generate speech

# Check STT    print("  Generating...")

stt_status = stt_local.get_status()    audio_path = tts_offline.speak_offline(text, lang='en')

print(f"   faster-whisper: {'✅' if stt_status['faster_whisper'] else '❌'}")    

print(f"   Vosk: {'✅' if stt_status['vosk'] else '❌'}")    if audio_path:

        print(f"{Fore.GREEN}  ✓ Generated: {audio_path}{Style.RESET_ALL}")

if not stt_status['faster_whisper']:        

    print("\n❌ faster-whisper not available!")        # Play audio

    exit(1)        print(f"  Playing...")

        subprocess.run(['start', audio_path], shell=True)

# Check TTS        

tts_status = tts_manager.get_status()        if i < len(test_cases):

print(f"   TTS offline: {'✅' if tts_status['offline_tts']['available'] else '❌'}")            cont = input(f"\n  {Fore.YELLOW}Continue to next? (y/n): {Style.RESET_ALL}")

print(f"   Engine: {tts_status['offline_tts']['engine']}")            if cont.lower() != 'y':

                break

# Test 2: Record voice    else:

print("\n🎤 Step 2: Recording your voice...")        print(f"{Fore.RED}  ✗ Failed to generate audio{Style.RESET_ALL}")

print("-" * 70)        break



CHUNK = 1024print(f"\n{Fore.GREEN}✨ Test complete!{Style.RESET_ALL}\n")
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
OUTPUT_FILE = "test_offline_audio.wav"

audio = pyaudio.PyAudio()

print("\n   You can test these skills (works offline):")
print("   • 'What time is it?'")
print("   • 'What's the date today?'")
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
    
    # Test 3: STT (faster-whisper OFFLINE)
    print("\n📝 Step 3: Transcribing with faster-whisper (OFFLINE)...")
    print("-" * 70)
    print("   ⏳ First run will download ~140MB model (one-time only)...")
    
    start_time = time.time()
    text = stt_local.transcribe_file(OUTPUT_FILE, method="whisper")
    stt_time = time.time() - start_time
    
    print(f"\n   YOU SAID: \"{text}\"")
    print(f"   ⏱️  STT Time: {stt_time:.2f}s")
    
    if not text or "[" in text:
        print("\n❌ Transcription failed!")
        exit(1)
    
    # Test 4: Brain Processing (Qwen - still needs internet)
    print("\n🧠 Step 4: Processing with Qwen AI...")
    print("-" * 70)
    print("   ⚠️  Note: Qwen still requires internet")
    
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
    
    # Test 5: TTS (pyttsx3 OFFLINE)
    print("\n🔊 Step 5: Speaking with pyttsx3 (OFFLINE)...")
    print("-" * 70)
    
    start_time = time.time()
    audio_path, engine = tts_manager.speak(response, lang='en', prefer_offline=True)
    tts_time = time.time() - start_time
    
    print(f"   Engine: {engine}")
    print(f"   ⏱️  TTS Time: {tts_time:.2f}s")
    
    if audio_path:
        print(f"   Audio: {audio_path}")
        
        # Play audio
        print("\n   🔊 Playing audio...")
        if audio_path == "pyttsx3_direct":
            print("   ✅ Audio played directly (no file saved)")
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
    print("✅ OFFLINE VOICE PIPELINE TEST COMPLETE!")
    print("=" * 70)
    
    print("\n📊 Performance Summary:")
    print(f"   STT (faster-whisper): {stt_time:.2f}s")
    print(f"   Brain (Qwen):         {brain_time:.2f}s")
    print(f"   TTS (pyttsx3):        {tts_time:.2f}s")
    print(f"   {'─' * 40}")
    print(f"   Total Processing:     {total_time:.2f}s")
    
    print("\n✅ All offline components working!")
    print("\n⚠️  Note: Brain (Qwen) still requires internet")
    print("   For 100% offline, we'd need a local LLM")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    audio.terminate()
