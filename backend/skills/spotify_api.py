"""
Spotify API Integration using Spotipy
Professional music playback - works like Alexa/Google Home
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try importing spotipy
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False
    logger.warning("Spotipy not installed. Install: pip install spotipy")


class SpotifyPlayer:
    """Spotify API player - direct control without window automation"""
    
    def __init__(self):
        """Initialize Spotify API client"""
        self.sp = None
        self.authenticated = False
        
        if SPOTIPY_AVAILABLE:
            self._setup_client()
    
    def _setup_client(self):
        """Setup Spotify API client with OAuth"""
        try:
            # Get credentials from environment
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
            
            if not client_id or not client_secret:
                logger.warning("Spotify API credentials not set. Using fallback method.")
                return
            
            # Setup OAuth with required scopes
            scope = "user-read-playback-state,user-modify-playback-state"
            
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope,
                cache_path=".spotify_cache"
            ))
            
            # Test authentication
            self.sp.current_user()
            self.authenticated = True
            logger.info("✅ Spotify API authenticated successfully")
            
        except Exception as e:
            logger.error(f"Spotify API setup failed: {e}")
            self.authenticated = False
    
    def search_and_play(self, query: str) -> dict:
        """
        Search for a song and play it instantly.
        
        Args:
            query: Song name or "artist - song" format
        
        Returns:
            dict: Result with status and track info
        """
        if not self.authenticated:
            return {
                'success': False,
                'message': 'Spotify API not authenticated',
                'fallback': True
            }
        
        try:
            # Search for the track
            results = self.sp.search(q=query, type='track', limit=1)
            
            if not results['tracks']['items']:
                return {
                    'success': False,
                    'message': f"No results found for '{query}'",
                    'fallback': True
                }
            
            # Get first result
            track = results['tracks']['items'][0]
            track_uri = track['uri']
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            
            # Get available devices
            devices = self.sp.devices()
            
            if not devices['devices']:
                return {
                    'success': False,
                    'message': 'No active Spotify devices found. Open Spotify app first.',
                    'fallback': True
                }
            
            # Play on the first available device
            device_id = devices['devices'][0]['id']
            self.sp.start_playback(device_id=device_id, uris=[track_uri])
            
            logger.info(f"✅ Playing: {track_name} by {artist_name}")
            
            return {
                'success': True,
                'message': f"Playing '{track_name}' by {artist_name}",
                'track': track_name,
                'artist': artist_name
            }
            
        except Exception as e:
            logger.error(f"Spotify playback failed: {e}")
            return {
                'success': False,
                'message': f'Playback error: {str(e)}',
                'fallback': True
            }
    
    def pause(self) -> bool:
        """Pause current playback"""
        try:
            self.sp.pause_playback()
            return True
        except:
            return False
    
    def resume(self) -> bool:
        """Resume playback"""
        try:
            self.sp.start_playback()
            return True
        except:
            return False
    
    def next_track(self) -> bool:
        """Skip to next track"""
        try:
            self.sp.next_track()
            return True
        except:
            return False
    
    def previous_track(self) -> bool:
        """Go to previous track"""
        try:
            self.sp.previous_track()
            return True
        except:
            return False


# Global instance
_spotify_player = None

def get_spotify_player() -> Optional[SpotifyPlayer]:
    """Get or create Spotify player instance"""
    global _spotify_player
    
    if _spotify_player is None:
        _spotify_player = SpotifyPlayer()
    
    return _spotify_player if _spotify_player.authenticated else None
