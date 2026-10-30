import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

OLD_VER = "3.3.5"
NEW_VER = "3.3.6"
OLD_CODE = "29"
NEW_CODE = "30"

print(f"BẮT ĐẦU NÂNG CẤP PHIÊN BẢN: {OLD_VER} ({OLD_CODE}) -> {NEW_VER} ({NEW_CODE})")

# 1. TV build.gradle.kts
tv_gradle = "HuyCaBuonCa_TV/app/build.gradle.kts"
with open(tv_gradle, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace(f'versionCode = {OLD_CODE}', f'versionCode = {NEW_CODE}')
c = c.replace(f'versionName = "{OLD_VER}"', f'versionName = "{NEW_VER}"')
with open(tv_gradle, "w", encoding="utf-8", newline="\n") as f:
    f.write(c)
print(f"✔ Đã nâng cấp {tv_gradle}")

# 2. Mobile build.gradle.kts
mobile_gradle = "HuyCaBuonCa_Mobile/app/build.gradle.kts"
with open(mobile_gradle, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace(f'versionCode = {OLD_CODE}', f'versionCode = {NEW_CODE}')
c = c.replace(f'versionName = "{OLD_VER}"', f'versionName = "{NEW_VER}"')
with open(mobile_gradle, "w", encoding="utf-8", newline="\n") as f:
    f.write(c)
print(f"✔ Đã nâng cấp {mobile_gradle}")

# 3. LG webOS appinfo.json
webos_appinfo = "HuyCaBuonCa_LG_webOS/appinfo.json"
with open(webos_appinfo, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace(f'"version": "{OLD_VER}"', f'"version": "{NEW_VER}"')
with open(webos_appinfo, "w", encoding="utf-8", newline="\n") as f:
    f.write(c)
print(f"✔ Đã nâng cấp {webos_appinfo}")

# 4. Windows .csproj
win_csproj = "HuyCa_Windows/HuyCa_Windows.csproj"
with open(win_csproj, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace(f'<AssemblyVersion>{OLD_VER}</AssemblyVersion>', f'<AssemblyVersion>{NEW_VER}</AssemblyVersion>')
c = c.replace(f'<FileVersion>{OLD_VER}</FileVersion>', f'<FileVersion>{NEW_VER}</FileVersion>')
c = c.replace(f'<Version>{OLD_VER}</Version>', f'<Version>{NEW_VER}</Version>')
with open(win_csproj, "w", encoding="utf-8", newline="\n") as f:
    f.write(c)
print(f"✔ Đã nâng cấp {win_csproj}")

# 5. Web index.html & other index.html
for idx_path in [
    "HuyCa_Web/index.html",
    "HuyCaBuonCa_LG_webOS/index.html",
    "HuyCa_Windows/www/index.html"
]:
    with open(idx_path, "r", encoding="utf-8") as f:
        c = f.read()
    c = c.replace(f"v{OLD_VER}", f"v{NEW_VER}")
    c = c.replace(f"Huy Cá {OLD_VER}", f"Huy Cá {NEW_VER}")
    with open(idx_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(c)
    print(f"✔ Đã nâng cấp {idx_path}")

# 6. Web _worker.js
worker_js = "HuyCa_Web/_worker.js"
with open(worker_js, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace(OLD_VER, NEW_VER)
c = c.replace(f'"versionCode": {OLD_CODE}', f'"versionCode": {NEW_CODE}')
with open(worker_js, "w", encoding="utf-8", newline="\n") as f:
    f.write(c)
print(f"✔ Đã nâng cấp {worker_js}")

# 7. version.json
ver_json = "version.json"
with open(ver_json, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace(f'"versionCode": {OLD_CODE}', f'"versionCode": {NEW_CODE}')
c = c.replace(f'"versionName": "{OLD_VER}"', f'"versionName": "{NEW_VER}"')
c = c.replace(f"v{OLD_VER}", f"v{NEW_VER}")
with open(ver_json, "w", encoding="utf-8", newline="\n") as f:
    f.write(c)
print(f"✔ Đã nâng cấp {ver_json}")

print(f"🎉 ĐÃ HOÀN TẤT NÂNG CẤP ĐỒNG BỘ TOÀN BỘ DỰ ÁN LÊN {NEW_VER} ({NEW_CODE})!")
