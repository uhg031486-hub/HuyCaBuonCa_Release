import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("=== NÂNG CẤP PHIÊN BẢN LÊN V3.3.5 (VERSIONCODE = 29) ===")

NEW_VERSION = "3.3.5"
NEW_CODE = 29

# 1. TV build.gradle.kts
tv_gradle = "HuyCaBuonCa_TV/app/build.gradle.kts"
with open(tv_gradle, "r", encoding="utf-8") as f:
    c = f.read()
c = re.sub(r'versionCode\s*=\s*\d+', f'versionCode = {NEW_CODE}', c)
c = re.sub(r'versionName\s*=\s*"[^"]+"', f'versionName = "{NEW_VERSION}"', c)
with open(tv_gradle, "w", encoding="utf-8") as f:
    f.write(c)
print(f" -> Cập nhật {tv_gradle}")

# 2. Mobile build.gradle.kts
mb_gradle = "HuyCaBuonCa_Mobile/app/build.gradle.kts"
with open(mb_gradle, "r", encoding="utf-8") as f:
    c = f.read()
c = re.sub(r'versionCode\s*=\s*\d+', f'versionCode = {NEW_CODE}', c)
c = re.sub(r'versionName\s*=\s*"[^"]+"', f'versionName = "{NEW_VERSION}"', c)
with open(mb_gradle, "w", encoding="utf-8") as f:
    f.write(c)
print(f" -> Cập nhật {mb_gradle}")

# 3. LG appinfo.json
lg_info = "HuyCaBuonCa_LG_webOS/appinfo.json"
with open(lg_info, "r", encoding="utf-8") as f:
    j = json.load(f)
j["version"] = NEW_VERSION
with open(lg_info, "w", encoding="utf-8") as f:
    json.dump(j, f, indent=2, ensure_ascii=False)
print(f" -> Cập nhật {lg_info}")

# 4. Windows .csproj
win_proj = "HuyCa_Windows/HuyCa_Windows.csproj"
with open(win_proj, "r", encoding="utf-8") as f:
    c = f.read()
c = re.sub(r'<Version>[^<]+</Version>', f'<Version>{NEW_VERSION}</Version>', c)
c = re.sub(r'<FileVersion>[^<]+</FileVersion>', f'<FileVersion>{NEW_VERSION}.0</FileVersion>', c)
c = re.sub(r'<AssemblyVersion>[^<]+</AssemblyVersion>', f'<AssemblyVersion>{NEW_VERSION}.0</AssemblyVersion>', c)
with open(win_proj, "w", encoding="utf-8") as f:
    f.write(c)
print(f" -> Cập nhật {win_proj}")

# 5. HTML files (HuyCa_Web, LG, Windows)
for html_path in ["HuyCa_Web/index.html", "HuyCaBuonCa_LG_webOS/index.html", "HuyCa_Windows/www/index.html"]:
    with open(html_path, "r", encoding="utf-8") as f:
        c = f.read()
    c = c.replace("v3.3.4", f"v{NEW_VERSION}")
    c = c.replace("v3.3.3", f"v{NEW_VERSION}")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(c)
    print(f" -> Cập nhật {html_path}")

# 6. _worker.js
worker_path = "HuyCa_Web/_worker.js"
with open(worker_path, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("v3.3.4", f"v{NEW_VERSION}")
c = c.replace("v3.3.3", f"v{NEW_VERSION}")
with open(worker_path, "w", encoding="utf-8") as f:
    f.write(c)
print(f" -> Cập nhật {worker_path}")

# 7. version.json
v_json = {
    "versionCode": NEW_CODE,
    "versionName": NEW_VERSION,
    "title": f"Huy Cá v{NEW_VERSION} - Sửa Triệt Để Lỗi Phát Video & Phụ Đề ExoPlayer Cho Tất Cả Các Nguồn Phim Ngắn",
    "changelog": "1. Khắc phục triệt để lỗi ExoPlayer Playback Error (Legacy decoding is disabled) trên Android TV và Mobile khi phát phim ngắn có phụ đề.\n2. Tích hợp cơ chế tự động giải mã phụ đề cũ và cơ chế Fallback an toàn tự phục hồi luồng video.\n3. Đồng bộ hóa nguồn Gà Mờ Mê Phim, nhận diện chính xác luồng stream MP4 Thuyết Minh và Vietsub trực tiếp từ Cloudflare R2.\n4. Đảm bảo 100% tất cả 7 sub-sources (ReelShort, DramaBox, ShortMax, FreeReels Gốc, Gà Mờ Mê Phim, AI Cinema, GoodShort) nạp mượt mà và phát trơn tru.",
    "isMaintenanceLocked": False,
    "maintenanceMessage": "Hệ thống đang bảo trì định kỳ. Vui lòng quay lại sau!",
    "windowsZipUrl": f"https://github.com/uhg031486-hub/HuyCaBuonCa_Release/releases/download/v{NEW_VERSION}/HuyCa_Windows_v{NEW_VERSION}.zip",
    "mobileApkUrl": f"https://github.com/uhg031486-hub/HuyCaBuonCa_Release/releases/download/v{NEW_VERSION}/HuyCa_Mobile_v{NEW_VERSION}.apk",
    "tvApkUrl": f"https://github.com/uhg031486-hub/HuyCaBuonCa_Release/releases/download/v{NEW_VERSION}/HuyCa_TV_v{NEW_VERSION}.apk",
    "lgIpkUrl": f"https://github.com/uhg031486-hub/HuyCaBuonCa_Release/releases/download/v{NEW_VERSION}/HuyCa_LG_webOS_v{NEW_VERSION}.ipk"
}
with open("version.json", "w", encoding="utf-8") as f:
    json.dump(v_json, f, indent=2, ensure_ascii=False)
print(" -> Cập nhật version.json")

print(f"\n🎉 ĐÃ NÂNG CẤP TOÀN BỘ DỰ ÁN LÊN V{NEW_VERSION} (versionCode={NEW_CODE})!")
