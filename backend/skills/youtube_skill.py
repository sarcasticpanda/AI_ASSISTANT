"""
YouTube Skill - Search and play YouTube videos
Uses pywhatkit for searching and playing videos.
"""

import logging

logger = logging.getLogger(__name__)

# Try importing pywhatkit
try:
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except (ImportError, Exception) as e:
    logger.warning(f"pywhatkit not available: {e}")
    PYWHATKIT_AVAILABLE = False


def play_youtube(query: str) -> str:
    """
    Search and play a YouTube video.
    
    Args:
        query: Search query or video topic
    
    Returns:
        str: Status message
    
    Examples:
        play_youtube("python tutorials")  # Searches and opens first result
        play_youtube("despacito")  # Opens music video
    """
    if not PYWHATKIT_AVAILABLE:
        return "YouTube playback requires pywhatkit. Install with: pip install pywhatkit"
    
    try:
        logger.info(f"Playing YouTube: {query}")
        
        # pywhatkit opens the first search result in default browser
        pywhatkit.playonyt(query)
        
        logger.info(f"✓ Opened YouTube video: {query}")
        return f"Playing '{query}' on YouTube"
    
    except Exception as e:
        logger.error(f"Failed to play YouTube video: {e}")
        return f"Error playing YouTube video: {e}"


def is_available() -> bool:
    """Check if YouTube functionality is available"""
    return PYWHATKIT_AVAILABLE
