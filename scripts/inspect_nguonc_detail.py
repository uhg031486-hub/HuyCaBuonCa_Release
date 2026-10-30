import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://phim.nguonc.com/api/film/hau-cung-nhu-y-truyen"
print(f"Fetching {url}...")

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
    data = json.loads(r.read().decode('utf-8'))
    movie = data.get('movie', {})
    episodes = movie.get('episodes', [])
    print(f"Movie: {movie.get('name')} | Total servers: {len(episodes)}")
    for s_idx, srv in enumerate(episodes):
        srv_name = srv.get('server_name')
        items = srv.get('items', [])
        print(f"\nServer [{s_idx}] {srv_name}: {len(items)} tập")
        # Tìm tập 40
        ep40 = next((it for it in items if it.get('name') == '40' or '40' in it.get('name')), None)
        if ep40:
            print(f"  Tập {ep40.get('name')}:")
            print(f"   - embed: {ep40.get('embed')}")
            print(f"   - m3u8: {ep40.get('m3u8')}")
        else:
            for it in items[:3]:
                print(f"   Tập {it.get('name')}: embed={it.get('embed')} | m3u8={it.get('m3u8')}")
