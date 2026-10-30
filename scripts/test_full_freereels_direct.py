import urllib.request
import json
import hashlib
import time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

APP_SECRET = "8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv"
APP_NAME = "com.freereels.app"
APP_VERSION = "2.2.81"
API_BASE = "https://apiv2.free-reels.com/frv2-api"

deviceId = "fr_test_123456"
sessionId = "sess_test_123456"
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
    print("Login OK:", auth_key[:10])

# Now test buildAuthorizedRequest for feed
ts = str(int(time.time() * 1000))
sig = hashlib.md5(f"{APP_SECRET}&{auth_secret}".encode('utf-8')).hexdigest()
auth_header = f"oauth_signature={sig},oauth_token={auth_key},ts={ts}"

auth_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0',
    'app-name': APP_NAME,
    'app-version': APP_VERSION,
    'device': 'android',
    'device-version': '33',
    'device-id': deviceId,
    'session-id': sessionId,
    'language': 'vi-VN',
    'country': 'VN',
    'Authorization': auth_header
}

print("\n--- Testing Feed ---")
feed_url = f"{API_BASE}/foryou/feed"
req = urllib.request.Request(feed_url, headers=auth_headers)
with urllib.request.urlopen(req, timeout=10) as res:
    feed_data = json.loads(res.read().decode('utf-8'))
    print("Feed code:", feed_data.get('code'))
    items = feed_data.get('data', {}).get('items', [])
    print("Feed items:", len(items))
    if items:
        first = items[0]
        s = first.get('series') or first.get('info') or first
        series_id = s.get('id') or s.get('key')
        title = s.get('name') or s.get('title')
        print(f"First series: {series_id} - {title}")

        # Test Drama Detail
        print("\n--- Testing Drama Detail ---")
        detail_url = f"{API_BASE}/drama/info_v2?series_id={series_id}&scene=search"
        req = urllib.request.Request(detail_url, headers=auth_headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            det_data = json.loads(res.read().decode('utf-8'))
            print("Detail code:", det_data.get('code'))
            info = det_data.get('data', {}).get('info', {})
            ep_list = info.get('episode_list', [])
            print("Episodes:", len(ep_list))

            if ep_list:
                ep1 = ep_list[0]
                ep1_id = ep1.get('id') or ep1.get('key')
                print(f"Ep 1 ID: {ep1_id}")

                # Test Unlock Episode
                print("\n--- Testing Unlock Episode 1 ---")
                unlock_url = f"{API_BASE}/drama/unlock_episode"
                unlock_body = json.dumps({
                    "series_id": series_id,
                    "episode_id": ep1_id,
                    "lang": "vi"
                }).encode('utf-8')
                req = urllib.request.Request(unlock_url, data=unlock_body, headers=auth_headers)
                with urllib.request.urlopen(req, timeout=10) as res:
                    unl_data = json.loads(res.read().decode('utf-8'))
                    print("Unlock code:", unl_data.get('code'))
                    data = unl_data.get('data', {})
                    video_url = data.get('video_url')
                    m3u8_url = data.get('m3u8_url')
                    m3u8_h264 = data.get('external_audio_h264_m3u8')
                    print(f"Video URL: {video_url[:60] if video_url else 'None'}")
                    print(f"M3U8 URL: {m3u8_url[:60] if m3u8_url else 'None'}")
                    print(f"M3U8 H264: {m3u8_h264[:60] if m3u8_h264 else 'None'}")
