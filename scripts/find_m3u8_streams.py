import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl
import json
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Tải danh sách stream từ iptv-org
m3u_sources = [
    'https://iptv-org.github.io/iptv/index.m3u',
    'https://iptv-org.github.io/iptv/countries/uk.m3u',
    'https://iptv-org.github.io/iptv/countries/us.m3u',
    'https://iptv-org.github.io/iptv/categories/news.m3u',
    'https://iptv-org.github.io/iptv/categories/animation.m3u',
    'https://iptv-org.github.io/iptv/categories/documentary.m3u',
    'https://iptv-org.github.io/iptv/categories/movies.m3u'
]

streams = {} # name -> list of urls

for src in m3u_sources:
    try:
        print(f"Fetching {src}...")
        req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            lines = r.read().decode('utf-8', errors='ignore').splitlines()
            curr_name = ""
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    # extract channel name
                    m = re.search(r',([^,]+)$', line)
                    if m:
                        curr_name = m.group(1).strip()
                elif line.startswith('http') and curr_name:
                    if curr_name not in streams:
                        streams[curr_name] = []
                    streams[curr_name].append(line)
    except Exception as e:
        print(f"Failed {src}: {e}")

print(f"Total streams collected: {len(streams)}")

# Tìm stream cho các kênh cần thiết
targets = [
    'BBC News', 'BBC World News', 'CNN', 'Bloomberg', 'Cartoon Network', 
    'Discovery', 'Animal Planet', 'HBO', 'Cinemax', 'AXN', 'Fashion TV'
]

results = {}
for target in targets:
    results[target] = []
    for name, urls in streams.items():
        if target.lower() in name.lower():
            for u in urls:
                if '.m3u8' in u:
                    results[target].append({'name': name, 'url': u})

print("\n--- KẾT QUẢ TÌM THẤY ---")
for t, list_u in results.items():
    print(f"\n{t} ({len(list_u)} links):")
    for item in list_u[:3]:
        print(f"  - [{item['name']}] {item['url']}")

with open('scripts/iptv_found.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
