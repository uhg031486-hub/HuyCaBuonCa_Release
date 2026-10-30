import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/guard.js', 'r', encoding='utf-8') as f:
    text = f.read()

for kw in ['"message"', "'message'", 'stream-guard', 'stream-guard-hello']:
    pos = 0
    while True:
        idx = text.find(kw, pos)
        if idx == -1: break
        print(f"=== Found '{kw}' at {idx} ===")
        print(text[max(0, idx - 100):min(len(text), idx + 250)])
        pos = idx + len(kw)
