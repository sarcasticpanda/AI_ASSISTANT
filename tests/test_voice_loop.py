"""
Test the parallel voice loop with continuous listening, interruption support, and follow-up handling.

This test demonstrates the 3-threaded architecture:
1. Listener Thread: Continuously listens for speech using VAD
2. Processor Thread: STT → Brain → TTS pipeline
3. Player Thread: Plays responses and handles follow-up questions

Features tested:
- Continuous listening (while Jarvis is speaking)
- Interruption detection (stops playback when you talk)
- Follow-up question handling (waits for response with timeout)
- Statistics tracking (commands, interruptions, followups)
"""

import os
import sys
import time
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.voice_loop import VoiceLoop

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)


def print_header():
    """Print test header with instructions."""
    print("\n" + "="*70)
    print("🎙️  PARALLEL VOICE LOOP TEST")
    print("="*70)
    print("\n📋 FEATURES TO TEST:")
    print("  ✓ Continuous listening (even while Jarvis speaks)")
    print("  ✓ Interruption support (talk while Jarvis is speaking)")
    print("  ✓ Follow-up questions (Jarvis waits for your response)")
    print("  ✓ Automatic timeout (closes conversation after 10s silence)")
    print("\n💡 TEST SUGGESTIONS:")
    print("  1. Ask 'What time is it?' → Should get instant response")
    print("  2. Ask 'Explain quantum computing' → Should ask follow-up → Respond or wait")
    print("  3. Try interrupting while Jarvis speaks → Should stop and listen")
    print("  4. Check statistics at end → Commands, interruptions, followups")
    print("\n⚠️  HOW TO USE:")
    print("  • Speak naturally after the beep")
    print("  • Wait 1.3 seconds of silence to complete your sentence")
    print("  • Interrupt anytime by speaking (it will detect you)")
    print("  • Press Ctrl+C when done to see statistics")
    print("\n" + "="*70)


def select_mode():
    """Let user choose between offline and online mode."""
    print("\n🔧 SELECT MODE:")
    print("  1. OFFLINE (Recommended) - Faster, no internet needed")
    print("     STT: faster-whisper medium | TTS: pyttsx3")
    print("     Expected latency: 2-3s STT + 0-2s Brain + instant TTS")
    print("\n  2. ONLINE - Better accuracy, needs internet")
    print("     STT: Groq Whisper API | TTS: Edge TTS Arjun")
    print("     Expected latency: 4-5s STT + 0-2s Brain + 4-5s TTS")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == "1":
            return "offline"
        elif choice == "2":
            return "online"
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")


def main():
    """Run the parallel voice loop test."""
    try:
        # Print header and instructions
        print_header()
        
        # Let user select mode
        mode = select_mode()
        
        print(f"\n✅ Selected mode: {mode.upper()}")
        print("\n🚀 STARTING VOICE LOOP...")
        print("   (First-time STT model download may take time)")
        print("\n" + "="*70)
        
        # Create and start voice loop
        loop = VoiceLoop(use_offline=(mode == "offline"))
        loop.start()
        
        print("\n🎧 LISTENING... (Speak after the beep)")
        print("   Press Ctrl+C to stop and view statistics\n")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 STOPPING VOICE LOOP...")
        loop.stop()
        
        print("\n" + "="*70)
        print("📊 SESSION STATISTICS")
        print("="*70)
        loop._print_stats()
        print("="*70)
        
        print("\n✅ TEST COMPLETE!")
        print("\n📝 CHECKLIST:")
        print(f"  • Commands processed: {loop.stats['commands_processed']} (Should be > 0)")
        print(f"  • Interruptions detected: {loop.stats['interruptions']} (If you interrupted)")
        print(f"  • Follow-ups handled: {loop.stats['followups_detected']} (If asked complex questions)")
        print(f"  • Avg processing time: {loop.stats['avg_processing_time']:.2f}s")
        print("\n💭 EXPECTED RESULTS:")
        if mode == "offline":
            print("  • STT: 2-3 seconds (faster-whisper medium)")
            print("  • Brain: 0-2 seconds (depends on query)")
            print("  • TTS: Instant (pyttsx3)")
            print("  • Total: 3-5 seconds per command")
        else:
            print("  • STT: 4-5 seconds (Groq API)")
            print("  • Brain: 0-2 seconds (depends on query)")
            print("  • TTS: 4-5 seconds (Edge TTS)")
            print("  • Total: 8-12 seconds per command")
        
        print("\n🎯 NEXT STEPS:")
        if loop.stats['avg_processing_time'] > 10:
            print("  ⚠️  Performance is slow. Consider:")
            print("     - Use offline mode for faster response")
            print("     - Check internet connection (if using online)")
            print("     - Use smaller STT model (small vs medium)")
        else:
            print("  ✅ Performance looks good!")
            print("     - Ready for wake word integration")
            print("     - Ready for production testing")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        if 'loop' in locals():
            loop.stop()


if __name__ == "__main__":
    main()
