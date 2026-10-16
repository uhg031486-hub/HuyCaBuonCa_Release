import json
import urllib.request
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://fptplay.vn/'
}

with open('discovered_sports.json', 'r', encoding='utf-8') as f:
    sports = json.load(f)

print(f"Total sports candidates in discovered_sports.json: {len(sports)}")

def test_stream(c):
    url = c['url']
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            ct = resp.headers.get('Content-Type', '').lower()
            if resp.status == 200:
                sample = resp.read(512).decode('utf-8', errors='ignore')
                if '#EXTM3U' in sample or 'video' in ct or 'mpegurl' in ct or 'octet-stream' in ct:
                    return (True, c, ct)
    except:
        pass
    return (False, c, None)

alive_new = []
with ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(test_stream, c) for c in sports[120:]]
    for future in as_completed(futures):
        ok, c, ct = future.result()
        if ok:
            print(f"[NEW ALIVE] {c['name']} ({c['group']}) -> {c['url']}")
            alive_new.append(c)

print(f"\nFound {len(alive_new)} additional alive sports channels!")
with open('alive_sports_part2.json', 'w', encoding='utf-8') as f:
    json.dump(alive_new, f, ensure_ascii=False, indent=2)
