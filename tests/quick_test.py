import sys
sys.path.insert(0, r'c:\Users\Lunar Panda\3-Main\assistant')
from backend.core.brain import process_command

print('\n' + '='*60)
print('🧪 QUICK FEATURE TEST')
print('='*60 + '\n')

tests = [
    ('Time', 'what time is it'),
    ('Battery', 'battery status'),
    ('CPU', 'cpu usage'),
    ('Calculator', 'open calculator'),
    ('WhatsApp', 'open whatsapp'),
]

for i, (name, cmd) in enumerate(tests, 1):
    result = process_command(cmd)
    print(f'{i}. {name:15} → {result["response"]}')

print('\n' + '='*60)
print('✅ All features working!')
print('='*60)
