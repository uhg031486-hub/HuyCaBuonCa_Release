import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    ('NHK World Japan', 'https://nhkwlive-ojp.akamaized.net/hls/live/2003459/nhkwlive-ojp-en/index.m3u8'),
    ('Al Jazeera English HD', 'https://aljazeera-eng-hd-live.akamaized.net/hls/live/2003890/aljazeera_en/index.m3u8'),
    ('Anime All Day HD', 'https://d2e1asnsl7br7b.cloudfront.net/7782/master.m3u8'),
    ('Euronews English', 'https://euronews-euronews-world-1-au.samsung.wurl.tv/playlist.m3u8')
]

for name, u in candidates:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=4) as r:
            cors = r.headers.get('Access-Control-Allow-Origin') is not None
            c = r.read(300).decode('utf-8', errors='ignore')
            if '#EXTM3U' in c and cors:
                print(f"✅ PASS: {name} (CORS: {cors}) -> {u}")
            else:
                print(f"⚠️ {name}: no cors or not m3u8")
    except Exception as e:
        print(f"❌ {name}: {e}")
