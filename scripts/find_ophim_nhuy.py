import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Kiểm tra OPhim API mới nhất
urls = [
    "https://ophim1.com/danh-sach/phim-moi-cap-nhat?page=1",
    "https://ophim1.com/v1/api/tim-kiem?keyword=nhu%20y",
    "https://ophim1.com/v1/api/tim-kiem?keyword=nhu-y",
    "https://ophim1.com/v1/api/tim-kiem?keyword=hau%20cung"
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=6) as r:
            data = json.loads(r.read().decode('utf-8'))
            items = data.get('data', {}).get('items', []) or data.get('items', [])
            print(f"URL: {u} -> {len(items)} items")
            for it in items:
                name = it.get('name', '')
                if any(k in name.lower() for k in ['như ý', 'nhu y', 'hậu cung', 'ruyi']):
                    print(f"  FOUND: {name} (Slug: {it.get('slug')})")
    except Exception as e:
        print(f"Err {u}: {e}")
