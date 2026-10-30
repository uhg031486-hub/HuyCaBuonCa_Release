import urllib.request
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = 'https://gamomephim.com/the-loai/trong-sinh'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10) as res:
    html = res.read().decode('utf-8')
    a = re.search(r'<a[^>]+href="/phim/[^"]+"[^>]*>.*?</a>', html, re.DOTALL)
    if a:
        print(a.group(0))
