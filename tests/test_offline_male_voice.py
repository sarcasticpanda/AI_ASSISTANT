"""
Test offline TTS with male voice fix
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from colorama import init, Fore, Style
init(autoreset=True)

from core import tts_offline
import subprocess


def test_offline_voice():
    """Test that offline TTS uses male voice"""
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"  TESTING OFFLINE TTS - MALE VOICE FIX")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    # Check availability
    if not tts_offline.is_available():
        print(f"{Fore.RED}✗ Offline TTS not available!{Style.RESET_ALL}")
        return
    
    # Show config
    print(f"{Fore.GREEN}Offline TTS Configuration:{Style.RESET_ALL}")
    config = tts_offline.get_voice_info()
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # Show engine
    print(f"{Fore.GREEN}Engine:{Style.RESET_ALL} {tts_offline.get_current_engine()}")
    print()
    
    # Test sentences
    test_cases = [
        "Good morning, sir. I am Jarvis, your offline assistant.",
        "All systems are operational. How may I assist you?",
        "Certainly, sir. Opening Chrome browser now.",
        "My pleasure, sir."
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{Fore.YELLOW}Test {i}:{Style.RESET_ALL}")
        print(f"  Text: '{text}'")
        
        # Generate speech
        audio_path = tts_offline.speak_offline(text, lang='en', use_coqui=False)
        
        if audio_path:
            print(f"{Fore.GREEN}  ✓ Generated: {audio_path}{Style.RESET_ALL}")
            
            # Play audio
            print(f"  Playing...")
            subprocess.run(['start', audio_path], shell=True)
            
            response = input(f"\n  {Fore.CYAN}Is this a MALE voice? (y/n): {Style.RESET_ALL}")
            
            if response.lower() == 'n':
                print(f"{Fore.RED}  ✗ Still female! Need to debug further.{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.GREEN}  ✓ Male voice confirmed!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}  ✗ Failed to generate audio{Style.RESET_ALL}")
        
        if i < len(test_cases):
            cont = input(f"\n  Continue to next test? (y/n): ")
            if cont.lower() != 'y':
                break
    
    print(f"\n{Fore.GREEN}✨ Test complete!{Style.RESET_ALL}\n")


if __name__ == "__main__":
    test_offline_voice()
