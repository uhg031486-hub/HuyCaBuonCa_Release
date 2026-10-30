import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCa_Web/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines[140:385], 141):
    if any(k in line for k in ['<div', '<section', 'id=', 'class=']):
        print(f"{i}: {line.strip()[:100]}")
