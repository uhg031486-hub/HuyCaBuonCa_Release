import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import json

with open('HuyCa_Web/data/tv_channels.js', 'r', encoding='utf-8') as f:
    text = f.read()

json_match = re.search(r'=\s*(\[.*\]);?\s*$', text, re.DOTALL)
if json_match:
    channels = json.loads(json_match.group(1))
else:
    with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
        channels = json.load(f)

print(f"Tổng số kênh TV: {len(channels)}")

mpd_channels = []
for ch in channels:
    url = ch.get('url', '')
    if '.mpd' in url or 'dash' in url.lower():
        mpd_channels.append(ch)

print(f"Số kênh dùng .mpd hoặc DASH: {len(mpd_channels)}")
for ch in mpd_channels:
    print(f"- [{ch.get('category', '')}] {ch.get('name')}: {ch.get('url')}")
