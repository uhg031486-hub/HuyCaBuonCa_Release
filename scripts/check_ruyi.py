import urllib.request, json, urllib.parse, sys
sys.stdout.reconfigure(encoding='utf-8')

for kw in ['ruyi', 'nhu-y', 'nhu y']:
    url = 'https://phimapi.com/v1/api/tim-kiem?keyword=' + urllib.parse.quote(kw)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read().decode('utf-8'))
            items = data.get('data', {}).get('items', [])
            print(f"=== Keyword: {kw} ({len(items)} items) ===")
            for it in items:
                print(f"  {it.get('name')} | {it.get('origin_name')} | slug: {it.get('slug')}")
    except Exception as e:
        print(f"Err {kw}: {e}")
