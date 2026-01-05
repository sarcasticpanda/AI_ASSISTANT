"""
SIMPLE VOICE TEST - Press ENTER to record, automatic VAD to stop
This uses a simple approach that WORKS:
1. Press ENTER to start recording
2. Speak your command
3. Automatic silence detection stops recording
4. Process command
"""

import os
import sys
import wave
import pyaudio
import time
import struct

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core import stt_local, brain, tts_manager

print("\n" + "="*70)
print("🎤 SIMPLE VOICE ASSISTANT TEST")
print("="*70)
print("\n📋 HOW IT WORKS:")
print("  1. Press ENTER to start recording")
print("  2. Speak your command CLEARLY and LOUDLY")
print("  3. Stop speaking - it auto-detects 1.5s silence and stops")
print("  4. Processing happens automatically")
print("\n💡 IMPORTANT:")
print("  • Speak clearly into your microphone")
print("  • Energy must exceed 230 to start recording")
print("  • Energy below 150 = silence (stops recording)")
print("  • Watch the energy meter when you speak")
print("\n⚠️  If it picks up fan noise, we'll adjust thresholds")
print("="*70 + "\n")

# Audio config
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

audio = pyaudio.PyAudio()

def record_with_vad():
    """Record audio with automatic silence detection"""
    print("🔴 Press ENTER to start recording...")
    input()
    
    print("\n🎙️  RECORDING... Speak now!")
    print("   (Will stop after 1.5 seconds of silence)")
    
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
    silence_threshold = 150   # Below this = silence/fan noise
    speech_threshold = 230    # Must exceed this to start recording
    silence_chunks = 0
    max_silence = 24  # ~1.5 seconds
    recording = False
    started = False
    
    print("   Waiting for speech (energy > 230)...")
    
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        # Calculate energy
        samples = struct.unpack(f"{len(data)//2}h", data)
        energy = int((sum(s**2 for s in samples) / len(samples))**0.5)
        
        # Visual feedback
        bar = "█" * min(50, energy // 5)
        status = "🎤 SPEAKING" if energy > speech_threshold else "🔇 waiting..."
        print(f"\r   {status} | Energy: {energy:4d} | {bar:50} ", end="", flush=True)
        
        # Start recording only on strong speech
        if not started and energy > speech_threshold:
            print("\n   ✅ Speech detected! Recording...")
            started = True
            recording = True
            frames = [data]
            silence_chunks = 0
            continue
        
        # Continue recording
        if recording:
            frames.append(data)
            
            # Silence detection
            if energy < silence_threshold:
                silence_chunks += 1
                if silence_chunks >= max_silence:
                    print("\n\n🔇 Silence detected - stopping...")
                    recording = False
                    break
            else:
                silence_chunks = 0
    
    stream.stop_stream()
    stream.close()
    winsound.Beep(800, 100)
    
    # Save to file
    filename = "simple_test.wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print(f"💾 Saved: {filename}\n")
    return filename

try:
    while True:
        # Record
        audio_file = record_with_vad()
        
        # STT
        print("🎧 Transcribing...")
        start = time.time()
        text = stt_local.transcribe_file(audio_file)
        stt_time = time.time() - start
        
        if not text or text.strip() == "":
            print("❌ No speech detected. Try speaking louder!\n")
            continue
        
        print(f"   You said: \"{text}\"")
        print(f"   STT time: {stt_time:.2f}s\n")
        
        # Brain
        print("🧠 Processing...")
        start = time.time()
        result = brain.process_command(text)
        brain_time = time.time() - start
        
        response = result.get("response", "")
        print(f"   Response: \"{response}\"")
        print(f"   Brain time: {brain_time:.2f}s\n")
        
        # TTS
        print("🔊 Speaking...")
        start = time.time()
        tts_manager.speak(response, use_offline=True)
        tts_time = time.time() - start
        print(f"   TTS time: {tts_time:.2f}s\n")
        
        # Summary
        total = stt_time + brain_time + tts_time
        print("="*70)
        print(f"⏱️  TOTAL TIME: {total:.2f}s (STT: {stt_time:.1f}s | Brain: {brain_time:.1f}s | TTS: {tts_time:.1f}s)")
        print("="*70 + "\n")
        
        # Cleanup
        os.remove(audio_file)

except KeyboardInterrupt:
    print("\n\n✅ Test complete!")
    audio.terminate()
