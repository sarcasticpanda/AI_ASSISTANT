"""
Quick test: Arjun at +15% speed
"""
import asyncio
import edge_tts
import tempfile
import subprocess

async def test_arjun_15():
    """Test Arjun at +15% speed"""
    
    # Hindi test
    print("\n🔊 Testing Arjun (Male) at +15% speed - HINDI")
    print('   "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।"')
    
    communicate = edge_tts.Communicate(
        "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।",
        "hi-IN-ArjunNeural",
        rate="+15%"
    )
    
    audio_file = tempfile.mktemp(suffix='.mp3')
    await communicate.save(audio_file)
    
    print(f"✓ Audio saved: {audio_file}")
    print("Playing...")
    subprocess.run(['start', audio_file], shell=True)
    
    rating = input("\nRate this voice (1-5): ")
    print(f"You rated: {rating}/5")
    
    # English test
    print("\n🔊 Testing Arjun (Male) at +15% speed - ENGLISH")
    print('   "Good morning, sir. All systems are operational."')
    
    communicate = edge_tts.Communicate(
        "Good morning, sir. All systems are operational.",
        "hi-IN-ArjunNeural",
        rate="+15%"
    )
    
    audio_file = tempfile.mktemp(suffix='.mp3')
    await communicate.save(audio_file)
    
    print(f"✓ Audio saved: {audio_file}")
    print("Playing...")
    subprocess.run(['start', audio_file], shell=True)
    
    rating = input("\nRate this voice (1-5): ")
    print(f"You rated: {rating}/5")
    
    print("\n✨ Done! Arjun at +15% speed tested.")

if __name__ == "__main__":
    asyncio.run(test_arjun_15())
