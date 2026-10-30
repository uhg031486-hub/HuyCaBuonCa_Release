import os
import sys
import json
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

OLD_VER = "3.3.6"
NEW_VER = "3.3.7"
OLD_CODE = 30
NEW_CODE = 31

print(f"=== NÂNG CẤP PHIÊN BẢN TỪ v{OLD_VER} LÊN v{NEW_VER} (versionCode = {NEW_CODE}) ===")

# 1. version.json
v_path = "version.json"
if os.path.exists(v_path):
    with open(v_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["versionCode"] = NEW_CODE
    data["versionName"] = NEW_VER
    data["title"] = f"Bản Cập Nhật Huy Cá v{NEW_VER}"
    data["changelog"] = "1. Khắc phục triệt để lỗi chạm màn hình video trên thiết bị di động không hiển thị thanh điều hướng/controls.\n2. Chuẩn hóa cơ chế xử lý cảm ứng (Touch & Click Ergonomics) tách biệt cử chỉ chạm TAP và vuốt, ngăn chặn hoàn toàn xung đột synthetic mousemove.\n3. Bổ sung thanh điều khiển Thoát & Chọn Tập phim nổi bật cho trình phát nhúng Embed Iframe trên điện thoại.\n4. Đồng bộ hoàn hảo trên Android TV, Mobile, LG webOS, Windows và Web."
    data["apkUrl"] = f"https://github.com/uhg031486-hub/HuyCaBuonCa_Release/releases/download/v{NEW_VER}/HuyCa_TV_v{NEW_VER}.apk"
    data["mobileApkUrl"] = f"https://github.com/uhg031486-hub/HuyCaBuonCa_Release/releases/download/v{NEW_VER}/HuyCa_Mobile_v{NEW_VER}.apk"
    data["lgIpkUrl"] = f"https://github.com/uhg031486-hub/HuyCaBuonCa_Release/releases/download/v{NEW_VER}/HuyCa_LG_webOS_v{NEW_VER}.ipk"
    data["windowsZipUrl"] = f"https://github.com/uhg031486-hub/HuyCaBuonCa_Release/releases/download/v{NEW_VER}/HuyCa_Windows_v{NEW_VER}.zip"
    with open(v_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(" -> Đã cập nhật: version.json")

# 2. build.gradle.kts TV
tv_gradle = "HuyCaBuonCa_TV/app/build.gradle.kts"
if os.path.exists(tv_gradle):
    with open(tv_gradle, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'versionCode\s*=\s*\d+', f'versionCode = {NEW_CODE}', content)
    content = re.sub(r'versionName\s*=\s*"[^"]+"', f'versionName = "{NEW_VER}"', content)
    with open(tv_gradle, "w", encoding="utf-8") as f:
        f.write(content)
    print(f" -> Đã cập nhật: {tv_gradle}")

# 3. build.gradle.kts Mobile
mobile_gradle = "HuyCaBuonCa_Mobile/app/build.gradle.kts"
if os.path.exists(mobile_gradle):
    with open(mobile_gradle, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'versionCode\s*=\s*\d+', f'versionCode = {NEW_CODE}', content)
    content = re.sub(r'versionName\s*=\s*"[^"]+"', f'versionName = "{NEW_VER}"', content)
    with open(mobile_gradle, "w", encoding="utf-8") as f:
        f.write(content)
    print(f" -> Đã cập nhật: {mobile_gradle}")

# 4. LG webOS appinfo.json
webos_json = "HuyCaBuonCa_LG_webOS/appinfo.json"
if os.path.exists(webos_json):
    with open(webos_json, "r", encoding="utf-8") as f:
        w_data = json.load(f)
    w_data["version"] = NEW_VER
    with open(webos_json, "w", encoding="utf-8") as f:
        json.dump(w_data, f, ensure_ascii=False, indent=2)
    print(f" -> Đã cập nhật: {webos_json}")

# 5. Windows csproj
win_csproj = "HuyCa_Windows/HuyCa_Windows.csproj"
if os.path.exists(win_csproj):
    with open(win_csproj, "r", encoding="utf-8") as f:
        c = f.read()
    c = re.sub(r'<Version>[^<]+</Version>', f'<Version>{NEW_VER}</Version>', c)
    c = re.sub(r'<AssemblyVersion>[^<]+</AssemblyVersion>', f'<AssemblyVersion>{NEW_VER}.0</AssemblyVersion>', c)
    c = re.sub(r'<FileVersion>[^<]+</FileVersion>', f'<FileVersion>{NEW_VER}.0</FileVersion>', c)
    with open(win_csproj, "w", encoding="utf-8") as f:
        f.write(c)
    print(f" -> Đã cập nhật: {win_csproj}")

# 6. HTML & JS version banners
for html_f in ["HuyCa_Web/index.html", "HuyCaBuonCa_LG_webOS/index.html", "HuyCa_Windows/www/index.html"]:
    if os.path.exists(html_f):
        with open(html_f, "r", encoding="utf-8") as f:
            hc = f.read()
        hc = hc.replace(f"v{OLD_VER}", f"v{NEW_VER}").replace(f"v={OLD_VER}", f"v={NEW_VER}")
        with open(html_f, "w", encoding="utf-8") as f:
            f.write(hc)
        print(f" -> Đã cập nhật: {html_f}")

print("✅ ĐÃ NÂNG CẤP ĐỒNG BỘ PHIÊN BẢN v3.3.7!")
