import sys
import requests
import json
import hashlib
import time

sys.stdout.reconfigure(encoding='utf-8')

API_BASE = "https://apiv2.free-reels.com/frv2-api"
APP_NAME = "com.freereels.app"
APP_VERSION = "2.6.0"
APP_SECRET = "8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv"
DEVICE_ID = "c74f5359a16f0e42"
SESSION_ID = "da1bc37b805ec6b1d120a116f1947b99"

def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def login():
    login_url = f"{API_BASE}/anonymous/login"
    login_body = {
        "device_id": DEVICE_ID,
        "session_id": SESSION_ID,
        "sign": md5(f"device_id={DEVICE_ID}&session_id={SESSION_ID}&key={APP_SECRET}")
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "app-name": APP_NAME,
        "app-version": APP_VERSION,
        "device": "android",
        "device-version": "33",
        "device-id": DEVICE_ID,
        "session-id": SESSION_ID,
        "language": "vi-VN",
        "country": "VN"
    }
    resp = requests.post(login_url, json=login_body, headers=headers, timeout=10)
    data = resp.json().get("data", {})
    return data.get("auth_key"), data.get("auth_secret")

def get_auth_headers(auth_key, auth_secret):
    ts = str(int(time.time() * 1000))
    sig = md5(f"{APP_SECRET}&{auth_secret}")
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "app-name": APP_NAME,
        "app-version": APP_VERSION,
        "device": "android",
        "device-version": "33",
        "device-id": DEVICE_ID,
        "session-id": SESSION_ID,
        "language": "vi-VN",
        "country": "VN",
        "Authorization": f"oauth_signature={sig},oauth_token={auth_key},ts={ts}"
    }

print("1. Đăng nhập FreeReels...")
auth_key, auth_secret = login()
print(" -> auth_key:", auth_key[:10] if auth_key else "None")
headers = get_auth_headers(auth_key, auth_secret)

print("\n2. Kiểm tra Tab Feed 503 (Hot)...")
feed_resp = requests.post(f"{API_BASE}/homepage/v2/tab/feed", json={"tab_key": "503", "module_key": "1036", "next": "offset=0&position_index=10000"}, headers=headers, timeout=10)
feed_data = feed_resp.json().get("data", {})
items = feed_data.get("items") or feed_data.get("list") or []
print(f" -> Nạp được {len(items)} items từ tab 503")

if items:
    first_item = items[0]
    series = first_item.get("series") or first_item.get("info") or first_item
    series_id = series.get("id") or series.get("key") or series.get("series_id")
    title = series.get("title") or series.get("name")
    print(f" -> Phim đầu tiên: ID={series_id}, Title={title}")

    print("\n3. Lấy chi tiết drama info_v2...")
    detail_url = f"{API_BASE}/drama/info_v2?series_id={series_id}&scene=search"
    detail_resp = requests.get(detail_url, headers=headers, timeout=10)
    detail_data = detail_resp.json().get("data", {})
    info = detail_data.get("info") if isinstance(detail_data.get("info"), dict) else detail_data
    ep_list = info.get("episode_list", [])
    print(f" -> Có {len(ep_list)} tập phim")

    if ep_list:
        ep0 = ep_list[0]
        ep_id = ep0.get("id") or ep0.get("key")
        print(f" -> Tập 1: ID={ep_id}, Name={ep0.get('name')}")
        print("    el keys:", list(ep0.keys()))
        print("    external_audio_h264_m3u8:", ep0.get("external_audio_h264_m3u8"))
        print("    m3u8_url:", ep0.get("m3u8_url"))
        print("    video_url:", ep0.get("video_url"))

        print("\n4. Gọi API unlock_episode...")
        unlock_url = f"{API_BASE}/drama/unlock_episode"
        unlock_body = {"series_id": series_id, "episode_id": ep_id, "lang": "vi"}
        unlock_resp = requests.post(unlock_url, json=unlock_body, headers=headers, timeout=10)
        print(" -> HTTP status:", unlock_resp.status_code)
        unlock_data = unlock_resp.json().get("data", {})
        print(" -> Unlock data keys:", list(unlock_data.keys()))
        m3u8_stream = unlock_data.get("external_audio_h264_m3u8") or unlock_data.get("m3u8_url") or unlock_data.get("video_url")
        print(f" -> Stream URL: {m3u8_stream[:80] if m3u8_stream else 'None'}...")

        if m3u8_stream:
            print("\n5. Thử tải stream m3u8...")
            test_m3u8 = requests.get(m3u8_stream, timeout=10)
            print(" -> M3u8 Status:", test_m3u8.status_code)
            print(" -> M3u8 Content preview:")
            for line in test_m3u8.text.split("\n")[:8]:
                print("   ", line)
