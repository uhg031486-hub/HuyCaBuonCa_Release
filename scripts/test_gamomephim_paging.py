import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for page in [1, 2]:
    url = f"https://gamomephim.com/the-loai/hien-dai?page={page}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            # Lấy danh sách item từ chunk RSC của Next.js:
            # Pattern: "title":"...","slug":"...","img":"...","badge":"...","year":"..."
            items = re.findall(r'\"title\":\"([^\"]+)\",\"slug\":\"([^\"]+)\",\"img\":\"([^\"]+)\"[^}]*?\"badge\":\"([^\"]+)\"[^}]*?\"year\":\"([^\"]+)\"', html)
            if not items:
                # Tìm theo mẫu linh hoạt hơn
                items = re.findall(r'\"title\":\"([^\"]+)\",\"slug\":\"([^\"]+)\",\"img\":\"([^\"]+)\"', html)
            print(f"Page {page}: {len(items)} movies found.")
            for it in items[:3]:
                print(f"  {it[0]} | slug: {it[1]} | img: {it[2][:50]}...")
    except Exception as e:
        print(f"Page {page} error: {e}")
