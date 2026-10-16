import urllib.request
import re
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

playlist_urls = [
    ('khanh71', 'https://raw.githubusercontent.com/khanh71/All-In-One-IPTV/main/http-iptv.m3u'),
    ('iptv-org-sports', 'https://iptv-org.github.io/iptv/categories/sports.m3u'),
    ('freetv', 'https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8')
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://fptplay.vn/'
}

def fetch_m3u(source_name, url):
    print(f"Fetching playlist {source_name}...")
    req = urllib.request.Request(url, headers={'User-Agent': headers['User-Agent']})
    channels = []
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            lines = content.splitlines()
            cur_name = None
            cur_group = None
            cur_logo = ""
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    g = re.search(r'group-title="([^"]+)"', line)
                    cur_group = g.group(1) if g else 'Thể Thao'
                    logo = re.search(r'tvg-logo="([^"]+)"', line)
                    cur_logo = logo.group(1) if logo else ''
                    cur_name = line.split(',')[-1].strip()
                elif line.startswith('http') and cur_name:
                    channels.append({
                        'source': source_name,
                        'name': cur_name,
                        'group': cur_group,
                        'logo': cur_logo,
                        'url': line
                    })
                    cur_name = None
    except Exception as e:
        print(f"Failed {source_name}: {e}")
    print(f"Loaded {len(channels)} channels from {source_name}")
    return channels

all_channels = []
for sname, surl in playlist_urls:
    all_channels.extend(fetch_m3u(sname, surl))

# Filter for sports / football keywords
keywords = [
    'sport', 'thể thao', 'football', 'soccer', 'k+', 'tnt', 'espn', 
    'bein', 'arena', 'match', 'premier', 'league', 'canal', 'fifa',
    'golf', 'bóng đá', 'onsport', 'redbull', 'nba', 'ufc', 'f1'
]

sports_candidates = []
seen_urls = set()
for c in all_channels:
    text = (c['name'] + ' ' + c['group']).lower()
    if any(k in text for k in keywords) and c['url'] not in seen_urls:
        seen_urls.add(c['url'])
        sports_candidates.append(c)

print(f"\nTotal unique sports candidates: {len(sports_candidates)}")

def test_stream(channel):
    url = channel['url']
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            status = resp.status
            ct = resp.headers.get('Content-Type', '').lower()
            if status == 200:
                # Read first 512 bytes to verify HLS / stream
                sample = resp.read(512).decode('utf-8', errors='ignore')
                if '#EXTM3U' in sample or 'video' in ct or 'mpegurl' in ct or 'octet-stream' in ct:
                    return (True, channel, ct, None)
                else:
                    return (False, channel, ct, "Not a valid stream manifest")
            else:
                return (False, channel, ct, f"HTTP {status}")
    except Exception as e:
        return (False, channel, None, str(e)[:60])

print("\nTesting first 120 sports candidates concurrently with 20 threads...")
alive_list = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(test_stream, c) for c in sports_candidates[:120]]
    for future in as_completed(futures):
        is_alive, chan, ct, err = future.result()
        if is_alive:
            print(f"[ALIVE] {chan['name']} | Group: {chan['group']} | Type: {ct}")
            alive_list.append(chan)
        else:
            # print(f"[DEAD] {chan['name']} - {err}")
            pass

print(f"\n================ SUMMARY ================")
print(f"Total Alive Streams: {len(alive_list)}")
for a in alive_list:
    print(f"- {a['name']} ({a['group']}): {a['url']}")

with open('alive_sports_verified.json', 'w', encoding='utf-8') as f:
    json.dump(alive_list, f, ensure_ascii=False, indent=2)
print("Saved to alive_sports_verified.json")
