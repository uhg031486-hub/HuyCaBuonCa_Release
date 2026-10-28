import urllib.request
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for kw in ['tổng tài', 'giang thiếu']:
    url = f"https://gamomephim.com/tim-kiem?q={urllib.parse.quote(kw)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            pattern = r'<a[^>]+title="([^"]+)"[^>]+href="/phim/([^"]+)".*?<img[^>]+src="([^"]+)"'
            matches = re.findall(pattern, html, re.DOTALL)
            print(f"Search '{kw}': {len(matches)} results")
            for m in matches[:3]:
                print(f"  - {m[0]} | slug: {m[1]}")
    except Exception as e:
        print(f"Search '{kw}' error: {e}")
