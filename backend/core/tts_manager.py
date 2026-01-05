"""
TTS Manager - Unified TTS System
Intelligently switches between online and offline TTS engines.

Priority Chain:
1. Edge TTS Streaming (online, best quality - Arjun voice +11% +7Hz, sentence-by-sentence)
2. Edge TTS Standard (online, full text at once)
3. gTTS (online fallback)
4. pyttsx3 (offline, system TTS)
5. Coqui TTS (offline, neural)
"""

import logging
import urllib.request
import os
import time
import threading
from typing import Optional, Tuple

from . import tts_online
from . import tts_offline
from . import tts_streaming

logger = logging.getLogger(__name__)


# ============================================================================
# INTERNET CONNECTION CHECK
# ============================================================================

def is_online() -> bool:
    """
    Check if internet connection is available.
    
    Returns:
        bool: True if online, False if offline
    """
    # Try multiple URLs with longer timeout
    test_urls = [
        'https://www.google.com',
        'https://1.1.1.1',  # Cloudflare DNS
        'https://8.8.8.8',  # Google DNS
    ]
    
    for url in test_urls:
        try:
            urllib.request.urlopen(url, timeout=5)
            return True
        except:
            continue
    
    return False


# ============================================================================
# UNIFIED TTS INTERFACE
# ============================================================================

def speak_streaming(text: str, lang: str = "en", interrupt_flag: Optional[threading.Event] = None) -> Tuple[float, str]:
    """
    Streaming TTS - Speaks sentence-by-sentence for faster perceived response.
    Generates and plays sentences in parallel.
    
    Args:
        text: Text to speak
        lang: Language code ('en', 'hi', 'mixed')
        interrupt_flag: Optional threading.Event to allow external interruption
    
    Returns:
        Tuple[float, str]: (total_time, engine_used)
    
    Example:
        total_time, engine = speak_streaming("Hello. How are you? I'm fine!")
        # First sentence plays in ~1-2s, rest streams in background
        
        # With interrupt:
        interrupt = threading.Event()
        total_time, engine = speak_streaming("Long text...", interrupt_flag=interrupt)
        # Call interrupt.set() from another thread to stop playback
    """
    logger.info(f"Streaming TTS: '{text[:50]}...' (lang={lang})")
    
    # Check if streaming is available
    if not tts_streaming.is_available():
        logger.warning("Streaming TTS not available, falling back to standard")
        audio_path, engine = speak(text, lang=lang, prefer_offline=False)
        return 0.0, engine
    
    # Check internet
    if not is_online():
        logger.warning("Offline - falling back to standard TTS")
        audio_path, engine = speak(text, lang=lang, prefer_offline=False)
        return 0.0, engine
    
    try:
        print(f"   🎵 Streaming TTS (sentence-by-sentence)...", flush=True)
        total_time, sentence_count = tts_streaming.speak_streaming(text, lang=lang, interrupt_flag=interrupt_flag)
        engine = tts_streaming.get_engine_info()
        
        logger.info(f"✓ Streaming TTS successful: {sentence_count} sentences in {total_time:.1f}s")
        print(f"   ✅ Spoke {sentence_count} sentences in {total_time:.1f}s", flush=True)
        
        return total_time, engine
    
    except Exception as e:
        logger.error(f"Streaming TTS failed: {e}")
        print(f"   ❌ Streaming failed: {e}", flush=True)
        
        # Fallback to standard TTS
        audio_path, engine = speak(text, lang=lang, prefer_offline=False)
        return 0.0, engine


def speak(text: str, lang: str = "en", prefer_offline: bool = False) -> Tuple[str, str]:
    """
    Universal TTS function - auto-selects best available engine.
    
    Args:
        text: Text to speak
        lang: Language code ('en', 'hi', 'mixed')
        prefer_offline: Force offline mode even if online available
    
    Returns:
        Tuple[str, str]: (audio_file_path, engine_used)
    
    Example:
        audio_path, engine = speak("Hello, I am Jarvis")
        # Returns: ("/tmp/tts_123.mp3", "Edge TTS")
    """
    logger.info(f"TTS request: '{text[:50]}...' (lang={lang}, prefer_offline={prefer_offline})")
    
    # Force offline mode if requested
    if prefer_offline:
        logger.info("Offline mode preferred by user")
        return _speak_offline(text, lang)
    
    # Check internet connection
    online = is_online()
    logger.info(f"Internet status: {'online' if online else 'offline'}")
    
    if online:
        # Try online TTS (Edge TTS -> gTTS) with a couple retries before falling back
        attempts = 2
        for attempt in range(1, attempts + 1):
            try:
                print(f"   🌐 Attempting Edge TTS (attempt {attempt}/{attempts})...", flush=True)
                audio_path = tts_online.speak_online(text, lang=lang)
                # Ensure we got a real file back
                if audio_path and os.path.exists(audio_path):
                    engine = tts_online.get_current_engine()
                    logger.info(f"✓ TTS successful using: {engine}")
                    print(f"   ✅ Edge TTS success!", flush=True)
                    return audio_path, engine
                else:
                    logger.warning(f"Online TTS returned no file (attempt {attempt}/{attempts}). Retrying...")
                    print(f"   ⚠️  No file returned, retrying...", flush=True)
            except Exception as e:
                logger.warning(f"Online TTS failed on attempt {attempt}/{attempts}: {e}")
                print(f"   ❌ Edge TTS error: {e}", flush=True)
            # small backoff before retry
            time.sleep(0.7)
    
    # Fallback to offline TTS
    print("   ⚠️  Edge TTS failed, falling back to offline pyttsx3...", flush=True)
    return _speak_offline(text, lang)


def _speak_offline(text: str, lang: str) -> Tuple[str, str]:
    """Use offline TTS"""
    logger.info("Using offline TTS")
    
    if not tts_offline.is_available():
        logger.error("No offline TTS available!")
        return "", "None"
    
    try:
        # Note: Offline TTS primarily supports English
        # Hindi will be spoken with English pronunciation
        if lang == 'hi':
            logger.warning("Hindi requested but offline TTS only supports English pronunciation")
        
        audio_path = tts_offline.speak_offline(text, lang='en')
        engine = tts_offline.get_current_engine()
        
        logger.info(f"✓ Offline TTS successful using: {engine}")
        return audio_path, engine
    
    except Exception as e:
        logger.error(f"Offline TTS failed: {e}")
        return "", "None"


def speak_simple(text: str):
    """
    Simple blocking TTS - speaks immediately.
    Useful for quick notifications.
    
    Args:
        text: Text to speak
    """
    if is_online():
        # Online: Generate and return path for external player
        audio_path = tts_online.speak_online(text)
        logger.info(f"Generated online TTS: {audio_path}")
        return audio_path
    else:
        # Offline: Use pyttsx3 direct speak
        tts_offline.speak_local_simple(text)
        return None


# ============================================================================
# STATUS AND INFO
# ============================================================================

def get_status() -> dict:
    """
    Get comprehensive TTS system status.
    
    Returns:
        dict: Status of all TTS engines and internet
    """
    online = is_online()
    
    status = {
        'internet': online,
        'online_tts': {
            'available': tts_online.is_available(),
            'engine': tts_online.get_current_engine(),
            'voice_config': tts_online.get_voice_info(),
            'languages': tts_online.get_supported_languages()
        },
        'offline_tts': {
            'available': tts_offline.is_available(),
            'engine': tts_offline.get_current_engine(),
            'voice_config': tts_offline.get_voice_info(),
            'languages': tts_offline.get_supported_languages(),
            'engines': tts_offline.get_status()
        },
        'streaming_tts': {
            'available': tts_streaming.is_available(),
            'engine': tts_streaming.get_engine_info()
        },
        'recommended_engine': tts_online.get_current_engine() if online else tts_offline.get_current_engine()
    }
    
    return status


def get_current_voice() -> str:
    """Get description of current active voice"""
    if is_online():
        return f"Online: {tts_online.get_current_engine()}"
    else:
        return f"Offline: {tts_offline.get_current_engine()}"


def print_status():
    """Print formatted TTS system status"""
    status = get_status()
    
    print("\n" + "="*70)
    print("🔊 TTS SYSTEM STATUS")
    print("="*70)
    
    # Internet
    internet_status = "✅ Online" if status['internet'] else "❌ Offline"
    print(f"\n📡 Internet: {internet_status}")
    
    # Online TTS
    print(f"\n🌐 ONLINE TTS:")
    if status['online_tts']['available']:
        print(f"   ✅ Available: {status['online_tts']['engine']}")
        voice = status['online_tts']['voice_config']
        print(f"   🎤 Voice: {voice['voice']} ({voice['description']})")
        print(f"   📊 Rating: {voice['rating']}")
        print(f"   🌍 Languages: {', '.join(voice['supports_languages'])}")
    else:
        print("   ❌ Not available")
    
    # Streaming TTS
    print(f"\n🎵 STREAMING TTS:")
    if status['streaming_tts']['available']:
        print(f"   ✅ Available: {status['streaming_tts']['engine']}")
    else:
        print("   ❌ Not available")
    
    # Offline TTS
    print(f"\n💻 OFFLINE TTS:")
    if status['offline_tts']['available']:
        print(f"   ✅ Available: {status['offline_tts']['engine']}")
        voice = status['offline_tts']['voice_config']
        print(f"   🎤 Voice: {voice.get('voice', 'System Default')}")
        print(f"   🌍 Languages: {', '.join(voice.get('supports_languages', ['en']))}")
    else:
        print("   ❌ Not available")
    
    # Recommendation
    print(f"\n💡 RECOMMENDED: {status['recommended_engine']}")
    print("="*70 + "\n")


# ============================================================================
# UTILITIES
# ============================================================================

def test_tts():
    """Test TTS system with a sample phrase"""
    print("\n🧪 Testing TTS System...")
    print_status()
    
    test_text = "Hello! I am Jarvis, your AI assistant. Testing text to speech."
    
    print(f"\n📝 Test text: \"{test_text}\"\n")
    
    # Test online
    if is_online():
        print("Testing Online TTS...")
        audio_path, engine = speak(test_text, lang='en')
        if audio_path:
            print(f"✅ Online TTS Success: {engine}")
            print(f"   Audio saved to: {audio_path}")
            
            # Play if possible
            try:
                tts_online.play_audio(audio_path)
                print("   ✅ Playback complete")
            except:
                print("   ⚠️  Could not play audio")
            
            # Cleanup
            try:
                os.remove(audio_path)
            except:
                pass
        else:
            print("❌ Online TTS Failed")
    else:
        print("⚠️  Offline - skipping online test")
    
    print("\n✅ TTS Test Complete!")
