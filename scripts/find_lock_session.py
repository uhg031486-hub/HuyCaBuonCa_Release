import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/guard.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = 0
while True:
    idx = text.find('lockSession', pos)
    if idx == -1: break
    print(f"=== Found lockSession at {idx} ===")
    print(text[max(0, idx - 100):min(len(text), idx + 200)])
    pos = idx + 11
