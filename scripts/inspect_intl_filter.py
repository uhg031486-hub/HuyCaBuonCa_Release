import sys
import json
import urllib.request
import time

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

intl_channels = [c for c in channels if any(k in (c.get('group') or '') for k in ['Quốc Tế', 'Hàn Quốc', 'Trung Quốc', 'Israel', 'In The Box', 'TVB'])]
print(f"Tổng số kênh trong filter 'tv://intl': {len(intl_channels)}")

for i, ch in enumerate(intl_channels):
    url = ch.get('url', '')
    name = ch.get('name', '')
    grp = ch.get('group', '')
    
    # Test stream
    status = 'Checking...'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = resp.read(256)
            elapsed = time.time() - t0
            status = f"✅ OK ({resp.status}, {elapsed:.2f}s)"
    except Exception as e:
        status = f"❌ LỖI: {e}"
        
    print(f"{i+1}. [{grp}] {name} -> {status}")
    print(f"   URL: {url}")
