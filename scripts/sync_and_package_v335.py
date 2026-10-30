import os
import sys
import shutil
import io
import time
import tarfile
import zipfile

sys.stdout.reconfigure(encoding='utf-8')

print("=== BẮT ĐẦU ĐỒNG BỘ VÀ ĐÓNG GÓI BẢN PHÁT HÀNH V3.3.5 ===")

web_dir = "HuyCa_Web"
webos_dir = "HuyCaBuonCa_LG_webOS"
win_dir = "HuyCa_Windows/www"

# 1. Đồng bộ file Web sang LG webOS và Windows www
files_to_sync = [
    ("index.html", "index.html"),
    (os.path.join("css", "style.css"), os.path.join("css", "style.css")),
    (os.path.join("js", "app.js"), os.path.join("js", "app.js")),
    (os.path.join("data", "tv_channels.json"), os.path.join("data", "tv_channels.json")),
    (os.path.join("data", "tv_channels.js"), os.path.join("data", "tv_channels.js")),
    ("favicon.ico", "favicon.ico"),
    ("icon.png", "icon.png"),
    ("icon_256.png", "icon_256.png"),
    ("largeIcon.png", "largeIcon.png"),
]

for src_rel, dst_rel in files_to_sync:
    src = os.path.join(web_dir, src_rel)
    if os.path.exists(src):
        dst_webos = os.path.join(webos_dir, dst_rel)
        os.makedirs(os.path.dirname(dst_webos), exist_ok=True)
        shutil.copy2(src, dst_webos)
        
        dst_win = os.path.join(win_dir, dst_rel)
        os.makedirs(os.path.dirname(dst_win), exist_ok=True)
        shutil.copy2(src, dst_win)

print(" -> Đã đồng bộ mã nguồn Web sang LG webOS và Windows www.")

# 2. Đóng gói LG webOS IPK
def build_ar_header(name, size, mtime=None, mode="100644", uid="0", gid="0"):
    if mtime is None:
        mtime = int(time.time())
    header = f"{name:<16}{str(mtime):<12}{uid:<6}{gid:<6}{mode:<8}{str(size):<10}`\n"
    return header.encode('ascii')

def package_ipk(source_dir, output_ipk, version="3.3.5", app_id="com.huycabuonca.tv.lg"):
    debian_binary = b"2.0\n"

    data_buf = io.BytesIO()
    total_installed_size = 0
    with tarfile.open(fileobj=data_buf, mode="w:gz") as tar:
        base_install_dir = f"usr/palm/applications/{app_id}"
        
        for p in ["usr", "usr/palm", "usr/palm/applications", base_install_dir]:
            ti = tarfile.TarInfo(p)
            ti.type = tarfile.DIRTYPE
            ti.mode = 0o755
            ti.mtime = int(time.time())
            tar.addfile(ti)

        for root, dirs, files in os.walk(source_dir):
            rel_dir = os.path.relpath(root, source_dir)
            if rel_dir == ".":
                target_dir = base_install_dir
            else:
                target_dir = f"{base_install_dir}/{rel_dir.replace(os.sep, '/')}"
                ti = tarfile.TarInfo(target_dir)
                ti.type = tarfile.DIRTYPE
                ti.mode = 0o755
                ti.mtime = int(time.time())
                tar.addfile(ti)

            for file in sorted(files):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                total_installed_size += file_size
                target_file = f"{target_dir}/{file}"
                tar.add(file_path, arcname=target_file)

    data_bytes = data_buf.getvalue()

    control_content = f"""Package: {app_id}
Version: {version}
Section: misc
Priority: optional
Architecture: all
Installed-Size: {total_installed_size}
Maintainer: HuyCa <huyca@example.com>
Description: Kho Phim & Truyen Hinh Huy Ca chuyen nghiep danh cho LG Smart TV webOS.
webOS-Package-Format-Version: 2
webOS-Packager-Version: x.y.x
"""
    control_buf = io.BytesIO()
    with tarfile.open(fileobj=control_buf, mode="w:gz") as tar:
        c_bytes = control_content.encode('utf-8')
        ti = tarfile.TarInfo("control")
        ti.size = len(c_bytes)
        ti.mode = 0o644
        ti.mtime = int(time.time())
        tar.addfile(ti, io.BytesIO(c_bytes))

    control_bytes = control_buf.getvalue()

    with open(output_ipk, "wb") as f:
        f.write(b"!<arch>\n")
        f.write(build_ar_header("debian-binary", len(debian_binary)))
        f.write(debian_binary)
        if len(debian_binary) % 2 == 1:
            f.write(b"\n")
            
        f.write(build_ar_header("control.tar.gz", len(control_bytes)))
        f.write(control_bytes)
        if len(control_bytes) % 2 == 1:
            f.write(b"\n")
            
        f.write(build_ar_header("data.tar.gz", len(data_bytes)))
        f.write(data_bytes)
        if len(data_bytes) % 2 == 1:
            f.write(b"\n")

    sz = round(os.path.getsize(output_ipk) / (1024 * 1024), 2)
    print(f" -> Đã đóng gói: {output_ipk} ({sz} MB)")

package_ipk(webos_dir, "HuyCa_LG_webOS_v3.3.5.ipk", "3.3.5")
shutil.copy2("HuyCa_LG_webOS_v3.3.5.ipk", "HuyCa_LG_webOS_v3.3.ipk")

# 3. Đóng gói Windows Desktop ZIP
if os.path.exists(win_dir):
    win_zip = "HuyCa_Windows_v3.3.5.zip"
    with zipfile.ZipFile(win_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(win_dir):
            for file in files:
                p = os.path.join(root, file)
                arcname = os.path.relpath(p, win_dir)
                z.write(p, arcname)
    shutil.copy2(win_zip, "HuyCa_Windows_v3.3.zip")
    print(f" -> Đã đóng gói: {win_zip} ({round(os.path.getsize(win_zip)/(1024*1024), 2)} MB)")

# 4. Xác nhận Android APKs
tv_apk_src = "HuyCaBuonCa_TV/app/build/outputs/apk/release/app-release.apk"
mobile_apk_src = "HuyCaBuonCa_Mobile/app/build/outputs/apk/release/app-release.apk"

if os.path.exists(tv_apk_src):
    shutil.copy2(tv_apk_src, "HuyCa_TV_v3.3.5.apk")
    shutil.copy2(tv_apk_src, "HuyCa_TV_v3.3.apk")
    print(f" -> Đã đóng gói: HuyCa_TV_v3.3.5.apk ({round(os.path.getsize('HuyCa_TV_v3.3.5.apk')/(1024*1024), 2)} MB)")

if os.path.exists(mobile_apk_src):
    shutil.copy2(mobile_apk_src, "HuyCa_Mobile_v3.3.5.apk")
    shutil.copy2(mobile_apk_src, "HuyCa_Mobile_v3.3.apk")
    print(f" -> Đã đóng gói: HuyCa_Mobile_v3.3.5.apk ({round(os.path.getsize('HuyCa_Mobile_v3.3.5.apk')/(1024*1024), 2)} MB)")

print("✅ ĐÃ ĐỒNG BỘ VÀ XUẤT TRỌN BỘ 4 BỘ CÀI ĐẶT THƯƠNG HIỆU HUY CÁ V3.3.5!")
