"""
TTS (Text-to-Speech) Test
Tests both online (gTTS) and offline (Coqui TTS) speech synthesis.
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


def test_online_tts():
    """Test online TTS (gTTS)"""
    print_header("TESTING ONLINE TTS (Google Text-to-Speech)")
    
    try:
        # Import module
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from core import tts_online
        
        print_success("tts_online module imported")
        
        # Test text
        test_text = "Hello! I am Jarvis, your AI assistant. This is a test of the online text to speech system using Google TTS."
        
        print_info(f"Test text: \"{test_text}\"")
        print(f"{Fore.YELLOW}🔊 Generating speech...{Style.RESET_ALL}")
        
        # Generate speech
        audio_path = tts_online.speak_online(test_text, lang="en")
        
        if audio_path and os.path.exists(audio_path):
            print_success(f"Audio file created: {audio_path}")
            
            # Get file size
            size = os.path.getsize(audio_path)
            print_info(f"File size: {size} bytes ({size/1024:.2f} KB)")
            
            # Ask to play
            print(f"\n{Fore.YELLOW}Would you like to play the audio?{Style.RESET_ALL}")
            choice = input(f"{Fore.CYAN}Play audio? (y/n): {Style.RESET_ALL}").lower()
            
            if choice == 'y':
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    
                    print_info("Playing audio... (press Enter when done)")
                    input()
                    pygame.mixer.music.stop()
                    print_success("Audio playback stopped")
                except Exception as e:
                    print_error(f"Playback failed: {e}")
                    print_info(f"You can manually play the file: {audio_path}")
            
            return True
        else:
            print_error("Audio file not created!")
            return False
            
    except Exception as e:
        print_error(f"Online TTS failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_offline_tts():
    """Test offline TTS (Coqui TTS)"""
    print_header("TESTING OFFLINE TTS (Coqui TTS)")
    
    try:
        # Import module
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from core import tts_offline
        
        print_success("tts_offline module imported")
        
        # Test text
        test_text = "This is a test of the offline text to speech system using Coqui TTS. The voice should sound more natural."
        
        print_info(f"Test text: \"{test_text}\"")
        print(f"{Fore.YELLOW}🔊 Generating speech with Coqui TTS...{Style.RESET_ALL}")
        print_info("This may take 10-30 seconds on first run (loading model)...")
        
        # Generate speech
        audio_path = tts_offline.speak_offline(test_text, lang="en")
        
        if audio_path and os.path.exists(audio_path):
            print_success(f"Audio file created: {audio_path}")
            
            # Get file size
            size = os.path.getsize(audio_path)
            print_info(f"File size: {size} bytes ({size/1024:.2f} KB)")
            
            # Ask to play
            print(f"\n{Fore.YELLOW}Would you like to play the audio?{Style.RESET_ALL}")
            choice = input(f"{Fore.CYAN}Play audio? (y/n): {Style.RESET_ALL}").lower()
            
            if choice == 'y':
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    
                    print_info("Playing audio... (press Enter when done)")
                    input()
                    pygame.mixer.music.stop()
                    print_success("Audio playback stopped")
                except Exception as e:
                    print_error(f"Playback failed: {e}")
                    print_info(f"You can manually play the file: {audio_path}")
            
            return True
        else:
            print_error("Audio file not created!")
            return False
            
    except Exception as e:
        print_error(f"Offline TTS failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"  JARVIS TTS (TEXT-TO-SPEECH) TEST")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}This will test both online and offline TTS systems.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Audio files will be generated and you can play them.{Style.RESET_ALL}\n")
    
    # Test online TTS
    online_result = test_online_tts()
    
    print("\n" + "-"*70 + "\n")
    
    # Test offline TTS
    offline_result = test_offline_tts()
    
    # Summary
    print_header("TEST SUMMARY")
    
    if online_result:
        print_success("Online TTS (gTTS): WORKING ✓")
    else:
        print_error("Online TTS (gTTS): FAILED ✗")
    
    if offline_result:
        print_success("Offline TTS (Coqui): WORKING ✓")
    else:
        print_error("Offline TTS (Coqui): FAILED ✗")
    
    if online_result and offline_result:
        print(f"\n{Fore.GREEN}✓ All TTS systems working!{Style.RESET_ALL}\n")
    else:
        print(f"\n{Fore.YELLOW}⚠ Some TTS systems need attention{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
