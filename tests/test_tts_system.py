"""
Test unified TTS system (online + offline)
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from colorama import init, Fore, Style
init(autoreset=True)

from core import tts_manager
import subprocess


def test_tts_system():
    """Test the complete TTS system"""
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"  JARVIS UNIFIED TTS SYSTEM TEST")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    # Show system status
    tts_manager.print_status()
    
    # Test sentences
    test_cases = [
        ("English greeting", "Good morning, sir. All systems are operational.", "en"),
        ("Quick response", "My pleasure, sir.", "en"),
        ("Hindi greeting", "नमस्ते। मैं जार्विस हूं।", "hi"),
        ("Hinglish", "Sir, Chrome browser open हो गया है।", "mixed")
    ]
    
    print(f"{Fore.YELLOW}Testing TTS with automatic engine selection:{Style.RESET_ALL}\n")
    
    for title, text, lang in test_cases:
        print(f"\n{Fore.GREEN}Test: {title}{Style.RESET_ALL}")
        print(f"  Text: '{text}'")
        print(f"  Language: {lang}")
        
        # Generate speech (auto-selects online/offline)
        audio_path, engine = tts_manager.speak(text, lang=lang)
        
        if audio_path:
            print(f"{Fore.GREEN}  ✓ Success{Style.RESET_ALL}")
            print(f"  Engine: {engine}")
            print(f"  File: {audio_path}")
            
            # Play audio
            print(f"  Playing...")
            subprocess.run(['start', audio_path], shell=True)
            
            input(f"\n  {Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}  ✗ Failed to generate audio{Style.RESET_ALL}")
    
    # Test offline mode
    print(f"\n\n{Fore.YELLOW}Testing OFFLINE mode (forced):{Style.RESET_ALL}\n")
    
    text = "Testing offline mode. This is Jarvis speaking without internet."
    print(f"  Text: '{text}'")
    
    audio_path, engine = tts_manager.speak(text, prefer_offline=True)
    
    if audio_path:
        print(f"{Fore.GREEN}  ✓ Offline TTS works!{Style.RESET_ALL}")
        print(f"  Engine: {engine}")
        print(f"  File: {audio_path}")
        
        subprocess.run(['start', audio_path], shell=True)
    else:
        print(f"{Fore.RED}  ✗ Offline TTS failed{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}✨ TTS system test complete!{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"  • Online TTS: Edge TTS (Arjun +11% +7Hz) + gTTS fallback")
    print(f"  • Offline TTS: pyttsx3 (male voice, +11% faster)")
    print(f"  • Auto-selection: Checks internet and uses best available")
    print(f"  • Fallback chain: Edge TTS → gTTS → pyttsx3")


if __name__ == "__main__":
    test_tts_system()
