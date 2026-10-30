import urllib.request
import json
import hashlib
import time

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

unlock_url = f"{API_BASE}/drama/unlock_episode"
unlock_body = json.dumps({
    "series_id": "ioey9aqQ6L",
    "episode_id": "XZ5nOZ43jc",
    "lang": "vi"
}).encode('utf-8')
req = urllib.request.Request(unlock_url, data=unlock_body, headers=auth_headers)
with urllib.request.urlopen(req, timeout=10) as res:
    unl_data = json.loads(res.read().decode('utf-8'))
    m3u8_url = unl_data['data']['external_audio_h264_m3u8']
    print("M3U8 Stream URL:", m3u8_url)

# Now test fetching this m3u8 stream without headers (like ExoPlayer default)
print("\nTesting fetching M3U8 with default User-Agent...")
req = urllib.request.Request(m3u8_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
try:
    with urllib.request.urlopen(req, timeout=10) as res:
        print("M3U8 fetch status:", res.status)
        content = res.read().decode('utf-8')
        print("M3U8 preview:\n", content[:200])
        # Check first ts segment
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
        if lines:
            seg_url = lines[0]
            if not seg_url.startswith('http'):
                import urllib.parse
                seg_url = urllib.parse.urljoin(m3u8_url, seg_url)
            print("First segment URL:", seg_url[:80])
            req_seg = urllib.request.Request(seg_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_seg, timeout=10) as s_res:
                print("Segment status:", s_res.status, "Length:", len(s_res.read()))
except Exception as e:
    print("M3U8 fetch ERROR:", e)
