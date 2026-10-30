import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://gamomephim.com/phim/noi-som-khong-som"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=10) as res:
    html = res.read().decode('utf-8', errors='ignore')

# In ra các đoạn script có chứa json hoặc r2 hoặc video hoặc player
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print("Total scripts:", len(scripts))
for i, s in enumerate(scripts):
    if any(k in s for k in ['video', 'player', 'stream', 'part', 'r2.', 'url', 'mp4', 'episodes']):
        print(f"\n--- Script {i} (len: {len(s)}) ---")
        lines = [line.strip() for line in s.split('\n') if any(k in line.lower() for k in ['video', 'player', 'mp4', 'part', 'url', 'episode'])][:10]
        for l in lines:
            print("  ", l[:120])
