import os
import sys
import shutil
import zipfile
import subprocess

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=== BẮT ĐẦU ĐỒNG BỘ VÀ ĐÓNG GÓI BẢN PHÁT HÀNH V3.3.8 ===")

# 1. Đồng bộ JS, CSS, Cinematic từ HuyCa_Web sang LG webOS và Windows www
web_files = ["js/app.js", "css/style.css", "index.html", "data/tv_channels.json", "data/tv_channels.js"]
targets = ["HuyCaBuonCa_LG_webOS", "HuyCa_Windows/www"]

for target in targets:
    for rel_f in web_files:
        src = os.path.join("HuyCa_Web", rel_f)
        dst = os.path.join(target, rel_f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(src):
            shutil.copy2(src, dst)
print(" -> Đã đồng bộ mã nguồn Web (app.js, style.css) sang LG webOS và Windows www.")

# Đồng bộ thư mục cinematic
for target in targets:
    src_cinematic = "HuyCa_Web/cinematic"
    dst_cinematic = os.path.join(target, "cinematic")
    if os.path.exists(src_cinematic):
        shutil.copytree(src_cinematic, dst_cinematic, dirs_exist_ok=True)
print(" -> Đã đồng bộ thư mục cinematic sang LG webOS và Windows www.")

def create_zip(source_dir, output_filename):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            if 'bin' in root.split(os.sep) or 'obj' in root.split(os.sep) or '.git' in root:
                continue
            for file in files:
                if file.endswith('.ipk') or file.endswith('.zip'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

# 2. Đóng gói IPK cho LG webOS
ipk_name_v = "HuyCa_LG_webOS_v3.3.8.ipk"
ipk_name_s = "HuyCa_LG_webOS_v3.3.ipk"
create_zip("HuyCaBuonCa_LG_webOS", ipk_name_v)
shutil.copy2(ipk_name_v, ipk_name_s)
print(f" -> Đã đóng gói: {ipk_name_v} ({os.path.getsize(ipk_name_v) / (1024*1024):.2f} MB)")

# 3. Đóng gói ZIP cho Windows
win_zip_v = "HuyCa_Windows_v3.3.8.zip"
win_zip_s = "HuyCa_Windows_v3.3.zip"
create_zip("HuyCa_Windows", win_zip_v)
shutil.copy2(win_zip_v, win_zip_s)
print(f" -> Đã đóng gói: {win_zip_v} ({os.path.getsize(win_zip_v) / (1024*1024):.2f} MB)")

# 4. Copy Release APK nếu đã build
tv_apk_src = "HuyCaBuonCa_TV/app/build/outputs/apk/release/app-release.apk"
if os.path.exists(tv_apk_src):
    shutil.copy2(tv_apk_src, "HuyCa_TV_v3.3.8.apk")
    shutil.copy2(tv_apk_src, "HuyCa_TV_v3.3.apk")
    print(f" -> Đã đóng gói: HuyCa_TV_v3.3.8.apk ({os.path.getsize('HuyCa_TV_v3.3.8.apk') / (1024*1024):.2f} MB)")

mobile_apk_src = "HuyCaBuonCa_Mobile/app/build/outputs/apk/release/app-release.apk"
if os.path.exists(mobile_apk_src):
    shutil.copy2(mobile_apk_src, "HuyCa_Mobile_v3.3.8.apk")
    shutil.copy2(mobile_apk_src, "HuyCa_Mobile_v3.3.apk")
    print(f" -> Đã đóng gói: HuyCa_Mobile_v3.3.8.apk ({os.path.getsize('HuyCa_Mobile_v3.3.8.apk') / (1024*1024):.2f} MB)")

print("✅ ĐÃ ĐỒNG BỘ VÀ XUẤT TRỌN BỘ 4 BỘ CÀI ĐẶT THƯƠNG HIỆU HUY CÁ V3.3.8!")
