"""
Music & Media Playback Skill
Play songs on Spotify app or YouTube, open any website
"""

import logging
import webbrowser
import subprocess
import urllib.parse

logger = logging.getLogger(__name__)

# Try importing pywhatkit for YouTube
try:
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except (ImportError, Exception) as e:
    logger.warning(f"pywhatkit not available: {e}")
    PYWHATKIT_AVAILABLE = False

# Try importing Spotify API
try:
    from backend.skills.spotify_api import get_spotify_player
    SPOTIFY_API_AVAILABLE = True
except (ImportError, Exception) as e:
    logger.warning(f"Spotify API not available: {e}")
    SPOTIFY_API_AVAILABLE = False


def play_on_spotify(song_name: str) -> str:
    """
    Search and play song on Spotify.
    
    Tries in order:
    1. Spotify API (like Alexa/Google Home) - instant, reliable
    2. Fallback to app opening (manual play required)
    
    Args:
        song_name: Song name, artist, or search query
    
    Returns:
        str: Status message
    """
    # METHOD 1: Try Spotify API first (BEST - like Alexa)
    if SPOTIFY_API_AVAILABLE:
        try:
            player = get_spotify_player()
            if player:
                result = player.search_and_play(song_name)
                if result['success']:
                    logger.info(f"✅ Spotify API: {result['message']}")
                    return result['message']
                elif not result.get('fallback'):
                    # API error but don't fallback
                    return result['message']
                # Otherwise fallback to method 2
                logger.warning("Spotify API failed, trying app method...")
        except Exception as e:
            logger.warning(f"Spotify API error: {e}, trying app method...")
    
    # METHOD 2: Fallback - Open Spotify app (requires manual Enter press)
    try:
        query = urllib.parse.quote(song_name)
        
        logger.info(f"Playing on Spotify app: {song_name}")
        
        # Open Spotify app with search
        spotify_uri = f"spotify:search:{query}"
        subprocess.Popen(['cmd', '/c', 'start', '', spotify_uri], shell=True)
        logger.info(f"✓ Opened Spotify app with: {song_name}")
        
        return f"Opened Spotify for '{song_name}' (press Enter to play, or setup Spotify API for auto-play)"
    
    except Exception as e:
        logger.error(f"Failed to play on Spotify: {e}")
        
        # METHOD 3: Last resort - web player
        try:
            web_url = f"https://open.spotify.com/search/{query}"
            webbrowser.open(web_url)
            logger.info(f"✓ Opened Spotify web player: {song_name}")
            return f"Opened Spotify web player for '{song_name}'"
        except:
            return f"Error playing on Spotify: {e}"


def play_on_youtube(query: str) -> str:
    """
    Search and play video/song on YouTube.
    
    Args:
        query: Search query or song name
    
    Returns:
        str: Status message
    
    Examples:
        play_on_youtube("Bohemian Rhapsody")
        play_on_youtube("Python tutorial")
    """
    if not PYWHATKIT_AVAILABLE:
        # Fallback: Open YouTube search in browser
        try:
            search_query = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={search_query}"
            webbrowser.open(url)
            return f"Opened YouTube search for '{query}'"
        except Exception as e:
            return f"Error opening YouTube: {e}"
    
    try:
        logger.info(f"Playing YouTube: {query}")
        
        # pywhatkit opens the first search result in default browser
        pywhatkit.playonyt(query)
        
        logger.info(f"✓ Opened YouTube video: {query}")
        return f"Playing '{query}' on YouTube"
    
    except Exception as e:
        logger.error(f"Failed to play YouTube video: {e}")
        return f"Error playing YouTube video: {e}"


def open_link(url: str) -> str:
    """
    Open any link/website in default browser.
    
    Args:
        url: Website URL (with or without http/https)
    
    Returns:
        str: Status message
    
    Examples:
        open_link("google.com")
        open_link("https://github.com")
        open_link("reddit.com/r/python")
    """
    try:
        # Add https:// if no protocol specified
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        
        logger.info(f"Opening link: {url}")
        webbrowser.open(url)
        
        logger.info(f"✓ Opened: {url}")
        return f"Opened {url}"
    
    except Exception as e:
        logger.error(f"Failed to open link: {e}")
        return f"Error opening link: {e}"


def play_music(song_name: str, platform: str = "spotify") -> str:
    """
    Play music on specified platform.
    
    Args:
        song_name: Song name or search query
        platform: "spotify" or "youtube" (default: spotify)
    
    Returns:
        str: Status message
    
    Examples:
        play_music("Imagine Dragons Radioactive", "spotify")
        play_music("Coldplay Fix You", "youtube")
    """
    platform = platform.lower().strip()
    
    if platform == "spotify":
        return play_on_spotify(song_name)
    elif platform == "youtube":
        return play_on_youtube(song_name)
    else:
        # Default to Spotify
        return play_on_spotify(song_name)


def is_available() -> bool:
    """Check if music playback is available"""
    return True  # Always available (uses browser fallback)
