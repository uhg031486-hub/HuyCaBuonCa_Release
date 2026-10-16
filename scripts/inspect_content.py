import json
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_Mobile/app/src/main/assets/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

for c in channels:
    if 'CANAL+' in c['name'] or 'TNT Sports' in c['name'] or 'Sky Sport' in c['name']:
        url = c['url']
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                content = resp.read(300).decode('utf-8', errors='ignore')
                print(f"{c['name']} -> {url}")
                print(f"   First 150 chars: {content[:150].strip()}")
        except Exception as e:
            print(f"{c['name']} -> ERROR: {e}")
