"""
Quick MongoDB Data Viewer - See what's stored in your database
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core import mongo_manager
import json


def main():
    print("\n" + "="*70)
    print("🗄️  JARVIS MONGODB - QUICK VIEW")
    print("="*70)
    
    # Initialize MongoDB
    print("\n🔌 Connecting to MongoDB...")
    try:
        mongo_manager.initialize()
        print("✅ Connected!\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Check conversations
    print("="*70)
    print("📜 RECENT CONVERSATIONS (Last 10)")
    print("="*70)
    
    conversations = mongo_manager.get_recent_history(limit=10)
    
    if not conversations:
        print("\n⚠️  No conversations found yet!")
        print("\nℹ️  Data will start saving from your next voice interaction.")
        print("   Run: python tests\\phase1_online.py")
    else:
        print(f"\n✅ Found {len(conversations)} conversations!\n")
        
        for i, conv in enumerate(conversations, 1):
            print(f"\n{'─'*70}")
            print(f"💬 Conversation #{i}")
            print(f"   Time: {conv.get('timestamp', 'Unknown')}")
            print(f"   Language: {conv.get('language_detected', 'en').upper()}")
            print(f"{'─'*70}")
            
            print(f"\n👤 YOU: {conv.get('user_query', 'N/A')}")
            print(f"\n🤖 JARVIS: {conv.get('jarvis_response', 'N/A')}")
            
            perf = conv.get('performance', {})
            if perf:
                print(f"\n📊 Performance:")
                print(f"   Intent: {conv.get('intent', 'unknown')}")
                print(f"   Total Time: {perf.get('total_time', 0):.2f}s")
                print(f"   (STT: {perf.get('stt_time', 0):.2f}s | "
                      f"Brain: {perf.get('brain_time', 0):.2f}s | "
                      f"TTS: {perf.get('tts_time', 0):.2f}s)")
    
    # Check app commands
    print(f"\n\n{'='*70}")
    print("🚀 RECENT APP COMMANDS (Last 5)")
    print("="*70)
    
    apps = mongo_manager.get_recent_apps(limit=5)
    
    if apps:
        print(f"\n✅ Found {len(apps)} app commands!\n")
        for i, app in enumerate(apps, 1):
            status = "✅" if app.get('success', True) else "❌"
            print(f"{i}. {status} {app.get('command_type', 'unknown').upper()}: {app.get('target', 'N/A')}")
            print(f"   Query: \"{app.get('user_query', 'N/A')}\"")
    else:
        print("\n⚠️  No app commands yet")
    
    # Check statistics
    print(f"\n\n{'='*70}")
    print("📊 COMMAND STATISTICS")
    print("="*70)
    
    stats = mongo_manager.get_command_stats()
    
    if stats and stats.get('total_commands', 0) > 0:
        print(f"\n✅ Total Commands: {stats.get('total_commands', 0)}")
        print(f"   Success Rate: {stats.get('success_rate', 0) * 100:.1f}%")
        
        top_intents = stats.get('top_intents', [])
        if top_intents:
            print(f"\n   🎯 Top Commands:")
            for intent_data in top_intents[:5]:
                print(f"      • {intent_data.get('intent', 'unknown')}: {intent_data.get('count', 0)} times")
    else:
        print("\n⚠️  No analytics data yet")
    
    print(f"\n\n{'='*70}")
    print("💡 TIPS")
    print("="*70)
    print(f"""
📊 STORAGE STATUS:
   Total conversations stored: {mongo_manager.get_conversation_count()}
   Data location: MongoDB → jarvis_db → conversations

🧠 CONTEXT MEMORY (Smart Loading):
   • Normal questions: Loads last 3 conversations (fast)
   • History questions: Loads last 20 conversations (full context)
   
   Try asking:
   - "What did I ask before?" → Loads 20 conversations
   - "What was my first question?" → Loads 20 conversations
   - "What time is it?" → Loads 3 conversations (normal)

🌐 LANGUAGE DETECTION:
   Groq Whisper auto-detects: en (English), hi (Hindi), mixed (Hinglish)
   Test by speaking in different languages!

🚀 To interact with Jarvis:
   python tests\\phase1_online.py

🔍 For detailed view with interactive menu:
   python tests\\view_mongodb_data.py

📖 Full context memory guide:
   docs\\CONTEXT_MEMORY_GUIDE.md
""")
    
    mongo_manager.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
