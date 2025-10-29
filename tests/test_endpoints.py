"""
Test Script for Jarvis API Endpoints
Tests each endpoint step-by-step with clear output.
"""

import requests
import json
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://127.0.0.1:5000"

def print_header(step, title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"{Fore.CYAN}STEP {step}: {title}{Style.RESET_ALL}")
    print("="*70)

def print_success(message):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print error message"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_json(data):
    """Print formatted JSON"""
    print(json.dumps(data, indent=2))


# ============================================================================
# STEP 1: Root Endpoint
# ============================================================================
def test_root():
    print_header(1, "Test Root Endpoint (GET /)")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            print_json(response.json())
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed: {e}")
        return False


# ============================================================================
# STEP 2: Health Check
# ============================================================================
def test_health():
    print_header(2, "Test Health Check (GET /health)")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            data = response.json()
            print_json(data)
            
            # Check MongoDB status
            if data.get("services", {}).get("mongodb") == "connected":
                print_success("MongoDB is connected!")
            else:
                print_error(f"MongoDB status: {data.get('services', {}).get('mongodb')}")
            
            # Check LLM configuration
            if data.get("services", {}).get("llm") == "openrouter":
                print_success("OpenRouter API key configured!")
            else:
                print_error("OpenRouter API key not configured")
            
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed: {e}")
        return False


# ============================================================================
# STEP 3: Text-to-Speech
# ============================================================================
def test_speak():
    print_header(3, "Test Text-to-Speech (POST /speak)")
    
    # Test online TTS (gTTS)
    print(f"\n{Fore.YELLOW}Testing ONLINE TTS (gTTS)...{Style.RESET_ALL}")
    try:
        payload = {
            "text": "Hello! I am Jarvis, your AI assistant.",
            "online": True,
            "lang": "en"
        }
        response = requests.post(f"{BASE_URL}/speak", json=payload)
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            data = response.json()
            print_json(data)
            print_success(f"Audio saved to: {data.get('audio_path')}")
        else:
            print_error(f"Status Code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print_error(f"Online TTS failed: {e}")
    
    # Test offline TTS (Coqui)
    print(f"\n{Fore.YELLOW}Testing OFFLINE TTS (Coqui)...{Style.RESET_ALL}")
    try:
        payload = {
            "text": "This is offline text to speech using Coqui TTS.",
            "online": False,
            "lang": "en"
        }
        response = requests.post(f"{BASE_URL}/speak", json=payload)
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            data = response.json()
            print_json(data)
            print_success(f"Audio saved to: {data.get('audio_path')}")
        else:
            print_error(f"Status Code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print_error(f"Offline TTS failed: {e}")


# ============================================================================
# STEP 4: Conversation History
# ============================================================================
def test_history():
    print_header(4, "Test Conversation History (GET /history)")
    try:
        response = requests.get(f"{BASE_URL}/history?limit=5")
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"\n{Fore.YELLOW}Total conversations: {data.get('total')}{Style.RESET_ALL}")
            
            if data.get('history'):
                print(f"\n{Fore.YELLOW}Recent conversations:{Style.RESET_ALL}")
                for i, conv in enumerate(data.get('history', [])[:3], 1):
                    print(f"\n{Fore.CYAN}Conversation {i}:{Style.RESET_ALL}")
                    print(f"  User: {conv.get('user_text', 'N/A')}")
                    print(f"  Assistant: {conv.get('assistant_text', 'N/A')}")
                    print(f"  Intent: {conv.get('intent', 'N/A')}")
            else:
                print_success("No conversation history yet (empty database)")
            
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed: {e}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def main():
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"  JARVIS API ENDPOINT TESTING")
    print(f"  Testing backend: {BASE_URL}")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    # Check if server is running
    print(f"{Fore.YELLOW}Checking if server is running...{Style.RESET_ALL}")
    try:
        requests.get(BASE_URL, timeout=2)
        print_success("Server is running!")
    except:
        print_error("Server is NOT running!")
        print(f"\n{Fore.YELLOW}Please start the server first:{Style.RESET_ALL}")
        print("  cd backend")
        print("  python app.py")
        return
    
    # Run tests
    test_root()
    test_health()
    test_speak()
    test_history()
    
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"  TESTING COMPLETE!")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Next Steps:{Style.RESET_ALL}")
    print("  1. Test PDF summarization with an actual PDF file")
    print("  2. Test Speech-to-Text with an audio file")
    print("  3. Build the Electron frontend!")


if __name__ == "__main__":
    main()
