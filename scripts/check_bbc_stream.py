import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://s7771.cdn.mytvnet.vn/pkg20/live_dzones/bbcworldnews.smil/manifest.mpd',
    'https://s7771.cdn.mytvnet.vn/pkg20/live_dzones/bbcworldnews.smil/manifest.m3u8',
    'https://s7771.cdn.mytvnet.vn/pkg20/live_dzones/bbcworldnews.smil/playlist.m3u8',
    'https://s7771.cdn.mytvnet.vn/pkg20/live_dzones/bbcworldnews.smil/chunklist.m3u8'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=ctx, timeout=6) as r:
            content = r.read(1000)
            print(f"URL: {u}\nStatus: {r.status}\nContent-Type: {r.headers.get('Content-Type')}\nLength: {len(content)}")
            print("Content Preview:\n", content[:300].decode('utf-8', errors='ignore'))
            print("="*60)
    except Exception as e:
        print(f"URL: {u} -> ERROR: {e}\n" + "="*60)
