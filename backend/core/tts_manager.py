"""
TTS Manager - Unified TTS System
Intelligently switches between online and offline TTS engines.

Priority Chain:
1. Edge TTS (online, best quality - Arjun voice +11% +7Hz)
2. gTTS (online fallback)
3. pyttsx3 (offline, system TTS)
4. Coqui TTS (offline, neural)
"""

import logging
import urllib.request
from typing import Optional, Tuple

from . import tts_online
from . import tts_offline

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
    try:
        # Try to reach Google DNS
        urllib.request.urlopen('https://www.google.com', timeout=2)
        return True
    except:
        return False


# ============================================================================
# UNIFIED TTS INTERFACE
# ============================================================================

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
        # Try online TTS (Edge TTS -> gTTS)
        try:
            audio_path = tts_online.speak_online(text, lang=lang)
            if audio_path:
                engine = tts_online.get_current_engine()
                logger.info(f"✓ TTS successful using: {engine}")
                return audio_path, engine
        except Exception as e:
            logger.warning(f"Online TTS failed: {e}")
    
    # Fallback to offline TTS
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
    print("  JARVIS TTS SYSTEM STATUS")
    print("="*70)
    
    print(f"\n🌐 Internet: {'✓ Connected' if status['internet'] else '✗ Offline'}")
    
    print(f"\n📡 Online TTS:")
    if status['online_tts']['available']:
        print(f"  ✓ {status['online_tts']['engine']}")
        config = status['online_tts']['voice_config']
        print(f"  Voice: {config['voice']}")
        print(f"  Rate: {config['rate']}, Pitch: {config['pitch']}")
        print(f"  Languages: {', '.join(status['online_tts']['languages'])}")
    else:
        print("  ✗ Not available")
    
    print(f"\n💾 Offline TTS:")
    if status['offline_tts']['available']:
        print(f"  ✓ {status['offline_tts']['engine']}")
        config = status['offline_tts']['voice_config']
        print(f"  Rate: {config['rate']}")
        print(f"  Languages: {', '.join(status['offline_tts']['languages'])}")
        engines = status['offline_tts']['engines']
        print(f"  Engines: pyttsx3={'✓' if engines['pyttsx3'] else '✗'}, Coqui={'✓' if engines['coqui'] else '✗'}")
    else:
        print("  ✗ Not available")
    
    print(f"\n🎯 Recommended: {status['recommended_engine']}")
    print("="*70 + "\n")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Quick test
    print_status()
    
    print("\nTesting TTS:")
    audio_path, engine = speak("Hello, I am Jarvis. All systems are operational.", lang='en')
    print(f"Generated: {audio_path}")
    print(f"Engine: {engine}")
