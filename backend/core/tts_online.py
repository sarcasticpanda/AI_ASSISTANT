"""
TTS Online - Online Text-to-Speech
Uses Edge TTS (Microsoft) for natural, high-quality speech synthesis.
Configured with Arjun voice at +11% speed, +7Hz pitch for perfect Jarvis tone.
"""

import os
import logging
import tempfile
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

# Try importing Edge TTS (primary)
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    logger.warning("edge-tts not installed. Install with: pip install edge-tts")
    EDGE_TTS_AVAILABLE = False

# Try importing gTTS (fallback)
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    logger.warning("gTTS not installed. Install with: pip install gtts")
    GTTS_AVAILABLE = False

# Try importing pygame for audio playback
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    logger.warning("pygame not installed. Install with: pip install pygame")
    PYGAME_AVAILABLE = False

# ============================================================================
# JARVIS VOICE CONFIGURATION (Your Selected Settings!)
# ============================================================================

JARVIS_VOICE_CONFIG = {
    'voice': 'hi-IN-ArjunNeural',  # Male, Indian - Your 5/5 rated voice!
    'rate': '+11%',                 # Slightly slower for clarity
    'pitch': '+7Hz',                # Slightly energetic + calm
    'volume': '+0%'                 # Default volume
}

# Language detection for auto voice selection
VOICE_MAP = {
    'en': 'hi-IN-ArjunNeural',      # Use Arjun for English (works great!)
    'hi': 'hi-IN-ArjunNeural',      # Use Arjun for Hindi
    'mixed': 'hi-IN-ArjunNeural'    # Use Arjun for mixed Hinglish
}


def speak_online(text: str, lang: str = "en", slow: bool = False) -> str:
    """
    Convert text to speech using Edge TTS with Jarvis voice configuration.
    Falls back to gTTS if Edge TTS unavailable.
    
    Args:
        text: Text to speak
        lang: Language code (en, hi, mixed)
        slow: Speak slowly (overrides rate setting)
    
    Returns:
        str: Path to generated audio file
    
    Example:
        audio_path = speak_online("Hello, how are you?")
        # Returns: "/tmp/jarvis_tts_123.mp3"
    """
    # Try Edge TTS first (best quality)
    if EDGE_TTS_AVAILABLE:
        return _speak_edge_tts(text, lang, slow)
    
    # Fallback to gTTS
    elif GTTS_AVAILABLE:
        logger.warning("Using gTTS fallback (Edge TTS not available)")
        return _speak_gtts(text, lang, slow)
    
    else:
        logger.error("No TTS engine available!")
        return ""


def _speak_edge_tts(text: str, lang: str = "en", slow: bool = False) -> str:
    """
    Use Edge TTS with Jarvis voice configuration.
    
    Args:
        text: Text to speak
        lang: Language code
        slow: Speak slowly
    
    Returns:
        str: Path to audio file
    """
    logger.info(f"Generating speech (Edge TTS): '{text[:50]}...'")
    
    try:
        # Select voice based on language
        voice = VOICE_MAP.get(lang, JARVIS_VOICE_CONFIG['voice'])
        
        # Adjust rate if slow requested
        rate = '+5%' if slow else JARVIS_VOICE_CONFIG['rate']
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3",
            prefix="jarvis_tts_"
        )
        audio_path = temp_file.name
        temp_file.close()
        
        # Generate speech asynchronously
        async def generate():
            communicate = edge_tts.Communicate(
                text,
                voice,
                rate=rate,
                pitch=JARVIS_VOICE_CONFIG['pitch'],
                volume=JARVIS_VOICE_CONFIG['volume']
            )
            await communicate.save(audio_path)
        
        # Run async function
        asyncio.run(generate())
        
        logger.info(f"✓ Audio saved to: {audio_path}")
        return audio_path
    
    except Exception as e:
        logger.error(f"Edge TTS failed: {e}")
        
        # Try gTTS fallback
        if GTTS_AVAILABLE:
            logger.info("Falling back to gTTS...")
            return _speak_gtts(text, lang, slow)
        
        return ""


def _speak_gtts(text: str, lang: str = "en", slow: bool = False) -> str:
    """
    Fallback to gTTS (Google Text-to-Speech).
    
    Args:
        text: Text to speak
        lang: Language code
        slow: Speak slowly
    
    Returns:
        str: Path to audio file
    """
    logger.info(f"Generating speech (gTTS): '{text[:50]}...'")
    
    try:
        # Map language codes
        gtts_lang = 'hi' if lang == 'hi' else 'en'
        
        # Create gTTS object
        tts = gTTS(text=text, lang=gtts_lang, slow=slow)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3",
            prefix="jarvis_tts_"
        )
        
        audio_path = temp_file.name
        temp_file.close()
        
        # Generate audio
        tts.save(audio_path)
        
        logger.info(f"✓ Audio saved to: {audio_path}")
        return audio_path
    
    except Exception as e:
        logger.error(f"gTTS failed: {e}")
        return ""



def play_audio(audio_path: str):
    """
    Play audio file using pygame.
    
    Args:
        audio_path: Path to audio file (MP3, WAV, etc.)
    """
    if not PYGAME_AVAILABLE:
        logger.warning("pygame not available - cannot play audio")
        return
    
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return
    
    try:
        logger.info(f"Playing audio: {audio_path}")
        
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        
        # Wait until finished
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        logger.info("✓ Playback finished")
    
    except Exception as e:
        logger.error(f"Audio playback failed: {e}")


def cleanup_temp_audio(audio_path: str):
    """
    Delete temporary audio file.
    
    Args:
        audio_path: Path to audio file to delete
    """
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            logger.info(f"✓ Cleaned up: {audio_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup audio file: {e}")


# ============================================================================
# UTILITIES
# ============================================================================

def is_online() -> bool:
    """
    Check if we can reach Google's servers.
    
    Returns:
        bool: True if online, False otherwise
    """
    try:
        import requests
        response = requests.get("https://www.google.com", timeout=3)
        return response.status_code == 200
    except:
        return False


def is_available() -> bool:
    """Check if any TTS engine is available"""
    return EDGE_TTS_AVAILABLE or GTTS_AVAILABLE


def get_current_engine() -> str:
    """Get name of current TTS engine"""
    if EDGE_TTS_AVAILABLE:
        return "Edge TTS (Microsoft) - Arjun Voice"
    elif GTTS_AVAILABLE:
        return "gTTS (Google) - Fallback"
    else:
        return "None"


def get_voice_info() -> dict:
    """Get information about current voice configuration"""
    return {
        "engine": get_current_engine(),
        "voice": JARVIS_VOICE_CONFIG['voice'],
        "rate": JARVIS_VOICE_CONFIG['rate'],
        "pitch": JARVIS_VOICE_CONFIG['pitch'],
        "description": "Male, Indian, Slightly Energetic + Calm",
        "rating": "5/5",
        "supports_languages": ["en", "hi", "mixed"]
    }


def get_supported_languages() -> list:
    """
    Get list of supported language codes.
    
    Returns:
        list: Language codes (e.g., ['en', 'hi', 'mixed'])
    """
    return ['en', 'hi', 'mixed']

