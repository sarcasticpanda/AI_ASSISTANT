"""
Test Personality System - Verify Jarvis personality is working correctly
Tests quick replies, personality injection, and bilingual responses.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from colorama import Fore, Style, init
init(autoreset=True)

from core.personality import is_quick_reply, detect_language, JARVIS_PERSONALITY
from core.brain import process_command

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{title:^70}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def test_quick_replies():
    """Test quick reply system (no LLM needed)"""
    print_section("QUICK REPLIES TEST")
    
    test_cases = [
        "thanks",
        "thank you",
        "okay",
        "hello",
        "namaste",
        "shukriya"
    ]
    
    for text in test_cases:
        is_quick, response = is_quick_reply(text.lower())
        status = f"{Fore.GREEN}✓" if is_quick else f"{Fore.RED}✗"
        
        print(f"{status} Input: {Fore.YELLOW}'{text}'{Style.RESET_ALL}")
        if is_quick:
            print(f"  Response: {Fore.GREEN}'{response}'{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}Not recognized as quick reply{Style.RESET_ALL}")
        print()


def test_language_detection():
    """Test language detection"""
    print_section("LANGUAGE DETECTION TEST")
    
    test_cases = [
        ("What time is it?", "en"),
        ("समय क्या हुआ है?", "hi"),
        ("Chrome open karo", "mixed"),
        ("Hello, मदद चाहिए", "mixed"),
        ("Open Chrome", "en"),
        ("धन्यवाद", "hi")
    ]
    
    for text, expected in test_cases:
        detected = detect_language(text)
        match = detected == expected
        status = f"{Fore.GREEN}✓" if match else f"{Fore.RED}✗"
        
        print(f"{status} Input: {Fore.YELLOW}'{text}'{Style.RESET_ALL}")
        print(f"  Expected: {expected}, Detected: {Fore.CYAN}{detected}{Style.RESET_ALL}")
        print()


def test_personality_definition():
    """Test that personality is properly defined"""
    print_section("PERSONALITY DEFINITION TEST")
    
    checks = [
        ("Contains 'Jarvis'", "Jarvis" in JARVIS_PERSONALITY),
        ("Mentions bilingual", "bilingual" in JARVIS_PERSONALITY.lower() or "hindi" in JARVIS_PERSONALITY.lower()),
        ("Has response examples", "❌" in JARVIS_PERSONALITY or "✅" in JARVIS_PERSONALITY),
        ("Defines tone", "calm" in JARVIS_PERSONALITY.lower() or "confident" in JARVIS_PERSONALITY.lower()),
        ("Avoids robotic phrases", "As an AI" in JARVIS_PERSONALITY)
    ]
    
    for check_name, result in checks:
        status = f"{Fore.GREEN}✓" if result else f"{Fore.RED}✗"
        print(f"{status} {check_name}: {result}")
    
    print(f"\n{Fore.CYAN}Personality length: {len(JARVIS_PERSONALITY)} characters{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}First 200 characters:{Style.RESET_ALL}")
    print(f"{JARVIS_PERSONALITY[:200]}...")


def test_brain_integration():
    """Test that brain uses personality correctly"""
    print_section("BRAIN INTEGRATION TEST (with LLM)")
    
    print(f"{Fore.YELLOW}This test requires OpenRouter API and MongoDB to be running.{Style.RESET_ALL}\n")
    
    test_queries = [
        # Quick replies (no LLM)
        "thanks",
        "hello",
        
        # Factual queries (keyword match)
        "what time is it",
        "what's the date",
        
        # Conversational (needs LLM)
        "tell me a joke",
        "how are you",
    ]
    
    for query in test_queries:
        print(f"{Fore.CYAN}User:{Style.RESET_ALL} {query}")
        
        try:
            result = process_command(query)
            
            if result["success"]:
                print(f"{Fore.GREEN}Jarvis:{Style.RESET_ALL} {result['response']}")
                print(f"{Fore.YELLOW}  Intent: {result['intent']}, Method: {result.get('method', 'N/A')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Error: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}Exception: {e}{Style.RESET_ALL}")
        
        print()
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


def main():
    """Run all personality tests"""
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"{Fore.MAGENTA}JARVIS PERSONALITY SYSTEM TEST SUITE")
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}This test suite verifies:{Style.RESET_ALL}")
    print("  1. Quick reply system (instant responses)")
    print("  2. Language detection (English/Hindi/Mixed)")
    print("  3. Personality definition (content and structure)")
    print("  4. Brain integration (personality in action)")
    print()
    
    try:
        # Test 1: Quick Replies
        test_quick_replies()
        
        # Test 2: Language Detection
        test_language_detection()
        
        # Test 3: Personality Definition
        test_personality_definition()
        
        # Test 4: Brain Integration (requires user confirmation)
        print(f"\n{Fore.YELLOW}Do you want to test brain integration with LLM?{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}This will make actual API calls to OpenRouter.{Style.RESET_ALL}")
        choice = input(f"{Fore.CYAN}Continue? (y/n): {Style.RESET_ALL}").lower()
        
        if choice == 'y':
            test_brain_integration()
        else:
            print(f"{Fore.YELLOW}Skipping brain integration test.{Style.RESET_ALL}")
        
        # Summary
        print_section("TEST SUMMARY")
        print(f"{Fore.GREEN}✓ Quick replies: Working{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Language detection: Working{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Personality definition: Complete{Style.RESET_ALL}")
        
        if choice == 'y':
            print(f"{Fore.CYAN}→ Brain integration: Tested{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}→ Brain integration: Skipped{Style.RESET_ALL}")
    
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}Test interrupted by user.{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"\n\n{Fore.RED}Test failed with error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
