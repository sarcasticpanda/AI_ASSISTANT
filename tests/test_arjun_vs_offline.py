"""
Test to compare online (Arjun) vs offline (David tuned) voice
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from colorama import init, Fore, Style
init(autoreset=True)

from core import tts_manager
import subprocess

print("\n" + "="*70)
print("  ARJUN VOICE COMPARISON: Online vs Offline")
print("="*70 + "\n")

test_text = "Good morning, sir. All systems are operational. How may I assist you?"

print(f"Test sentence: '{test_text}'\n")

# Test 1: Online (Arjun - your 5/5 rated voice)
print(f"{Fore.CYAN}1. ONLINE MODE (Arjun +11% +7Hz - Your 5/5 rated voice):{Style.RESET_ALL}")
print("   Generating...")
audio_online, engine_online = tts_manager.speak(test_text, prefer_offline=False)
if audio_online:
    print(f"   ✓ Generated with: {engine_online}")
    print(f"   Playing online voice...")
    subprocess.run(['start', audio_online], shell=True)
    input(f"\n   {Fore.GREEN}Press Enter after listening...{Style.RESET_ALL}")
else:
    print(f"   {Fore.RED}✗ Failed{Style.RESET_ALL}")

print()

# Test 2: Offline (David tuned to match Arjun speed)
print(f"{Fore.CYAN}2. OFFLINE MODE (Microsoft David at 175 WPM - tuned to match Arjun):{Style.RESET_ALL}")
print("   Generating...")
audio_offline, engine_offline = tts_manager.speak(test_text, prefer_offline=True)
if audio_offline:
    print(f"   ✓ Generated with: {engine_offline}")
    print(f"   Playing offline voice...")
    subprocess.run(['start', audio_offline], shell=True)
    input(f"\n   {Fore.GREEN}Press Enter after listening...{Style.RESET_ALL}")
else:
    print(f"   {Fore.RED}✗ Failed{Style.RESET_ALL}")

print()
print("="*70)
print(f"{Fore.YELLOW}COMPARISON NOTES:{Style.RESET_ALL}")
print()
print("Online (Arjun):")
print("  ✓ Natural neural voice")
print("  ✓ Perfect pronunciation")
print("  ✓ Smooth and human-like")
print("  ✓ Your selected 5/5 voice")
print("  ✗ Requires internet")
print()
print("Offline (David tuned):")
print("  ✓ Works without internet")
print("  ✓ Male voice (not female)")
print("  ✓ Speed tuned to match Arjun (+11%)")
print("  ✗ More robotic/mechanical")
print("  ✗ System TTS limitations")
print()
print("="*70)
print()
print(f"{Fore.GREEN}RECOMMENDATION:{Style.RESET_ALL}")
print("• Use ONLINE (Arjun) when internet available - much better quality")
print("• Use OFFLINE (David) only as emergency fallback")
print("• System auto-selects best available")
print()
