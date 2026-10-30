import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 1. Tìm kiếm slug của Hậu Cung Như Ý Truyện
search_url = "https://phimapi.com/v1/api/tim-kiem?keyword=nhu-y-truyen&limit=10"
print("Đang tìm kiếm phim...")
slug = ""
try:
    req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=6) as r:
        res = json.loads(r.read().decode('utf-8'))
        items = res.get('data', {}).get('items', [])
        for item in items:
            print(f"- {item.get('name')} | Slug: {item.get('slug')}")
            if 'như ý' in item.get('name', '').lower() or 'nhu-y' in item.get('slug', ''):
                slug = item.get('slug')
                break
except Exception as e:
    print("Search err:", e)

if not slug:
    # Thử từ khóa khác
    search_url2 = "https://phimapi.com/v1/api/tim-kiem?keyword=hau-cung-nhu-y-truyen&limit=10"
    req = urllib.request.Request(search_url2, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=6) as r:
        res = json.loads(r.read().decode('utf-8'))
        items = res.get('data', {}).get('items', [])
        for item in items:
            print(f"- {item.get('name')} | Slug: {item.get('slug')}")
            slug = item.get('slug')
            break

print("\n--- Chi tiết phim với slug:", slug)
detail_url = f"https://phimapi.com/phim/{slug}"
try:
    req = urllib.request.Request(detail_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
        detail = json.loads(r.read().decode('utf-8'))
        episodes = detail.get('episodes', [])
        print(f"Số lượng server: {len(episodes)}")
        for s_idx, srv in enumerate(episodes):
            server_name = srv.get('server_name')
            server_data = srv.get('server_data', [])
            print(f"\nServer [{s_idx}]: {server_name} ({len(server_data)} tập)")
            # Tìm tập 40
            ep40 = next((ep for ep in server_data if ep.get('name') == '40' or '40' in ep.get('name')), None)
            if ep40:
                print(f"  Tập 40: name={ep40.get('name')}")
                print(f"  - link_embed: {ep40.get('link_embed')}")
                print(f"  - link_m3u8: {ep40.get('link_m3u8')}")
            else:
                print("  Không tìm thấy tập 40, 3 tập đầu:")
                for ep in server_data[:3]:
                    print(f"    Tập {ep.get('name')}: embed={ep.get('link_embed')} | m3u8={ep.get('link_m3u8')}")
except Exception as e:
    print("Detail err:", e)
