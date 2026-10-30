import os
import sys
import subprocess
import json
import base64
import requests

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

def get_token():
    try:
        res = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
        if "@github.com" in res and "https://" in res:
            token = res.split("https://")[1].split("@github.com")[0]
            if token.startswith("ghp_") or token.startswith("github_pat_"):
                return token
    except Exception as e:
        print("Lỗi đọc git remote:", e)
    return ""

TOKEN = get_token()
REPO_OWNER = "uhg031486-hub"
REPO_NAME = "HuyCaBuonCa_Release"
TAG = "v3.3.6"
TITLE = "Huy Cá v3.3.6 - Chuẩn Hóa & Bổ Sung 100% Icon Sắc Nét Cho Toàn Bộ Kho Kênh Truyền Hình (Mỗi Kênh 1 Icon)"

BODY = """### 🚀 Bản Phát Hành Huy Cá v3.3.6 - Chuẩn Hóa 100% Icon Kênh Truyền Hình Đa Nền Tảng

#### 🌟 Các Nâng Cấp & Sửa Lỗi Cốt Lõi Trên Phiên Bản v3.3.6:
1. **Khắc Phục Hoàn Toàn Vấn Đề Thiếu Icon & Mất Logo Trong Mục Xem Tivi**:
   - Tích hợp và đồng bộ đầy đủ **152 icon riêng biệt, sắc nét** cho 100% danh mục kênh truyền hình (VTV, VTVcab, HTV, SCTV, THVL, Ngoại Hạng Anh, Thể Thao Quốc Tế, Vệ Tinh, Tin Tức Quốc Tế, Địa Phương).
   - Chuyển đổi toàn bộ các logo SVG sang PNG độ phân giải cao 300 DPI, tích hợp trực tiếp vào bộ nhớ cục bộ `assets/logos/` của APK Android (TV & Mobile).
   - Nhờ đó, icon hiển thị **ngay lập tức (0ms latency)**, hoàn toàn không phụ thuộc vào đường truyền mạng và không bao giờ bị lỗi hiển thị.
2. **Loại Bỏ Triệt Để Các Link Ảnh Lỗi (Wikimedia 400 & iptv-org 404)**:
   - Thay thế toàn bộ các liên kết Wikimedia thumbnail bị lỗi `HTTP 400` bằng nguồn ảnh PNG/JPG/WebP tĩnh hoạt động 100% trả về mã `200 OK`.
   - Bổ sung cơ chế `resolveChannelLogo()` thông minh trong `MovieRepository`: tự động ánh xạ thông minh các kênh VTV1-10, HTV, VTVcab, Premier League, TNT Sports, Sky Sports, beIN Sports... về kho logo nội bộ chuẩn.
   - Thay thế fallback `R.drawable.tv_banner` (banner ngang Huy Cá TV) bằng icon kênh TV chuyên nghiệp, loại bỏ hoàn toàn hiện tượng thẻ kênh bị che khuất hoặc lặp banner.
3. **Trọn Bộ Cài Đặt Phát Hành v3.3.6 Chuẩn Thương Hiệu Duy Nhất Huy Cá**:
   - **Android Smart TV & TV Box**: `HuyCa_TV_v3.3.6.apk` / `HuyCa_TV_v3.3.apk`
   - **Android Mobile**: `HuyCa_Mobile_v3.3.6.apk` / `HuyCa_Mobile_v3.3.apk`
   - **LG Smart TV (webOS)**: `HuyCa_LG_webOS_v3.3.6.ipk` / `HuyCa_LG_webOS_v3.3.ipk`
   - **Windows Desktop**: `HuyCa_Windows_v3.3.6.zip` / `HuyCa_Windows_v3.3.zip`
   - **Web Trực Tuyến**: [https://huyca.pages.dev](https://huyca.pages.dev)
"""

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "User-Agent": "Antigravity-Release-Bot",
    "Accept": "application/vnd.github.v3+json",
}

def update_version_json():
    print("1. Cập nhật file version.json trên repository...")
    new_version_info = {
        "versionCode": 30,
        "versionName": "3.3.6",
        "title": "Bản Cập Nhật Huy Cá v3.3.6",
        "changelog": "1. Chuẩn hóa và hiển thị 100% icon sắc nét cho toàn bộ 152 kênh truyền hình (mỗi kênh 1 icon riêng biệt).\n2. Tích hợp trực tiếp 77+ logo PNG chất lượng cao vào asset cục bộ giúp nạp icon tức thì (0ms latency).\n3. Khắc phục triệt để lỗi link logo Wikimedia 400 và iptv-org 404.\n4. Đồng bộ trải nghiệm giao diện xem Tivi hoàn hảo trên Android TV, Mobile, LG webOS và Windows.",
        "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.3.6.apk",
        "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Mobile_v3.3.6.apk",
        "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_LG_webOS_v3.3.6.ipk",
        "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Windows_v3.3.6.zip",
        "forceUpdate": False
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
    res = requests.get(url, headers=HEADERS)
    sha = res.json().get("sha") if res.status_code == 200 else None

    b64_content = base64.b64encode(json.dumps(new_version_info, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"release: nâng cấp version.json lên {TAG} (Huy Cá v3.3.6)",
        "content": b64_content,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    put_res = requests.put(url, headers=HEADERS, json=payload)
    if put_res.status_code in (200, 201):
        print(f" -> Đã cập nhật version.json thành công trên GitHub (sha: {put_res.json().get('commit', {}).get('sha', '')[:7]})")
    else:
        payload["branch"] = "master"
        put_res2 = requests.put(url, headers=HEADERS, json=payload)
        print(f" -> Kết quả branch master: {put_res2.status_code}")

def create_or_get_release():
    print(f"2. Kiểm tra/Tạo Release {TAG} trên GitHub...")
    rel_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{TAG}"
    res = requests.get(rel_url, headers=HEADERS)
    if res.status_code == 200:
        print(" -> Release đã tồn tại!")
        return res.json()

    create_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    payload = {
        "tag_name": TAG,
        "name": TITLE,
        "body": BODY,
        "draft": False,
        "prerelease": False
    }
    res = requests.post(create_url, headers=HEADERS, json=payload)
    if res.status_code in (200, 201):
        print(f" -> Tạo Release {TAG} thành công!")
        return res.json()
    else:
        print(f"Lỗi tạo release: {res.status_code} - {res.text}")
        return None

def upload_asset(upload_url_template, file_path):
    filename = os.path.basename(file_path)
    upload_url = upload_url_template.split("{?")[0] + f"?name={filename}"
    sz_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
    print(f" -> Đang tải lên {filename} ({sz_mb} MB)...")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/octet-stream",
        "User-Agent": "Antigravity-Release-Bot"
    }
    res = requests.post(upload_url, headers=headers, data=file_bytes)
    if res.status_code in (200, 201):
        print(f"    ✔ Thành công: {filename}")
        return True
    else:
        print(f"    ❌ Lỗi tải lên {filename}: {res.status_code} - {res.text}")
        return False

def main():
    if not TOKEN:
        print("❌ Không tìm thấy GitHub Token!")
        sys.exit(1)

    update_version_json()
    rel = create_or_get_release()
    if not rel:
        print("❌ Không thể tạo/lấy release!")
        sys.exit(1)

    upload_url = rel.get("upload_url")
    existing_assets = {a["name"]: a["id"] for a in rel.get("assets", [])}

    files = [
        "HuyCa_TV_v3.3.6.apk",
        "HuyCa_TV_v3.3.apk",
        "HuyCa_Mobile_v3.3.6.apk",
        "HuyCa_Mobile_v3.3.apk",
        "HuyCa_LG_webOS_v3.3.6.ipk",
        "HuyCa_LG_webOS_v3.3.ipk",
        "HuyCa_Windows_v3.3.6.zip",
        "HuyCa_Windows_v3.3.zip"
    ]

    print(f"\n3. Bắt đầu tải lên {len(files)} tệp phát hành lên Release {TAG}...")
    for f in files:
        if not os.path.exists(f):
            print(f" ⚠️ Cảnh báo: File không tồn tại: {f}")
            continue

        if f in existing_assets:
            print(f" -> Tệp {f} đã tồn tại trên release, xóa để nạp bản mới...")
            del_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{existing_assets[f]}"
            requests.delete(del_url, headers=HEADERS)

        upload_asset(upload_url, f)

    print(f"\n🎉 HOÀN TẤT PHÁT HÀNH TOÀN DIỆN HUY CÁ {TAG} LÊN GITHUB!")

if __name__ == "__main__":
    main()
