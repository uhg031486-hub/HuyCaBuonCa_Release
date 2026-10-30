import urllib.request
import json
import time
import hashlib
import hmac

APP_SECRET = "8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv"
APP_NAME = "com.freereels.app"
APP_VERSION = "2.2.81"
API_BASE = "https://apiv2.free-reels.com/frv2-api"

device_id = "test_dev_12345678"
timestamp = str(int(time.time()))

# Test login
body = json.dumps({
    "device_id": device_id,
    "system_name": "android",
    "system_version": "14",
    "app_version": APP_VERSION,
    "app_name": APP_NAME,
    "language": "vi",
    "country": "VN",
    "timezone": "Asia/Ho_Chi_Minh"
})

sign_str = f"body={body}&timestamp={timestamp}&key={APP_SECRET}"
sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

headers = {
    "User-Agent": "FreeReels/2.2.81 (Android 14; Mobile)",
    "Content-Type": "application/json",
    "X-App-Name": APP_NAME,
    "X-App-Version": APP_VERSION,
    "X-Device-Id": device_id,
    "X-Timestamp": timestamp,
    "X-Signature": sign
}

print("1. Testing login...")
req = urllib.request.Request(f"{API_BASE}/anonymous/login", data=body.encode('utf-8'), headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as res:
        login_data = json.loads(res.read().decode('utf-8'))
        print("Login response code:", login_data.get('code'))
        token = login_data.get('data', {}).get('token')
        secret = login_data.get('data', {}).get('secret')
        print("Token exists:", bool(token), "Secret exists:", bool(secret))
except Exception as e:
    print("Login error:", e)
    token, secret = None, None

# Test get feed
if token:
    print("\n2. Testing get feed...")
    ts = str(int(time.time()))
    sign_str = f"timestamp={ts}&token={token}&key={secret or APP_SECRET}"
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    feed_headers = {
        "User-Agent": "FreeReels/2.2.81 (Android 14; Mobile)",
        "X-App-Name": APP_NAME,
        "X-App-Version": APP_VERSION,
        "X-Device-Id": device_id,
        "X-Timestamp": ts,
        "X-Token": token,
        "X-Signature": sign
    }
    req = urllib.request.Request(f"{API_BASE}/foryou/feed", headers=feed_headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            feed_data = json.loads(res.read().decode('utf-8'))
            print("Feed response code:", feed_data.get('code'))
            items = feed_data.get('data', {}).get('items', [])
            print("Feed items count:", len(items))
            if items:
                first = items[0]
                s = first.get('series') or first.get('info') or first
                print("First series:", s.get('id'), s.get('title'))
    except Exception as e:
        print("Feed error:", e)
