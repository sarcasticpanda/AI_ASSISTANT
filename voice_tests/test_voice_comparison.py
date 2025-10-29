"""
Voice Comparison Test - Find Your Perfect Jarvis Voice
Tests multiple TTS engines with both English and Hindi samples.
Requirement: Male, optimistic, calm, bilingual (English + Hindi), fast
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Initialize
init(autoreset=True)
load_dotenv('backend/.env')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

def print_header(title):
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Style.RESET_ALL}\n")

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")


# Test sentences
TEST_SENTENCES = {
    "english": "Good morning, sir. All systems are operational and ready for deployment.",
    "hindi": "नमस्ते। सभी सिस्टम तैयार हैं। मैं आपकी सहायता के लिए उपलब्ध हूं।",
    "mixed": "Sir, Chrome browser open हो गया है। Kuch aur chahiye?"
}


def play_audio_file(file_path):
    """Play audio file using Windows default player"""
    try:
        import subprocess
        subprocess.run(['start', file_path], shell=True, check=True)
        return True
    except Exception as e:
        print_error(f"Playback failed: {e}")
        return False


def rate_voice():
    """Ask user to rate the voice and add a review"""
    while True:
        rating = input(f"\n{Fore.CYAN}Rate this voice (1-5, or 's' to skip): {Style.RESET_ALL}").strip()
        if rating == 's':
            return 0, "skipped"
        try:
            r = int(rating)
            if 1 <= r <= 5:
                # Ask for review
                review = input(f"{Fore.CYAN}One-two word review (optional): {Style.RESET_ALL}").strip()
                if not review:
                    review = "no comment"
                return r, review
        except:
            pass
        print_error("Please enter 1-5 or 's'")


# ============================================================================
# TEST 1: Edge TTS (Microsoft - Best Free Option!)
# ============================================================================

def test_edge_tts():
    """Test Edge TTS - Microsoft's free, natural voices"""
    print_header("TEST 1: Edge TTS (Microsoft) - ONLINE - RECOMMENDED!")
    
    print_info("Pros: Natural voice, free, fast, supports Hindi, MALE voices")
    print_info("Cons: Requires internet")
    
    try:
        import edge_tts
        import asyncio
        import tempfile
        
        ratings = {}
        reviews = {}
        
        # Best male voices
        male_voices = [
            ("en-US-GuyNeural", "Guy (US Male - Calm)"),
            ("en-IN-PrabhatNeural", "Prabhat (Indian Male - Perfect for Hindi+English!)"),
            ("en-GB-RyanNeural", "Ryan (UK Male - Professional)")
        ]
        
        print(f"\n{Fore.CYAN}Testing 3 excellent male voices:{Style.RESET_ALL}\n")
        
        for voice_id, voice_name in male_voices:
            print(f"\n{Fore.YELLOW}🔊 Testing: {voice_name}{Style.RESET_ALL}")
            print(f'   "{TEST_SENTENCES["english"]}"')
            
            # Generate speech
            async def generate():
                communicate = edge_tts.Communicate(TEST_SENTENCES["english"], voice_id, rate="+10%")
                audio_file = tempfile.mktemp(suffix='.mp3')
                await communicate.save(audio_file)
                return audio_file
            
            audio_file = asyncio.run(generate())
            
            print_success(f"Audio saved: {audio_file}")
            play_audio_file(audio_file)
            
            ratings[voice_name], reviews[voice_name] = rate_voice()
        
        # Test Hindi with Indian voice
        print(f"\n{Fore.YELLOW}🔊 Testing Hindi (Prabhat - Indian Male)...{Style.RESET_ALL}")
        print(f'   "{TEST_SENTENCES["hindi"]}"')
        
        async def generate_hindi():
            communicate = edge_tts.Communicate(TEST_SENTENCES["hindi"], "hi-IN-MadhurNeural", rate="+10%")
            audio_file = tempfile.mktemp(suffix='.mp3')
            await communicate.save(audio_file)
            return audio_file
        
        audio_file = asyncio.run(generate_hindi())
        print_success(f"Audio saved: {audio_file}")
        play_audio_file(audio_file)
        
        ratings['Hindi (Madhur)'], reviews['Hindi (Madhur)'] = rate_voice()
        
        return {
            'name': 'Edge TTS (Microsoft)',
            'type': 'online',
            'ratings': ratings,
            'reviews': reviews,
            'avg': sum(ratings.values()) / len(ratings) if ratings else 0,
            'speed': 'Fast',
            'quality': 'Natural',
            'hindi_support': True,
            'cost': 'Free'
        }
        
    except ImportError:
        print_error("edge-tts not installed. Installing...")
        import subprocess
        subprocess.run(['pip', 'install', 'edge-tts'], check=True)
        print_success("Installed! Please run the test again.")
        return None
    except Exception as e:
        print_error(f"Edge TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 2: gTTS (Online - Google Text-to-Speech)
# ============================================================================

def test_gtts():
    """Test gTTS - Online, free, multiple languages"""
    print_header("TEST 2: gTTS (Google Text-to-Speech) - ONLINE")
    
    print_info("Pros: Free, supports Hindi, simple")
    print_info("Cons: More robotic than Edge TTS, generic voice")
    
    try:
        from gtts import gTTS
        import tempfile
        from pydub import AudioSegment
        from pydub.playback import play
        
        ratings = {}
        reviews = {}
        
        # Test English with faster speed
        print(f"\n{Fore.YELLOW}🔊 Testing English (sped up 1.3x)...{Style.RESET_ALL}")
        print(f'   "{TEST_SENTENCES["english"]}"')
        
        tts = gTTS(text=TEST_SENTENCES["english"], lang='en', slow=False)
        audio_file = tempfile.mktemp(suffix='.mp3')
        tts.save(audio_file)
        
        # Speed up audio by 30%
        try:
            sound = AudioSegment.from_mp3(audio_file)
            faster_sound = sound.speedup(playback_speed=1.3)
            fast_file = tempfile.mktemp(suffix='.mp3')
            faster_sound.export(fast_file, format="mp3")
            audio_file = fast_file
            print_success(f"Audio sped up 1.3x for faster playback")
        except:
            print_info("Speed adjustment not available, playing normal speed")
        
        print_success(f"Audio saved: {audio_file}")
        play_audio_file(audio_file)
        ratings['english'], reviews['english'] = rate_voice()
        
        # Test Hindi
        print(f"\n{Fore.YELLOW}🔊 Testing Hindi...{Style.RESET_ALL}")
        print(f'   "{TEST_SENTENCES["hindi"]}"')
        
        tts = gTTS(text=TEST_SENTENCES["hindi"], lang='hi', slow=False)
        audio_file = tempfile.mktemp(suffix='.mp3')
        tts.save(audio_file)
        
        print_success(f"Audio saved: {audio_file}")
        play_audio_file(audio_file)
        ratings['hindi'], reviews['hindi'] = rate_voice()
        
        return {
            'name': 'gTTS (Google)',
            'type': 'online',
            'ratings': ratings,
            'reviews': reviews,
            'avg': sum(ratings.values()) / len(ratings) if ratings else 0,
            'speed': 'Fast',
            'quality': 'Robotic',
            'hindi_support': True,
            'cost': 'Free'
        }
        
    except Exception as e:
        print_error(f"gTTS test failed: {e}")
        return None


# ============================================================================
# TEST 2: Coqui TTS (Offline - High Quality)
# ============================================================================

def test_coqui():
    """Test Coqui TTS - Offline, high quality"""
    print_header("TEST 2: Coqui TTS - OFFLINE HIGH QUALITY")
    
    print_info("Pros: Natural voice, offline, customizable")
    print_info("Cons: Slow first run (downloads model), English only")
    print_info("Loading model (may take 30-60 seconds on first run)...")
    
    try:
        from TTS.api import TTS
        import tempfile
        
        ratings = {}
        reviews = {}
        
        # Test with default English model
        print(f"\n{Fore.YELLOW}🔊 Testing English (ljspeech model)...{Style.RESET_ALL}")
        print(f'   "{TEST_SENTENCES["english"]}"')
        
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        audio_file = tempfile.mktemp(suffix='.wav')
        tts.tts_to_file(text=TEST_SENTENCES["english"], file_path=audio_file)
        
        print_success(f"Audio saved: {audio_file}")
        play_audio_file(audio_file)
        ratings['english'], reviews['english'] = rate_voice()
        
        print_info("Hindi not supported in this model ❌")
        
        return {
            'name': 'Coqui TTS (LJSpeech)',
            'type': 'offline',
            'ratings': ratings,
            'reviews': reviews,
            'avg': ratings.get('english', 0),
            'speed': 'Slow (first run)',
            'quality': 'Natural',
            'hindi_support': False,
            'cost': 'Free'
        }
        
    except Exception as e:
        print_error(f"Coqui TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 3: pyttsx3 (Offline - System Voices)
# ============================================================================

def test_pyttsx3():
    """Test pyttsx3 - Uses Windows system voices"""
    print_header("TEST 3: pyttsx3 (Windows System Voices) - OFFLINE")
    
    print_info("Pros: Fast, offline, multiple voices")
    print_info("Cons: Robotic, limited Hindi support")
    
    try:
        import pyttsx3
        import tempfile
        import time
        
        ratings = {}
        reviews = {}
        
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            print(f"\n{Fore.CYAN}Available voices on your system:{Style.RESET_ALL}")
            for i, voice in enumerate(voices):
                print(f"  {i+1}. {voice.name}")
            
            # Only test first voice to avoid hanging
            print(f"\n{Fore.YELLOW}Testing only the first voice to avoid hanging...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}(You can test other voices manually later if needed){Style.RESET_ALL}")
            
            if voices:
                voice = voices[0]
                print(f"\n{Fore.YELLOW}🔊 Testing: {voice.name}{Style.RESET_ALL}")
                print(f'   "{TEST_SENTENCES["english"]}"')
                
                engine.setProperty('voice', voice.id)
                engine.setProperty('rate', 175)  # Speed (default 200)
                
                audio_file = tempfile.mktemp(suffix='.wav')
                engine.save_to_file(TEST_SENTENCES["english"], audio_file)
                engine.runAndWait()
                
                # Give it a moment to finish
                time.sleep(1)
                
                print_success(f"Audio saved: {audio_file}")
                play_audio_file(audio_file)
                
                ratings[voice.name], reviews[voice.name] = rate_voice()
                
                # Stop engine to prevent hanging
                engine.stop()
        
        except Exception as e:
            print_error(f"pyttsx3 engine error: {e}")
            return None
        
        return {
            'name': 'pyttsx3 (System Voices)',
            'type': 'offline',
            'ratings': ratings,
            'reviews': reviews,
            'avg': sum(ratings.values()) / len(ratings) if ratings else 0,
            'speed': 'Very Fast',
            'quality': 'Robotic',
            'hindi_support': 'Limited',
            'cost': 'Free'
        }
        
    except Exception as e:
        print_error(f"pyttsx3 test failed: {e}")
        return None


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"  JARVIS VOICE SELECTION TEST")
    print(f"  Finding the perfect male, bilingual, calm voice")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}REQUIREMENTS:{Style.RESET_ALL}")
    print("  ✓ Male voice")
    print("  ✓ Optimistic and calm tone")
    print("  ✓ Supports English + Hindi")
    print("  ✓ Fast (not slow/laggy)")
    print()
    
    print(f"{Fore.YELLOW}TEST PLAN:{Style.RESET_ALL}")
    print("  1. Edge TTS (Microsoft) - BEST FREE OPTION! Natural male voices 🌟")
    print("  2. gTTS (Google) - Online, bilingual (faster playback)")
    print("  3. Coqui TTS - Offline, high quality (English only)")
    print("  4. pyttsx3 - Offline, system voices (English only)")
    print()
    print(f"{Fore.GREEN}RECOMMENDED: Try Edge TTS first - it has calm male voices!{Style.RESET_ALL}")
    print()
    
    input(f"{Fore.CYAN}Press Enter to start testing...{Style.RESET_ALL}")
    
    results = []
    
    # Test Edge TTS first (best option)
    print(f"\n{Fore.GREEN}Testing Edge TTS - This is the best free option!{Style.RESET_ALL}")
    result0 = test_edge_tts()
    if result0:
        results.append(result0)
    
    print("\n" + "-"*70 + "\n")
    
    # Ask if they want to continue testing others
    choice = input(f"{Fore.CYAN}Edge TTS is recommended. Test other options? (y/n): {Style.RESET_ALL}").lower()
    if choice != 'y':
        print(f"{Fore.GREEN}Great choice! Edge TTS it is.{Style.RESET_ALL}")
    else:
        # Test gTTS
        result1 = test_gtts()
        if result1:
            results.append(result1)
        
        print("\n" + "-"*70 + "\n")
        
        # Ask before Coqui (can be slow)
        choice = input(f"{Fore.CYAN}Test Coqui TTS? (first run downloads ~500MB model) (y/n): {Style.RESET_ALL}").lower()
        if choice == 'y':
            result2 = test_coqui()
            if result2:
                results.append(result2)
        else:
            print(f"{Fore.YELLOW}Skipping Coqui TTS test{Style.RESET_ALL}")
    
    print("\n" + "-"*70 + "\n")
    
    # Ask before pyttsx3
    choice = input(f"{Fore.CYAN}Test pyttsx3 system voices? (y/n): {Style.RESET_ALL}").lower()
    if choice == 'y':
        result3 = test_pyttsx3()
        if result3:
            results.append(result3)
    else:
        print(f"{Fore.YELLOW}Skipping pyttsx3 test{Style.RESET_ALL}")
    
    # Show results
    print_header("TEST RESULTS SUMMARY")
    
    if not results:
        print_error("No successful tests!")
        return
    
    # Sort by average rating
    results.sort(key=lambda x: x['avg'], reverse=True)
    
    print(f"\n{Fore.CYAN}Ranking (by your ratings):{Style.RESET_ALL}\n")
    
    for i, result in enumerate(results, 1):
        print(f"{Fore.GREEN if i == 1 else Fore.YELLOW}{i}. {result['name']}{Style.RESET_ALL}")
        print(f"   Average Rating: {result['avg']:.1f}/5.0 ⭐")
        print(f"   Ratings: {result['ratings']}")
        print(f"   Reviews: {result.get('reviews', {})}")
        print(f"   Type: {result['type']}")
        print(f"   Speed: {result['speed']}")
        print(f"   Quality: {result['quality']}")
        print(f"   Hindi Support: {'✓' if result['hindi_support'] else '✗'}")
        print(f"   Cost: {result['cost']}")
        print()
    
    # Recommendation
    print_header("RECOMMENDATION")
    
    winner = results[0]
    print(f"{Fore.GREEN}🏆 Best voice: {winner['name']}{Style.RESET_ALL}")
    print(f"   Your rating: {winner['avg']:.1f}/5.0")
    print()
    
    # Analysis based on requirements
    print(f"{Fore.YELLOW}Based on your requirements:{Style.RESET_ALL}\n")
    
    if winner['hindi_support']:
        print(f"{Fore.GREEN}✓ Hindi support: YES{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Hindi support: NO{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}→ For Hindi, consider using gTTS{Style.RESET_ALL}")
    
    if winner['type'] == 'offline':
        print(f"{Fore.GREEN}✓ Works offline: YES{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ Requires internet{Style.RESET_ALL}")
    
    print()
    print(f"{Fore.CYAN}Final Suggestion:{Style.RESET_ALL}")
    print(f"  Use {Fore.GREEN}{winner['name']}{Style.RESET_ALL} as primary voice")
    
    # Check if we need dual setup
    if not winner['hindi_support'] and any(r['hindi_support'] for r in results):
        hindi_option = next(r for r in results if r['hindi_support'])
        print(f"  Use {Fore.GREEN}{hindi_option['name']}{Style.RESET_ALL} for Hindi support")
        print(f"  {Fore.YELLOW}→ Hybrid setup: English={winner['name']}, Hindi={hindi_option['name']}{Style.RESET_ALL}")
    
    print()
    
    # Save results to file
    save_results(results, winner)


def save_results(results, winner):
    """Save test results and ratings to a JSON file"""
    try:
        results_file = Path(__file__).parent / 'voice_test_results.json'
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'winner': winner['name'],
            'winner_rating': winner['avg'],
            'all_results': results,
            'recommendation': {
                'primary_voice': winner['name'],
                'hindi_support': winner['hindi_support'],
                'type': winner['type']
            }
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"{Fore.GREEN}✓ Results saved to: {results_file}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}You can review your ratings and reviews anytime!{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.YELLOW}⚠ Could not save results: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
