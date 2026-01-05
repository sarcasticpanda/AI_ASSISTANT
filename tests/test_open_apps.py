"""
Test Open Apps Skill - Smart App Launcher
Tests the new Windows-native app detection system.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.skills.open_app import open_app, open_folder, open_website

def test_app(name: str, description: str):
    """Test opening an app"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {description}")
    print(f"   Command: open_app('{name}')")
    print(f"{'='*60}")
    
    result = open_app(name)
    print(f"✓ Result: {result}")
    
    return result

def main():
    """Run all app opening tests"""
    
    print("\n" + "="*60)
    print("🚀 SMART APP LAUNCHER TEST")
    print("="*60)
    print("\nNOTE: This will actually open applications!")
    print("Make sure you're ready to close apps that open.\n")
    
    input("Press ENTER to continue...")
    
    # System Apps (should work on all Windows)
    print("\n" + "="*60)
    print("📌 SYSTEM APPS (Guaranteed to work)")
    print("="*60)
    test_app("calculator", "Windows Calculator")
    test_app("notepad", "Notepad")
    test_app("explorer", "File Explorer")
    
    # Common Apps (work if installed)
    print("\n" + "="*60)
    print("🌐 BROWSERS (If installed)")
    print("="*60)
    test_app("chrome", "Google Chrome")
    test_app("edge", "Microsoft Edge")
    test_app("firefox", "Mozilla Firefox")
    
    # Productivity Apps
    print("\n" + "="*60)
    print("💼 PRODUCTIVITY (If installed)")
    print("="*60)
    test_app("notion", "Notion")
    test_app("vscode", "Visual Studio Code")
    test_app("obsidian", "Obsidian")
    
    # Communication Apps
    print("\n" + "="*60)
    print("💬 COMMUNICATION (If installed)")
    print("="*60)
    test_app("whatsapp", "WhatsApp")
    test_app("discord", "Discord")
    test_app("telegram", "Telegram")
    test_app("slack", "Slack")
    test_app("teams", "Microsoft Teams")
    
    # Entertainment
    print("\n" + "="*60)
    print("🎵 ENTERTAINMENT (If installed)")
    print("="*60)
    test_app("spotify", "Spotify")
    test_app("vlc", "VLC Media Player")
    
    # Folders
    print("\n" + "="*60)
    print("📁 FOLDERS")
    print("="*60)
    print(f"\n✓ Downloads: {open_folder('downloads')}")
    print(f"✓ Documents: {open_folder('documents')}")
    print(f"✓ Desktop: {open_folder('desktop')}")
    
    # Websites
    print("\n" + "="*60)
    print("🌐 WEBSITES")
    print("="*60)
    print(f"\n✓ Google: {open_website('google.com')}")
    print(f"✓ GitHub: {open_website('github.com')}")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETED")
    print("="*60)
    print("\n📊 SUMMARY:")
    print("   • System apps: Work via 'start' command")
    print("   • Installed apps: Auto-detected from Start Menu")
    print("   • No hardcoded paths needed!")
    print("   • Works on ANY Windows PC")
    print("\n💡 TIP: If an app didn't open, check:")
    print("   1. Is it installed?")
    print("   2. Can you find it in Start Menu?")
    print("   3. Try saying the exact Start Menu name")
    print()

if __name__ == "__main__":
    main()
