import urllib.request
import re
import sys
import json
import concurrent.futures

sys.stdout.reconfigure(encoding='utf-8')

PLAYLISTS = [
    "https://iptv-org.github.io/iptv/categories/news.m3u",
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://iptv-org.github.io/iptv/categories/movies.m3u",
    "https://iptv-org.github.io/iptv/categories/documentary.m3u",
    "https://iptv-org.github.io/iptv/categories/animation.m3u",
    "https://iptv-org.github.io/iptv/countries/us.m3u",
    "https://iptv-org.github.io/iptv/countries/uk.m3u"
]

TARGETS = [
    "NHK World", "Al Jazeera", "ABC News", "CBS News", "NBC News NOW",
    "Sky News", "Euronews", "CNA", "Bloomberg", "DW", "France 24",
    "TRT World", "NASA TV", "Red Bull TV", "Eurosport", "beIN SPORTS",
    "Discovery", "History", "National Geographic", "Nat Geo",
    "Cartoon", "Boomerang", "Animax", "HBO", "Cinemax", "Warner",
    "Fashion TV", "Qwest", "Stingray", "Arirang", "YTN", "KBS World"
]

def parse_m3u(url):
    results = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode('utf-8', errors='ignore')
            lines = text.splitlines()
            current_name = None
            current_logo = None
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    logo_m = re.search(r'tvg-logo="([^"]*)"', line)
                    current_logo = logo_m.group(1) if logo_m else ''
                    parts = line.split(',', 1)
                    current_name = parts[1].strip() if len(parts) > 1 else 'Unknown'
                elif line and not line.startswith('#'):
                    if current_name:
                        # Check match
                        for t in TARGETS:
                            if t.lower() in current_name.lower():
                                results.append({
                                    'target': t,
                                    'name': current_name,
                                    'logo': current_logo,
                                    'url': line
                                })
                                break
                    current_name = None
                    current_logo = None
    except Exception as e:
        print(f"Error {url}: {e}")
    return results

def test_stream(item):
    url = item['url']
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        })
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = resp.read(256).decode('utf-8', errors='ignore')
            if resp.status == 200 and ('#EXTM3U' in data or 'EXT-X-' in data or len(data) > 30):
                return (item, True)
    except:
        pass
    return (item, False)

print("Đang quét các danh mục kênh quốc tế...")
candidates = []
for p in PLAYLISTS:
    res = parse_m3u(p)
    print(f"  {p.split('/')[-1]}: {len(res)} kênh phù hợp")
    candidates.extend(res)

print(f"Tổng số kênh tìm thấy: {len(candidates)}")

# Loại bỏ trùng URL
seen = set()
unique_cands = []
for c in candidates:
    if c['url'] not in seen:
        seen.add(c['url'])
        unique_cands.append(c)

print(f"Số kênh duy nhất: {len(unique_cands)}")
print("Đang kiểm thử chất lượng luồng phát...")

working = []
with concurrent.futures.ThreadPoolExecutor(max_workers=35) as executor:
    futures = [executor.submit(test_stream, c) for c in unique_cands]
    for f in concurrent.futures.as_completed(futures):
        item, is_ok = f.result()
        if is_ok:
            working.append(item)

print(f"✅ Số kênh quốc tế hoạt động HOÀN HẢO: {len(working)}")

# Gom nhóm theo Target Brand
by_target = {}
for w in working:
    t = w['target']
    by_target.setdefault(t, []).append(w)

for t, ch_list in sorted(by_target.items()):
    print(f"\n[Thương hiệu: {t}] - {len(ch_list)} luồng hoạt động:")
    for ch in ch_list[:3]:
        print(f"  - {ch['name']} -> {ch['url']}")

with open('scripts/intl_verified_streams.json', 'w', encoding='utf-8') as f:
    json.dump(working, f, ensure_ascii=False, indent=2)
