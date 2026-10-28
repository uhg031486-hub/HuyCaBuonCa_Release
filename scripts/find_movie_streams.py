import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl
import json
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8'
print("Scanning Free-TV for Cinema / Action / Movie channels...")

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=8) as res:
    lines = res.read().decode('utf-8', errors='ignore').splitlines()

movie_channels = []
curr = ""
for line in lines:
    line = line.strip()
    if line.startswith('#EXTINF:'):
        curr = line
    elif line.startswith('https://') and curr and '.m3u8' in line:
        if any(w in curr.upper() for w in ['CINEMA', 'MOVIE', 'ACTION', 'HOLLYWOOD', 'HBO', 'FILM']):
            m = re.search(r',([^,]+)$', curr)
            name = m.group(1).strip() if m else curr
            movie_channels.append({'name': name, 'url': line})

print(f"Found {len(movie_channels)} movie channels. Testing top 15 for CORS:")

tested = []
for item in movie_channels[:25]:
    u = item['url']
    try:
        req2 = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req2, context=ctx, timeout=4) as r:
            if r.status == 200:
                data = r.read(400).decode('utf-8', errors='ignore')
                if '#EXTM3U' in data and 'SAMPLE-AES' not in data:
                    cors = r.headers.get('Access-Control-Allow-Origin') is not None
                    if cors:
                        print(f"✅ {item['name']}: CORS OK -> {u}")
                        tested.append(item)
                        if len(tested) >= 5:
                            break
    except Exception:
        pass

with open('scripts/movie_channels_found.json', 'w', encoding='utf-8') as f:
    json.dump(tested, f, ensure_ascii=False, indent=2)
