"""
Final fine-tuning: Arjun at +11% (slightly slower) with energetic + calm pitch
"""
import asyncio
import edge_tts
import tempfile
import subprocess

async def test_final_tuning():
    """Test Arjun with final fine-tuned settings"""
    
    test_sentences = {
        "hindi": "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।",
        "english": "Good morning, sir. All systems are operational and ready for deployment.",
        "question": "Sir, would you like me to open Chrome browser?",
        "mixed": "Sir, Chrome browser open हो गया है। और क्या मदद चाहिए?",
        "casual": "Sure, I'm on it.",
        "casual_hindi": "समझ गया। मैं करता हूं।"
    }
    
    # Fine-tuned variations at +11% (slightly slower than +13%)
    # Energetic + calm = moderate pitch increase
    
    configs = [
        {
            "name": "Slightly Energetic + Calm",
            "rate": "+11%",
            "pitch": "+7Hz"  # A bit energetic but calm
        },
        {
            "name": "Moderately Energetic + Calm",
            "rate": "+11%",
            "pitch": "+9Hz"  # More energetic, still calm
        },
        {
            "name": "Balanced Energy (Recommended)",
            "rate": "+11%",
            "pitch": "+8Hz"  # Perfect balance
        },
        {
            "name": "Alternative: +10% speed",
            "rate": "+10%",
            "pitch": "+8Hz"  # Even slower if +11% is still fast
        }
    ]
    
    for config in configs:
        print("\n" + "="*70)
        print(f"🔊 ARJUN - {config['name']}")
        print(f"   Rate: {config['rate']}, Pitch: {config['pitch']}")
        print("="*70)
        
        # Test all sentence types
        for test_type, sentence in test_sentences.items():
            print(f'\n{test_type.upper()}: "{sentence}"')
            
            communicate = edge_tts.Communicate(
                sentence,
                "hi-IN-ArjunNeural",
                rate=config['rate'],
                pitch=config['pitch']
            )
            
            audio_file = tempfile.mktemp(suffix='.mp3')
            await communicate.save(audio_file)
            print(f"✓ Saved: {audio_file}")
            subprocess.run(['start', audio_file], shell=True)
            
            import time
            time.sleep(1)  # Small delay between files
        
        rating = input("\n\nRate this overall (1-5): ")
        print(f"You rated: {rating}/5")
        
        review = input("One word review (optional): ")
        if review:
            print(f"Review: {review}")
        
        choice = input("\nTest next variation? (y/n): ")
        if choice.lower() != 'y':
            print(f"\n✅ FINAL SELECTION: {config['name']}")
            print(f"   Settings: Rate={config['rate']}, Pitch={config['pitch']}")
            print(f"\n🎯 This will be your Jarvis voice!")
            
            # Save to file
            with open('voice_tests/SELECTED_VOICE.txt', 'w') as f:
                f.write(f"JARVIS VOICE CONFIGURATION\n")
                f.write(f"=========================\n\n")
                f.write(f"Voice: hi-IN-ArjunNeural (Male, Indian)\n")
                f.write(f"Rate: {config['rate']}\n")
                f.write(f"Pitch: {config['pitch']}\n")
                f.write(f"Description: {config['name']}\n")
                f.write(f"Your Rating: {rating}/5\n")
                f.write(f"Review: {review}\n")
            
            print(f"\n✓ Saved settings to: voice_tests/SELECTED_VOICE.txt")
            break
    
    print("\n✨ Voice selection complete!")
    print("\nNext steps:")
    print("  1. Configure this as default TTS in backend")
    print("  2. Test with actual Jarvis responses")
    print("  3. Integrate with STT and communication loop")

if __name__ == "__main__":
    asyncio.run(test_final_tuning())
