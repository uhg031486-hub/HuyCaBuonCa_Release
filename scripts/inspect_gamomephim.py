import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = 'https://gamomephim.com/the-loai/hien-dai'
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
        print(f"Page length: {len(html)}")
        
        # In một đoạn HTML mẫu quanh thẻ chứa phim
        matches = re.findall(r'<a[^>]+href="(/phim/[^"]+|/[^"/]+/[^"/]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
        print(f"Movie links: {len(matches)}")
        for m in matches[:10]:
            print("  Href:", m[0], "| Content:", re.sub(r'\s+', ' ', m[1])[:80])
            
        # Tìm các thẻ img
        imgs = re.findall(r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]*)"', html)
        print(f"Images: {len(imgs)}")
        for img in imgs[:8]:
            print("  Img:", img[0], "| Alt:", img[1])
except Exception as e:
    print(f"Error: {e}")
