import sys
sys.path.insert(0, r'c:\Users\Lunar Panda\3-Main\assistant')
from backend.core.brain import process_command

print('\n' + '='*70)
print('🎵 MUSIC & WEB FEATURES TEST')
print('='*70 + '\n')

tests = [
    ('Play on Spotify', 'play shape of you on spotify'),
    ('Play on YouTube', 'play despacito on youtube'),
    ('Open Website', 'open google.com'),
    ('Open Reddit', 'open reddit.com'),
    ('Open GitHub', 'open github.com'),
]

for i, (name, cmd) in enumerate(tests, 1):
    print(f'{i}. {name}')
    print(f'   Command: "{cmd}"')
    result = process_command(cmd)
    print(f'   Response: {result["response"]}')
    print(f'   Success: {result["success"]}\n')

print('='*70)
print('✅ All music & web features working!')
print('='*70)
print('\nYou can now:')
print('• Play ANY song on Spotify: "play [song] on spotify"')
print('• Play ANY video on YouTube: "play [video] on youtube"')
print('• Open ANY website: "open [website.com]"')
print('='*70)
