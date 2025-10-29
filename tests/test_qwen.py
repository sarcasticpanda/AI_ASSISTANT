"""
Test Qwen LLM Communication
Send questions to Qwen via the /listen endpoint and see responses.
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Load environment variables from backend/.env
load_dotenv('backend/.env')

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://127.0.0.1:5000"

def ask_question(question):
    """Ask a question through the brain (simulating voice input)"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"YOU: {question}")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    try:
        # We'll use the /listen endpoint with a placeholder
        # (since we're simulating text input, not actual audio)
        payload = {
            "online": True,
            "audio_path": None
        }
        
        # For now, let's directly test the brain through a custom endpoint
        # But since we don't have a direct /ask endpoint, let's create a workaround
        # by directly calling the qwen_api module
        
        print(f"{Fore.YELLOW}🤔 Thinking...{Style.RESET_ALL}")
        
        # Add backend to path and import qwen_api module
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from core import qwen_api
        
        # Call Qwen with proper message format
        messages = [
            {"role": "system", "content": "You are Jarvis, a helpful AI assistant."},
            {"role": "user", "content": question}
        ]
        response = qwen_api.chat_completion(messages)
        
        print(f"{Fore.GREEN}JARVIS: {response}{Style.RESET_ALL}\n")
        return response
        
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
        return None


def main():
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"  QWEN LLM COMMUNICATION TEST")
    print(f"  Testing AI responses via OpenRouter")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    # Test questions
    questions = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms.",
        "Write a haiku about artificial intelligence.",
        "What is 25 multiplied by 47?",
        "Who won the FIFA World Cup in 2022?"
    ]
    
    print(f"{Fore.YELLOW}Select a question to ask Qwen:{Style.RESET_ALL}\n")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
    print(f"  6. Ask your own question")
    print(f"  7. Ask all questions (batch test)")
    
    try:
        choice = input(f"\n{Fore.CYAN}Enter your choice (1-7): {Style.RESET_ALL}")
        
        if choice == "6":
            custom_q = input(f"{Fore.CYAN}Enter your question: {Style.RESET_ALL}")
            ask_question(custom_q)
        elif choice == "7":
            print(f"\n{Fore.YELLOW}🚀 Running batch test...{Style.RESET_ALL}")
            for q in questions:
                ask_question(q)
                print(f"{Fore.BLUE}{'-'*70}{Style.RESET_ALL}")
        elif choice.isdigit() and 1 <= int(choice) <= 5:
            ask_question(questions[int(choice) - 1])
        else:
            print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"  TEST COMPLETE")
    print(f"{'='*70}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
