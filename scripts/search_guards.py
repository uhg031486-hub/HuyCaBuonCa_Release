import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

for path in ['scripts/guard.js', 'scripts/player.js', 'scripts/cdn-start.js']:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    print(f'=== {path} ===')
    for m in re.finditer(r'(top\.location|window\.top|parent\.location|location\.href\s*=|location\.replace|phim\.nguonc|\.open\()', text):
        start = max(0, m.start() - 50)
        end = min(len(text), m.end() + 50)
        clean = text[start:end].replace('\n', ' ')
        print('MATCH:', clean)
