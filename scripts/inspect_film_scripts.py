import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
req = urllib.request.Request('https://phim.nguonc.com/phim/shaun-the-sheep-quai-la-ghe-nha', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

srcs = re.findall(r'<script[^>]*src="([^"]+)"', html)
print('External scripts:', srcs)
for m in re.finditer(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', html, re.DOTALL):
    s = m.group(1).strip()
    if s:
        print('--- Inline script (len', len(s), ') ---')
        print(s[:300])
