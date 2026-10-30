import urllib.request, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for u in ['https://gamomephim.com/anh-ay-tham-tinh-xam-nhap', 'https://gamomephim.com/phim/anh-ay-tham-tinh-xam-nhap']:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode('utf-8')
            print(f"URL: {u} -> Status: {res.status}, Len: {len(html)}")
            has_video = 'https://r2.gamomephim.com/videos/' in html
            print(f"  Has video stream: {has_video}")
    except Exception as e:
        print(f"URL: {u} -> Error: {e}")
