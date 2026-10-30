import urllib.request
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

hash_code = "6d8dbf7d53b9867fd9987659c2c9a09f"
mirrors = [
    "embed1.streamc.xyz",
    "embed2.streamc.xyz",
    "embed3.streamc.xyz",
    "embed4.streamc.xyz",
    "embed5.streamc.xyz",
    "embed6.streamc.xyz",
    "embed10.streamc.xyz",
    "embed11.streamc.xyz",
    "embed12.streamc.xyz",
    "embed13.streamc.xyz",
    "embed14.streamc.xyz",
    "embed15.streamc.xyz",
    "embed16.streamc.xyz",
    "embed17.streamc.xyz",
    "embed18.streamc.xyz",
]

for m in mirrors:
    url = f"https://{m}/embed.php?hash={hash_code}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://phim.nguonc.com/'
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=4) as r:
            body = r.read().decode('utf-8', errors='ignore')
            is_cf = "Attention Required! | Cloudflare" in body or "Sorry, you have been blocked" in body
            print(f"[{m}] Status: {r.status}, Cloudflare Block: {is_cf}, Body size: {len(body)}")
    except urllib.error.HTTPError as e:
        print(f"[{m}] HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"[{m}] Error: {e}")
