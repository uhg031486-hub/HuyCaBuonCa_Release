import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
url = 'https://gamomephim.com/ban-tinh-ca-nho-trong-anh-sang-le-loi'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    html = r.read().decode('utf-8', errors='ignore')
    print("Watch page length:", len(html))
    
    # Tìm m3u8 hoặc mp4 hoặc iframe player
    m3u8s = re.findall(r'https?://[^\s"\'<>]+\.(?:m3u8|mp4)[^\s"\'<>]*', html)
    print("Direct streams:", m3u8s)
    
    # Tìm iframe
    iframes = re.findall(r'<iframe[^>]+src="([^"]+)"', html)
    print("Iframes:", iframes)
    
    # Tìm Next data hoặc script player
    for s in re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL):
        if 'm3u8' in s or 'player' in s or 'video' in s or 'episode' in s:
            print("Player script snippet:", s[:300])
