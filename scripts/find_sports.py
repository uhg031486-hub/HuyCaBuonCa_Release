import urllib.request
import re
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

urls = [
    'https://raw.githubusercontent.com/khanh71/All-In-One-IPTV/main/http-iptv.m3u',
    'https://iptv-org.github.io/iptv/categories/sports.m3u',
    'https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8'
]

def parse_m3u(url):
    print(f"\nFetching {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            lines = content.splitlines()
            channels = []
            cur_name = None
            cur_group = None
            cur_logo = ""
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    group_match = re.search(r'group-title="([^"]+)"', line)
                    cur_group = group_match.group(1) if group_match else 'Other'
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    cur_logo = logo_match.group(1) if logo_match else ''
                    name = line.split(',')[-1].strip()
                    cur_name = name
                elif line.startswith('http') and cur_name:
                    channels.append({
                        'name': cur_name,
                        'group': cur_group,
                        'logo': cur_logo,
                        'url': line
                    })
                    cur_name = None
            print(f"Total channels in {url}: {len(channels)}")
            return channels
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

all_channels = []
for u in urls:
    chans = parse_m3u(u)
    all_channels.extend(chans)

sports_keywords = ['thể thao', 'sport', 'k+', 'bóng đá', 'football', 'soccer', 'golf', 'tnt', 'espn', 'bein', 'arena', 'match', 'premier', 'league', 'canal']
sports_channels = []
for c in all_channels:
    text = (c['name'] + ' ' + c['group']).lower()
    if any(k in text for k in sports_keywords):
        sports_channels.append(c)

print(f"\nTotal potential sports channels found: {len(sports_channels)}")
with open('discovered_sports.json', 'w', encoding='utf-8') as f:
    json.dump(sports_channels, f, ensure_ascii=False, indent=2)

print("Saved to discovered_sports.json. Now testing first 50 channels for alive status...")

alive = []
for i, c in enumerate(sports_channels[:50]):
    u = c['url']
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            status = resp.status
            ct = resp.headers.get('Content-Type', '')
            if status == 200:
                print(f"[{i+1}/50] [ALIVE 200] {c['name']} ({c['group']}) -> {ct}")
                c['content_type'] = ct
                alive.append(c)
            else:
                print(f"[{i+1}/50] [FAIL {status}] {c['name']}")
    except Exception as e:
        print(f"[{i+1}/50] [ERR] {c['name']}: {e}")

print(f"\nFound {len(alive)} alive channels out of 50 tested!")
with open('alive_sports_test.json', 'w', encoding='utf-8') as f:
    json.dump(alive, f, ensure_ascii=False, indent=2)
