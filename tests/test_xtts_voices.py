"""
Test XTTS-v2 voices for offline TTS
Goal: Find male voice similar to online Arjun (calm, energetic, not robotic)
"""

from TTS.api import TTS
import os

# Initialize XTTS-v2
print("🔧 Loading XTTS-v2 model...")
print("⚠️  First time will download ~2GB model, please wait...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# Test sentences (English + Hindi)
test_sentences = [
    "Hello! I am Jarvis, your AI assistant.",
    "The weather today is sunny and pleasant.",
    "मैं हिंदी भी बोल सकता हूं।",  # "I can speak Hindi too"
    "Let me help you with that task."
]

# Available speaker voices in XTTS-v2
# These are pre-trained voices from the model
speakers = [
    "Claribel Dervla",     # Female
    "Daisy Studious",      # Female  
    "Gracie Wise",         # Female
    "Tammie Ema",          # Female
    "Alison Dietlinde",    # Female
    "Ana Florence",        # Female
    "Annmarie Nele",       # Female
    "Asya Anara",          # Female
    "Brenda Stern",        # Female
    "Gitta Nikolina",      # Female
    "Henriette Usha",      # Female
    "Sofia Hellen",        # Female
    "Tammy Grit",          # Female
    "Tanja Adelina",       # Female
    "Vjollca Johnnie",     # Female
    "Andrew Chipper",      # Male ✓
    "Badr Odhiambo",       # Male ✓
    "Dionisio Schuyler",   # Male ✓
    "Royston Min",         # Male ✓
    "Viktor Eka",          # Male ✓
    "Abrahan Mack",        # Male ✓
    "Adde Michal",         # Male ✓
    "Baldur Sanjin",       # Male ✓
    "Craig Gutsy",         # Male ✓
    "Damien Black",        # Male ✓
    "Gilberto Mathias",    # Male ✓
    "Ilkin Urbano",        # Male ✓
    "Kazuhiko Atallah",    # Male ✓
    "Ludvig Milivoj",      # Male ✓
    "Suad Qasim",          # Male ✓
    "Torcull Diarmuid",    # Male ✓
    "Viktor Menelaos",     # Male ✓
    "Zacharie Aimilios",   # Male ✓
]

# Filter male voices only
male_speakers = [
    "Andrew Chipper",
    "Dionisio Schuyler", 
    "Royston Min",
    "Viktor Eka",
    "Abrahan Mack",
    "Craig Gutsy",
    "Damien Black"
]

print(f"\n📢 Testing {len(male_speakers)} male voices for Jarvis")
print("=" * 60)

output_dir = "c:/Users/Lunar Panda/3-Main/assistant/voice_tests/xtts_samples"
os.makedirs(output_dir, exist_ok=True)

for speaker in male_speakers:
    print(f"\n🎤 Testing: {speaker}")
    print("-" * 60)
    
    try:
        # Test English
        output_file = f"{output_dir}/{speaker.replace(' ', '_')}_english.wav"
        tts.tts_to_file(
            text=test_sentences[0],
            speaker=speaker,
            language="en",
            file_path=output_file
        )
        print(f"   ✅ English: {output_file}")
        
        # Test Hindi
        output_file_hindi = f"{output_dir}/{speaker.replace(' ', '_')}_hindi.wav"
        tts.tts_to_file(
            text=test_sentences[2],
            speaker=speaker,
            language="hi",
            file_path=output_file_hindi
        )
        print(f"   ✅ Hindi: {output_file_hindi}")
        
        # Play sample
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        
        # Wait for playback
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        rating = input(f"\n   Rate {speaker} (1-5 stars, or 's' to skip): ")
        
        if rating.lower() == 's':
            print(f"   ⏭️  Skipped {speaker}")
            continue
            
        print(f"   ⭐ Rating: {rating}/5")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("-" * 60)

print("\n✅ Voice testing complete!")
print(f"📁 Audio files saved to: {output_dir}")
print("\nNOTE: All files saved for comparison. Listen and pick your favorite!")
