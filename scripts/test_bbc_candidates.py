import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    'http://103.151.60.162:2122/play/a0fl/index.m3u8?hls',
    'https://mumbai-edge.smartplaytv.in/BBCNews/index.m3u8',
    'https://tvsen1.aynaott.com/shn6jGTk/index.m3u8',
    'https://stream8.cinerama.uz/1251/tracks-v1a1/mono.m3u8',
    'https://nord.ayakkabiparti.lol/bbc/index.m3u8',
    'http://45.14.84.37/bbc4/index.m3u8',
    'https://i.mjh.nz/au/Sydney/tv.m3u8'
]

for url in candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=ctx, timeout=4) as res:
            data = res.read(1000)
            print(f"OK ({res.status}): {url} - {res.headers.get('Content-Type')}")
            print(data[:200].decode('utf-8', errors='ignore'))
            print("-" * 50)
    except Exception as e:
        print(f"FAILED: {url} -> {e}")
