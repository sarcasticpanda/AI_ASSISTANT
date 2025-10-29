"""
JARVIS SYSTEM VERIFICATION
Systematically test each component before full integration
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=" * 70)
print("🔍 JARVIS SYSTEM VERIFICATION")
print("=" * 70)

# ============================================================================
# TEST 1: Environment Variables
# ============================================================================
print("\n📋 TEST 1: Checking .env file and API keys")
print("-" * 70)

from dotenv import load_dotenv

# Load from backend/.env
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
print(f"   Loading .env from: {env_path}")

if not os.path.exists(env_path):
    print(f"   ❌ .env file NOT FOUND at {env_path}")
    exit(1)

load_dotenv(env_path)

# Check API keys
groq_key = os.getenv('GROQ_API_KEY')
openrouter_key = os.getenv('OPENROUTER_API_KEY')
mongo_uri = os.getenv('MONGO_URI')

if groq_key and groq_key != 'gsk_REPLACE_ME':
    print(f"   ✅ GROQ_API_KEY loaded: {groq_key[:20]}...")
else:
    print(f"   ❌ GROQ_API_KEY missing or invalid")

if openrouter_key and openrouter_key != 'sk-or-v1-REPLACE_ME':
    print(f"   ✅ OPENROUTER_API_KEY loaded: {openrouter_key[:20]}...")
else:
    print(f"   ❌ OPENROUTER_API_KEY missing or invalid")

if mongo_uri:
    print(f"   ✅ MONGO_URI loaded: {mongo_uri}")
else:
    print(f"   ❌ MONGO_URI missing")

# ============================================================================
# TEST 2: Module Imports
# ============================================================================
print("\n📦 TEST 2: Testing module imports")
print("-" * 70)

errors = []

try:
    from backend.core import stt_online
    print("   ✅ stt_online imported successfully")
except Exception as e:
    print(f"   ❌ stt_online import failed: {e}")
    errors.append(f"stt_online: {e}")

try:
    from backend.core import brain
    print("   ✅ brain imported successfully")
except Exception as e:
    print(f"   ❌ brain import failed: {e}")
    errors.append(f"brain: {e}")

try:
    from backend.core import tts_manager
    print("   ✅ tts_manager imported successfully")
except Exception as e:
    print(f"   ❌ tts_manager import failed: {e}")
    errors.append(f"tts_manager: {e}")

try:
    from backend.core import mongo_manager
    print("   ✅ mongo_manager imported successfully")
except Exception as e:
    print(f"   ❌ mongo_manager import failed: {e}")
    errors.append(f"mongo_manager: {e}")

try:
    from backend.core import qwen_api
    print("   ✅ qwen_api imported successfully")
except Exception as e:
    print(f"   ❌ qwen_api import failed: {e}")
    errors.append(f"qwen_api: {e}")

if errors:
    print(f"\n⚠️  {len(errors)} import error(s) found")
    for err in errors:
        print(f"   - {err}")
    exit(1)

# ============================================================================
# TEST 3: MongoDB Connection
# ============================================================================
print("\n🗄️  TEST 3: Testing MongoDB connection")
print("-" * 70)

try:
    mongo_manager.initialize()
    mongo_manager.ping()
    print("   ✅ MongoDB connected successfully")
except Exception as e:
    print(f"   ⚠️  MongoDB connection failed: {e}")
    print("   ℹ️  This is OK - system will work without database")

# ============================================================================
# TEST 4: Groq API (STT)
# ============================================================================
print("\n📡 TEST 4: Testing Groq API (STT)")
print("-" * 70)

try:
    status = stt_online.test_connection()
    print(f"   {status}")
    
    if "✗" in status:
        print("   ⚠️  Groq API not reachable - check internet or API key")
except Exception as e:
    print(f"   ❌ STT test failed: {e}")

# ============================================================================
# TEST 5: TTS System
# ============================================================================
print("\n🔊 TEST 5: Testing TTS system")
print("-" * 70)

try:
    tts_status = tts_manager.get_status()
    print(f"   Internet: {tts_status['internet']}")
    print(f"   Online TTS available: {tts_status['online_tts']['available']}")
    print(f"   Online engine: {tts_status['online_tts']['engine']}")
    print(f"   Offline TTS available: {tts_status['offline_tts']['available']}")
    print(f"   Offline engine: {tts_status['offline_tts']['engine']}")
    print(f"   Recommended: {tts_status['recommended_engine']}")
    print("   ✅ TTS system loaded")
except Exception as e:
    print(f"   ❌ TTS test failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 6: Brain (process_command)
# ============================================================================
print("\n🧠 TEST 6: Testing brain.process_command()")
print("-" * 70)

try:
    # Test with simple time query
    response = brain.process_command("what time is it?")
    
    if isinstance(response, dict):
        print(f"   Response type: {type(response)}")
        print(f"   Keys: {response.keys()}")
        
        if 'response' in response:
            print(f"   ✅ Brain returned: \"{response['response'][:50]}...\"")
        else:
            print(f"   ⚠️  No 'response' key in output: {response}")
    else:
        # brain.py might return string directly
        print(f"   ✅ Brain returned (string): \"{response[:50]}...\"")
        
except Exception as e:
    print(f"   ❌ Brain test failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 7: PyAudio (Microphone)
# ============================================================================
print("\n🎤 TEST 7: Testing PyAudio (microphone support)")
print("-" * 70)

try:
    import pyaudio
    pa = pyaudio.PyAudio()
    
    # List devices
    device_count = pa.get_device_count()
    print(f"   Found {device_count} audio devices")
    
    # Find default input
    default_input = pa.get_default_input_device_info()
    print(f"   Default input: {default_input['name']}")
    print(f"   Max channels: {default_input['maxInputChannels']}")
    
    pa.terminate()
    print("   ✅ PyAudio working - microphone ready")
    
except Exception as e:
    print(f"   ❌ PyAudio test failed: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("📊 VERIFICATION SUMMARY")
print("=" * 70)

print("\n✅ READY:")
print("   - Environment variables loaded")
print("   - All core modules imported")

print("\n⚠️  NEEDS TESTING:")
print("   - STT with real audio (need to record voice)")
print("   - Full voice loop (record → STT → brain → TTS)")
print("   - MongoDB conversation save/load")

print("\n❌ NOT IMPLEMENTED:")
print("   - Wake word detection (OpenWakeWord)")
print("   - Threading/async optimization")

print("\n" + "=" * 70)
print("🎯 NEXT STEP: If no errors above, proceed to test_complete_voice.py")
print("=" * 70)
