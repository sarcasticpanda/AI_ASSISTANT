
import sys
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv('backend/.env')

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core import brain, mongo_manager
from backend.skills import pdf_summarizer

def run_demo():
    print("\n" + "="*60)
    print("🚀 JARVIS CUSTOM DEMO (Weather & PDF Check)")
    print("="*60)

    # 1. Check MongoDB
    print("\n📊 CHECKING DATABASE...")
    mongo_manager.initialize()
    if mongo_manager._client:
        print("✅ MongoDB Connected")
    else:
        print("❌ MongoDB Not Connected")

    # 2. Check Weather (Simulated)
    print("\nbf CHECKING WEATHER CAPABILITY...")
    print("Command: 'what is the weather in London'")
    result = brain.process_command("what is the weather in London")
    print(f"Response: {result['response']}")
    print(f"Intent Detected: {result['intent']}")
    
    if result['intent'] == 'weather':
        print("✅ Weather skill detected!")
    else:
        print("⚠️  Weather skill NOT detected (handled by LLM or fallback)")

    # 3. Check PDF Capability
    print("\n📄 CHECKING PDF CAPABILITY...")
    # Check if we have the module
    if 'summarize_pdf' in dir(pdf_summarizer):
        print("✅ PDF Summarizer module loaded successfully")
        print("   Function: summarize_pdf(pdf_path)")
    else:
        print("❌ PDF Summarizer module missing functions")

    # 4. Check LLM (Chat)
    print("\n💬 CHECKING LLM (Chat)...")
    result = brain.process_command("Hello Jarvis, are you online?")
    print(f"Response: {result['response']}")
    
    if "Error" not in result['response']:
        print("✅ LLM/API Key Working")
    else:
        print("❌ LLM/API Key Failed")

    print("\n" + "="*60)
    print("✅ DEMO COMPLETE")
    print("="*60)

if __name__ == "__main__":
    run_demo()
