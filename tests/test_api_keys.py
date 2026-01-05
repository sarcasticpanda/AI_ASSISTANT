"""
Quick API Test Script
Tests OpenRouter and Groq API keys
"""

import requests
import os


# Test OpenRouter (Qwen)
print("🔍 Testing OpenRouter API...")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_key or openrouter_key.startswith("sk-or-v1-"):
    print("❌ OpenRouter: API key not set or using placeholder. Please set OPENROUTER_API_KEY in your environment.")
else:
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen-2.5-7b-instruct",
                "messages": [{"role": "user", "content": "Say 'API key working!'"}]
            },
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            print(f"✅ OpenRouter: SUCCESS")
            print(f"   Response: {message}")
        else:
            print(f"❌ OpenRouter: FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ OpenRouter: ERROR - {e}")
print()

try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "qwen/qwen-2.5-7b-instruct",
            "messages": [{"role": "user", "content": "Say 'API key working!'"}]
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        message = result["choices"][0]["message"]["content"]
        print(f"✅ OpenRouter: SUCCESS")
        print(f"   Response: {message}")
    else:
        print(f"❌ OpenRouter: FAILED")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")

except Exception as e:
    print(f"❌ OpenRouter: ERROR - {e}")

print()

# Test Groq
print("🔍 Testing Groq API...")
groq_key = os.getenv("GROQ_API_KEY", "")  # Load from environment variable or leave empty

try:
    response = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        models = response.json()
        print(f"✅ Groq: SUCCESS - API key is valid")
        print(f"   Available models: {len(models.get('data', []))} models")
    else:
        print(f"❌ Groq: FAILED")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")

except Exception as e:
    print(f"❌ Groq: ERROR - {e}")

print("\n✅ API test complete!")
