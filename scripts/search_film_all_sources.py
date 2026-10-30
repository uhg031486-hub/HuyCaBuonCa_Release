import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import ssl
import urllib.parse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

kw = "Hậu Cung Như Ý Truyện"
encoded = urllib.parse.quote(kw)

endpoints = [
    f"https://phimapi.com/v1/api/tim-kiem?keyword={encoded}",
    f"https://phim.nguonc.com/api/films/search?keyword={encoded}",
    f"https://ophim1.com/v1/api/tim-kiem?keyword={encoded}"
]

for ep in endpoints:
    try:
        req = urllib.request.Request(ep, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=6) as r:
            data = json.loads(r.read().decode('utf-8'))
            print(f"\n--- Endpoint: {ep} ---")
            items = data.get('data', {}).get('items', []) or data.get('items', [])
            print(f"Items count: {len(items)}")
            for it in items[:5]:
                print(f"- Name: {it.get('name')} | Slug: {it.get('slug')}")
    except Exception as e:
        print(f"Err {ep}: {e}")
