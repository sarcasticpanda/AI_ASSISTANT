"""
Research and test better offline TTS libraries for male voice
"""

print("\n" + "="*70)
print("  OFFLINE TTS ALTERNATIVES FOR JARVIS (MALE VOICE)")
print("="*70 + "\n")

print("Available offline TTS libraries:")
print()

alternatives = [
    {
        'name': 'pyttsx3',
        'pros': [
            '✓ Already installed',
            '✓ Male voice (Microsoft David)',
            '✓ Fast generation',
            '✓ No model download needed'
        ],
        'cons': [
            '✗ Very robotic/mechanical',
            '✗ Limited voice quality',
            '✗ No pitch control',
            '✗ Sounds old-fashioned'
        ],
        'status': 'CURRENT (but robotic)'
    },
    {
        'name': 'Coqui TTS',
        'pros': [
            '✓ Already installed',
            '✓ Neural voice (more natural)',
            '✓ Multiple models available'
        ],
        'cons': [
            '✗ Default model (ljspeech) is FEMALE',
            '✗ Slow generation (3+ seconds)',
            '✗ Large model downloads',
            '✗ No good male English models easily available'
        ],
        'status': 'INSTALLED (but female voice)'
    },
    {
        'name': 'Piper TTS',
        'pros': [
            '✓ Fast neural TTS',
            '✓ Multiple male voices available',
            '✓ Better quality than pyttsx3',
            '✓ Lightweight models',
            '✓ Offline-first design',
            '✓ Good for edge devices'
        ],
        'cons': [
            '✗ Need to install',
            '✗ Need to download model',
            '✗ More complex setup'
        ],
        'status': 'RECOMMENDED - Best quality/speed balance',
        'install': 'pip install piper-tts',
        'voices': [
            'en_US-lessac-medium (Male, clear)',
            'en_US-danny-low (Male, fast)',
            'en_US-ryan-high (Male, best quality)'
        ]
    },
    {
        'name': 'espeak-ng',
        'pros': [
            '✓ Very fast',
            '✓ Lightweight',
            '✓ Male voice available',
            '✓ Works offline'
        ],
        'cons': [
            '✗ VERY robotic (worse than pyttsx3)',
            '✗ Sounds like old computer',
            '✗ Not natural at all'
        ],
        'status': 'NOT RECOMMENDED - Too robotic'
    },
    {
        'name': 'Larynx',
        'pros': [
            '✓ Neural TTS',
            '✓ Multiple voices',
            '✓ Offline'
        ],
        'cons': [
            '✗ Complex setup',
            '✗ Heavy dependencies',
            '✗ Limited documentation'
        ],
        'status': 'NOT RECOMMENDED - Too complex'
    },
    {
        'name': 'Sherpa-ONNX',
        'pros': [
            '✓ Fast neural TTS',
            '✓ ONNX runtime (optimized)',
            '✓ Multiple voices',
            '✓ Good quality'
        ],
        'cons': [
            '✗ Need to install',
            '✗ Model setup required',
            '✗ Less documentation'
        ],
        'status': 'ALTERNATIVE - Good but complex'
    }
]

for i, lib in enumerate(alternatives, 1):
    print(f"{i}. {lib['name']}")
    print(f"   Status: {lib['status']}")
    print()
    
    print("   Pros:")
    for pro in lib['pros']:
        print(f"     {pro}")
    print()
    
    print("   Cons:")
    for con in lib['cons']:
        print(f"     {con}")
    print()
    
    if 'install' in lib:
        print(f"   Install: {lib['install']}")
    
    if 'voices' in lib:
        print(f"   Male Voices:")
        for voice in lib['voices']:
            print(f"     - {voice}")
    
    print()
    print("-" * 70)
    print()

print("\n" + "="*70)
print("  RECOMMENDATION")
print("="*70 + "\n")

print("🎯 Best Option: Piper TTS")
print()
print("Piper is specifically designed for offline TTS with:")
print("  • Fast generation (faster than Coqui)")
print("  • Natural neural voices (better than pyttsx3)")
print("  • Multiple male voices (en_US-lessac, danny, ryan)")
print("  • Lightweight models (50-100MB vs Coqui's 500MB+)")
print("  • Easy integration")
print()
print("Installation:")
print("  1. pip install piper-tts")
print("  2. Download male voice model (auto-downloads on first use)")
print("  3. Configure in tts_offline.py")
print()
print("Would you like to install Piper TTS? (Recommended)")
print()
