"""
Quick Alarm Test - Verify alarm functionality
"""

import sys
sys.path.insert(0, r'c:\Users\Lunar Panda\3-Main\assistant')

from backend.skills import alarms
from datetime import datetime, timedelta

print("\n" + "="*70)
print("⏰ ALARM FUNCTIONALITY TEST")
print("="*70)

# Test 1: Parse alarm from text
print("\n📝 Test 1: Parsing alarm commands")
test_commands = [
    "set alarm for 5pm",
    "remind me in 10 minutes",
    "set alarm for 2:30pm",
    "wake me up at 7am"
]

for cmd in test_commands:
    desc, scheduled_time = alarms.parse_alarm_from_text(cmd)
    if desc and scheduled_time:
        print(f"✅ '{cmd}'")
        print(f"   → Description: {desc}")
        print(f"   → Time: {scheduled_time.strftime('%I:%M %p')}")
    else:
        print(f"❌ '{cmd}' - Failed to parse")

# Test 2: Set a real alarm (2 minutes from now)
print("\n⏰ Test 2: Setting a test alarm")
future_time = datetime.now() + timedelta(minutes=2)
result = alarms.set_alarm("Test Alarm", future_time)
print(f"Result: {result}")

# Test 3: List all alarms
print("\n📋 Test 3: Checking all active alarms")
try:
    active = alarms.list_alarms()
    if active:
        print(f"Found {len(active)} active alarm(s):")
        for alarm in active:
            print(f"   • {alarm.get('description')} at {alarm.get('time')}")
    else:
        print("   No active alarms")
except Exception as e:
    print(f"   Error listing alarms: {e}")

print("\n" + "="*70)
print("✅ Test complete! If you see alarms listed above, they're working.")
print("💡 The alarm will ring in 2 minutes if everything works!")
print("="*70)
