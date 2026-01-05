"""
Test Spotify auto-play with different songs
"""

import sys
sys.path.insert(0, r'c:\Users\Lunar Panda\3-Main\assistant')
from backend.skills.music_player import play_on_spotify
import time

print('\n' + '='*70)
print('🎵 SPOTIFY AUTO-PLAY TEST')
print('='*70 + '\n')

# Test different songs
songs = [
    'shape of you',
    'despacito',
    'bohemian rhapsody',
]

print('Testing Spotify auto-play with different songs...\n')
print('⚠️  NOTE: Each song will wait 3.5 seconds then auto-play')
print('    Make sure Spotify window is visible!\n')

for i, song in enumerate(songs, 1):
    print(f'{i}. Testing: "{song}"')
    result = play_on_spotify(song)
    print(f'   Result: {result}')
    print(f'   ⏳ Waiting 10 seconds before next song...\n')
    
    if i < len(songs):
        time.sleep(10)  # Wait between songs to hear them play

print('='*70)
print('✅ Test complete! Check if all songs auto-played correctly.')
print('='*70)
