"""
Quick test for AI song extraction with platform detection
"""

import sys
sys.path.insert(0, r'c:\Users\Lunar Panda\3-Main\assistant')
from backend.core.brain import process_command

print('\n' + '='*70)
print('🎵 AI SONG EXTRACTION + PLATFORM DETECTION TEST')
print('='*70 + '\n')

# Test cases with expected results (command, expected_song, expected_platform)
tests = [
    ('play tears on spotify', 'tears', 'spotify'),
    ('song tears on spotify', 'tears', 'spotify'),
    ('play tears on youtube', 'tears', 'youtube'),
    ('the song tears', 'tears', 'spotify'),  # Should default to Spotify
    ('play shape of you on spotify', 'shape of you', 'spotify'),
    ('play despacito on youtube', 'despacito', 'youtube'),
]

for i, (cmd, expected_song, expected_platform) in enumerate(tests, 1):
    print(f'{i}. Testing: "{cmd}"')
    result = process_command(cmd)
    
    extracted = result.get('query', 'NONE')
    platform = result.get('intent', 'unknown')
    
    song_ok = '✅' if extracted.lower() == expected_song.lower() else '❌'
    platform_ok = '✅' if platform == expected_platform else '❌'
    
    print(f'   Song: {song_ok} "{extracted}" (expected: "{expected_song}")')
    print(f'   Platform: {platform_ok} {platform} (expected: {expected_platform})')
    print(f'   Response: {result.get("response", "N/A")}\n')

print('='*70)
print('✅ Check if Spotify/YouTube opened with correct songs!')
print('='*70)
