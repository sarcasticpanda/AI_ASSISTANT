"""
Test the updated TTS system with Arjun voice
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from colorama import init, Fore, Style
init(autoreset=True)

from core import tts_online
import subprocess

def test_tts():
    """Test the TTS system"""
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"  JARVIS TTS SYSTEM TEST")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    # Show current configuration
    print(f"{Fore.GREEN}Current TTS Engine:{Style.RESET_ALL}")
    print(f"  {tts_online.get_current_engine()}\n")
    
    voice_info = tts_online.get_voice_info()
    print(f"{Fore.GREEN}Voice Configuration:{Style.RESET_ALL}")
    for key, value in voice_info.items():
        print(f"  {key}: {value}")
    print()
    
    # Test sentences
    test_cases = [
        ("English greeting", "Good morning, sir. All systems are operational.", "en"),
        ("Hindi greeting", "नमस्ते। मैं जार्विस हूं। आपकी सहायता के लिए तैयार हूं।", "hi"),
        ("English response", "Certainly, sir. Opening Chrome browser now.", "en"),
        ("Hindi response", "समझ गया। मैं इसे तुरंत करता हूं।", "hi"),
        ("Hinglish mixed", "Sir, Chrome browser open हो गया है। और क्या मदद चाहिए?", "mixed"),
        ("Quick reply", "My pleasure, sir.", "en"),
        ("Question", "Would you like me to proceed with the next step?", "en")
    ]
    
    for title, text, lang in test_cases:
        print(f"\n{Fore.YELLOW}Testing: {title}{Style.RESET_ALL}")
        print(f"  Text: '{text}'")
        print(f"  Language: {lang}")
        
        # Generate speech
        audio_path = tts_online.speak_online(text, lang=lang)
        
        if audio_path:
            print(f"{Fore.GREEN}  ✓ Generated: {audio_path}{Style.RESET_ALL}")
            
            # Play audio
            print(f"  Playing audio...")
            subprocess.run(['start', audio_path], shell=True)
            
            rating = input(f"\n  {Fore.CYAN}Rate this (1-5 or Enter to continue): {Style.RESET_ALL}")
            if rating:
                print(f"  You rated: {rating}/5")
        else:
            print(f"{Fore.RED}  ✗ Failed to generate audio{Style.RESET_ALL}")
        
        choice = input(f"\n  {Fore.CYAN}Continue to next test? (y/n): {Style.RESET_ALL}")
        if choice.lower() != 'y':
            break
    
    print(f"\n{Fore.GREEN}✨ TTS testing complete!{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}Your Jarvis voice is ready to use!{Style.RESET_ALL}")
    print(f"\nNext steps:")
    print(f"  1. Test with backend API (/speak endpoint)")
    print(f"  2. Integrate with STT for full conversation")
    print(f"  3. Build communication loop")


if __name__ == "__main__":
    test_tts()
