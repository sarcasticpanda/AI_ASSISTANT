"""
Simple XTTS Voice Testing - Just like we did with Arjun!
Play one voice at a time, rate it, add comment. Easy!
"""

from TTS.api import TTS
import os
import tempfile
import winsound

print("🔧 Loading XTTS-v2 model (this takes a moment)...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
print("✅ Model loaded!\n")

# Test sentences (same as Arjun testing)
test_english = "Good morning sir. I am Jarvis, your AI assistant. How may I help you today?"
test_hindi = "नमस्ते सर। मैं जार्विस हूं, आपका AI सहायक। मैं आपकी कैसे मदद कर सकता हूं?"

# 7 Male voices to test
voices = [
    "Andrew Chipper",
    "Dionisio Schuyler", 
    "Royston Min",
    "Viktor Eka",
    "Abrahan Mack",
    "Craig Gutsy",
    "Damien Black"
]

print("=" * 70)
print("🎤 OFFLINE VOICE TESTING - XTTS-v2 Male Voices")
print("=" * 70)
print("\nJust like we tested Arjun voice!")
print("Listen to each voice (English + Hindi), then rate it.\n")
print("Controls:")
print("  - Rate: Enter 1-5 stars")
print("  - Comment: Short note (e.g., 'too deep', 'perfect', 'robotic')")
print("  - Type 'skip' to skip a voice")
print("  - Type 'quit' to stop testing")
print("=" * 70)

results = []
temp_dir = tempfile.gettempdir()

for i, voice_name in enumerate(voices, 1):
    print(f"\n\n{'='*70}")
    print(f"🎤 Voice {i}/{len(voices)}: {voice_name}")
    print(f"{'='*70}")
    
    try:
        # Generate English
        print(f"\n🔊 Playing ENGLISH...")
        print(f'   "{test_english[:50]}..."')
        
        temp_file_en = os.path.join(temp_dir, f"xtts_test_en.wav")
        tts.tts_to_file(
            text=test_english,
            speaker=voice_name,
            language="en",
            file_path=temp_file_en
        )
        
        # Play using Windows sound
        winsound.PlaySound(temp_file_en, winsound.SND_FILENAME)
        os.remove(temp_file_en)
        
        # Generate Hindi
        print(f"\n🔊 Playing HINDI...")
        print(f'   "{test_hindi[:50]}..."')
        
        temp_file_hi = os.path.join(temp_dir, f"xtts_test_hi.wav")
        tts.tts_to_file(
            text=test_hindi,
            speaker=voice_name,
            language="hi",
            file_path=temp_file_hi
        )
        
        # Play using Windows sound
        winsound.PlaySound(temp_file_hi, winsound.SND_FILENAME)
        os.remove(temp_file_hi)
        
        # Get rating
        print(f"\n{'─'*70}")
        rating_input = input(f"⭐ Rate '{voice_name}' (1-5 stars, or 'skip'/'quit'): ").strip()
        
        if rating_input.lower() == 'quit':
            print("\n👋 Testing stopped!")
            break
        
        if rating_input.lower() == 'skip':
            print(f"⏭️  Skipped {voice_name}")
            results.append({
                'voice': voice_name,
                'rating': 'SKIPPED',
                'comment': ''
            })
            continue
        
        # Validate rating
        if rating_input not in ['1', '2', '3', '4', '5']:
            print("❌ Invalid rating. Skipping this voice.")
            continue
        
        rating = int(rating_input)
        stars = '⭐' * rating
        
        # Get comment
        comment = input(f"💬 Quick comment (optional, 1-2 words): ").strip()
        
        print(f"\n✅ Saved: {voice_name} - {stars} ({rating}/5)")
        if comment:
            print(f"   Comment: {comment}")
        
        results.append({
            'voice': voice_name,
            'rating': rating,
            'comment': comment
        })
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted!")
        break
    except Exception as e:
        print(f"\n❌ Error with {voice_name}: {e}")
        print("Skipping to next voice...")

# Show final results
print("\n\n" + "=" * 70)
print("📊 FINAL RESULTS - XTTS-v2 Voice Ratings")
print("=" * 70)

if results:
    print("\nAll Ratings:")
    for result in results:
        voice = result['voice']
        rating = result['rating']
        comment = result['comment']
        
        if rating == 'SKIPPED':
            print(f"\n  {voice}: ⏭️  SKIPPED")
        else:
            stars = '⭐' * rating
            print(f"\n  {voice}: {stars} ({rating}/5)")
            if comment:
                print(f"    💬 {comment}")
    
    # Find best rated
    rated = [r for r in results if r['rating'] != 'SKIPPED']
    if rated:
        best = max(rated, key=lambda x: x['rating'])
        print(f"\n{'='*70}")
        print(f"🏆 HIGHEST RATED: {best['voice']}")
        print(f"   Rating: {'⭐' * best['rating']} ({best['rating']}/5)")
        if best['comment']:
            print(f"   Comment: {best['comment']}")
        print(f"{'='*70}")
        
        print(f"\n💡 Want to use '{best['voice']}' as your offline voice?")
        print(f"   I can integrate it into the system!")
else:
    print("\n❌ No voices were rated.")

print("\n✅ Voice testing complete!")
