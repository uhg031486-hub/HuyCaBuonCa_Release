import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec"

test_cases = [
    ("Direct / Empty origins", [], ""),
    ("phim.nguonc.com", ["https://phim.nguonc.com"], "https://phim.nguonc.com/"),
    ("huyca.pages.dev", ["https://huyca.pages.dev"], "https://huyca.pages.dev/"),
    ("null origin", ["null"], ""),
    ("localhost", ["http://localhost:3000"], "http://localhost:3000/"),
]

for name, origins, ref in test_cases:
    post_body = {
        "action": "bootstrap",
        "referrer": ref,
        "frame_origins": origins,
        "request_grant": True,
        "playlist_format": "hls",
        "pretty_url": True,
        "path_chunks": True,
        "bootstrap_format": "aesgcm-v1"
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': url if not ref else ref,
        'Origin': 'https://embed14.streamc.xyz',
        'Content-Type': 'application/json'
    }
    req = urllib.request.Request(url, data=json.dumps(post_body).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            print(f"[{name}] SUCCESS! Status: {resp.status}, Body length: {len(data)}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        print(f"[{name}] FAILED! Status: {e.code}, Reason: {e.reason}, Body: {err_body[:200]}")
    except Exception as e:
        print(f"[{name}] ERROR: {e}")
