import urllib.request
import json
import hashlib
import time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== KIỂM TRA CHI TIẾT TẤT CẢ 7 NGUỒN PHIM NGẮN ===")

APP_SECRET = "8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv"
APP_NAME = "com.freereels.app"
APP_VERSION = "2.2.81"
API_BASE = "https://apiv2.free-reels.com/frv2-api"

deviceId = "fr_test_debug_1"
sessionId = "sess_debug_1"
sign = hashlib.md5((APP_SECRET + deviceId).encode('utf-8')).hexdigest()

login_body = json.dumps({
    "device_id": deviceId,
    "device_name": "samsung SM-A536E",
    "sign": sign
}).encode('utf-8')

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'app-name': APP_NAME,
    'app-version': APP_VERSION,
    'device': 'android',
    'device-version': '33',
    'device-id': deviceId,
    'session-id': sessionId,
    'language': 'vi-VN',
    'country': 'VN'
}

req = urllib.request.Request(f"{API_BASE}/anonymous/login", data=login_body, headers=headers)
with urllib.request.urlopen(req, timeout=10) as res:
    login_data = json.loads(res.read().decode('utf-8'))
    auth_key = login_data['data']['auth_key']
    auth_secret = login_data['data']['auth_secret']

ts = str(int(time.time() * 1000))
sig = hashlib.md5(f"{APP_SECRET}&{auth_secret}".encode('utf-8')).hexdigest()
auth_header = f"oauth_signature={sig},oauth_token={auth_key},ts={ts}"
auth_headers = headers.copy()
auth_headers['Authorization'] = auth_header
auth_headers['User-Agent'] = 'Mozilla/5.0'

# Test 7 sub-sources:
# 1. ReelShort (keyword: "người sói")
# 2. DramaBox (keyword: "tổng tài")
# 3. ShortMax (keyword: "cao thủ")
# 4. FreeReels Gốc (tab 503 / 504 / 505)
# 5. Gà Mờ Mê Phim (gamomephim)
# 6. AI Cinema (tab 547)
# 7. GoodShort (keyword: "cưng chiều")

def test_freereels_kw(source_name, kw):
    print(f"\n--- Testing [{source_name}] with keyword: '{kw}' ---")
    url = f"{API_BASE}/search/drama"
    body = json.dumps({"keyword": kw, "page_size": 10, "next": ""}).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=auth_headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8')).get('data', {})
            items = data.get('items') or data.get('list') or []
            print(f" -> Tìm kiếm ra {len(items)} items")
            if items:
                s = items[0].get('series') or items[0].get('info') or items[0]
                sid = s.get('id') or s.get('key')
                name = s.get('name') or s.get('title')
                print(f" -> Phim 1: ID={sid}, Name='{name}'")
                test_detail_and_unlock(sid)
            else:
                print(" -> Search rỗng, test fallback feed...")
    except Exception as e:
        print(" -> Error:", e)

def test_freereels_tab(source_name, tab_key, module_key):
    print(f"\n--- Testing [{source_name}] with tab: {tab_key} ---")
    url = f"{API_BASE}/homepage/v2/tab/feed"
    body = json.dumps({"tab_key": tab_key, "module_key": module_key, "next": "offset=0&position_index=10000"}).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=auth_headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8')).get('data', {})
            items = data.get('items') or data.get('list') or []
            print(f" -> Tab Feed ra {len(items)} items")
            if items:
                s = items[0].get('series') or items[0].get('info') or items[0]
                sid = s.get('id') or s.get('key')
                name = s.get('name') or s.get('title')
                print(f" -> Phim 1: ID={sid}, Name='{name}'")
                test_detail_and_unlock(sid)
    except Exception as e:
        print(" -> Error:", e)

def test_detail_and_unlock(series_id):
    det_url = f"{API_BASE}/drama/info_v2?series_id={series_id}&scene=search"
    req = urllib.request.Request(det_url, headers=auth_headers)
    with urllib.request.urlopen(req, timeout=10) as res:
        det_data = json.loads(res.read().decode('utf-8'))
        info = det_data.get('data', {}).get('info') or det_data.get('data', {})
        eps = info.get('episode_list', [])
        print(f"    * Chi tiết phim: {len(eps)} tập")
        if eps:
            ep1 = eps[0]
            epid = ep1.get('id') or ep1.get('key')
            unl_url = f"{API_BASE}/drama/unlock_episode"
            unl_body = json.dumps({"series_id": series_id, "episode_id": epid, "lang": "vi"}).encode('utf-8')
            req2 = urllib.request.Request(unl_url, data=unl_body, headers=auth_headers)
            with urllib.request.urlopen(req2, timeout=10) as res2:
                unl_data = json.loads(res2.read().decode('utf-8')).get('data', {})
                stream = unl_data.get('external_audio_h264_m3u8') or unl_data.get('m3u8_url') or unl_data.get('video_url')
                subs = unl_data.get('subtitle_list', [])
                sub_count = len(subs) if isinstance(subs, list) else 0
                print(f"    * Mở khóa Tập 1: Stream={'Có m3u8 (' + stream[:45] + '...)' if stream else 'KHÔNG CÓ'}")
                print(f"    * Phụ đề: {sub_count} track phụ đề")
                if stream:
                    # Kiểm tra HEAD / GET m3u8
                    m_req = urllib.request.Request(stream, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(m_req, timeout=10) as m_res:
                        print(f"    * Stream Status: {m_res.status} OK (Content-Type: {m_res.headers.get('content-type')})")

def test_gamomephim():
    print(f"\n--- Testing [Nguồn Gà Mờ Mê Phim] ---")
    url = "https://gamomephim.com/phim-moi"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode('utf-8', errors='ignore')
            import re
            links = re.findall(r'href=["\'](/[^"\'\s]+)["\']', html)
            film_links = [l for l in links if not any(x in l for x in ['the-loai', 'phim-moi', 'ban-xep-hang', 'css', 'js', 'icon', 'login', 'register'])]
            film_links = list(dict.fromkeys(film_links))[:3]
            print(f" -> Tìm thấy {len(film_links)} phim Gà Mờ Mê Phim:")
            for fl in film_links:
                detail_url = f"https://gamomephim.com{fl}"
                req2 = urllib.request.Request(detail_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req2, timeout=10) as res2:
                    d_html = res2.read().decode('utf-8', errors='ignore')
                    streams = re.findall(r'https://r2\.gamomephim\.com/videos/[^\s"\'<>]+\.mp4', d_html)
                    print(f"    * Phim: {fl} -> Streams MP4: {len(streams)}")
                    if streams:
                        print(f"      Stream 1: {streams[0]}")
    except Exception as e:
        print(" -> Gà Mờ Mê Phim Error:", e)

# 1. ReelShort
test_freereels_kw("1. ReelShort", "người sói")
# 2. DramaBox
test_freereels_kw("2. DramaBox", "tổng tài")
# 3. ShortMax
test_freereels_kw("3. ShortMax", "cao thủ")
# 4. FreeReels Gốc (tab 503)
test_freereels_tab("4. FreeReels Gốc", "503", "1036")
# 5. Gà Mờ Mê Phim
test_gamomephim()
# 6. AI Cinema (tab 547)
test_freereels_tab("6. AI Cinema", "547", "2204")
# 7. GoodShort
test_freereels_kw("7. GoodShort", "cưng chiều")
