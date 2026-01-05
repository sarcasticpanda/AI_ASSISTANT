"""
STT Online - Online Speech-to-Text
Uses Groq Whisper API or OpenAI Whisper API for cloud-based transcription.
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


def _get_groq_api_key() -> str:
    """Get Groq API key from environment"""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key or api_key == "gsk_REPLACE_ME":
        raise ValueError(
            "GROQ_API_KEY not set in .env file. "
            "Get your key from https://console.groq.com/keys"
        )
    
    return api_key


def transcribe_online(audio_file_path: str, language: str = None) -> dict:
    """
    Transcribe audio file using Groq Whisper API with automatic language detection.
    
    Args:
        audio_file_path: Path to audio file
        language: Language code (None = auto-detect, "en" = English, "hi" = Hindi)
    
    Returns:
        dict: {"text": str, "language": str}
        Example: {"text": "नमस्ते", "language": "hi"}
    
    Example:
        result = transcribe_online("recording.mp3")
        # Returns: {"text": "नमस्ते, आप कैसे हैं?", "language": "hi"}
    
    curl equivalent:
        curl -X POST https://api.groq.com/openai/v1/audio/transcriptions \
          -H "Authorization: Bearer YOUR_GROQ_KEY" \
          -F "file=@recording.mp3" \
          -F "model=whisper-large-v3" \
          (no language param = auto-detect)
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    logger.info(f"Transcribing {audio_file_path} using Groq Whisper API")
    
    try:
        api_key = _get_groq_api_key()
    except ValueError as e:
        logger.error(str(e))
        return f"[API key error: {e}]"
    
    # Groq Whisper API endpoint
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Prepare file upload
    with open(audio_file_path, "rb") as audio_file:
        files = {
            "file": (os.path.basename(audio_file_path), audio_file, "audio/mpeg")
        }
        
        # Build data dict - only include language if specified
        data = {
            "model": "whisper-large-v3",  # Groq's Whisper model
            "response_format": "verbose_json"  # Get language info too
        }
        
        # Only add language if specified (None = auto-detect)
        if language:
            data["language"] = language
            logger.info(f"Using specified language: {language}")
        else:
            logger.info("Auto-detecting language...")
        
        try:
            logger.info("Sending request to Groq API...")
            
            response = requests.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=60  # Whisper can take time for long audio
            )
            
            response.raise_for_status()
            
            result = response.json()
            text = result.get("text", "")
            detected_language = result.get("language", "unknown")
            
            logger.info(f"Detected language: {detected_language}")
            logger.info(f"Transcribed: '{text[:50]}...'")
            
            return {
                "text": text.strip(),
                "language": detected_language
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {e}")
            
            # Try to get error message from response
            try:
                error_detail = response.json()
                logger.error(f"API error details: {error_detail}")
            except:
                pass
            
            return {
                "text": f"[Transcription failed: {e}]",
                "language": "unknown"
            }


def transcribe_with_openai(audio_file_path: str, language: str = "en") -> str:
    """
    Alternative: Transcribe using OpenAI Whisper API.
    
    Requires OPENAI_API_KEY in environment.
    
    Args:
        audio_file_path: Path to audio file
        language: Language code
    
    Returns:
        str: Transcribed text
    
    curl equivalent:
        curl -X POST https://api.openai.com/v1/audio/transcriptions \
          -H "Authorization: Bearer YOUR_OPENAI_KEY" \
          -F "file=@recording.mp3" \
          -F "model=whisper-1"
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in .env file")
    
    url = "https://api.openai.com/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    with open(audio_file_path, "rb") as audio_file:
        files = {
            "file": audio_file
        }
        
        data = {
            "model": "whisper-1",
            "language": language
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )
            
            response.raise_for_status()
            
            result = response.json()
            text = result.get("text", "")
            
            logger.info(f"Transcribed: '{text[:50]}...'")
            
            return text.strip()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API request failed: {e}")
            return f"[Transcription failed: {e}]"


# ============================================================================
# UTILITIES
# ============================================================================

def is_online() -> bool:
    """
    Check if we can reach Groq API.
    
    Returns:
        bool: True if online, False otherwise
    """
    try:
        response = requests.get("https://api.groq.com", timeout=3)
        return response.status_code in [200, 404]  # 404 is OK (root endpoint doesn't exist)
    except:
        return False


def test_connection() -> str:
    """
    Test Groq API connection.
    
    Returns:
        str: Status message
    """
    try:
        api_key = _get_groq_api_key()
        
        if is_online():
            return "✓ Groq API is reachable and API key is set"
        else:
            return "✗ Cannot reach Groq API (check internet connection)"
    
    except ValueError as e:
        return f"✗ {e}"
