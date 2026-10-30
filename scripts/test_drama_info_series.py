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

series_id = "ATvrUStvBQ"
url = f"{API_BASE}/drama/info_v2?series_id={series_id}&scene=search"
req = urllib.request.Request(url, headers=auth_headers)
with urllib.request.urlopen(req, timeout=10) as res:
    d = json.loads(res.read().decode('utf-8'))
    print("Drama detail code:", d.get('code'))
    print("Drama detail message:", d.get('message'))
    print("Drama info exists:", 'info' in d.get('data', {}))
    print("Drama episode_list exists:", 'episode_list' in d.get('data', {}).get('info', {}))
    print("Episode count in list:", len(d.get('data', {}).get('info', {}).get('episode_list', [])))
