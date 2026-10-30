import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Let's test what embed.php returns when format is hls!
url = "https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec"
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Referer': 'https://phim.nguonc.com/',
    'Origin': 'https://embed14.streamc.xyz',
    'Content-Type': 'application/json'
}

# 1. First fetch HTML to get bootstrap
req = urllib.request.Request(url, headers={'User-Agent': headers['User-Agent'], 'Referer': 'https://phim.nguonc.com/'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Extract bootstrap JSON
import re
m = re.search(r'<script id="stream-bootstrap" type="application/json">(.*?)</script>', html)
if m:
    bootstrap_data = json.loads(m.group(1))
    print("Bootstrap keys:", list(bootstrap_data.keys()))
    
    # 2. Make POST bootstrap request with playlist_format: "hls"
    post_body = {
        "action": "bootstrap",
        "referrer": "https://phim.nguonc.com/",
        "frame_origins": ["https://phim.nguonc.com"],
        "request_grant": True,
        "playlist_format": "hls",
        "pretty_url": True,
        "path_chunks": True,
        "bootstrap_format": "aesgcm-v1"
    }
    
    req_post = urllib.request.Request(url, data=json.dumps(post_body).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req_post) as resp_post:
            resp_data = json.loads(resp_post.read().decode())
            print("POST response format:", resp_data.get('format'))
            print("POST response keys:", list(resp_data.keys()))
    except Exception as e:
        print("POST error:", e)
else:
    print("Could not find stream-bootstrap")
