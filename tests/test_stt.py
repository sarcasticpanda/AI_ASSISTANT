"""
STT (Speech-to-Text) Test
Tests both online (Groq Whisper) and offline (faster-whisper) transcription.
"""

import sys
import os
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Load environment
load_dotenv('backend/.env')

def print_header(title):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Style.RESET_ALL}\n")

def print_success(message):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print error message"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")


def create_test_audio():
    """Create a test audio file using TTS"""
    print_header("CREATING TEST AUDIO FILE")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from core import tts_online
        
        test_text = "Hello, this is a test of the speech to text system. The quick brown fox jumps over the lazy dog."
        
        print_info(f"Generating test audio with text: \"{test_text}\"")
        
        audio_path = tts_online.speak_online(test_text, lang="en")
        
        if audio_path and os.path.exists(audio_path):
            print_success(f"Test audio created: {audio_path}")
            return audio_path, test_text
        else:
            print_error("Failed to create test audio")
            return None, None
            
    except Exception as e:
        print_error(f"Failed to create test audio: {e}")
        return None, None


def test_online_stt(audio_path, expected_text):
    """Test online STT (Groq Whisper)"""
    print_header("TESTING ONLINE STT (Groq Whisper API)")
    
    if not audio_path:
        print_error("No audio file provided!")
        return False
    
    try:
        # Import module
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from core import stt_online
        
        print_success("stt_online module imported")
        print_info(f"Audio file: {audio_path}")
        print_info(f"Expected text: \"{expected_text}\"")
        
        print(f"\n{Fore.YELLOW}🎤 Transcribing with Groq Whisper...{Style.RESET_ALL}")
        
        # Transcribe
        transcribed_text = stt_online.transcribe_online(audio_path)
        
        if transcribed_text:
            print_success("Transcription successful!")
            print(f"\n{Fore.CYAN}Transcribed text:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}\"{transcribed_text}\"{Style.RESET_ALL}\n")
            
            # Compare with expected
            if expected_text.lower() in transcribed_text.lower() or transcribed_text.lower() in expected_text.lower():
                print_success("✓ Transcription matches expected text!")
            else:
                print_info("⚠ Transcription differs from expected (this is normal)")
            
            return True
        else:
            print_error("No transcription returned!")
            return False
            
    except Exception as e:
        print_error(f"Online STT failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_offline_stt(audio_path, expected_text):
    """Test offline STT (faster-whisper)"""
    print_header("TESTING OFFLINE STT (faster-whisper)")
    
    if not audio_path:
        print_error("No audio file provided!")
        return False
    
    try:
        # Import module
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from core import stt_local
        
        print_success("stt_local module imported")
        print_info(f"Audio file: {audio_path}")
        print_info(f"Expected text: \"{expected_text}\"")
        
        print(f"\n{Fore.YELLOW}🎤 Transcribing with faster-whisper...{Style.RESET_ALL}")
        print_info("This may take 10-30 seconds on first run (downloading model)...")
        
        # Transcribe
        transcribed_text = stt_local.transcribe_file(audio_path)
        
        if transcribed_text:
            print_success("Transcription successful!")
            print(f"\n{Fore.CYAN}Transcribed text:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}\"{transcribed_text}\"{Style.RESET_ALL}\n")
            
            # Compare with expected
            if expected_text.lower() in transcribed_text.lower() or transcribed_text.lower() in expected_text.lower():
                print_success("✓ Transcription matches expected text!")
            else:
                print_info("⚠ Transcription differs from expected (this is normal)")
            
            return True
        else:
            print_error("No transcription returned!")
            return False
            
    except Exception as e:
        print_error(f"Offline STT failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_custom_audio():
    """Test with user-provided audio file"""
    print_header("TEST WITH CUSTOM AUDIO FILE")
    
    audio_path = input(f"\n{Fore.CYAN}Enter path to audio file (MP3/WAV): {Style.RESET_ALL}").strip()
    
    if not os.path.exists(audio_path):
        print_error(f"File not found: {audio_path}")
        return False
    
    print_success(f"Using audio file: {audio_path}")
    
    # Test online
    print("\n" + "-"*70 + "\n")
    test_online_stt(audio_path, "")
    
    # Test offline
    print("\n" + "-"*70 + "\n")
    test_offline_stt(audio_path, "")
    
    return True


def main():
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"  JARVIS STT (SPEECH-TO-TEXT) TEST")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Choose test mode:{Style.RESET_ALL}\n")
    print("  1. Auto test (generate audio + transcribe)")
    print("  2. Test with your own audio file")
    
    choice = input(f"\n{Fore.CYAN}Enter choice (1-2): {Style.RESET_ALL}").strip()
    
    if choice == "2":
        test_with_custom_audio()
    else:
        # Auto test mode
        audio_path, expected_text = create_test_audio()
        
        if not audio_path:
            print_error("Cannot proceed without test audio")
            return
        
        print("\n" + "-"*70 + "\n")
        
        # Test online STT
        online_result = test_online_stt(audio_path, expected_text)
        
        print("\n" + "-"*70 + "\n")
        
        # Test offline STT
        offline_result = test_offline_stt(audio_path, expected_text)
        
        # Summary
        print_header("TEST SUMMARY")
        
        if online_result:
            print_success("Online STT (Groq Whisper): WORKING ✓")
        else:
            print_error("Online STT (Groq Whisper): FAILED ✗")
        
        if offline_result:
            print_success("Offline STT (faster-whisper): WORKING ✓")
        else:
            print_error("Offline STT (faster-whisper): FAILED ✗")
        
        if online_result and offline_result:
            print(f"\n{Fore.GREEN}✓ All STT systems working!{Style.RESET_ALL}\n")
        else:
            print(f"\n{Fore.YELLOW}⚠ Some STT systems need attention{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
