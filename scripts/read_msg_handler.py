import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/guard.js', 'r', encoding='utf-8') as f:
    text = f.read()

print(text[19200:21000])
