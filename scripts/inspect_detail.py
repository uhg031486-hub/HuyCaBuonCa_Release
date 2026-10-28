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
        print(f"Detail page length: {len(html)}")
        
        # Tìm tiêu đề, poster, mô tả
        title = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        print("Title:", title.group(1) if title else "not found")
        
        # Tìm iframe hoặc video hoặc script chứa dữ liệu tập
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for s in scripts:
            if 'episode' in s.lower() or 'm3u8' in s.lower() or 'player' in s.lower() or 'props' in s.lower() or '__next' in s.lower():
                print("Found interesting script snippet:", s[:300])
                if len(s) > 300:
                    print("... tail:", s[-300:])
                    
        # Kiểm tra xem có __NEXT_DATA__ không (Next.js)
        next_data = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if next_data:
            print("FOUND __NEXT_DATA__! Length:", len(next_data.group(1)))
            import json
            j = json.loads(next_data.group(1))
            props = j.get('props', {}).get('pageProps', {})
            print("pageProps keys:", list(props.keys()))
            movie = props.get('movie') or props.get('film') or props.get('data') or props
            print("Sample data:", json.dumps(movie, ensure_ascii=False)[:500])
except Exception as e:
    print(f"Error: {e}")
