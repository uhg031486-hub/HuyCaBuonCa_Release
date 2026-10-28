import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

test_target = "http://88.212.15.50/live/test_hbo2_hd_hevc/playlist.m3u8"
proxy_url = f"https://huyca.pages.dev/api/proxy?url={urllib.parse.quote(test_target)}"

print(f"Testing Live Proxy: {proxy_url}...")
try:
    req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=8) as res:
        print(f"Status: {res.status}")
        print(f"CORS Header: {res.headers.get('Access-Control-Allow-Origin')}")
        content = res.read(600).decode('utf-8', errors='ignore')
        print("Content preview:\n", content[:300])
except Exception as e:
    print(f"Error testing live proxy: {e}")
