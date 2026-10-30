import urllib.request, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

u = 'https://gamomephim.com/sau-khi-treo-nham-canh-cao'
try:
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=10) as res:
        html = res.read().decode('utf-8')
        videos = re.findall(r'https://r2\.gamomephim\.com/videos/[^\s"\'<>]+\.mp4', html)
        print("Videos found:", videos)
except Exception as e:
    print("Error:", e)
