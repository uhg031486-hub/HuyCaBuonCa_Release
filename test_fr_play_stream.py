import urllib.request, json, hashlib, time, sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE = "https://apiv2.free-reels.com/frv2-api"
APP_SECRET = "8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv"
APP_NAME = "com.freereels.app"
APP_VERSION = "2.2.81"
deviceId = "dev_verify_99"
sessionId = "sess_verify_99"

sign = hashlib.md5((APP_SECRET + deviceId).encode('utf-8')).hexdigest()
login_data = json.dumps({"device_id": deviceId, "device_name": "samsung SM-A536E", "sign": sign}).encode('utf-8')

req = urllib.request.Request(f"{API_BASE}/anonymous/login", data=login_data, headers={
    "Accept": "application/json", "Content-Type": "application/json",
    "app-name": APP_NAME, "app-version": APP_VERSION, "device": "android"
})
res_json = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
oauthToken = res_json['data']['auth_key']
oauthSecret = res_json['data']['auth_secret']

def make_req(url, body=None):
    ts = str(int(time.time() * 1000))
    sig = hashlib.md5(f"{APP_SECRET}&{oauthSecret}".encode('utf-8')).hexdigest()
    authHeader = f"oauth_signature={sig},oauth_token={oauthToken},ts={ts}"
    data = json.dumps(body).encode('utf-8') if body else None
    return urllib.request.Request(url, data=data, headers={
        "Accept": "application/json", "Content-Type": "application/json",
        "app-name": APP_NAME, "app-version": APP_VERSION, "device": "android",
        "device-version": "33", "device-id": deviceId, "session-id": sessionId,
        "language": "vi-VN", "country": "VN", "Authorization": authHeader
    })

# 1. Search 'tổng tài'
b1 = {"keyword": "tổng tài", "next": ""}
r1 = json.loads(urllib.request.urlopen(make_req(f"{API_BASE}/search/drama", b1)).read().decode('utf-8'))
items = r1.get('data', {}).get('items', [])
print(f"Search results: {len(items)} items")
if items:
    m = items[0]
    series_id = m.get('id')
    print(f"First series: {m.get('name')}, ID: {series_id}")

    # 2. Get Drama Detail
    det_url = f"{API_BASE}/drama/info_v2?series_id={series_id}&scene=search"
    r_det = json.loads(urllib.request.urlopen(make_req(det_url)).read().decode('utf-8'))
    print("Detail code:", r_det.get('code'))
    d_info = r_det.get('data', {}).get('info', {})
    ep_list = d_info.get('episode_list', [])
    print(f"Episodes count in detail: {len(ep_list)}")
    if ep_list:
        ep0 = ep_list[0]
        ep_id = ep0.get('id') or ep0.get('key')
        print(f"First Ep: {ep0.get('name')}, ID: {ep_id}")

        # 3. Unlock Episode
        unl_body = {"series_id": series_id, "episode_id": ep_id, "lang": "vi"}
        r_unl = json.loads(urllib.request.urlopen(make_req(f"{API_BASE}/drama/unlock_episode", unl_body)).read().decode('utf-8'))
        print("Unlock code:", r_unl.get('code'), r_unl.get('message'))
        unl_data = r_unl.get('data', {})
        print("Unlock stream keys:", list(unl_data.keys()))
        stream_url = unl_data.get('external_audio_h264_m3u8') or unl_data.get('m3u8_url') or unl_data.get('video_url')
        print(f"Stream URL: {stream_url}")

        # 4. Check if stream URL is accessible and what content-type it returns
        if stream_url:
            s_head = urllib.request.Request(stream_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(s_head) as s_resp:
                print("Stream HTTP Status:", s_resp.status)
                print("Stream Content-Type:", s_resp.headers.get('Content-Type'))
                print("Stream first 100 bytes:", s_resp.read(100))
