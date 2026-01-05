"""
Simple test for Spotify auto-play
Just tests one song to verify it works
"""

import sys
sys.path.insert(0, r'c:\Users\Lunar Panda\3-Main\assistant')
from backend.skills.music_player import play_on_spotify

print('\n🎵 Testing Spotify Auto-Play...\n')
print('Make sure Spotify window will be visible!')
print('Song will start playing in 4 seconds...\n')

song = input('Enter song name (or press Enter for "shape of you"): ').strip()
if not song:
    song = 'shape of you'

print(f'\nSearching for: {song}')
result = play_on_spotify(song)
print(f'Result: {result}')
print('\n✅ Check if song is playing in Spotify!')
