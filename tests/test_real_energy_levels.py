"""
Test to measure ACTUAL energy levels in your environment.
This will help us set realistic thresholds.
"""

import pyaudio
import struct
import time

# Audio config
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

def measure_energy():
    """Measure real energy levels in different conditions"""
    
    audio = pyaudio.PyAudio()
    
    print("\n" + "="*70)
    print("🔬 REAL ENERGY LEVEL MEASUREMENT")
    print("="*70)
    
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    # Test 1: Pure silence
    print("\n📊 TEST 1: PURE SILENCE")
    print("   Please stay COMPLETELY SILENT for 5 seconds...")
    print("   Don't move, don't breathe loudly, just freeze!")
    time.sleep(2)
    
    silence_energies = []
    for i in range(80):  # 5 seconds
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = struct.unpack(f"{len(data)//2}h", data)
        energy = int((sum(s**2 for s in samples) / len(samples))**0.5)
        silence_energies.append(energy)
        
        if i % 16 == 0:  # Every second
            bar = "█" * min(50, energy // 2)
            print(f"   [{i//16 + 1}s] Energy: {energy:4d} | {bar}")
    
    silence_avg = sum(silence_energies) / len(silence_energies)
    silence_max = max(silence_energies)
    print(f"\n   ✅ Pure Silence Results:")
    print(f"      Average: {silence_avg:.1f}")
    print(f"      Maximum: {silence_max}")
    print(f"      Minimum: {min(silence_energies)}")
    
    # Test 2: Normal speaking
    print("\n📊 TEST 2: NORMAL SPEAKING")
    print("   Now speak NORMALLY for 5 seconds...")
    print("   Say things like: 'What time is it? Tell me about the weather.'")
    time.sleep(2)
    
    speech_energies = []
    for i in range(80):  # 5 seconds
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = struct.unpack(f"{len(data)//2}h", data)
        energy = int((sum(s**2 for s in samples) / len(samples))**0.5)
        speech_energies.append(energy)
        
        if i % 16 == 0:  # Every second
            bar = "█" * min(50, energy // 10)
            print(f"   [{i//16 + 1}s] Energy: {energy:4d} | {bar}")
    
    speech_avg = sum(speech_energies) / len(speech_energies)
    speech_max = max(speech_energies)
    
    print(f"\n   ✅ Normal Speaking Results:")
    print(f"      Average: {speech_avg:.1f}")
    print(f"      Maximum: {speech_max}")
    print(f"      Minimum: {min(speech_energies)}")
    
    # Test 3: Loud speaking
    print("\n📊 TEST 3: LOUD SPEAKING")
    print("   Now speak LOUDLY for 5 seconds...")
    print("   Speak like you're calling someone across a room!")
    time.sleep(2)
    
    loud_energies = []
    for i in range(80):  # 5 seconds
        data = stream.read(CHUNK, exception_on_overflow=False)
        samples = struct.unpack(f"{len(data)//2}h", data)
        energy = int((sum(s**2 for s in samples) / len(samples))**0.5)
        loud_energies.append(energy)
        
        if i % 16 == 0:  # Every second
            bar = "█" * min(50, energy // 10)
            print(f"   [{i//16 + 1}s] Energy: {energy:4d} | {bar}")
    
    loud_avg = sum(loud_energies) / len(loud_energies)
    loud_max = max(loud_energies)
    
    print(f"\n   ✅ Loud Speaking Results:")
    print(f"      Average: {loud_avg:.1f}")
    print(f"      Maximum: {loud_max}")
    print(f"      Minimum: {min(loud_energies)}")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Analysis
    print("\n" + "="*70)
    print("📈 ANALYSIS & RECOMMENDATIONS")
    print("="*70)
    
    print(f"\n1. SILENCE BASELINE:")
    print(f"   Average ambient noise: {silence_avg:.1f}")
    print(f"   Peak ambient noise: {silence_max}")
    
    print(f"\n2. SPEECH DETECTION:")
    print(f"   Normal speech average: {speech_avg:.1f}")
    print(f"   Normal speech peak: {speech_max}")
    print(f"   SNR (Signal-to-Noise Ratio): {speech_avg / silence_avg:.1f}x")
    
    print(f"\n3. RECOMMENDED THRESHOLDS:")
    
    # Calculate smart thresholds
    # Speech threshold should be between silence max and speech average
    recommended_speech = int((silence_max + speech_avg) / 2)
    # But ensure it's at least 2x silence average
    recommended_speech = max(recommended_speech, int(silence_avg * 2))
    
    # Silence threshold should be just above ambient noise
    recommended_silence = int(silence_avg + (silence_max - silence_avg) * 0.5)
    
    print(f"   Speech threshold: {recommended_speech} (triggers recording)")
    print(f"   Silence threshold: {recommended_silence} (stops recording)")
    print(f"   Min speech duration: 0.3-0.5s (5-8 chunks)")
    
    print(f"\n4. VALIDATION:")
    if speech_avg > recommended_speech:
        print(f"   ✅ Normal speech ({speech_avg:.1f}) > threshold ({recommended_speech}) ✅")
    else:
        print(f"   ⚠️  WARNING: Normal speech ({speech_avg:.1f}) < threshold ({recommended_speech})")
        print(f"   You'll need to speak louder or lower the threshold!")
    
    if loud_avg > recommended_speech:
        print(f"   ✅ Loud speech ({loud_avg:.1f}) > threshold ({recommended_speech}) ✅")
    
    if silence_max < recommended_speech:
        print(f"   ✅ Silence ({silence_max}) < threshold ({recommended_speech}) ✅")
    else:
        print(f"   ⚠️  WARNING: Some ambient noise ({silence_max}) > threshold ({recommended_speech})")
        print(f"   May cause false triggers!")
    
    print("\n" + "="*70)
    print("✅ Test complete! Use these thresholds in phase1_online.py")
    print("="*70)
    
    return {
        'silence_avg': silence_avg,
        'silence_max': silence_max,
        'speech_avg': speech_avg,
        'speech_max': speech_max,
        'loud_avg': loud_avg,
        'loud_max': loud_max,
        'recommended_speech_threshold': recommended_speech,
        'recommended_silence_threshold': recommended_silence
    }

if __name__ == "__main__":
    results = measure_energy()
