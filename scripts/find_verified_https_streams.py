import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl
import re
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Tải playlist iptv-org và Free-TV
sources = [
    'https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8',
    'https://iptv-org.github.io/iptv/index.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/us.m3u',
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/uk.m3u'
]

https_streams = {} # name -> list of https urls

for s in sources:
    try:
        print(f"Fetching {s}...")
        req = urllib.request.Request(s, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            lines = res.read().decode('utf-8', errors='ignore').splitlines()
            curr_name = ""
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    m = re.search(r',([^,]+)$', line)
                    if m:
                        curr_name = m.group(1).strip()
                elif line.startswith('https://') and curr_name and '.m3u8' in line:
                    if curr_name not in https_streams:
                        https_streams[curr_name] = []
                    if line not in https_streams[curr_name]:
                        https_streams[curr_name].append(line)
    except Exception as e:
        print(f"Err {s}: {e}")

print(f"Collected {len(https_streams)} channels with HTTPS streams.")

# Hàm test thử xem 1 link https có 200 OK và có EXT-X-KEY DRM không
def test_stream(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=ctx, timeout=4) as r:
            if r.status != 200:
                return False, 'status ' + str(r.status)
            c = r.read(1000).decode('utf-8', errors='ignore')
            if '#EXTM3U' not in c:
                return False, 'not m3u8'
            if 'SAMPLE-AES' in c or 'skd://' in c:
                return False, 'drm'
            return True, 'ok'
    except Exception as e:
        return False, str(e)

# Tìm kiếm cho các từ khóa quốc tế quan trọng
keywords = [
    'HBO', 'Cinemax', 'Cinema', 'Movie', 'Film', 'Action',
    'Discovery', 'National Geographic', 'Nat Geo', 'Animal Planet', 'History',
    'Cartoon', 'Nickelodeon', 'Kids', 'Animation',
    'Sport', 'ESPN', 'Fox Sports', 'Eurosport', 'Sky Sports', 'TNT Sports', 'beIN',
    'BBC', 'CNN', 'Bloomberg', 'Euronews', 'Al Jazeera', 'NHK', 'DW', 'France 24'
]

verified_by_keyword = {}

for kw in keywords:
    verified_by_keyword[kw] = []
    candidates = []
    for name, urls in https_streams.items():
        if kw.lower() in name.lower():
            for u in urls:
                candidates.append((name, u))
    
    print(f"\nChecking {kw} (found {len(candidates)} candidates)...")
    for name, u in candidates[:15]:
        ok, msg = test_stream(u)
        if ok:
            print(f"  ✅ [{kw}] {name}: {u}")
            verified_by_keyword[kw].append({'name': name, 'url': u})
            if len(verified_by_keyword[kw]) >= 4:
                break
        else:
            # print(f"  ❌ {name}: {msg}")
            pass

with open('scripts/https_verified_streams.json', 'w', encoding='utf-8') as f:
    json.dump(verified_by_keyword, f, ensure_ascii=False, indent=2)

print("\nSaved verified streams to scripts/https_verified_streams.json")
