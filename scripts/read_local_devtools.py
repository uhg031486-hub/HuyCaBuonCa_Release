import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/guard.js', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function sampleLocalDevtools')
if idx == -1:
    idx = text.find('sampleLocalDevtools=')
print(text[max(0, idx - 100):min(len(text), idx + 2000)])
