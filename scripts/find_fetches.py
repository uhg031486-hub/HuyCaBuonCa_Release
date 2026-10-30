import urllib.request
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://phim.nguonc.com/'}
url = 'https://embed14.streamc.xyz/assets/player-messages-r25.f8deeb2bf0fe759c.js'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    c = resp.read().decode('utf-8', errors='ignore')
    for m in re.finditer(r'fetch\(', c):
        idx = m.start()
        print('--- FETCH AT', idx, '---')
        print(c[max(0, idx-50):min(len(c), idx+300)])
