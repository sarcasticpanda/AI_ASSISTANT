"""
TTS Offline - Offline Text-to-Speech
Uses Piper TTS (neural male voice) or pyttsx3 for offline speech synthesis.
Configured to match Jarvis voice characteristics (calm, slightly energetic male).
"""

import os
import logging
import tempfile
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Try importing Piper TTS (recommended offline TTS)
try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PiperVoice = None
    logger.warning("Piper TTS not installed. Install with: pip install piper-tts")
    PIPER_AVAILABLE = False

# Try importing Coqui TTS
try:
    from TTS.api import TTS as CoquiTTS
    COQUI_AVAILABLE = True
except ImportError:
    CoquiTTS = None  # Define as None if not available
    logger.warning("Coqui TTS not installed. Install with: pip install TTS")
    COQUI_AVAILABLE = False

# Try importing pyttsx3 (lightweight fallback)
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    pyttsx3 = None  # Define as None if not available
    logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")
    PYTTSX3_AVAILABLE = False


# JARVIS OFFLINE VOICE CONFIG
# Tuned to approximate online Arjun voice (+11% speed, calm + energetic)
JARVIS_OFFLINE_CONFIG = {
    'engine': 'pyttsx3',  # Use pyttsx3 (works reliably on Windows)
    'piper_voice': 'en_US-danny-low',  # Backup if Piper works
    'pyttsx3_rate': 200,  # Faster = more energetic
    'pyttsx3_volume': 0.95,  # Clear volume
    'voice_preference': 'male'
}
  

# Global TTS engine instances (lazy loaded)
_piper_voice: Optional[Any] = None
_coqui_tts: Optional[Any] = None
_pyttsx3_engine: Optional[Any] = None


def _load_piper_voice():
    """Load Piper TTS voice (male, natural)"""
    global _piper_voice
    
    if _piper_voice is not None:
        return _piper_voice
    
    if not PIPER_AVAILABLE:
        raise ImportError("Piper TTS not available")
    
    voice_name = JARVIS_OFFLINE_CONFIG['piper_voice']
    logger.info(f"Loading Piper voice: {voice_name}")
    
    try:
        # Piper voice loading (no extra arguments needed)
        import piper
        _piper_voice = piper.PiperVoice.load(voice_name)
        logger.info(f"✓ Piper voice loaded: {voice_name}")
        return _piper_voice
    
    except Exception as e:
        logger.error(f"Failed to load Piper voice: {e}")
        logger.info("Note: Voice models are auto-downloaded on first use")
        raise


def _load_coqui_model(model_name: Optional[str] = None):
    """
    Load Coqui TTS model.
    
    Args:
        model_name: Model to use (e.g., "tts_models/en/ljspeech/vits")
                   If None, reads from environment USE_COQUI_MODEL_NAME
    """
    global _coqui_tts
    
    if _coqui_tts is not None:
        return _coqui_tts
    
    if not COQUI_AVAILABLE:
        raise ImportError("Coqui TTS not available")
    
    if model_name is None:
        model_name = os.getenv("USE_COQUI_MODEL_NAME", "tts_models/en/ljspeech/vits")
    
    logger.info(f"Loading Coqui TTS model: {model_name}")
    
    try:
        _coqui_tts = CoquiTTS(model_name=model_name)
        logger.info(f"✓ Coqui TTS model loaded")
        return _coqui_tts
    
    except Exception as e:
        logger.error(f"Failed to load Coqui TTS: {e}")
        raise


def _load_pyttsx3_engine():
    """Load pyttsx3 engine with Jarvis voice configuration"""
    global _pyttsx3_engine
    
    if _pyttsx3_engine is not None:
        return _pyttsx3_engine
    
    if not PYTTSX3_AVAILABLE:
        raise ImportError("pyttsx3 not available")
    
    logger.info("Initializing pyttsx3 engine with Jarvis voice settings")
    
    try:
        _pyttsx3_engine = pyttsx3.init()
        
        # Get available voices
        voices = _pyttsx3_engine.getProperty('voices')
        
        # Try to select male voice
        selected_voice = None
        if voices:
            # Strategy 1: Check for gender attribute (most reliable)
            for voice in voices:
                if hasattr(voice, 'gender') and voice.gender:
                    if 'male' in str(voice.gender).lower() and 'female' not in str(voice.gender).lower():
                        selected_voice = voice.id
                        logger.info(f"Selected male voice by gender: {voice.name}")
                        break
            
            # Strategy 2: Check name for male indicators
            if selected_voice is None:
                for voice in voices:
                    voice_name = voice.name.lower()
                    # Check for male voice names (exclude Zira which is female)
                    if any(name in voice_name for name in ['david', 'mark', 'ryan', 'james', 'george']) and 'zira' not in voice_name:
                        selected_voice = voice.id
                        logger.info(f"Selected male voice by name: {voice.name}")
                        break
            
            # Strategy 3: Check ID for male marker
            if selected_voice is None:
                for voice in voices:
                    voice_id = voice.id.lower()
                    if 'male' in voice_id and 'female' not in voice_id:
                        selected_voice = voice.id
                        logger.info(f"Selected male voice by ID: {voice.name}")
                        break
            
            # Fallback: Use first voice (usually David on Windows)
            if selected_voice is None:
                selected_voice = voices[0].id
                logger.info(f"Using default voice (Voice 0): {voices[0].name}")
            
            _pyttsx3_engine.setProperty('voice', selected_voice)
        
        # Configure voice settings to match Arjun characteristics
        # Rate: +11% faster than default (150 -> 175 WPM for better match)
        _pyttsx3_engine.setProperty('rate', JARVIS_OFFLINE_CONFIG['pyttsx3_rate'])
        
        # Volume: Full volume for clarity
        _pyttsx3_engine.setProperty('volume', JARVIS_OFFLINE_CONFIG['pyttsx3_volume'])
        
        logger.info(f"✓ pyttsx3 engine initialized (rate={JARVIS_OFFLINE_CONFIG['pyttsx3_rate']} WPM, tuned to match Arjun)")
        return _pyttsx3_engine
    
    except Exception as e:
        logger.error(f"Failed to initialize pyttsx3: {e}")
        raise


# ============================================================================
# TTS FUNCTIONS
# ============================================================================

def speak_offline(text: str, lang: str = "en", use_coqui: bool = False) -> str:
    """
    Convert text to speech using offline TTS.
    Priority: Piper TTS (male, natural) -> pyttsx3 (male, robotic) -> Coqui (female)
    
    Args:
        text: Text to speak
        lang: Language code (currently only English supported well)
        use_coqui: Force Coqui TTS (not recommended, female voice)
    
    Returns:
        str: Path to generated audio file
    
    Example:
        audio_path = speak_offline("Hello, I am Jarvis")
        # Returns: "/tmp/jarvis_offline_tts_123.wav"
    """
    logger.info(f"Generating offline speech for: '{text[:50]}...'")
    
    # Priority 1: Piper TTS (best quality, male voice)
    if PIPER_AVAILABLE and not use_coqui:
        try:
            return _speak_with_piper(text)
        except Exception as e:
            logger.warning(f"Piper TTS failed: {e}")
    
    # Priority 2: pyttsx3 (male but robotic)
    if PYTTSX3_AVAILABLE:
        try:
            return _speak_with_pyttsx3(text)
        except Exception as e:
            logger.warning(f"pyttsx3 failed: {e}")
    
    # Priority 3: Coqui TTS (female voice, last resort)
    if use_coqui and COQUI_AVAILABLE:
        logger.warning("Using Coqui TTS (female voice)")
        return _speak_with_coqui(text)
    
    logger.error("No offline TTS available")
    return ""


def _speak_with_piper(text: str) -> str:
    """Generate speech using Piper TTS (neural male voice)"""
    try:
        voice = _load_piper_voice()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
            prefix="jarvis_piper_"
        )
        
        audio_path = temp_file.name
        temp_file.close()
        
        # Generate speech
        with open(audio_path, 'wb') as f:
            voice.synthesize(text, f)
        
        logger.info(f"✓ Piper TTS audio saved to: {audio_path}")
        
        return audio_path
    
    except Exception as e:
        logger.error(f"Piper TTS failed: {e}")
        raise


def _speak_with_coqui(text: str) -> str:
    """Generate speech using Coqui TTS"""
    try:
        tts = _load_coqui_model()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
            prefix="jarvis_coqui_"
        )
        
        audio_path = temp_file.name
        temp_file.close()
        
        # Generate speech
        tts.tts_to_file(text=text, file_path=audio_path)
        
        logger.info(f"✓ Coqui TTS audio saved to: {audio_path}")
        
        return audio_path
    
    except Exception as e:
        logger.error(f"Coqui TTS failed: {e}")
        raise


def _speak_with_pyttsx3(text: str) -> str:
    """Generate speech using pyttsx3"""
    try:
        engine = _load_pyttsx3_engine()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
            prefix="jarvis_pyttsx3_"
        )
        
        audio_path = temp_file.name
        temp_file.close()
        
        # Generate speech
        engine.save_to_file(text, audio_path)
        engine.runAndWait()
        
        logger.info(f"✓ pyttsx3 audio saved to: {audio_path}")
        
        return audio_path
    
    except Exception as e:
        logger.error(f"pyttsx3 failed: {e}")
        raise


def speak_local_simple(text: str):
    """
    Simple blocking TTS - speaks immediately without returning file.
    Uses pyttsx3 for simplicity.
    
    Args:
        text: Text to speak
    
    Example:
        speak_local_simple("Hello")  # Speaks and returns when done
    """
    if not PYTTSX3_AVAILABLE:
        logger.error("pyttsx3 not available")
        return
    
    try:
        engine = _load_pyttsx3_engine()
        
        logger.info(f"Speaking: '{text[:50]}...'")
        
        engine.say(text)
        engine.runAndWait()
        
        logger.info("✓ Speech complete")
    
    except Exception as e:
        logger.error(f"Simple TTS failed: {e}")


# ============================================================================
# UTILITIES
# ============================================================================

def is_available() -> bool:
    """Check if any offline TTS is available"""
    return PIPER_AVAILABLE or PYTTSX3_AVAILABLE or COQUI_AVAILABLE


def get_status() -> dict:
    """Get status of offline TTS engines"""
    return {
        "piper": PIPER_AVAILABLE,
        "pyttsx3": PYTTSX3_AVAILABLE,
        "coqui": COQUI_AVAILABLE,
        "piper_loaded": _piper_voice is not None,
        "pyttsx3_loaded": _pyttsx3_engine is not None,
        "coqui_loaded": _coqui_tts is not None
    }


def get_current_engine() -> str:
    """Get current offline TTS engine name"""
    if PIPER_AVAILABLE:
        return f"Piper TTS (Neural) - {JARVIS_OFFLINE_CONFIG['piper_voice']} (Male)"
    elif PYTTSX3_AVAILABLE:
        return "pyttsx3 (System TTS) - Male Voice"
    elif COQUI_AVAILABLE:
        return "Coqui TTS (Neural) - Female (fallback)"
    else:
        return "No offline TTS available"


def get_voice_info() -> dict:
    """Get offline voice configuration"""
    if PIPER_AVAILABLE:
        return {
            'engine': 'Piper TTS',
            'voice': JARVIS_OFFLINE_CONFIG['piper_voice'],
            'gender': 'Male',
            'quality': 'Neural (Natural)',
            'description': 'Offline neural male voice, tuned to approximate Arjun characteristics'
        }
    else:
        return {
            'engine': 'pyttsx3 (Microsoft David)',
            'rate': f"{JARVIS_OFFLINE_CONFIG['pyttsx3_rate']} WPM",
            'volume': JARVIS_OFFLINE_CONFIG['pyttsx3_volume'],
            'voice_preference': JARVIS_OFFLINE_CONFIG['voice_preference'],
            'description': f'Offline male voice at {JARVIS_OFFLINE_CONFIG["pyttsx3_rate"]} WPM (tuned to match Arjun +11% speed)',
            'note': 'Offline TTS is more robotic than online Arjun voice due to system limitations'
        }


def get_supported_languages() -> list:
    """Get supported languages for offline TTS"""
    # Piper and pyttsx3 primarily support English well
    # Coqui has multi-language models but we use English model
    return ['en']


def list_coqui_models() -> list:
    """
    List available Coqui TTS models.
    
    Returns:
        list: Model names
    """
    if not COQUI_AVAILABLE:
        return []
    
    try:
        return CoquiTTS().list_models()
    except:
        return []
