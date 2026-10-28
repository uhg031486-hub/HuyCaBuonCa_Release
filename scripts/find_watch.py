import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = 'https://gamomephim.com/phim/ban-tinh-ca-nho-trong-anh-sang-le-loi'
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
        
        # Tìm tất cả link trong trang detail
        links = re.findall(r'href="([^"]+)"', html)
        watch_links = [l for l in links if 'xem' in l or 'tap' in l or 'play' in l or 'watch' in l]
        print("Watch links:", watch_links)
        
        # Tìm các chuỗi URL m3u8 hoặc stream hoặc cdn
        streams = re.findall(r'https?://[^\s"\'<>]+\.(?:m3u8|mp4)', html)
        print("Direct streams found:", streams)
        
        # Tìm các chunk next_f có chứa tập phim
        chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
        for c in chunks:
            if 'tap' in c.lower() or 'episode' in c.lower() or 'server' in c.lower():
                print("Chunk snippet:", c[:200])
except Exception as e:
    print(f"Error: {e}")
