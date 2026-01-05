"""
TTS Streaming - Sentence-by-Sentence Audio Streaming
Splits text into sentences and generates/plays them in parallel for faster perceived response.
"""

import os
import re
import logging
import tempfile
import asyncio
import threading
import time
from typing import List, Tuple, Optional
from queue import Queue

logger = logging.getLogger(__name__)

# Import Edge TTS
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    logger.warning("edge-tts not installed. Install with: pip install edge-tts")
    EDGE_TTS_AVAILABLE = False

# Import pygame for playback
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    logger.warning("pygame not installed. Install with: pip install pygame")
    PYGAME_AVAILABLE = False


# ============================================================================
# JARVIS VOICE CONFIGURATION
# ============================================================================

JARVIS_VOICE_CONFIG = {
    'voice': 'hi-IN-ArjunNeural',
    'rate': '+11%',
    'pitch': '+7Hz',
    'volume': '+0%'
}

VOICE_MAP = {
    'en': 'hi-IN-ArjunNeural',
    'hi': 'hi-IN-ArjunNeural',
    'mixed': 'hi-IN-ArjunNeural'
}


# ============================================================================
# SENTENCE SPLITTING
# ============================================================================

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences for streaming playback.
    Handles Hindi (Devanagari), English, and Hinglish.
    
    Args:
        text: Text to split
    
    Returns:
        List of sentences
    
    Example:
        >>> split_into_sentences("Hello. How are you? I'm fine!")
        ['Hello.', 'How are you?', "I'm fine!"]
    """
    # Replace common abbreviations to avoid false splits
    text = text.replace('Mr.', 'Mr').replace('Mrs.', 'Mrs').replace('Dr.', 'Dr')
    text = text.replace('etc.', 'etc').replace('e.g.', 'eg').replace('i.e.', 'ie')
    
    # Split on sentence boundaries (., !, ?, । for Hindi)
    # Keep the punctuation with the sentence
    sentences = re.split(r'([.!?।]+)', text)
    
    # Recombine sentences with their punctuation
    result = []
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i].strip()
        punct = sentences[i+1] if i+1 < len(sentences) else ''
        if sentence:
            result.append(sentence + punct)
    
    # Add last sentence if no punctuation
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        result.append(sentences[-1].strip())
    
    # Filter out very short sentences (< 3 chars)
    result = [s for s in result if len(s.strip()) > 2]
    
    # If no sentences found, return original text
    if not result:
        return [text]
    
    return result


# ============================================================================
# ASYNC AUDIO GENERATION
# ============================================================================

async def generate_audio_async(text: str, lang: str = "en") -> str:
    """
    Generate audio file asynchronously using Edge TTS.
    
    Args:
        text: Text to convert
        lang: Language code
    
    Returns:
        Path to generated audio file
    """
    try:
        # Select voice
        voice = VOICE_MAP.get(lang, JARVIS_VOICE_CONFIG['voice'])
        
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3",
            prefix="jarvis_stream_"
        )
        audio_path = temp_file.name
        temp_file.close()
        
        # Generate audio
        communicate = edge_tts.Communicate(
            text,
            voice,
            rate=JARVIS_VOICE_CONFIG['rate'],
            pitch=JARVIS_VOICE_CONFIG['pitch'],
            volume=JARVIS_VOICE_CONFIG['volume']
        )
        await communicate.save(audio_path)
        
        return audio_path
    
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        return ""


def generate_audio_sync(text: str, lang: str = "en") -> str:
    """
    Synchronous wrapper for async audio generation.
    
    Args:
        text: Text to convert
        lang: Language code
    
    Returns:
        Path to audio file
    """
    return asyncio.run(generate_audio_async(text, lang))


# ============================================================================
# STREAMING PLAYBACK
# ============================================================================

class StreamingTTS:
    """
    Streams TTS by generating and playing sentences in parallel.
    """
    
    def __init__(self):
        self.audio_queue = Queue()
        self.generation_threads = []
        self.playback_thread = None
        self.stop_flag = threading.Event()
        self.temp_files = []
        self.interrupt_flag = None  # External interrupt flag
    
    def speak_streaming(self, text: str, lang: str = "en", interrupt_flag: Optional[threading.Event] = None) -> Tuple[float, int]:
        """
        Speak text with streaming (sentence-by-sentence).
        
        Args:
            text: Full text to speak
            lang: Language code
            interrupt_flag: Optional threading.Event to allow external interruption
        
        Returns:
            Tuple of (total_time, sentence_count)
        
        Example:
            tts = StreamingTTS()
            interrupt = threading.Event()
            total_time, sentences = tts.speak_streaming("Hello. How are you?", interrupt_flag=interrupt)
            # In another thread: interrupt.set() to stop playback
        """
        start_time = time.time()
        
        # Split into sentences
        sentences = split_into_sentences(text)
        logger.info(f"Split into {len(sentences)} sentences")
        
        # Reset state
        self.stop_flag.clear()
        self.temp_files = []
        self.generation_threads = []
        self.interrupt_flag = interrupt_flag
        
        # Start playback thread (consumes from queue)
        self.playback_thread = threading.Thread(
            target=self._playback_worker,
            daemon=True
        )
        self.playback_thread.start()
        
        # Start ALL generation threads in parallel
        for i, sentence in enumerate(sentences):
            thread = threading.Thread(
                target=self._generate_worker,
                args=(sentence, lang, i),
                daemon=True
            )
            thread.start()
            self.generation_threads.append(thread)
            
            # Small delay to ensure first sentence starts generating immediately
            if i == 0:
                time.sleep(0.1)
        
        # Wait for all generation to complete
        for thread in self.generation_threads:
            thread.join()
        
        # Signal end of queue
        self.audio_queue.put(None)
        
        # Wait for playback to finish
        self.playback_thread.join()
        
        # Cleanup temp files (with retry for locked files)
        self._cleanup()
        
        total_time = time.time() - start_time
        return total_time, len(sentences)
    
    def _generate_worker(self, text: str, lang: str, index: int):
        """
        Worker thread to generate audio for one sentence.
        """
        logger.info(f"[{index}] Generating: '{text[:50]}...'")
        
        audio_path = generate_audio_sync(text, lang)
        
        if audio_path:
            logger.info(f"[{index}] ✓ Generated: {audio_path}")
            self.audio_queue.put((index, audio_path))
            self.temp_files.append(audio_path)
        else:
            logger.error(f"[{index}] ✗ Failed to generate audio")
    
    def _playback_worker(self):
        """
        Worker thread to play audio files in order.
        Supports external interruption via interrupt_flag.
        """
        if not PYGAME_AVAILABLE:
            logger.error("pygame not available - cannot play audio")
            return
        
        # Buffer to handle out-of-order generation
        buffer = {}
        next_index = 0
        
        while not self.stop_flag.is_set():
            # Check for external interrupt
            if self.interrupt_flag and self.interrupt_flag.is_set():
                logger.info("Playback interrupted by external flag")
                pygame.mixer.music.stop()
                break
            
            # Get next audio from queue (with timeout to check interrupt)
            try:
                item = self.audio_queue.get(timeout=0.1)
            except:
                continue
            
            # None signals end of queue
            if item is None:
                break
            
            index, audio_path = item
            buffer[index] = audio_path
            
            # Play all consecutive sentences in buffer
            while next_index in buffer:
                # Check interrupt before playing
                if self.interrupt_flag and self.interrupt_flag.is_set():
                    logger.info("Playback interrupted before playing sentence")
                    pygame.mixer.music.stop()
                    return
                
                audio_path = buffer[next_index]
                logger.info(f"[{next_index}] Playing: {audio_path}")
                
                try:
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    
                    # Wait for playback to finish, checking interrupt periodically
                    while pygame.mixer.music.get_busy():
                        # Check for interrupt during playback
                        if self.interrupt_flag and self.interrupt_flag.is_set():
                            logger.info(f"[{next_index}] Interrupted during playback")
                            pygame.mixer.music.stop()
                            return
                        pygame.time.Clock().tick(10)
                    
                    logger.info(f"[{next_index}] ✓ Finished playing")
                
                except Exception as e:
                    logger.error(f"[{next_index}] Playback failed: {e}")
                
                next_index += 1
    
    def _cleanup(self):
        """Delete all temporary audio files with retry for locked files."""
        for audio_path in self.temp_files:
            # Try multiple times with delay (pygame might still be using file)
            for attempt in range(3):
                try:
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                        logger.debug(f"✓ Cleaned: {audio_path}")
                    break
                except Exception as e:
                    if attempt < 2:
                        time.sleep(0.2)  # Wait and retry
                    else:
                        # Give up after 3 attempts, file will be cleaned by OS
                        logger.debug(f"Cleanup deferred: {audio_path}")
        
        self.temp_files = []
        self.generation_threads = []


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def speak_streaming(text: str, lang: str = "en", interrupt_flag: Optional[threading.Event] = None) -> Tuple[float, int]:
    """
    Quick function to speak with streaming.
    
    Args:
        text: Text to speak
        lang: Language code
        interrupt_flag: Optional threading.Event to allow external interruption
    
    Returns:
        Tuple of (total_time, sentence_count)
    
    Example:
        total_time, sentences = speak_streaming("Hello. How are you? I'm fine!")
        print(f"Spoke {sentences} sentences in {total_time:.1f}s")
        
        # With interrupt capability:
        interrupt = threading.Event()
        total_time, sentences = speak_streaming("Long text...", interrupt_flag=interrupt)
        # In another thread: interrupt.set() to stop playback
    """
    if not EDGE_TTS_AVAILABLE:
        logger.error("Edge TTS not available!")
        return 0.0, 0
    
    if not PYGAME_AVAILABLE:
        logger.error("pygame not available!")
        return 0.0, 0
    
    tts = StreamingTTS()
    return tts.speak_streaming(text, lang, interrupt_flag=interrupt_flag)


def is_available() -> bool:
    """Check if streaming TTS is available."""
    return EDGE_TTS_AVAILABLE and PYGAME_AVAILABLE


def get_engine_info() -> str:
    """Get TTS engine information."""
    return "Edge TTS (Streaming) - Arjun Voice"
