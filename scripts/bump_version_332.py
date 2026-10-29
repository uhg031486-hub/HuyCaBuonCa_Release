import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("=== NÂNG CẤP PHIÊN BẢN LÊN V3.3.2 (VERSIONCODE = 26) ===")

# 1. TV build.gradle.kts
tv_gradle = "HuyCaBuonCa_TV/app/build.gradle.kts"
with open(tv_gradle, "r", encoding="utf-8") as f:
    c = f.read()
c = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 26', c)
c = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "3.3.2"', c)
with open(tv_gradle, "w", encoding="utf-8") as f:
    f.write(c)
print(f" -> Đã cập nhật {tv_gradle} -> v3.3.2 (code 26)")

# 2. Mobile build.gradle.kts
mob_gradle = "HuyCaBuonCa_Mobile/app/build.gradle.kts"
with open(mob_gradle, "r", encoding="utf-8") as f:
    c = f.read()
c = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 26', c)
c = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "3.3.2"', c)
with open(mob_gradle, "w", encoding="utf-8") as f:
    f.write(c)
print(f" -> Đã cập nhật {mob_gradle} -> v3.3.2 (code 26)")

# 3. LG webOS appinfo.json
webos_json = "HuyCaBuonCa_LG_webOS/appinfo.json"
with open(webos_json, "r", encoding="utf-8") as f:
    c = f.read()
c = re.sub(r'"version"\s*:\s*"[^"]+"', '"version": "3.3.2"', c)
with open(webos_json, "w", encoding="utf-8") as f:
    f.write(c)
print(f" -> Đã cập nhật {webos_json} -> 3.3.2")

# 4. HuyCa_Web index.html
web_html = "HuyCa_Web/index.html"
with open(web_html, "r", encoding="utf-8") as f:
    c = f.read()
c = re.sub(r'v3\.3\.[0-9]+', 'v3.3.2', c)
c = re.sub(r'v3\.3', 'v3.3.2', c)
with open(web_html, "w", encoding="utf-8") as f:
    f.write(c)
print(f" -> Đã cập nhật {web_html} -> v3.3.2")

# 5. Functions & Worker
for p in ["HuyCa_Web/functions/api/download.js", "HuyCa_Web/_worker.js"]:
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'v3\.3\.[0-9]+', 'v3.3.2', c)
        with open(p, "w", encoding="utf-8") as f:
            f.write(c)
        print(f" -> Đã cập nhật {p} -> v3.3.2")

print("\n🎉 HOÀN THÀNH TĂNG VERSION TOÀN BỘ HỆ THỐNG LÊN v3.3.2!")
