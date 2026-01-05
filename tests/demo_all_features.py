"""
Feature Demonstration - Jarvis Voice Assistant
Run this to see all implemented features in action!
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.brain import process_command
from backend.skills.open_app import open_app

def demo_feature(category: str, feature: str, command: str, description: str):
    """Demonstrate a single feature"""
    print(f"\n{'='*70}")
    print(f"📌 {category} > {feature}")
    print(f"{'='*70}")
    print(f"Description: {description}")
    print(f"Command: \"{command}\"")
    print(f"\nProcessing...")
    
    try:
        result = process_command(command)
        print(f"✅ Response: {result['response']}")
        print(f"✅ Intent: {result['intent']}")
        print(f"✅ Success: {result['success']}")
        
        if 'method' in result:
            print(f"✅ Method: {result['method']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\nPress ENTER to continue to next feature...")
    input()

def main():
    """Run comprehensive feature demonstration"""
    
    print("\n" + "="*70)
    print("🚀 JARVIS VOICE ASSISTANT - FEATURE DEMONSTRATION")
    print("="*70)
    print("\nThis demo will show you ALL implemented features.")
    print("Some features will open apps/websites - be ready to close them!")
    print("\n" + "="*70)
    
    input("\nPress ENTER to start the demo...")
    
    # ========================================================================
    # CATEGORY 1: TIME & DATE
    # ========================================================================
    print("\n\n" + "🔷"*35)
    print("CATEGORY 1: TIME & DATE QUERIES")
    print("🔷"*35)
    
    demo_feature(
        "Time & Date",
        "Current Time",
        "what time is it",
        "Get current time with date"
    )
    
    demo_feature(
        "Time & Date",
        "Current Date",
        "what is today's date",
        "Get current date and day of week"
    )
    
    # ========================================================================
    # CATEGORY 2: SYSTEM INFORMATION
    # ========================================================================
    print("\n\n" + "🔷"*35)
    print("CATEGORY 2: SYSTEM INFORMATION")
    print("🔷"*35)
    
    demo_feature(
        "System Info",
        "Battery Status",
        "battery status",
        "Check battery percentage and charging status"
    )
    
    demo_feature(
        "System Info",
        "CPU Usage",
        "what is my cpu usage",
        "Monitor CPU usage percentage"
    )
    
    demo_feature(
        "System Info",
        "Memory/RAM Usage",
        "how much memory am I using",
        "Check RAM usage in GB"
    )
    
    demo_feature(
        "System Info",
        "Complete System Info",
        "system info",
        "Get CPU, Memory, Disk, and Battery at once"
    )
    
    # ========================================================================
    # CATEGORY 3: OPEN APPLICATIONS
    # ========================================================================
    print("\n\n" + "🔷"*35)
    print("CATEGORY 3: OPEN APPLICATIONS")
    print("🔷"*35)
    print("\n⚠️  WARNING: This will actually open apps on your computer!")
    print("Be ready to close them after each demo.\n")
    input("Press ENTER to continue...")
    
    demo_feature(
        "Open Apps",
        "System Apps",
        "open calculator",
        "Opens Windows Calculator"
    )
    
    demo_feature(
        "Open Apps",
        "Browsers",
        "open chrome",
        "Opens Google Chrome (if installed)"
    )
    
    demo_feature(
        "Open Apps",
        "Productivity Apps",
        "open notion",
        "Opens Notion (if installed)"
    )
    
    demo_feature(
        "Open Apps",
        "Microsoft Store Apps (UWP)",
        "open whatsapp",
        "Opens WhatsApp Desktop (Microsoft Store version)"
    )
    
    demo_feature(
        "Open Apps",
        "Communication Apps",
        "open discord",
        "Opens Discord (if installed)"
    )
    
    # ========================================================================
    # CATEGORY 4: FOLDERS
    # ========================================================================
    print("\n\n" + "🔷"*35)
    print("CATEGORY 4: OPEN FOLDERS")
    print("🔷"*35)
    
    demo_feature(
        "Folders",
        "Downloads Folder",
        "open downloads",
        "Opens Downloads folder in File Explorer"
    )
    
    demo_feature(
        "Folders",
        "Documents Folder",
        "open documents",
        "Opens Documents folder in File Explorer"
    )
    
    demo_feature(
        "Folders",
        "Desktop Folder",
        "open desktop",
        "Opens Desktop folder in File Explorer"
    )
    
    # ========================================================================
    # CATEGORY 5: ALARMS & REMINDERS
    # ========================================================================
    print("\n\n" + "🔷"*35)
    print("CATEGORY 5: ALARMS & REMINDERS")
    print("🔷"*35)
    
    demo_feature(
        "Alarms",
        "Set Alarm (Relative Time)",
        "set alarm in 2 minutes",
        "Schedule alarm 2 minutes from now"
    )
    
    demo_feature(
        "Alarms",
        "Set Reminder with Description",
        "remind me in 5 minutes to check the oven",
        "Schedule reminder with custom message"
    )
    
    # ========================================================================
    # CATEGORY 6: YOUTUBE PLAYBACK
    # ========================================================================
    print("\n\n" + "🔷"*35)
    print("CATEGORY 6: YOUTUBE PLAYBACK")
    print("🔷"*35)
    print("\n⚠️  WARNING: This will open YouTube in your browser!\n")
    input("Press ENTER to continue...")
    
    demo_feature(
        "YouTube",
        "Play Video",
        "play never gonna give you up on youtube",
        "Searches and plays video on YouTube"
    )
    
    # ========================================================================
    # CATEGORY 7: CONVERSATIONAL AI (LLM)
    # ========================================================================
    print("\n\n" + "🔷"*35)
    print("CATEGORY 7: CONVERSATIONAL AI")
    print("🔷"*35)
    print("\n⚠️  Requires API keys to work (Qwen/OpenRouter)\n")
    input("Press ENTER to continue...")
    
    demo_feature(
        "AI Chat",
        "General Questions",
        "explain quantum computing in simple terms",
        "Uses LLM with conversation context for complex queries"
    )
    
    demo_feature(
        "AI Chat",
        "Context Memory",
        "what did I just ask you about",
        "Recalls previous conversation (last 3 by default)"
    )
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n\n" + "="*70)
    print("✅ FEATURE DEMONSTRATION COMPLETE!")
    print("="*70)
    
    print("\n📊 SUMMARY OF FEATURES:")
    print("\n1. ⏰ TIME & DATE")
    print("   • Current time")
    print("   • Current date")
    
    print("\n2. 💻 SYSTEM INFORMATION")
    print("   • Battery status")
    print("   • CPU usage")
    print("   • Memory (RAM) usage")
    print("   • Disk usage")
    print("   • Complete system overview")
    
    print("\n3. 🖥️  OPEN APPLICATIONS")
    print("   • System apps (Calculator, Notepad, etc.)")
    print("   • Browsers (Chrome, Edge, Firefox)")
    print("   • Productivity (Notion, VS Code, etc.)")
    print("   • Microsoft Store apps (WhatsApp, etc.)")
    print("   • Communication (Discord, Telegram, Slack)")
    print("   • Entertainment (Spotify, VLC)")
    
    print("\n4. 📁 FOLDERS")
    print("   • Downloads")
    print("   • Documents")
    print("   • Desktop")
    print("   • Pictures")
    print("   • Music")
    print("   • Videos")
    
    print("\n5. ⏰ ALARMS & REMINDERS")
    print("   • Set alarm with relative time (in X minutes/hours)")
    print("   • Set alarm with absolute time (at 5pm)")
    print("   • Reminders with descriptions")
    print("   • Persistent storage (MongoDB)")
    
    print("\n6. 🎵 YOUTUBE PLAYBACK")
    print("   • Search and play videos")
    print("   • Opens in default browser")
    
    print("\n7. 💬 CONVERSATIONAL AI")
    print("   • LLM-powered responses (Qwen)")
    print("   • Context memory (last 3 or 20 conversations)")
    print("   • Multi-language support (English, Hindi, Hinglish)")
    print("   • Conversation history detection")
    
    print("\n8. 🔧 ADVANCED FEATURES")
    print("   • Streaming TTS (sentence-by-sentence)")
    print("   • Interrupt support (press 'S' to stop)")
    print("   • MongoDB persistence")
    print("   • Smart context loading")
    print("   • Performance metrics")
    
    print("\n" + "="*70)
    print("📚 DOCUMENTATION:")
    print("   • Full guide: docs/SKILLS_IMPLEMENTATION_SUMMARY.md")
    print("   • Test guide: docs/SKILLS_TEST_GUIDE.md")
    print("   • App launcher: docs/SMART_APP_LAUNCHER.md")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Run voice assistant: python tests/phase1_online.py")
    print("   2. Test all skills: python tests/test_all_skills.py")
    print("   3. View MongoDB data: python tests/quick_view_mongodb.py")
    
    print("\n" + "="*70)
    print()

if __name__ == "__main__":
    main()
