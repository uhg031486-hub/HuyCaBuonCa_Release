import json
import urllib.request
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

with open('alive_sports_verified.json', 'r', encoding='utf-8') as f:
    list1 = json.load(f)

with open('alive_sports_part2.json', 'r', encoding='utf-8') as f:
    list2 = json.load(f)

all_alive = list1 + list2
print(f"Total candidate alive channels: {len(all_alive)}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def verify_real_hls(c):
    url = c['url']
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = resp.read(1024).decode('utf-8', errors='ignore')
            # Check for genuine HLS manifest markers
            if data.startswith('#EXTM3U') and ('#EXT-X-STREAM-INF' in data or '#EXTINF:' in data or '#EXT-X-TARGETDURATION' in data):
                return (True, c, None)
            else:
                return (False, c, "Not genuine HLS manifest")
    except Exception as e:
        return (False, c, str(e)[:50])

verified_hls = []
with ThreadPoolExecutor(max_workers=30) as ex:
    futures = [ex.submit(verify_real_hls, c) for c in all_alive]
    for fut in as_completed(futures):
        ok, c, err = fut.result()
        if ok:
            verified_hls.append(c)
            print(f"[VERIFIED HLS] {c['name']} -> {c['url']}")

print(f"\nTotal VERIFIED Genuine HLS Sports Channels: {len(verified_hls)}")
with open('verified_genuine_sports.json', 'w', encoding='utf-8') as f:
    json.dump(verified_hls, f, ensure_ascii=False, indent=2)
