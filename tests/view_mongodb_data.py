"""
View MongoDB Data - Interactive viewer for Jarvis database
Shows conversations, app commands, analytics, and settings
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core import mongo_manager


def print_separator(title="", char="=", width=70):
    """Print a formatted separator line"""
    if title:
        print(f"\n{char*width}")
        print(f"{title.center(width)}")
        print(f"{char*width}")
    else:
        print(f"{char*width}")


def view_conversations(limit=10):
    """Display recent conversations"""
    print_separator("📜 RECENT CONVERSATIONS")
    
    conversations = mongo_manager.get_recent_history(limit=limit)
    
    if not conversations:
        print("No conversations found.")
        return
    
    print(f"\nShowing {len(conversations)} most recent conversations:\n")
    
    for i, conv in enumerate(conversations, 1):
        print(f"{'─'*70}")
        print(f"#{i} | {conv.get('timestamp', 'Unknown time')}")
        print(f"{'─'*70}")
        print(f"👤 USER ({conv.get('language_detected', 'en').upper()}):")
        print(f"   {conv.get('user_query', 'N/A')}")
        print(f"\n🤖 JARVIS:")
        print(f"   {conv.get('jarvis_response', 'N/A')}")
        print(f"\n📊 INFO:")
        print(f"   Intent: {conv.get('intent', 'unknown')}")
        print(f"   Follow-up: {conv.get('expects_followup', False)}")
        
        perf = conv.get('performance', {})
        if perf:
            total = perf.get('total_time', 0)
            print(f"   Performance: {total:.2f}s (STT: {perf.get('stt_time', 0):.2f}s, " +
                  f"Brain: {perf.get('brain_time', 0):.2f}s, TTS: {perf.get('tts_time', 0):.2f}s)")
        print()


def view_app_commands(limit=10):
    """Display recent app commands"""
    print_separator("🚀 RECENT APP/WEBSITE COMMANDS")
    
    apps = mongo_manager.get_recent_apps(limit=limit)
    
    if not apps:
        print("No app commands found.")
        return
    
    print(f"\nShowing {len(apps)} most recent commands:\n")
    
    for i, app in enumerate(apps, 1):
        status = "✅" if app.get('success', True) else "❌"
        print(f"{i}. {status} {app.get('command_type', 'unknown').upper()}: {app.get('target', 'N/A')}")
        print(f"   Query: \"{app.get('user_query', 'N/A')}\"")
        print(f"   Time: {app.get('timestamp', 'Unknown')}")
        if app.get('error'):
            print(f"   Error: {app.get('error')}")
        print()


def view_frequent_apps(limit=10):
    """Display most frequently used apps"""
    print_separator("📈 MOST FREQUENTLY USED APPS")
    
    apps = mongo_manager.get_frequent_apps(limit=limit)
    
    if not apps:
        print("No app usage data found.")
        return
    
    print(f"\nTop {len(apps)} most opened apps/websites:\n")
    
    for i, app in enumerate(apps, 1):
        bar_length = min(int(app['count'] / 2), 50)
        bar = "█" * bar_length
        print(f"{i:2d}. {app['app']:20s} {bar} {app['count']} times")


def view_command_stats():
    """Display command usage statistics"""
    print_separator("📊 COMMAND STATISTICS")
    
    stats = mongo_manager.get_command_stats()
    
    if not stats:
        print("No statistics available.")
        return
    
    print(f"\n📈 OVERALL STATS:")
    print(f"   Total commands: {stats.get('total_commands', 0)}")
    print(f"   Success rate: {stats.get('success_rate', 0) * 100:.1f}%")
    
    top_intents = stats.get('top_intents', [])
    if top_intents:
        print(f"\n🎯 TOP COMMAND TYPES:\n")
        for i, intent_data in enumerate(top_intents, 1):
            intent = intent_data.get('intent', 'unknown')
            count = intent_data.get('count', 0)
            success = intent_data.get('success_rate', 0) * 100
            avg_time = intent_data.get('avg_response_time', 0)
            
            print(f"{i:2d}. {intent:20s} | Count: {count:3d} | " +
                  f"Success: {success:5.1f}% | Avg: {avg_time:.2f}s")


def view_user_settings():
    """Display user settings"""
    print_separator("⚙️  USER SETTINGS")
    
    settings = mongo_manager.get_all_settings()
    
    if not settings:
        print("No user settings found.")
        return
    
    print("\nCurrent settings:\n")
    for key, value in settings.items():
        print(f"   {key}: {value}")


def interactive_menu():
    """Interactive menu for viewing data"""
    while True:
        print_separator("🗄️  JARVIS MONGODB VIEWER", char="═")
        print("\nWhat would you like to view?\n")
        print("   1. Recent conversations")
        print("   2. Recent app/website commands")
        print("   3. Most frequently used apps")
        print("   4. Command statistics")
        print("   5. User settings")
        print("   6. Everything (full report)")
        print("   7. Exit")
        
        choice = input("\n👉 Enter choice (1-7): ").strip()
        
        if choice == "1":
            limit = input("How many conversations? (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            view_conversations(limit)
            input("\nPress ENTER to continue...")
        
        elif choice == "2":
            limit = input("How many commands? (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            view_app_commands(limit)
            input("\nPress ENTER to continue...")
        
        elif choice == "3":
            limit = input("How many apps? (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            view_frequent_apps(limit)
            input("\nPress ENTER to continue...")
        
        elif choice == "4":
            view_command_stats()
            input("\nPress ENTER to continue...")
        
        elif choice == "5":
            view_user_settings()
            input("\nPress ENTER to continue...")
        
        elif choice == "6":
            view_conversations(5)
            view_app_commands(5)
            view_frequent_apps(10)
            view_command_stats()
            view_user_settings()
            input("\nPress ENTER to continue...")
        
        elif choice == "7":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please enter 1-7.")
            input("Press ENTER to continue...")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 JARVIS MONGODB VIEWER")
    print("="*70)
    
    # Initialize MongoDB
    print("\n🗄️  Connecting to MongoDB...")
    try:
        mongo_manager.initialize()
        print("✅ Connected!\n")
        
        # Run interactive menu
        interactive_menu()
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mongo_manager.close()
