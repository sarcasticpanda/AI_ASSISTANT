"""
Test XTTS-v2 voices with live playback and tweaking
Similar to online voice testing - play, rate, and adjust!
"""

from TTS.api import TTS
import pygame
import os
import tempfile

print("🔧 Loading XTTS-v2 model...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# Initialize pygame for audio playback
pygame.mixer.init()

# Test sentences
test_sentences = {
    "english": "Hello! I am Jarvis, your AI assistant. How can I help you today?",
    "hindi": "मैं हिंदी भी बोल सकता हूं। मैं आपका सहायक जार्विस हूं।",
    "mix": "Hello! मैं जार्विस हूं, your AI assistant."
}

# Male voices to test
male_speakers = [
    "Andrew Chipper",
    "Dionisio Schuyler", 
    "Royston Min",
    "Viktor Eka",
    "Abrahan Mack",
    "Craig Gutsy",
    "Damien Black"
]

print(f"\n🎤 Interactive XTTS Voice Testing")
print("=" * 60)
print("Commands:")
print("  [Enter] = Play English")
print("  'h' = Play Hindi")
print("  'm' = Play Mixed (English + Hindi)")
print("  'r' = Rate this voice (1-5 stars)")
print("  's' = Skip to next voice")
print("  'q' = Quit")
print("=" * 60)

ratings = {}
temp_dir = tempfile.gettempdir()

for speaker in male_speakers:
    print(f"\n{'='*60}")
    print(f"🎤 Voice: {speaker}")
    print(f"{'='*60}")
    
    while True:
        choice = input("\n[Enter/h/m/r/s/q]: ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Exiting voice test...")
            break
        
        if choice == 's':
            print(f"⏭️  Skipped {speaker}")
            break
        
        if choice == 'r':
            rating = input(f"⭐ Rate {speaker} (1-5 stars): ").strip()
            ratings[speaker] = rating
            print(f"✅ Saved rating: {rating}/5")
            continue
        
        # Select language
        if choice == 'h':
            text = test_sentences["hindi"]
            lang = "hi"
            lang_name = "Hindi"
        elif choice == 'm':
            text = test_sentences["mix"]
            lang = "en"  # Mixed uses English engine
            lang_name = "Mixed"
        else:  # default: English
            text = test_sentences["english"]
            lang = "en"
            lang_name = "English"
        
        print(f"\n🔊 Playing {speaker} - {lang_name}...")
        print(f"   Text: {text[:50]}...")
        
        try:
            # Generate to temp file
            temp_file = os.path.join(temp_dir, f"xtts_test_{speaker.replace(' ', '_')}.wav")
            
            tts.tts_to_file(
                text=text,
                speaker=speaker,
                language=lang,
                file_path=temp_file
            )
            
            # Load and play with pygame
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if choice == 'q':
        break

# Show ratings
print("\n" + "=" * 60)
print("📊 VOICE RATINGS:")
print("=" * 60)
if ratings:
    for voice, rating in ratings.items():
        stars = "⭐" * int(rating) if rating.isdigit() else rating
        print(f"  {voice}: {stars}")
    
    # Find highest rated
    numeric_ratings = {k: int(v) for k, v in ratings.items() if v.isdigit()}
    if numeric_ratings:
        best_voice = max(numeric_ratings, key=numeric_ratings.get)
        best_rating = numeric_ratings[best_voice]
        print(f"\n🏆 Top rated: {best_voice} ({best_rating}/5)")
else:
    print("  No ratings recorded")

print("\n✅ Voice testing complete!")
