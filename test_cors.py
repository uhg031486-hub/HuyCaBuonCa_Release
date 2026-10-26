import urllib.request, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

url = "https://video-v81.mydramawave.com/vt/665a6635-3fda-47eb-9e2f-ca59dad9eff7/h264-3a965b6f-a94b-41fb-ac66-40c298bbbb51.m3u8"
req = urllib.request.Request(url, headers={
    'Origin': 'https://huyca.pages.dev',
    'User-Agent': 'Mozilla/5.0'
})

try:
    with urllib.request.urlopen(req) as resp:
        print("Status:", resp.status)
        print("CORS Header:", resp.headers.get('Access-Control-Allow-Origin'))
        print("All headers:", dict(resp.headers))
except Exception as e:
    print("Error:", e)
