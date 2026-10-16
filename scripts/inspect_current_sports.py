import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_Mobile/app/src/main/assets/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

sports_groups = ['ASEAN HUYNDAI CUP 2026', 'LIVE EVENTS 🔴', 'THỂ THAO QUỐC TẾ', '⚽| Thể thao quốc tế', 'Sự Kiện TV360', 'Sự Kiện VTVPrime']
sports_chans = [c for c in channels if c['group'] in sports_groups]
print(f"Total sports channels in tv_channels.json: {len(sports_chans)}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://fptplay.vn/'
}

def test_c(c):
    url = c['url']
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                return (True, c, None)
    except Exception as e:
        return (False, c, str(e)[:50])
    return (False, c, "unknown")

alive = []
dead = []
with ThreadPoolExecutor(max_workers=20) as ex:
    futs = [ex.submit(test_c, c) for c in sports_chans]
    for fut in as_completed(futs):
        ok, c, err = fut.result()
        if ok:
            alive.append(c)
            print(f"[ALIVE] {c['group']} - {c['name']}")
        else:
            dead.append(c)
            # print(f"[DEAD] {c['group']} - {c['name']}: {err}")

print(f"\nCurrent tv_channels.json sports: {len(alive)} ALIVE, {len(dead)} DEAD")
