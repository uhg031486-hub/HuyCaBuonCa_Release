import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import urllib.request
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

# Lọc tất cả các kênh thuộc nhóm Quốc Tế hoặc có tên quốc tế
intl_channels = [c for c in channels if c.get('group') == 'Quốc Tế' or any(kw in c.get('name', '').lower() for kw in ['bbc', 'cnn', 'bloomberg', 'discovery', 'hbo', 'cinemax', 'axn', 'cartoon', 'animal', 'fashion', 'nhk', 'kbs', 'arirang', 'dw', 'france', 'cgtn', 'rt', 'cna'])]

print(f"Tổng số kênh Quốc Tế tìm thấy: {len(intl_channels)}")

results = []
for idx, ch in enumerate(intl_channels):
    name = ch.get('name')
    url = ch.get('url', '')
    is_http = url.startswith('http://')
    status = 'UNKNOWN'
    err_msg = ''
    content_type = ''
    has_cors = False
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=ctx, timeout=6) as res:
            status = res.status
            content_type = res.headers.get('Content-Type', '')
            has_cors = res.headers.get('Access-Control-Allow-Origin') is not None
            data = res.read(400).decode('utf-8', errors='ignore')
            is_valid_m3u8 = '#EXTM3U' in data
            has_drm = 'SAMPLE-AES' in data or 'skd://' in data
    except Exception as e:
        status = 'ERROR'
        err_msg = str(e)
        is_valid_m3u8 = False
        has_drm = False

    result = {
        'id': ch.get('id'),
        'name': name,
        'url': url,
        'is_http': is_http,
        'status': status,
        'content_type': content_type,
        'has_cors': has_cors,
        'is_valid_m3u8': is_valid_m3u8,
        'has_drm': has_drm,
        'err_msg': err_msg
    }
    results.append(result)

    state_icon = "✅" if (status == 200 and is_valid_m3u8 and not has_drm) else "❌"
    mixed_warn = "⚠️ MIXED CONTENT (HTTP)" if is_http else ""
    cors_info = "CORS: OK" if has_cors else "NO CORS (Cần Proxy)"
    print(f"{state_icon} [{idx+1}/{len(intl_channels)}] {name}: Status={status} | {mixed_warn} | {cors_info} | URL: {url[:60]}... {f'Error: {err_msg}' if err_msg else ''}")

# Thống kê
ok_count = sum(1 for r in results if r['status'] == 200 and r['is_valid_m3u8'] and not r['has_drm'])
http_count = sum(1 for r in results if r['is_http'])
no_cors_count = sum(1 for r in results if not r['has_cors'])
error_count = sum(1 for r in results if r['status'] != 200 or not r['is_valid_m3u8'] or r['has_drm'])

print("\n" + "="*60)
print(f"TỔNG KẾT KÊNH QUỐC TẾ:")
print(f"- Tổng số kênh: {len(results)}")
print(f"- Kênh stream sống: {ok_count}/{len(results)}")
print(f"- Kênh dùng HTTP không an toàn (bị Mixed Content chặn trên HTTPS): {http_count}")
print(f"- Kênh thiếu CORS header (bị chặn trên trình duyệt nếu không qua proxy): {no_cors_count}")
print(f"- Kênh lỗi/chết/DRM: {error_count}")
print("="*60)

with open('scripts/intl_channels_status.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
