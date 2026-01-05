
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core import brain
from backend.skills import weather_skill

def test_weather():
    print("\n" + "="*60)
    print("🌤️  TESTING WEATHER SKILL")
    print("="*60)

    # 1. Test Direct Skill Function
    print("\n1. Direct Skill Test:")
    try:
        print("   Checking London...")
        res = weather_skill.get_weather("London")
        print(f"   Result: {res}")
        
        print("   Checking Auto-IP...")
        res = weather_skill.get_weather(None)
        print(f"   Result: {res}")
    except Exception as e:
        print(f"   ❌ Direct test failed: {e}")

    # 2. Test via Brain (Command Processing)
    print("\n2. Brain Integration Test:")
    
    commands = [
        "what is the weather in Paris",
        "check weather for Tokyo",
        "weather"
    ]
    
    for cmd in commands:
        print(f"\n   Command: '{cmd}'")
        result = brain.process_command(cmd)
        print(f"   Response: {result['response']}")
        print(f"   Intent: {result['intent']}")
        
        if result['intent'] == 'weather':
            print("   ✅ Intent correctly detected")
        else:
            print("   ❌ Intent failed")

    print("\n" + "="*60)
    print("✅ WEATHER TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_weather()
