"""
Test lightweight TTS models for offline use
Using VITS models (~50MB) instead of XTTS (~2GB)
"""

from TTS.api import TTS
import os

print("🔧 Available lightweight TTS models:")
print("=" * 60)

# Lightweight single-language models
models_to_test = [
    {
        "name": "tts_models/en/ljspeech/vits",
        "language": "en",
        "description": "Female voice, lightweight",
        "size": "~50MB"
    },
    {
        "name": "tts_models/en/ljspeech/tacotron2-DDC",
        "language": "en", 
        "description": "Female voice, neural",
        "size": "~100MB"
    }
]

# For Hindi, we'll need to use pyttsx3 or look for alternatives
print("\n⚠️  Note: Lightweight models are mostly English-only")
print("For Hindi support offline, we'll use pyttsx3 or need XTTS-v2 (2GB)\n")

# Test sentence
test_text = "Hello! I am Jarvis, your AI assistant. How can I help you today?"

output_dir = "c:/Users/Lunar Panda/3-Main/assistant/voice_tests/lightweight_samples"
os.makedirs(output_dir, exist_ok=True)

print("\n🎤 Testing lightweight models...")
print("=" * 60)

for model_info in models_to_test:
    model_name = model_info["name"]
    print(f"\n📦 Model: {model_name}")
    print(f"   Size: {model_info['size']}")
    print(f"   Description: {model_info['description']}")
    print(f"   Downloading and testing...")
    
    try:
        tts = TTS(model_name=model_name)
        
        output_file = f"{output_dir}/{model_name.replace('/', '_')}.wav"
        tts.tts_to_file(
            text=test_text,
            file_path=output_file
        )
        
        print(f"   ✅ Generated: {output_file}")
        
        # Play sample
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        rating = input(f"\n   Rate this voice (1-5 stars): ")
        print(f"   ⭐ Rating: {rating}/5")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("💡 Recommendation:")
print("   For BEST quality with Hindi support: Keep trying XTTS-v2 download")
print("   For FAST lightweight: Use pyttsx3 (already working)")
print(f"\n📁 Samples saved to: {output_dir}")
