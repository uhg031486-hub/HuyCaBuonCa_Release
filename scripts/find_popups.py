import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/player.js', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'(window\.open|popup|\.open\(|target=)', text):
    start = max(0, m.start() - 60)
    end = min(len(text), m.end() + 80)
    print(text[start:end].replace('\n', ' '))
