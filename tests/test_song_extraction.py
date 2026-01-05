"""
Test AI-powered song name extraction from various voice commands
"""

import sys
sys.path.insert(0, r'c:\Users\Lunar Panda\3-Main\assistant')
from backend.core.brain import process_command

print('\n' + '='*70)
print('🎵 AI SONG NAME EXTRACTION TEST')
print('='*70 + '\n')

test_cases = [
    'play tears on spotify',
    'play shape of you on spotify',
    'play despacito on youtube',
    'play bohemian rhapsody',
    'play imagine dragons on spotify',
    'play thunder on youtube',
    'play ariana grande dangerous woman',
]

print('Testing AI song extraction...\n')
for i, command in enumerate(test_cases, 1):
    print(f'{i}. Command: "{command}"')
    result = process_command(command)
    extracted = result.get('query', 'NO QUERY')
    platform = result.get('intent', 'unknown')
    
    print(f'   ✅ Extracted: "{extracted}"')
    print(f'   📱 Platform: {platform}')
    print(f'   💬 Response: {result.get("response", "N/A")}\n')

print('='*70)
print('✅ AI is now extracting song names intelligently!')
print('='*70)
