"""
Test 10+ different male offline voices for Jarvis
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from colorama import init, Fore, Style
init(autoreset=True)

import subprocess
import tempfile

# Test sentence
test_text = "Good morning, sir. All systems are operational. How may I assist you?"

print("\n" + "="*70)
print("  JARVIS OFFLINE VOICE COMPARISON - 10+ MALE VOICES")
print("="*70 + "\n")

print(f"Test sentence: '{test_text}'\n")

# Voice configurations to test
voices = [
    # Skip pyttsx3 - it causes hanging issues with multiple tests
    # Only test Piper voices (better quality, no hanging)
    {
        'name': '1. Piper - en_US-danny-low',
        'type': 'piper',
        'voice': 'en_US-danny-low',
        'description': 'Higher pitch, energetic male (CURRENT)'
    },
    {
        'name': '2. Piper - en_US-lessac-medium',
        'type': 'piper',
        'voice': 'en_US-lessac-medium',
        'description': 'Clear, professional male'
    },
    {
        'name': '3. Piper - en_US-lessac-low',
        'type': 'piper',
        'voice': 'en_US-lessac-low',
        'description': 'Same as #2 but faster generation'
    },
    {
        'name': '4. Piper - en_US-lessac-high',
        'type': 'piper',
        'voice': 'en_US-lessac-high',
        'description': 'High quality Lessac voice'
    },
    {
        'name': '5. Piper - en_US-ryan-high',
        'type': 'piper',
        'voice': 'en_US-ryan-high',
        'description': 'British accent, smooth male'
    },
    {
        'name': '6. Piper - en_US-ryan-medium',
        'type': 'piper',
        'voice': 'en_US-ryan-medium',
        'description': 'Ryan voice, medium quality'
    },
    {
        'name': '7. Piper - en_US-ryan-low',
        'type': 'piper',
        'voice': 'en_US-ryan-low',
        'description': 'Ryan voice, fast generation'
    },
    {
        'name': '8. Piper - en_US-libritts-high',
        'type': 'piper',
        'voice': 'en_US-libritts-high',
        'description': 'Multiple speakers, very natural'
    },
    {
        'name': '9. Piper - en_GB-alan-medium',
        'type': 'piper',
        'voice': 'en_GB-alan-medium',
        'description': 'British male, medium quality'
    },
    {
        'name': '10. Piper - en_GB-alan-low',
        'type': 'piper',
        'voice': 'en_GB-alan-low',
        'description': 'British male, fast generation'
    }
]

# Store results
results = {}

for voice_config in voices:
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{voice_config['name']}{Style.RESET_ALL}")
    print(f"Description: {voice_config['description']}")
    print()
    
    audio_path = None
    
    try:
        if voice_config['type'] == 'pyttsx3':
            # Test with pyttsx3
            import pyttsx3
            engine = pyttsx3.init()
            
            # Set male voice (David)
            voices_list = engine.getProperty('voices')
            if voices_list:
                engine.setProperty('voice', voices_list[0].id)  # David
            
            engine.setProperty('rate', voice_config['rate'])
            engine.setProperty('volume', voice_config['volume'])
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", prefix="jarvis_test_")
            audio_path = temp_file.name
            temp_file.close()
            
            engine.save_to_file(test_text, audio_path)
            engine.runAndWait()
            engine.stop()
            
        else:  # Piper
            # Test with Piper
            try:
                from piper.voice import PiperVoice
                voice = PiperVoice.load(voice_config['voice'])
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", prefix="jarvis_piper_")
                audio_path = temp_file.name
                temp_file.close()
                
                with open(audio_path, 'wb') as f:
                    voice.synthesize(test_text, f)
                    
            except Exception as e:
                print(f"{Fore.RED}  Piper TTS error: {e}{Style.RESET_ALL}")
                print(f"  Skipping this voice (model may need to be downloaded)")
                continue
        
        if audio_path and os.path.exists(audio_path):
            print(f"{Fore.GREEN}  ✓ Generated successfully{Style.RESET_ALL}")
            print(f"  Playing audio...")
            subprocess.run(['start', audio_path], shell=True)
            
            # Get rating
            print()
            rating = input(f"  {Fore.CYAN}Rate this voice (1-5) or 's' to skip: {Style.RESET_ALL}")
            
            if rating.lower() == 's':
                print(f"  Skipped")
                continue
            
            try:
                rating_num = int(rating)
                if 1 <= rating_num <= 5:
                    review = input(f"  {Fore.CYAN}One word review (optional): {Style.RESET_ALL}") or "N/A"
                    results[voice_config['name']] = {
                        'rating': rating_num,
                        'review': review,
                        'config': voice_config
                    }
                    print(f"{Fore.GREEN}  ✓ Saved: {rating_num}/5 - {review}{Style.RESET_ALL}")
            except:
                print(f"  Invalid rating")
        
    except Exception as e:
        print(f"{Fore.RED}  ✗ Error: {e}{Style.RESET_ALL}")
        continue

# Show results
print(f"\n\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
print(f"{Fore.GREEN}  YOUR RATINGS{Style.RESET_ALL}")
print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

if results:
    # Sort by rating
    sorted_results = sorted(results.items(), key=lambda x: x[1]['rating'], reverse=True)
    
    for voice_name, data in sorted_results:
        print(f"{data['rating']}/5 - {voice_name}")
        print(f"       Review: {data['review']}")
        print()
    
    # Show winner
    winner = sorted_results[0]
    print(f"\n{Fore.GREEN}🏆 WINNER: {winner[0]}{Style.RESET_ALL}")
    print(f"   Rating: {winner[1]['rating']}/5")
    print(f"   Review: {winner[1]['review']}")
    print()
    
    # Show config to use
    winner_config = winner[1]['config']
    print(f"{Fore.YELLOW}Configuration to use:{Style.RESET_ALL}")
    if winner_config['type'] == 'pyttsx3':
        print(f"  'pyttsx3_rate': {winner_config['rate']},")
        print(f"  'pyttsx3_volume': {winner_config['volume']},")
    else:
        print(f"  'piper_voice': '{winner_config['voice']}',")
    print()
else:
    print("No voices rated")

print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
