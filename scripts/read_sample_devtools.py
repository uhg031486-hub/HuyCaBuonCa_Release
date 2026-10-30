import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/guard.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function sampleDevtools')
if idx == -1:
    idx = text.find('sampleDevtools=')
print(text[max(0, idx - 100):min(len(text), idx + 2500)])
