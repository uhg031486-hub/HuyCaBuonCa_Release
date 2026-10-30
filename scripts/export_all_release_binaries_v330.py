import os
import sys
import shutil
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

print("=== XUẤT TOÀN BỘ FILE CÀI ĐẶT RELEASE V3.3.0 ===")

tv_apk_src = "HuyCaBuonCa_TV/app/build/outputs/apk/release/app-release.apk"
mobile_apk_src = "HuyCaBuonCa_Mobile/app/build/outputs/apk/release/app-release.apk"

# 1. Android TV APK
if os.path.exists(tv_apk_src):
    shutil.copy2(tv_apk_src, "HuyCa_TV_v3.3.0.apk")
    shutil.copy2(tv_apk_src, "HuyCa_TV_v3.3.apk")
    shutil.copy2(tv_apk_src, "HuyCaBuonCa_TV_v3.3.apk")
    print(f" -> Đã xuất HuyCa_TV_v3.3.0.apk ({round(os.path.getsize('HuyCa_TV_v3.3.0.apk')/(1024*1024), 2)} MB)")

# 2. Android Mobile APK
if os.path.exists(mobile_apk_src):
    shutil.copy2(mobile_apk_src, "HuyCa_Mobile_v3.3.0.apk")
    shutil.copy2(mobile_apk_src, "HuyCa_Mobile_v3.3.apk")
    shutil.copy2(mobile_apk_src, "HuyCaBuonCa_Mobile_v3.3.apk")
    print(f" -> Đã xuất HuyCa_Mobile_v3.3.0.apk ({round(os.path.getsize('HuyCa_Mobile_v3.3.0.apk')/(1024*1024), 2)} MB)")

# 3. Windows Desktop ZIP
win_dir = "HuyCa_Windows/www"
if os.path.exists(win_dir):
    zip_name = "HuyCa_Windows_v3.3.0.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(win_dir):
            for file in files:
                p = os.path.join(root, file)
                arcname = os.path.relpath(p, win_dir)
                z.write(p, arcname)
    shutil.copy2(zip_name, "HuyCa_Windows_v3.3.zip")
    print(f" -> Đã xuất {zip_name} ({round(os.path.getsize(zip_name)/(1024*1024), 2)} MB)")

print("✅ ĐÃ XUẤT TRỌN BỘ 4 NỀN TẢNG (TV APK, Mobile APK, webOS IPK, Windows ZIP) V3.3.0!")
