"""
Wake Word Detection - Picovoice Porcupine Integration
Listens for wake word ("Jarvis") to activate the assistant.
"""

import os
import logging
import threading
from typing import Optional, Callable

logger = logging.getLogger(__name__)

# Try importing Porcupine
try:
    import pvporcupine
    import pyaudio
    import struct
    PORCUPINE_AVAILABLE = True
except ImportError:
    logger.warning("Porcupine/PyAudio not installed. Install with: pip install pvporcupine pyaudio")
    PORCUPINE_AVAILABLE = False


# Global state
_listener_thread: Optional[threading.Thread] = None
_listening = False
_porcupine: Optional[pvporcupine.Porcupine] = None


def _get_access_key() -> str:
    """
    Get Picovoice access key from environment.
    
    To get your key:
    1. Sign up at https://console.picovoice.ai/
    2. Get your AccessKey
    3. Add to .env file
    """
    access_key = os.getenv("PORCUPINE_ACCESS_KEY")
    
    if not access_key or access_key == "your-porcupine-access-key":
        raise ValueError(
            "PORCUPINE_ACCESS_KEY not set in .env file. "
            "Get your key from https://console.picovoice.ai/"
        )
    
    return access_key


def _wake_word_listener(callback: Callable, sensitivity: float = 0.5):
    """
    Background thread that listens for wake word.
    
    Args:
        callback: Function to call when wake word detected
        sensitivity: Detection sensitivity (0.0 to 1.0)
                    Higher = more sensitive but more false positives
    """
    global _listening, _porcupine
    
    if not PORCUPINE_AVAILABLE:
        logger.error("Porcupine not available")
        return
    
    try:
        access_key = _get_access_key()
    except ValueError as e:
        logger.error(str(e))
        return
    
    # Keywords to detect (you can use built-in or custom .ppn files)
    keywords = ["jarvis"]  # Built-in keyword
    
    # Alternatively, use custom .ppn file:
    # keyword_paths = ["/path/to/jarvis.ppn"]
    
    try:
        logger.info(f"Initializing Porcupine with keywords: {keywords}")
        
        # Create Porcupine instance
        _porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=keywords,
            sensitivities=[sensitivity]
        )
        
        # Initialize PyAudio
        pa = pyaudio.PyAudio()
        
        # Open audio stream
        audio_stream = pa.open(
            rate=_porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=_porcupine.frame_length
        )
        
        logger.info("✓ Wake word detection started - say 'Jarvis' to activate")
        
        _listening = True
        
        # Listen loop
        while _listening:
            # Read audio
            pcm = audio_stream.read(_porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * _porcupine.frame_length, pcm)
            
            # Process audio
            keyword_index = _porcupine.process(pcm)
            
            # Wake word detected!
            if keyword_index >= 0:
                logger.info(f"🎤 Wake word detected: {keywords[keyword_index]}")
                
                # Call callback function
                if callback:
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
        
        # Cleanup
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        
        if _porcupine:
            _porcupine.delete()
        
        logger.info("Wake word detection stopped")
    
    except Exception as e:
        logger.error(f"Wake word listener error: {e}")
        _listening = False


# ============================================================================
# PUBLIC API
# ============================================================================

def start_listener(callback: Callable, sensitivity: float = 0.5):
    """
    Start wake word detection in background thread.
    
    Args:
        callback: Function to call when "Jarvis" is detected
        sensitivity: Detection sensitivity (0.0 to 1.0)
    
    Example:
        def on_wake_word():
            print("Jarvis activated!")
            # Trigger STT, process command, etc.
        
        start_listener(on_wake_word)
    """
    global _listener_thread, _listening
    
    if not PORCUPINE_AVAILABLE:
        logger.error("Porcupine not available - wake word detection disabled")
        return False
    
    if _listening:
        logger.warning("Wake word listener already running")
        return False
    
    logger.info("Starting wake word listener...")
    
    # Start listener in background thread
    _listener_thread = threading.Thread(
        target=_wake_word_listener,
        args=(callback, sensitivity),
        daemon=True
    )
    _listener_thread.start()
    
    return True


def stop_listener():
    """Stop wake word detection"""
    global _listening
    
    if not _listening:
        logger.warning("Wake word listener not running")
        return
    
    logger.info("Stopping wake word listener...")
    
    _listening = False
    
    # Wait for thread to finish
    if _listener_thread:
        _listener_thread.join(timeout=2)


def is_listening() -> bool:
    """Check if wake word detection is active"""
    return _listening


# ============================================================================
# UTILITIES
# ============================================================================

def is_available() -> bool:
    """Check if Porcupine is available"""
    return PORCUPINE_AVAILABLE


def test_microphone():
    """
    Test microphone input.
    Records 3 seconds of audio and reports if it's working.
    """
    if not PORCUPINE_AVAILABLE:
        logger.error("PyAudio not available")
        return
    
    try:
        import pyaudio
        import wave
        import tempfile
        
        logger.info("Testing microphone (recording 3 seconds)...")
        
        pa = pyaudio.PyAudio()
        
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        
        frames = []
        
        for i in range(0, int(16000 / 1024 * 3)):  # 3 seconds
            data = stream.read(1024)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        pa.terminate()
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        logger.info(f"✓ Microphone working - recorded to {temp_file.name}")
        
        return temp_file.name
    
    except Exception as e:
        logger.error(f"Microphone test failed: {e}")
        return None
