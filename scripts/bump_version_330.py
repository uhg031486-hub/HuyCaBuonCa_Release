import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

print("=== NÂNG CẤP ĐỒNG BỘ TOÀN DIỆN LÊN V3.3.0 (VERSION CODE 24) ===")

# 1. HuyCaBuonCa_Mobile
mobile_gradle = 'HuyCaBuonCa_Mobile/app/build.gradle.kts'
with open(mobile_gradle, 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 24', c)
c = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "3.3.0"', c)
with open(mobile_gradle, 'w', encoding='utf-8') as f:
    f.write(c)
print(f" -> Đã cập nhật {mobile_gradle}: versionCode=24, versionName=3.3.0")

# 2. HuyCaBuonCa_TV
tv_gradle = 'HuyCaBuonCa_TV/app/build.gradle.kts'
with open(tv_gradle, 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 24', c)
c = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "3.3.0"', c)
with open(tv_gradle, 'w', encoding='utf-8') as f:
    f.write(c)
print(f" -> Đã cập nhật {tv_gradle}: versionCode=24, versionName=3.3.0")

# 3. LG webOS appinfo.json
lg_appinfo = 'HuyCaBuonCa_LG_webOS/appinfo.json'
with open(lg_appinfo, 'r', encoding='utf-8') as f:
    data = json.load(f)
data['version'] = '3.3.0'
with open(lg_appinfo, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f" -> Đã cập nhật {lg_appinfo}: version=3.3.0")

# 4. HuyCa_Web index.html
web_html = 'HuyCa_Web/index.html'
with open(web_html, 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'v=\d+\.\d+(\.\d+)?', 'v=3.3.0', html)
html = html.replace('Phiên Bản Web Trực Tuyến v3.2.9', 'Phiên Bản Web Trực Tuyến v3.3.0')
html = html.replace('HuyCa_Mobile_v2.8.apk', 'HuyCa_Mobile_v3.3.0.apk')
html = html.replace('HuyCa_TV_v2.8.apk', 'HuyCa_TV_v3.3.0.apk')
html = html.replace('HuyCa_LG_webOS_v2.8.ipk', 'HuyCa_LG_webOS_v3.3.0.ipk')
html = html.replace('HuyCa_Windows_v2.8.zip', 'HuyCa_Windows_v3.3.0.zip')
with open(web_html, 'w', encoding='utf-8') as f:
    f.write(html)
print(f" -> Đã cập nhật {web_html}: v=3.3.0 và tên file download")

# 5. HuyCa_Web functions/api/download.js
dl_js = 'HuyCa_Web/functions/api/download.js'
with open(dl_js, 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'HuyCa_Mobile_v\d+\.\d+(\.\d+)?\.apk', 'HuyCa_Mobile_v3.3.0.apk', c)
c = re.sub(r'HuyCa_TV_v\d+\.\d+(\.\d+)?\.apk', 'HuyCa_TV_v3.3.0.apk', c)
c = re.sub(r'HuyCa_LG_webOS_v\d+\.\d+(\.\d+)?\.ipk', 'HuyCa_LG_webOS_v3.3.0.ipk', c)
c = re.sub(r'HuyCa_Windows_v\d+\.\d+(\.\d+)?\.zip', 'HuyCa_Windows_v3.3.0.zip', c)
c = c.replace('/v2.8/', '/v3.3.0/')
with open(dl_js, 'w', encoding='utf-8') as f:
    f.write(c)
print(f" -> Đã cập nhật {dl_js}: v3.3.0")

print("✅ Đã nâng cấp đồng bộ toàn hệ thống lên v3.3.0 thành công!")
