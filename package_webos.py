import os
import io
import time
import tarfile

def build_ar_header(name, size, mtime=None, mode="100644", uid="0", gid="0"):
    if mtime is None:
        mtime = int(time.time())
    header = f"{name:<16}{str(mtime):<12}{uid:<6}{gid:<6}{mode:<8}{str(size):<10}`\n"
    return header.encode('ascii')

def package_webos_ipk(source_dir, output_ipk, version="2.6.0", app_id="com.huycabuonca.tv.lg"):
    # 1. debian-binary
    debian_binary = b"2.0\n"

    # 2. data.tar.gz
    data_buf = io.BytesIO()
    total_installed_size = 0
    with tarfile.open(fileobj=data_buf, mode="w:gz") as tar:
        base_install_dir = f"usr/palm/applications/{app_id}"
        
        # Add parent directories
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

    # 3. control.tar.gz
    control_content = f"""Package: {app_id}
Version: {version}
Section: misc
Priority: optional
Architecture: all
Installed-Size: {total_installed_size}
Maintainer: N/A <nobody@example.com>
Description: This is a webOS application.
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

    # 4. Pack into ar archive
    with open(output_ipk, "wb") as f:
        f.write(b"!<arch>\n")
        
        # debian-binary
        f.write(build_ar_header("debian-binary", len(debian_binary)))
        f.write(debian_binary)
        if len(debian_binary) % 2 == 1:
            f.write(b"\n")
            
        # control.tar.gz
        f.write(build_ar_header("control.tar.gz", len(control_bytes)))
        f.write(control_bytes)
        if len(control_bytes) % 2 == 1:
            f.write(b"\n")
            
        # data.tar.gz
        f.write(build_ar_header("data.tar.gz", len(data_bytes)))
        f.write(data_bytes)
        if len(data_bytes) % 2 == 1:
            f.write(b"\n")

    print(f"Created {output_ipk} ({round(os.path.getsize(output_ipk)/1024, 2)} KB)")

if __name__ == "__main__":
    package_webos_ipk("HuyCaBuonCa_LG_webOS", "com.huycabuonca.tv.lg_2.6.0_all.ipk", "2.6.0")
    import shutil
    shutil.copyfile("com.huycabuonca.tv.lg_2.6.0_all.ipk", "HuyCaBuonCa_LG_webOS_v2.6.ipk")
    shutil.copyfile("com.huycabuonca.tv.lg_2.6.0_all.ipk", "HuyCa_LG_webOS_v2.6.ipk")
    print("WebOS packaging complete!")
