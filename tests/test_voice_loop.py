"""
Test Voice Loop - Complete parallel voice assistant
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.core.voice_loop import VoiceLoop

print("=" * 70)
print("🎤 JARVIS PARALLEL VOICE LOOP TEST")
print("=" * 70)
print("\nThis test runs the complete voice assistant with:")
print("  • Continuous listening (VAD)")
print("  • Parallel processing (3 threads)")
print("  • Interruptible playback")
print("  • Follow-up question detection")
print("\nChoose mode:")
print("  1. Offline (faster-whisper + pyttsx3) - Fast, works offline")
print("  2. Online (Groq + Edge TTS) - More accurate, needs internet")

choice = input("\nEnter 1 or 2: ").strip()

use_offline = (choice == "1")

print(f"\n✅ Starting in {'OFFLINE' if use_offline else 'ONLINE'} mode...")
print("\nPress Ctrl+C to stop\n")

# Create and run voice loop
loop = VoiceLoop(use_offline_stt=use_offline)
loop.run_forever()
