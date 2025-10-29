"""
Test Arjun with curious/inquisitive pitch
Higher pitch variations for more curious, engaged tone
"""
import asyncio
import edge_tts
import tempfile
import subprocess

async def test_curious_pitch():
    """Test Arjun with curious, inquisitive pitch variations"""
    
    test_sentences = {
        "hindi": "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।",
        "english": "Good morning, sir. All systems are operational and ready for deployment.",
        "question": "Sir, would you like me to open Chrome browser?",
        "mixed": "Sir, Chrome browser open हो गया है। और क्या मदद चाहिए?"
    }
    
    # Curious/inquisitive variations
    # Higher pitch = more curious, engaged, alert
    # Moderate speed for clarity while being enthusiastic
    
    configs = [
        {
            "name": "Slightly Curious",
            "rate": "+13%",
            "pitch": "+8Hz"  # Moderately higher - curious tone
        },
        {
            "name": "More Curious",
            "rate": "+13%",
            "pitch": "+12Hz"  # Higher pitch - very curious/alert
        },
        {
            "name": "Very Curious + Faster",
            "rate": "+15%",
            "pitch": "+10Hz"  # Balanced curious with speed
        },
        {
            "name": "Enthusiastic Curious",
            "rate": "+15%",
            "pitch": "+15Hz"  # Very enthusiastic and curious
        },
        {
            "name": "Calm Curious (Best balance?)",
            "rate": "+13%",
            "pitch": "+6Hz"  # Slightly higher but still calm
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
        
        rating = input("\nRate Hindi (1-5): ")
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
        
        rating = input("\nRate English (1-5): ")
        print(f"You rated: {rating}/5")
        
        # Test as a question (curious tone test)
        print(f'\nQuestion (curious test): "{test_sentences["question"]}"')
        
        communicate = edge_tts.Communicate(
            test_sentences["question"],
            "hi-IN-ArjunNeural",
            rate=config['rate'],
            pitch=config['pitch']
        )
        
        audio_file = tempfile.mktemp(suffix='.mp3')
        await communicate.save(audio_file)
        print(f"✓ Saved: {audio_file}")
        subprocess.run(['start', audio_file], shell=True)
        
        rating = input("\nRate Question tone (1-5): ")
        print(f"You rated: {rating}/5")
        
        choice = input("\nTest next variation? (y/n): ")
        if choice.lower() != 'y':
            print(f"\n✅ You selected: {config['name']}")
            print(f"   Settings: Rate={config['rate']}, Pitch={config['pitch']}")
            break
    
    print("\n✨ Testing complete!")
    print("\nCURIOUS PITCH GUIDE:")
    print("  +6Hz  = Slightly curious (calm + interested)")
    print("  +8Hz  = Moderately curious (engaged)")
    print("  +10Hz = Curious + energetic")
    print("  +12Hz = Very curious/alert")
    print("  +15Hz = Highly enthusiastic")

if __name__ == "__main__":
    asyncio.run(test_curious_pitch())
