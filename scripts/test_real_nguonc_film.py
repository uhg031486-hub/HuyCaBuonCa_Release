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
print(f"Tổng số phim mới: {len(items)}")

sample = items[0]
slug = sample['slug']
print(f"Lấy chi tiết phim: {sample['name']} (slug: {slug})")

det_url = f"https://phim.nguonc.com/api/film/{slug}"
req_d = urllib.request.Request(det_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req_d, timeout=5) as r:
    det = json.load(r)

m = det.get('movie', {})
episodes = m.get('episodes', [])
print(f"Số server/nhóm tập: {len(episodes)}")

first_group = episodes[0]
items_list = first_group.get('items', [])
print(f"Số tập trong nhóm 1: {len(items_list)}")

if items_list:
    ep1 = items_list[0]
    print(f"Tập 1 name: {ep1.get('name')}")
    print(f"Tập 1 embed: {ep1.get('embed')}")
    print(f"Tập 1 m3u8: {ep1.get('m3u8')}")
    
    embed_url = ep1.get('embed')
    if embed_url:
        proxy_url = f"https://huyca.pages.dev/api/nguonc_stream?url={urllib.parse.quote(embed_url)}"
        print(f"\nGọi proxy giải mã trên Cloudflare Pages: {proxy_url}")
        try:
            req_p = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req_p, timeout=10) as resp:
                print(f"✅ KẾT QUẢ HTTP: {resp.status}")
                print("Header:", resp.headers.get('Content-Type'))
                body = resp.read().decode('utf-8', errors='ignore')
                print("Body preview:\n", body[:400])
        except urllib.error.HTTPError as e:
            print(f"❌ LỖI HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"❌ LỖI: {e}")
