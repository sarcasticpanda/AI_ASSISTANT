"""
Compare voices: Aarti vs Arjun at different speeds
"""
import asyncio
import edge_tts
import tempfile
import subprocess

async def test_comparison():
    """Test Aarti and Arjun at specific speeds"""
    
    # Test Aarti (your 5/5 rated voice)
    print("\n" + "="*70)
    print("🔊 AARTI (Female - Your 5/5 rated voice) at +20% speed")
    print("="*70)
    print('Hindi: "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।"')
    
    communicate = edge_tts.Communicate(
        "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।",
        "hi-IN-AartiNeural",
        rate="+20%"
    )
    
    audio_file = tempfile.mktemp(suffix='.mp3')
    await communicate.save(audio_file)
    print(f"✓ Audio saved: {audio_file}")
    subprocess.run(['start', audio_file], shell=True)
    
    rating = input("\nRate Aarti +20% (1-5): ")
    print(f"You rated: {rating}/5")
    
    # Test Arjun at 13%
    print("\n" + "="*70)
    print("🔊 ARJUN (Male) at +13% speed")
    print("="*70)
    print('Hindi: "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।"')
    
    communicate = edge_tts.Communicate(
        "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।",
        "hi-IN-ArjunNeural",
        rate="+13%"
    )
    
    audio_file = tempfile.mktemp(suffix='.mp3')
    await communicate.save(audio_file)
    print(f"✓ Audio saved: {audio_file}")
    subprocess.run(['start', audio_file], shell=True)
    
    rating = input("\nRate Arjun +13% (1-5): ")
    print(f"You rated: {rating}/5")
    
    # Test Arjun at 17%
    print("\n" + "="*70)
    print("🔊 ARJUN (Male) at +17% speed")
    print("="*70)
    print('Hindi: "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।"')
    
    communicate = edge_tts.Communicate(
        "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।",
        "hi-IN-ArjunNeural",
        rate="+17%"
    )
    
    audio_file = tempfile.mktemp(suffix='.mp3')
    await communicate.save(audio_file)
    print(f"✓ Audio saved: {audio_file}")
    subprocess.run(['start', audio_file], shell=True)
    
    rating = input("\nRate Arjun +17% (1-5): ")
    print(f"You rated: {rating}/5")
    
    # Test English with Arjun
    print("\n" + "="*70)
    print("🔊 BONUS: ARJUN speaking ENGLISH at +15% speed")
    print("="*70)
    print('English: "Good morning, sir. All systems are operational."')
    
    communicate = edge_tts.Communicate(
        "Good morning, sir. All systems are operational.",
        "hi-IN-ArjunNeural",
        rate="+15%"
    )
    
    audio_file = tempfile.mktemp(suffix='.mp3')
    await communicate.save(audio_file)
    print(f"✓ Audio saved: {audio_file}")
    subprocess.run(['start', audio_file], shell=True)
    
    rating = input("\nRate Arjun English +15% (1-5): ")
    print(f"You rated: {rating}/5")
    
    print("\n✨ Comparison complete!")
    print("\nNOTE: Aarti is female, Arjun is male.")
    print("For Jarvis, you need a male voice, so Arjun is better choice.")

if __name__ == "__main__":
    asyncio.run(test_comparison())
