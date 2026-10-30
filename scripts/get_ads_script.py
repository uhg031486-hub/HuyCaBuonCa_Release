import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://phim.nguonc.com/'})
with urllib.request.urlopen(req) as r:
    html = r.read().decode('utf-8')

m = re.search(r'"ads\.js"\s*:\s*"([^"]+)"', html)
if m:
    ads_url = 'https://embed17.streamc.xyz' + m.group(1)
    print('Downloading ads.js from:', ads_url)
    req2 = urllib.request.Request(ads_url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': url})
    with urllib.request.urlopen(req2) as r2:
        ads_code = r2.read().decode('utf-8')
    with open('scripts/ads.js', 'w', encoding='utf-8') as f:
        f.write(ads_code)
    print('Saved scripts/ads.js, length:', len(ads_code))
else:
    print('ads.js not found in HTML')
