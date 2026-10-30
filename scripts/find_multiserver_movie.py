import urllib.request
import json
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for page in [1, 2, 3]:
    url = f"https://phimapi.com/danh-sach/phim-moi-cap-nhat?page={page}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        for item in data.get('items', []):
            slug = item.get('slug')
            name = item.get('name')
            detail_url = f"https://phimapi.com/phim/{slug}"
            try:
                with urllib.request.urlopen(urllib.request.Request(detail_url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=5) as dresp:
                    ddata = json.loads(dresp.read().decode('utf-8'))
                    ep_servers = ddata.get('episodes', [])
                    if len(ep_servers) >= 2:
                        print(f"FOUND MULTI-SERVER MOVIE: [{name}] (slug: {slug})")
                        for s in ep_servers:
                            print(f"   -> Server: '{s.get('server_name')}', tập: {len(s.get('server_data', []))}")
                        sys.exit(0)
            except Exception:
                pass
    except Exception as e:
        print("Error fetching list:", e)
