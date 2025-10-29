"""
STT Local - Offline Speech-to-Text
Uses faster-whisper or Vosk for offline transcription.
"""

import os
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Try importing faster-whisper (preferred for offline STT)
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    WhisperModel = None  # Define as None if not available
    logger.warning("faster-whisper not installed. Install with: pip install faster-whisper")
    FASTER_WHISPER_AVAILABLE = False

# Try importing Vosk (lightweight alternative)
try:
    import vosk
    import json
    import wave
    VOSK_AVAILABLE = True
except ImportError:
    vosk = None  # Define as None if not available
    logger.warning("Vosk not installed. Install with: pip install vosk")
    VOSK_AVAILABLE = False


# Global model instance (lazy loaded)
_whisper_model: Optional[Any] = None
_vosk_model: Optional[Any] = None


def _load_whisper_model(model_size: str = "medium"):
    """
    Load faster-whisper model.
    
    Args:
        model_size: Model size - "tiny", "base", "small", "medium", "large"
                   Default: "medium" (best balance of accuracy vs speed)
                   - tiny: ~40MB, fast, 80% accurate
                   - base: ~140MB, faster, 90% accurate
                   - small: ~460MB, good, 94% accurate
                   - medium: ~1.5GB, excellent, 96-98% accurate ✅ RECOMMENDED
                   - large-v3: ~3GB, best, 99% accurate (overkill for voice)
    
    Models will be auto-downloaded to ~/.cache/huggingface/ on first use.
    """
    global _whisper_model
    
    if _whisper_model is not None:
        return _whisper_model
    
    if not FASTER_WHISPER_AVAILABLE:
        raise ImportError("faster-whisper not available")
    
    logger.info(f"Loading faster-whisper model: {model_size}")
    logger.info(f"⏳ First-time download: ~1.5GB (one-time only)...")
    
    try:
        # Use CPU with optimized settings
        # For GPU: device="cuda", compute_type="float16"
        _whisper_model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",  # Optimized for CPU (faster)
            num_workers=4,        # Parallel processing
            download_root=None    # Use default cache (~/.cache/huggingface)
        )
        
        logger.info(f"✓ Whisper model loaded: {model_size}")
        return _whisper_model
    
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise


def _load_vosk_model(model_path: str = None):
    """
    Load Vosk model.
    
    Args:
        model_path: Path to Vosk model directory
                   Download from: https://alphacephei.com/vosk/models
    
    Example:
        Download "vosk-model-small-en-us-0.15" and extract to models/vosk/
    """
    global _vosk_model
    
    if _vosk_model is not None:
        return _vosk_model
    
    if not VOSK_AVAILABLE:
        raise ImportError("Vosk not available")
    
    if model_path is None:
        # Default model path
        model_path = os.path.join("models", "vosk", "vosk-model-small-en-us-0.15")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Vosk model not found at {model_path}. "
            "Download from https://alphacephei.com/vosk/models"
        )
    
    logger.info(f"Loading Vosk model from: {model_path}")
    
    try:
        _vosk_model = vosk.Model(model_path)
        logger.info("✓ Vosk model loaded")
        return _vosk_model
    
    except Exception as e:
        logger.error(f"Failed to load Vosk model: {e}")
        raise


# ============================================================================
# TRANSCRIPTION FUNCTIONS
# ============================================================================

def transcribe_file(audio_path: str, method: str = "whisper") -> str:
    """
    Transcribe audio file to text using local models.
    
    Args:
        audio_path: Path to audio file (WAV, MP3, etc.)
        method: "whisper" or "vosk"
    
    Returns:
        str: Transcribed text
    
    Example:
        text = transcribe_file("recording.wav")
        # Returns: "hello how are you"
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    logger.info(f"Transcribing {audio_path} using {method}")
    
    if method == "whisper":
        return _transcribe_with_whisper(audio_path)
    elif method == "vosk":
        return _transcribe_with_vosk(audio_path)
    else:
        raise ValueError(f"Unknown STT method: {method}")


def _transcribe_with_whisper(audio_path: str) -> str:
    """Transcribe using faster-whisper with optimized settings"""
    try:
        model = _load_whisper_model(model_size="medium")
        
        # Transcribe with optimizations
        segments, info = model.transcribe(
            audio_path,
            language="en",      # Force English, or None for auto-detect
            beam_size=5,        # Balanced accuracy vs speed
            vad_filter=True,    # Voice Activity Detection - skip silence
            vad_parameters=dict(
                threshold=0.5,      # Sensitivity (0.0-1.0)
                min_speech_duration_ms=250,  # Ignore speech < 250ms
                min_silence_duration_ms=500  # Split on silence > 500ms
            ),
            temperature=0.0,    # Deterministic (no randomness)
            compression_ratio_threshold=2.4,  # Reject poor quality
            log_prob_threshold=-1.0,
            no_speech_threshold=0.6,
            condition_on_previous_text=True  # Use context for better accuracy
        )
        
        # Combine all segments
        text = " ".join([segment.text for segment in segments])
        
        logger.info(f"Transcribed ({info.language}): '{text[:50]}...'")
        logger.info(f"Duration: {info.duration:.2f}s, Detected language prob: {info.language_probability:.2f}")
        
        return text.strip()
    
    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        return f"[Transcription error: {e}]"


def _transcribe_with_vosk(audio_path: str) -> str:
    """Transcribe using Vosk"""
    try:
        model = _load_vosk_model()
        
        # Open WAV file
        wf = wave.open(audio_path, "rb")
        
        # Check format
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise ValueError("Audio must be WAV format mono PCM")
        
        # Create recognizer
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        # Transcribe
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if "text" in result:
                    results.append(result["text"])
        
        # Final result
        final_result = json.loads(rec.FinalResult())
        if "text" in final_result:
            results.append(final_result["text"])
        
        text = " ".join(results)
        
        logger.info(f"Transcribed: '{text[:50]}...'")
        
        return text.strip()
    
    except Exception as e:
        logger.error(f"Vosk transcription failed: {e}")
        return f"[Transcription error: {e}]"


# ============================================================================
# UTILITIES
# ============================================================================

def is_available() -> bool:
    """Check if local STT is available"""
    return FASTER_WHISPER_AVAILABLE or VOSK_AVAILABLE


def get_status() -> dict:
    """Get status of local STT engines"""
    return {
        "faster_whisper": FASTER_WHISPER_AVAILABLE,
        "vosk": VOSK_AVAILABLE,
        "whisper_loaded": _whisper_model is not None,
        "vosk_loaded": _vosk_model is not None
    }
