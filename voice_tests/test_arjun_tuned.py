"""
Test Arjun at +13.5% with calm + enthusiastic tone
Edge TTS supports pitch adjustment to make voice calmer/enthusiastic
"""
import asyncio
import edge_tts
import tempfile
import subprocess

async def test_arjun_tuned():
    """Test Arjun with fine-tuned settings"""
    
    test_sentences = {
        "hindi": "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।",
        "english": "Good morning, sir. All systems are operational and ready for deployment.",
        "mixed": "Sir, Chrome browser open हो गया है। और क्या मदद चाहिए?"
    }
    
    # Different pitch variations
    # Negative pitch = calmer, deeper
    # Positive pitch = enthusiastic, higher
    # Combining both: slightly lower pitch for calm, but with good rate for enthusiasm
    # Note: Rate must be whole numbers only (Edge TTS limitation)
    
    configs = [
        {
            "name": "Original (no pitch change)",
            "rate": "+13%",
            "pitch": "+0Hz"
        },
        {
            "name": "Calmer (lower pitch)",
            "rate": "+13%",
            "pitch": "-10Hz"  # Deeper, calmer voice
        },
        {
            "name": "Enthusiastic (higher pitch)",
            "rate": "+13%",
            "pitch": "+5Hz"  # Slightly higher, more energetic
        },
        {
            "name": "Balanced (calm + enthusiastic)",
            "rate": "+13%",
            "pitch": "-3Hz"  # Slightly deeper for calm, but fast rate for energy
        },
        {
            "name": "Slightly faster + balanced",
            "rate": "+15%",
            "pitch": "-3Hz"  # Alternative with slightly more speed
        }
    ]
    
    for config in configs:
        print("\n" + "="*70)
        print(f"🔊 ARJUN - {config['name']}")
        print(f"   Rate: {config['rate']}, Pitch: {config['pitch']}")
        print("="*70)
        
        # Test Hindi
        print(f'\nHindi: "{test_sentences["hindi"]}"')
        
        communicate = edge_tts.Communicate(
            test_sentences["hindi"],
            "hi-IN-ArjunNeural",
            rate=config['rate'],
            pitch=config['pitch']
        )
        
        audio_file = tempfile.mktemp(suffix='.mp3')
        await communicate.save(audio_file)
        print(f"✓ Saved: {audio_file}")
        subprocess.run(['start', audio_file], shell=True)
        
        rating = input("\nRate this (1-5): ")
        print(f"You rated: {rating}/5")
        
        # Test English
        print(f'\nEnglish: "{test_sentences["english"]}"')
        
        communicate = edge_tts.Communicate(
            test_sentences["english"],
            "hi-IN-ArjunNeural",
            rate=config['rate'],
            pitch=config['pitch']
        )
        
        audio_file = tempfile.mktemp(suffix='.mp3')
        await communicate.save(audio_file)
        print(f"✓ Saved: {audio_file}")
        subprocess.run(['start', audio_file], shell=True)
        
        rating = input("\nRate this (1-5): ")
        print(f"You rated: {rating}/5")
        
        choice = input("\nTest next variation? (y/n): ")
        if choice.lower() != 'y':
            break
    
    print("\n✨ Testing complete!")
    print("\nRECOMMENDATION:")
    print("  - For CALM: Use pitch -10Hz")
    print("  - For ENTHUSIASTIC: Use pitch +5Hz")
    print("  - For BALANCED (calm + enthusiastic): Use pitch -3Hz")
    print("  - Rate: +13% or +15% (closest to your preference)")
    print("\nNote: Edge TTS only accepts whole number rates (13%, 15%, etc.)")

if __name__ == "__main__":
    asyncio.run(test_arjun_tuned())
