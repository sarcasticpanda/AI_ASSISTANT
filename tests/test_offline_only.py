"""
Test offline voice only - tuned to match Arjun speed
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from colorama import init, Fore, Style
init(autoreset=True)

from core import tts_offline
import subprocess

print("\n" + "="*70)
print("  OFFLINE VOICE TEST (Microsoft David - Tuned to Arjun Speed)")
print("="*70 + "\n")

# Show config
print(f"{Fore.GREEN}Voice Configuration:{Style.RESET_ALL}")
config = tts_offline.get_voice_info()
for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Test sentences
test_cases = [
    "Good morning, sir. All systems are operational.",
    "My pleasure, sir. How may I assist you?",
    "Certainly, sir. Opening Chrome browser now.",
    "I am Jarvis, your offline assistant."
]

for i, text in enumerate(test_cases, 1):
    print(f"\n{Fore.CYAN}Test {i}:{Style.RESET_ALL}")
    print(f"  Text: '{text}'")
    
    # Generate speech
    print("  Generating...")
    audio_path = tts_offline.speak_offline(text, lang='en')
    
    if audio_path:
        print(f"{Fore.GREEN}  ✓ Generated: {audio_path}{Style.RESET_ALL}")
        
        # Play audio
        print(f"  Playing...")
        subprocess.run(['start', audio_path], shell=True)
        
        if i < len(test_cases):
            cont = input(f"\n  {Fore.YELLOW}Continue to next? (y/n): {Style.RESET_ALL}")
            if cont.lower() != 'y':
                break
    else:
        print(f"{Fore.RED}  ✗ Failed to generate audio{Style.RESET_ALL}")
        break

print(f"\n{Fore.GREEN}✨ Offline voice test complete!{Style.RESET_ALL}")
print(f"\n{Fore.CYAN}Note:{Style.RESET_ALL} Offline voice (Microsoft David) is tuned to 175 WPM")
print("to match Arjun's +11% speed. It will sound more robotic than")
print("the online Arjun voice, but it's the best offline option available.\n")
