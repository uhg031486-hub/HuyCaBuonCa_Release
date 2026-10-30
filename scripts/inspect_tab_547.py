import urllib.request
import json
import hashlib
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

APP_SECRET = "8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv"
APP_NAME = "com.freereels.app"
APP_VERSION = "2.2.81"
API_BASE = "https://apiv2.free-reels.com/frv2-api"

deviceId = "fr_test_ai_cinema"
sessionId = "sess_ai_cinema"
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

url = f"{API_BASE}/homepage/v2/tab/feed"
body = json.dumps({"tab_key": "547", "module_key": "2204", "next": "offset=0&position_index=10005"}).encode('utf-8')
req = urllib.request.Request(url, data=body, headers=auth_headers)
with urllib.request.urlopen(req, timeout=10) as res:
    data = json.loads(res.read().decode('utf-8')).get('data', {})
    items = data.get('items') or data.get('list') or []
    print("Tab 547 items count:", len(items))
    for i, it in enumerate(items):
        series = it.get('series') or it.get('info') or it
        sid = series.get('id') or series.get('key') or series.get('series_id')
        name = series.get('title') or series.get('name')
        print(f" Item {i}: ID='{sid}', Title='{name}'")
