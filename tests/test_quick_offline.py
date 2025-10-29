"""
Quick test: Verify male voice in offline mode
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from core import tts_manager
import subprocess

print("\n" + "="*70)
print("  QUICK OFFLINE MALE VOICE TEST")
print("="*70 + "\n")

# Test offline mode
text = "Good morning, sir. I am Jarvis. This is my offline male voice."

print("Generating speech in FORCED OFFLINE mode...")
audio_path, engine = tts_manager.speak(text, prefer_offline=True)

if audio_path:
    print(f"\n✓ Success!")
    print(f"  Engine: {engine}")
    print(f"  File: {audio_path}")
    print(f"\nPlaying audio...")
    
    subprocess.run(['start', audio_path], shell=True)
    
    print(f"\n{'='*70}")
    print("If you hear a MALE voice, the fix worked! ✓")
    print("If you hear a FEMALE voice, there's still an issue. ✗")
    print("="*70 + "\n")
else:
    print("✗ Failed to generate audio")
