import os
import sys
import shutil
import io
import time
import tarfile

sys.stdout.reconfigure(encoding='utf-8')

print("=== BẮT ĐẦU ĐỒNG BỘ VÀ ĐÓNG GÓI LG WEBOS V3.3.0 ===")

webos_dir = "HuyCaBuonCa_LG_webOS"
web_dir = "HuyCa_Web"

# 1. Đồng bộ file
shutil.copy2(os.path.join(web_dir, "index.html"), os.path.join(webos_dir, "index.html"))
shutil.copy2(os.path.join(web_dir, "css", "style.css"), os.path.join(webos_dir, "css", "style.css"))
shutil.copy2(os.path.join(web_dir, "js", "app.js"), os.path.join(webos_dir, "js", "app.js"))
shutil.copy2(os.path.join(web_dir, "data", "tv_channels.json"), os.path.join(webos_dir, "data", "tv_channels.json"))
shutil.copy2(os.path.join(web_dir, "data", "tv_channels.js"), os.path.join(webos_dir, "data", "tv_channels.js"))
print(" -> Đã đồng bộ mã nguồn Web sang LG webOS thành công!")

# 2. Đóng gói IPK
def build_ar_header(name, size, mtime=None, mode="100644", uid="0", gid="0"):
    if mtime is None:
        mtime = int(time.time())
    header = f"{name:<16}{str(mtime):<12}{uid:<6}{gid:<6}{mode:<8}{str(size):<10}`\n"
    return header.encode('ascii')

def package_ipk(source_dir, output_ipk, version="3.3.0", app_id="com.huycabuonca.tv.lg"):
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
    print(f" -> Đã đóng gói thành công: {output_ipk} ({sz} MB)")

# Đóng gói cả tên chính thức và tên alias theo đúng quy tắc thương hiệu
package_ipk(webos_dir, "HuyCa_LG_webOS_v3.3.0.ipk", "3.3.0")
shutil.copy2("HuyCa_LG_webOS_v3.3.0.ipk", "HuyCa_LG_webOS_v3.3.ipk")
shutil.copy2("HuyCa_LG_webOS_v3.3.0.ipk", "HuyCaBuonCa_LG_webOS_v3.3.ipk")
shutil.copy2("HuyCa_LG_webOS_v3.3.0.ipk", "com.huycabuonca.tv.lg_3.3.0_all.ipk")

print("✅ ĐÓNG GÓI LG WEBOS V3.3.0 THÀNH CÔNG VỚI ĐẦY ĐỦ CÁC BẢN IPK!")
