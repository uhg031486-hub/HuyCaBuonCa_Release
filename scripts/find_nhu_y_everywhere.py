import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import ssl
import urllib.parse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

search_terms = ['nhu-y', 'nhu y', 'như ý', 'ruyi', 'hau cung', 'hậu cung']

for term in search_terms:
    url = f"https://phimapi.com/v1/api/tim-kiem?keyword={urllib.parse.quote(term)}&limit=20"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as r:
            data = json.loads(r.read().decode('utf-8'))
            items = data.get('data', {}).get('items', [])
            print(f"Term '{term}': {len(items)} results")
            for it in items:
                if 'như ý' in it.get('name', '').lower() or 'nhu y' in it.get('name', '').lower() or 'cung' in it.get('name', '').lower():
                    print(f"  -> Found: {it.get('name')} | Slug: {it.get('slug')}")
    except Exception as e:
        print(f"Err {term}: {e}")

# Thử tìm trên OPhim API: https://ophim1.com/danh-sach/phim-moi-cap-nhat
# Hoặc api kkphim: https://phimapi.com/phim/{slug}
test_slugs = ['hau-cung-nhu-y-truyen', 'nhu-y-truyen', 'ruyis-royal-love-in-the-palace']
for sl in test_slugs:
    try:
        req = urllib.request.Request(f"https://phimapi.com/phim/{sl}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as r:
            d = json.loads(r.read().decode('utf-8'))
            if d.get('status') or d.get('movie'):
                print(f"✅ PhimAPI có slug '{sl}': {d.get('movie', {}).get('name')}")
    except Exception as e:
        # print(f"Slug {sl} err: {e}")
        pass
