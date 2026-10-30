import sys
import urllib.request
import json
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

api_url = "https://phim.nguonc.com/api/films/phim-moi-cap-nhat?page=1"
req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5) as r:
    data = json.load(r)

items = data.get('items', [])
found_ep = None
for item in items:
    slug = item['slug']
    det_url = f"https://phim.nguonc.com/api/film/{slug}"
    try:
        req_d = urllib.request.Request(det_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_d, timeout=3) as r:
            det = json.load(r)
            episodes = det.get('movie', {}).get('episodes', [])
            for ep_group in episodes:
                s_data = ep_group.get('server_data', [])
                if s_data and s_data[0].get('link_embed'):
                    found_ep = {
                        'title': item['name'],
                        'slug': slug,
                        'ep_name': s_data[0].get('name'),
                        'link_embed': s_data[0].get('link_embed'),
                        'link_m3u8': s_data[0].get('link_m3u8')
                    }
                    break
        if found_ep:
            break
    except:
        pass

if not found_ep:
    print("Không tìm thấy phim có tập")
    sys.exit(1)

print(f"Phim: {found_ep['title']} - Tập: {found_ep['ep_name']}")
print(f" -> link_embed: {found_ep['link_embed']}")
print(f" -> link_m3u8: {found_ep['link_m3u8']}")

embed_url = found_ep['link_embed']
proxy_url = f"https://huyca.pages.dev/api/nguonc_stream?url={urllib.parse.quote(embed_url)}"
print(f"\nGọi proxy giải mã: {proxy_url}")
try:
    req_p = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_p, timeout=10) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print(f"✅ THÀNH CÔNG (HTTP {resp.status}):")
        print(content[:300])
except urllib.error.HTTPError as e:
    print(f"❌ LỖI HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')}")
except Exception as e:
    print(f"❌ LỖI: {e}")
