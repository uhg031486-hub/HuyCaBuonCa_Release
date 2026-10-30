import urllib.request
import json
import hashlib

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

print("--- 1. DIRECT TO FREEREELS API ---")
try:
    req = urllib.request.Request(f"{API_BASE}/anonymous/login", data=login_body, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as res:
        print("Direct status:", res.status)
        print("Direct body:", res.read().decode('utf-8'))
except Exception as e:
    print("Direct error:", e)

print("\n--- 2. VIA CLOUDFLARE PROXY ---")
try:
    proxy_url = "https://huyca.pages.dev/api/proxy?url=" + urllib.parse.quote(f"{API_BASE}/anonymous/login")
    req = urllib.request.Request(proxy_url, data=login_body, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as res:
        print("Proxy status:", res.status)
        print("Proxy body:", res.read().decode('utf-8'))
except Exception as e:
    print("Proxy error:", e)
