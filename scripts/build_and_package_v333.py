import os
import sys
import shutil
import io
import time
import tarfile
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== BẮT ĐẦU ĐỒNG BỘ VÀ ĐÓNG GÓI TẤT CẢ CÁC BỘ CÀI V3.3.3 ===")

# 1. Copy Android APKs
tv_apk_src = "HuyCaBuonCa_TV/app/build/outputs/apk/release/app-release.apk"
tv_apk_dest = "HuyCa_TV_v3.3.3.apk"
if os.path.exists(tv_apk_src):
    shutil.copy2(tv_apk_src, tv_apk_dest)
    shutil.copy2(tv_apk_src, "HuyCa_TV_v3.3.apk")
    print(f" -> Đã xuất xưởng: {tv_apk_dest} ({os.path.getsize(tv_apk_dest):,} bytes)")

mobile_apk_src = "HuyCaBuonCa_Mobile/app/build/outputs/apk/release/app-release.apk"
mobile_apk_dest = "HuyCa_Mobile_v3.3.3.apk"
if os.path.exists(mobile_apk_src):
    shutil.copy2(mobile_apk_src, mobile_apk_dest)
    shutil.copy2(mobile_apk_src, "HuyCa_Mobile_v3.3.apk")
    print(f" -> Đã xuất xưởng: {mobile_apk_dest} ({os.path.getsize(mobile_apk_dest):,} bytes)")

# 2. Đồng bộ mã nguồn sang LG webOS
webos_dir = "HuyCaBuonCa_LG_webOS"
web_dir = "HuyCa_Web"

shutil.copy2(os.path.join(web_dir, "index.html"), os.path.join(webos_dir, "index.html"))
shutil.copy2(os.path.join(web_dir, "css", "style.css"), os.path.join(webos_dir, "css", "style.css"))
shutil.copy2(os.path.join(web_dir, "js", "app.js"), os.path.join(webos_dir, "js", "app.js"))
shutil.copy2(os.path.join(web_dir, "data", "tv_channels.json"), os.path.join(webos_dir, "data", "tv_channels.json"))
shutil.copy2(os.path.join(web_dir, "data", "tv_channels.js"), os.path.join(webos_dir, "data", "tv_channels.js"))
print(" -> Đã đồng bộ mã nguồn Web sang LG webOS thành công!")

# Đồng bộ sang HuyCa_Windows nếu có
win_www = "HuyCa_Windows/www"
if os.path.exists(win_www):
    shutil.copy2(os.path.join(web_dir, "index.html"), os.path.join(win_www, "index.html"))
    shutil.copy2(os.path.join(web_dir, "css", "style.css"), os.path.join(win_www, "css", "style.css"))
    shutil.copy2(os.path.join(web_dir, "js", "app.js"), os.path.join(win_www, "js", "app.js"))
    print(" -> Đã đồng bộ mã nguồn Web sang HuyCa_Windows/www thành công!")

# 3. Đóng gói IPK chuẩn webOS
def build_ar_header(name, size, mtime=None, mode="100644", uid="0", gid="0"):
    if mtime is None:
        mtime = int(time.time())
    header = f"{name:<16}{str(mtime):<12}{uid:<6}{gid:<6}{mode:<8}{str(size):<10}`\n"
    return header.encode('ascii')

def package_ipk(source_dir, output_ipk, version="3.3.3", app_id="com.huycabuonca.tv.lg"):
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

            for d in dirs:
                dir_path = os.path.join(root, d)
                tar_target = f"{target_dir}/{d}"
                ti = tarfile.TarInfo(tar_target)
                ti.type = tarfile.DIRTYPE
                ti.mode = 0o755
                ti.mtime = int(os.path.getmtime(dir_path))
                tar.addfile(ti)

            for f in files:
                file_path = os.path.join(root, f)
                tar_target = f"{target_dir}/{f}"
                ti = tarfile.TarInfo(tar_target)
                ti.size = os.path.getsize(file_path)
                total_installed_size += ti.size
                ti.mode = 0o644
                ti.mtime = int(os.path.getmtime(file_path))
                with open(file_path, "rb") as content_file:
                    tar.addfile(ti, content_file)

    data_bytes = data_buf.getvalue()

    installed_size_kb = (total_installed_size + 1023) // 1024
    control_content = f"""Package: {app_id}
Version: {version}
Section: misc
Priority: optional
Architecture: all
Installed-Size: {installed_size_kb}
Maintainer: Huy Ca <huyca@buonca.tv>
Description: Kho Phim & Truyen Hinh Dang Cap Huy Ca cho LG Smart TV webOS
"""
    control_buf = io.BytesIO()
    with tarfile.open(fileobj=control_buf, mode="w:gz") as tar:
        ti = tarfile.TarInfo("control")
        c_bytes = control_content.encode('utf-8')
        ti.size = len(c_bytes)
        ti.mode = 0o644
        ti.mtime = int(time.time())
        tar.addfile(ti, io.BytesIO(c_bytes))
    control_bytes = control_buf.getvalue()

    ar_data = bytearray(b"!<arch>\n")
    ar_data.extend(build_ar_header("debian-binary", len(debian_binary)))
    ar_data.extend(debian_binary)
    if len(debian_binary) % 2 != 0:
        ar_data.extend(b"\n")

    ar_data.extend(build_ar_header("control.tar.gz", len(control_bytes)))
    ar_data.extend(control_bytes)
    if len(control_bytes) % 2 != 0:
        ar_data.extend(b"\n")

    ar_data.extend(build_ar_header("data.tar.gz", len(data_bytes)))
    ar_data.extend(data_bytes)
    if len(data_bytes) % 2 != 0:
        ar_data.extend(b"\n")

    with open(output_ipk, "wb") as f:
        f.write(ar_data)
    print(f" -> Đã xuất xưởng: {output_ipk} ({os.path.getsize(output_ipk):,} bytes)")

ipk_dest = "HuyCa_LG_webOS_v3.3.3.ipk"
package_ipk(webos_dir, ipk_dest, version="3.3.3")
shutil.copy2(ipk_dest, "HuyCa_LG_webOS_v3.3.ipk")

# 4. Đóng gói Windows ZIP
win_zip_dest = "HuyCa_Windows_v3.3.3.zip"
with zipfile.ZipFile(win_zip_dest, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(web_dir):
        if "_worker.js" in files:
            pass
        for f in files:
            if f.endswith('.swp') or f.endswith('.map'):
                continue
            fp = os.path.join(root, f)
            arcname = os.path.relpath(fp, web_dir)
            zf.write(fp, arcname)
print(f" -> Đã xuất xưởng: {win_zip_dest} ({os.path.getsize(win_zip_dest):,} bytes)")
shutil.copy2(win_zip_dest, "HuyCa_Windows_v3.3.zip")

print("\n🎉 ĐÓNG GÓI HOÀN TẤT ĐẦY ĐỦ CÁC BỘ CÀI V3.3.3!")
