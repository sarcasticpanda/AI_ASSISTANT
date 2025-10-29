"""
Debug: Check available pyttsx3 voices and select male voice
"""
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print("\n" + "="*70)
print("AVAILABLE VOICES ON YOUR SYSTEM:")
print("="*70 + "\n")

for i, voice in enumerate(voices):
    print(f"Voice {i}:")
    print(f"  ID: {voice.id}")
    print(f"  Name: {voice.name}")
    print(f"  Languages: {voice.languages}")
    print(f"  Gender: {voice.gender if hasattr(voice, 'gender') else 'Unknown'}")
    print(f"  Age: {voice.age if hasattr(voice, 'age') else 'Unknown'}")
    print()

# Find male voices
print("\n" + "="*70)
print("MALE VOICE DETECTION:")
print("="*70 + "\n")

male_voice_found = None
for i, voice in enumerate(voices):
    voice_name = voice.name.lower()
    voice_id = voice.id.lower()
    
    # Check for male indicators
    is_male = False
    reason = []
    
    if hasattr(voice, 'gender') and voice.gender:
        if 'male' in str(voice.gender).lower() and 'female' not in str(voice.gender).lower():
            is_male = True
            reason.append(f"gender={voice.gender}")
    
    # Check name
    if any(name in voice_name for name in ['david', 'mark', 'ryan', 'james', 'george', 'zira']):
        # Note: Zira is actually female, need to exclude
        if 'zira' not in voice_name:
            is_male = True
            reason.append(f"name matches male pattern")
    
    # Check ID for male markers
    if 'male' in voice_id and 'female' not in voice_id:
        is_male = True
        reason.append(f"ID contains 'male'")
    
    if is_male:
        print(f"✓ Voice {i}: {voice.name}")
        print(f"  Reasons: {', '.join(reason)}")
        print(f"  ID: {voice.id}")
        if male_voice_found is None:
            male_voice_found = i
            print(f"  >>> SELECTING THIS AS DEFAULT MALE VOICE")
        print()

if male_voice_found is None:
    print("✗ No male voice found! Will use Voice 0 (default)")
    print(f"  Voice 0: {voices[0].name}")
else:
    print(f"\n✓ Male voice selected: Voice {male_voice_found}")

engine.stop()
