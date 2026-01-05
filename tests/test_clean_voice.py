"""
CLEAN VOICE TEST - Using the approach that works
Simple flow: Record → STT → Brain → TTS → Repeat
"""

import os
import sys
import wave
import pyaudio
import time
import struct
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv('backend/.env')

from backend.core import stt_online, brain, tts_manager, tts_online

print("\n" + "="*70)
print("🎤 JARVIS VOICE ASSISTANT - CLEAN TEST")
print("="*70)

# Audio config
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

audio = pyaudio.PyAudio()

def record_command():
    """Record with visual feedback and auto-stop"""
    print("\n🔴 Press ENTER to start recording...")
    input()
    
    print("\n🎙️  RECORDING... Speak your command!")
    print("   (Auto-stops after 1.5s silence)")
    
    # Beep to indicate start
    import winsound
    winsound.Beep(1000, 100)
    
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    silence_threshold = 150
    speech_threshold = 230
    silence_chunks = 0
    max_silence = 24
    recording = False
    started = False
    
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        # Calculate energy
        samples = struct.unpack(f"{len(data)//2}h", data)
        energy = int((sum(s**2 for s in samples) / len(samples))**0.5)
        
        # Visual feedback
        bar = "█" * min(40, energy // 6)
        status = "🎤 RECORDING" if energy > speech_threshold else "⏸️  waiting"
        print(f"\r   {status} | {energy:4d} | {bar:40} ", end="", flush=True)
        
        # Start on speech
        if not started and energy > speech_threshold:
            started = True
            recording = True
            frames = [data]
            silence_chunks = 0
            continue
        
        # Continue recording
        if recording:
            frames.append(data)
            
            if energy < silence_threshold:
                silence_chunks += 1
                if silence_chunks >= max_silence:
                    break
            else:
                silence_chunks = 0
    
    stream.stop_stream()
    stream.close()
    winsound.Beep(800, 100)
    print("\n")
    
    # Save
    filename = "temp_voice.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return filename

print("\n📡 Checking connection...")
if not tts_manager.is_online():
    print("⚠️  No internet! Please connect to internet.")
    exit(1)
print("✅ Online - using Groq STT + Edge TTS\n")

try:
    while True:
        # Record
        audio_file = record_command()
        
        # STT
        print("🎧 Transcribing...")
        start = time.time()
        text = stt_online.transcribe_online(audio_file)
        stt_time = time.time() - start
        
        if not text or text.strip() == "":
            print("❌ No speech detected\n")
            os.remove(audio_file)
            continue
        
        print(f"   📝 You: {text}")
        print(f"   ⏱️  STT: {stt_time:.2f}s\n")
        
        # Brain
        print("🧠 Processing...")
        start = time.time()
        result = brain.process_command(text)
        brain_time = time.time() - start
        
        response = result.get("response", "")
        expects_followup = result.get("expects_followup", False)
        followup_timeout = result.get("followup_timeout", 10)
        
        print(f"   💬 Jarvis: {response}")
        print(f"   ⏱️  Brain: {brain_time:.2f}s")
        
        if expects_followup:
            print(f"   ❓ Expects follow-up (timeout: {followup_timeout}s)")
        print()
        
        # TTS
        print("🔊 Speaking...")
        start = time.time()
        audio_path, engine = tts_manager.speak(response)
        if audio_path:
            tts_online.play_audio(audio_path)
            # Clean up audio file
            try:
                os.remove(audio_path)
            except:
                pass
        tts_time = time.time() - start
        print(f"   ⏱️  TTS: {tts_time:.2f}s ({engine})\n")
        
        # Summary
        total = stt_time + brain_time + tts_time
        print("="*70)
        print(f"⏱️  TOTAL: {total:.2f}s | STT: {stt_time:.1f}s | Brain: {brain_time:.1f}s | TTS: {tts_time:.1f}s")
        print("="*70 + "\n")
        
        # Handle follow-up
        if expects_followup:
            print(f"⏰ Waiting {followup_timeout}s for your response...")
            print("   Press ENTER to respond, or wait for timeout\n")
            
            # Simple timeout - you can respond or wait
            import threading
            responded = threading.Event()
            
            def wait_for_input():
                input()
                responded.set()
            
            thread = threading.Thread(target=wait_for_input, daemon=True)
            thread.start()
            thread.join(timeout=followup_timeout)
            
            if responded.is_set():
                print("✅ You responded - continuing conversation\n")
                # Loop continues to record next input
            else:
                print("⏱️  Timeout - closing conversation")
                print("💬 Jarvis: Let me know if you need anything else!")
                audio_path, _ = tts_manager.speak("Let me know if you need anything else!")
                if audio_path:
                    tts_online.play_audio(audio_path)
                    try:
                        os.remove(audio_path)
                    except:
                        pass
                print()
        
        # Cleanup
        os.remove(audio_file)

except KeyboardInterrupt:
    print("\n\n✅ Goodbye!")
    audio.terminate()
