"""
Quick test to list all available Edge TTS Hindi voices
"""

import asyncio
import edge_tts

async def list_hindi_voices():
    voices = await edge_tts.VoicesManager.create()
    hindi_voices = voices.find(Language="hi")
    
    print("\n🇮🇳 ALL HINDI VOICES IN EDGE TTS:\n")
    print("=" * 70)
    
    for voice in hindi_voices:
        gender = "MALE ♂️" if voice["Gender"] == "Male" else "FEMALE ♀️"
        print(f"\n{gender} {voice['ShortName']}")
        print(f"  Name: {voice.get('FriendlyName', voice['ShortName'])}")
        print(f"  Locale: {voice['Locale']}")
        
        # Test this voice
        test_text = "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।"
        print(f"  Testing: {test_text}")
        
        # Try different speeds
        for rate in ["+0%", "+20%", "+40%"]:
            print(f"    Speed {rate}...", end=" ")
            communicate = edge_tts.Communicate(test_text, voice['ShortName'], rate=rate)
            
            import tempfile
            audio_file = tempfile.mktemp(suffix='.mp3')
            await communicate.save(audio_file)
            
            print(f"saved to {audio_file}")
            
            # Play it
            import subprocess
            subprocess.run(['start', audio_file], shell=True)
            
            # Wait for user feedback
            feedback = input(f"      Rate {rate} speed (1-5 or 'n' for next): ").strip()
            if feedback != 'n':
                print(f"      You rated: {feedback}/5")

if __name__ == "__main__":
    asyncio.run(list_hindi_voices())
