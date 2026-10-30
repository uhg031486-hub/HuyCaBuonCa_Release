import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

print("=== NÂNG CẤP PHIÊN BẢN HỆ THỐNG LÊN V3.2.9 (VERSION CODE 23) ===")

# 1. HuyCaBuonCa_Mobile
mobile_gradle = 'HuyCaBuonCa_Mobile/app/build.gradle.kts'
with open(mobile_gradle, 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 23', c)
c = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "3.2.9"', c)
with open(mobile_gradle, 'w', encoding='utf-8') as f:
    f.write(c)
print(f" -> Đã cập nhật {mobile_gradle}: versionCode=23, versionName=3.2.9")

# 2. HuyCaBuonCa_TV
tv_gradle = 'HuyCaBuonCa_TV/app/build.gradle.kts'
with open(tv_gradle, 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 23', c)
c = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "3.2.9"', c)
with open(tv_gradle, 'w', encoding='utf-8') as f:
    f.write(c)
print(f" -> Đã cập nhật {tv_gradle}: versionCode=23, versionName=3.2.9")

# 3. LG webOS appinfo.json
lg_appinfo = 'HuyCaBuonCa_LG_webOS/appinfo.json'
with open(lg_appinfo, 'r', encoding='utf-8') as f:
    data = json.load(f)
data['version'] = '3.2.9'
with open(lg_appinfo, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f" -> Đã cập nhật {lg_appinfo}: version=3.2.9")

# 4. HuyCa_Web index.html
web_html = 'HuyCa_Web/index.html'
with open(web_html, 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'v=\d+\.\d+(\.\d+)?', 'v=3.2.9', html)
html = html.replace('Phiên Bản Web Trực Tuyến v3.2.8', 'Phiên Bản Web Trực Tuyến v3.2.9')
html = html.replace('Phiên Bản Web Trực Tuyến v2.8', 'Phiên Bản Web Trực Tuyến v3.2.9')
with open(web_html, 'w', encoding='utf-8') as f:
    f.write(html)
print(f" -> Đã cập nhật {web_html}: v=3.2.9")

print("✅ Đã nâng cấp đồng bộ phiên bản v3.2.9 thành công trên toàn bộ hệ thống!")
