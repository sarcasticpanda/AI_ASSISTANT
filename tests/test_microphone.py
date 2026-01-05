"""
Test microphone input and show audio levels in real-time.
Use this to verify your microphone is working before testing voice loop.
"""

import pyaudio
import struct
import sys

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

def test_microphone():
    """Test microphone and display audio levels."""
    print("\n" + "="*70)
    print("🎤 MICROPHONE TEST")
    print("="*70)
    print("\n📋 INSTRUCTIONS:")
    print("  • Speak into your microphone LOUDLY and CLEARLY")
    print("  • Watch the audio level meter below")
    print("  • Energy > 2000 = Strong speech (will trigger voice loop)")
    print("  • Energy 1500-2000 = Weak speech/background noise (ignored)")
    print("  • Energy < 1500 = Silence/fan noise (ignored)")
    print("  • Press Ctrl+C to stop")
    print("\n💡 TIP: If your speech is < 2000, speak louder or move closer to mic")
    print("\n" + "="*70 + "\n")
    
    audio = pyaudio.PyAudio()
    
    try:
        # List available devices
        print("🔍 Available audio devices:")
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"   [{i}] {info['name']} (Channels: {info['maxInputChannels']})")
        
        print("\n🎧 Using default input device...")
        
        # Open stream
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("✅ Microphone connected - Listening...\n")
        
        # Monitor audio levels
        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Calculate RMS energy
                audio_samples = struct.unpack(f"{len(data)//2}h", data)
                energy = int((sum(sample**2 for sample in audio_samples) / len(audio_samples))**0.5)
                
                # Visual meter
                bar_length = min(50, energy // 20)
                bar = "█" * bar_length
                
                # Color coding with updated thresholds
                if energy > 2000:
                    status = "🎤 STRONG SPEECH  "
                elif energy > 1500:
                    status = "🔊 Speech/Noise   "
                elif energy > 500:
                    status = "📢 Background     "
                else:
                    status = "🔇 Silence        "
                
                # Print meter (overwrite previous line)
                print(f"\r{status} | Energy: {energy:5d} | {bar:50}", end="", flush=True)
                
            except Exception as e:
                print(f"\n❌ Error reading audio: {e}")
                break
    
    except KeyboardInterrupt:
        print("\n\n✅ Test complete!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        audio.terminate()
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_microphone()
