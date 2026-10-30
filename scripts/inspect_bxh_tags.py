import urllib.request
import re

url = 'https://gamomephim.com/ban-xep-hang'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10) as res:
    html = res.read().decode('utf-8')
    a_tags = re.findall(r'<a[^>]+href="/phim/[^"]+"[^>]*>.*?</a>', html, re.DOTALL)
    print(f"Total /phim/ anchor tags: {len(a_tags)}")
    for tag in a_tags[:3]:
        print("TAG:\n", tag[:300])
        print("-" * 40)
