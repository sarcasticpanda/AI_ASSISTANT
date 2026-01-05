"""
Comprehensive Skills Test
Tests all integrated skills through the brain interface.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core import brain

def test_skill(command: str, expected_intent: str = None):
    """Test a single command and print results"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {command}")
    print(f"{'='*60}")
    
    result = brain.process_command(command)
    
    print(f"✓ Response: {result['response']}")
    print(f"✓ Intent: {result['intent']}")
    print(f"✓ Success: {result['success']}")
    
    if expected_intent and result['intent'] != expected_intent:
        print(f"⚠️  WARNING: Expected intent '{expected_intent}', got '{result['intent']}'")
    
    return result

def main():
    """Run all skill tests"""
    
    print("\n" + "="*60)
    print("🚀 COMPREHENSIVE SKILLS TEST")
    print("="*60)
    
    # Time & Date
    print("\n📅 TIME & DATE SKILLS")
    test_skill("what time is it", "time")
    test_skill("what is today's date", "date")
    
    # System Info
    print("\n💻 SYSTEM INFO SKILLS")
    test_skill("battery status", "battery")
    test_skill("cpu usage", "cpu")
    test_skill("memory usage", "memory")
    test_skill("system info")
    
    # Open App (will try to open - may fail if path incorrect)
    print("\n🖥️  OPEN APP SKILL")
    test_skill("open calculator", "open_app")
    test_skill("open notepad", "open_app")
    
    # Alarms
    print("\n⏰ ALARM SKILL")
    test_skill("set alarm in 5 minutes", "alarm")
    test_skill("remind me in 10 minutes to check the oven", "alarm")
    
    # YouTube (will open browser)
    print("\n🎵 YOUTUBE SKILL")
    print("⚠️  Note: This will open your browser!")
    # test_skill("play python tutorial on youtube", "youtube")  # Uncomment to test
    
    # LLM Chat
    print("\n💬 LLM CHAT (WITH CONTEXT)")
    test_skill("explain what is machine learning", "chat")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main()
