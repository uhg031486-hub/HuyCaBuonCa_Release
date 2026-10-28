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
TAG = "v3.3.1"
TITLE = "Huy Cá v3.3.1 - Sửa Triệt Để Lọc Anime & Phim Ngắn, Bổ Sung Thanh Chọn Server Phụ Đề / Thuyết Minh Trên Android TV"

BODY = """### 🚀 Bản Phát Hành Huy Cá v3.3.1 - Tối Ưu Hóa Bộ Lọc Danh Mục & Đa Server Android TV

#### 🌟 Các Tính Năng & Nâng Cấp Nổi Bật Trên v3.3.1:
1. **Khắc Phục Triệt Để Hiện Tượng "Ngồi Nhầm Lớp" (Phim Thường Sang Anime & Phim Ngắn)**:
   - **Mục Anime**: Áp dụng cơ chế lọc phân loại nghiêm ngặt (`type == "hoathinh"`, `category == "Hoạt Hình"` hoặc có từ khóa Anime), loại bỏ hoàn toàn 100% phim người đóng live-action lẫn vào danh sách.
   - **Mục Phim Ngắn (Tiểu kịch dọc 9:16)**: Loại bỏ hoàn toàn nguồn tìm kiếm phim dài tập KKPhim, chỉ giữ lại các kho phim ngắn chuyên biệt (FreeReels, Gà Mờ Mê Phim / Voice AI).
2. **Bổ Sung Thanh Chọn Server Phụ Đề / Thuyết Minh / Lồng Tiếng Trên Android TV**:
   - Màn hình chi tiết phim trên Android TV (`DetailActivity`) nay đã có thanh chọn Server trực quan nằm ngay trên danh sách tập.
   - Tự động gắn nhãn badge nhận diện rõ ràng: `🇻🇳 [Phụ Đề]`, `🎙️ [Thuyết Minh]`, `🗣️ [Lồng Tiếng]`.
   - Hỗ trợ đầy đủ điều khiển D-Pad điều hướng từ xa, hiệu ứng focus viền vàng kim chuẩn Android TV Box.
   - Khi chuyển đổi Server, danh sách tập được cập nhật tức thì theo đúng luồng phát đã chọn.
3. **Đồng Bộ Hoàn Hảo Trên Cả 5 Nền Tảng**:
   - **Android TV Box & Smart TV**: `HuyCa_TV_v3.3.1.apk` / `HuyCa_TV_v3.3.apk`
   - **Android Mobile**: `HuyCa_Mobile_v3.3.1.apk` / `HuyCa_Mobile_v3.3.apk`
   - **LG Smart TV (webOS)**: `HuyCa_LG_webOS_v3.3.1.ipk` / `HuyCa_LG_webOS_v3.3.ipk`
   - **Windows Desktop**: `HuyCa_Windows_v3.3.1.zip` / `HuyCa_Windows_v3.3.zip`
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
        "versionCode": 25,
        "versionName": "3.3.1",
        "title": "Bản Cập Nhật Huy Cá v3.3.1",
        "changelog": "1. Khắc phục triệt để lỗi phân loại Anime & Phim Ngắn (chấm dứt tình trạng ngồi nhầm lớp).\n2. Bổ sung thanh chọn Server Phụ Đề / Thuyết Minh / Lồng Tiếng trên Android TV.\n3. Nâng cấp trải nghiệm D-Pad và đồng bộ đa nền tảng.",
        "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.3.1.apk",
        "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Mobile_v3.3.1.apk",
        "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_LG_webOS_v3.3.1.ipk",
        "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Windows_v3.3.1.zip",
        "forceUpdate": False
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
    res = requests.get(url, headers=HEADERS)
    sha = res.json().get("sha") if res.status_code == 200 else None

    b64_content = base64.b64encode(json.dumps(new_version_info, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"release: nâng cấp version.json lên {TAG} (Huy Cá v3.3.1)",
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
    create_res = requests.post(create_url, headers=HEADERS, json=payload)
    if create_res.status_code in [200, 201]:
        print(" -> Tạo Release thành công!")
        return create_res.json()
    else:
        print(f" -> Lỗi tạo Release: {create_res.status_code} - {create_res.text}")
        return None

def upload_assets(release):
    if not release:
        return
    upload_url = release.get("upload_url", "").replace("{?name,label}", "")
    existing_assets = {a["name"]: a["id"] for a in release.get("assets", [])}

    files = [
        "HuyCa_TV_v3.3.1.apk",
        "HuyCa_TV_v3.3.apk",
        "HuyCa_Mobile_v3.3.1.apk",
        "HuyCa_Mobile_v3.3.apk",
        "HuyCa_LG_webOS_v3.3.1.ipk",
        "HuyCa_LG_webOS_v3.3.ipk",
        "HuyCa_Windows_v3.3.1.zip",
        "HuyCa_Windows_v3.3.zip"
    ]

    print(f"3. Đang tải lên {len(files)} tệp phát hành lên GitHub...")
    for filename in files:
        if not os.path.exists(filename):
            print(f" ⚠️ Không tìm thấy file: {filename}")
            continue

        if filename in existing_assets:
            print(f" -> Xóa file cũ {filename} để tải mới...")
            del_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{existing_assets[filename]}"
            requests.delete(del_url, headers=HEADERS)

        size_mb = round(os.path.getsize(filename) / (1024 * 1024), 2)
        print(f" -> Đang upload {filename} ({size_mb} MB)...")

        content_type = "application/octet-stream"
        if filename.endswith(".apk"):
            content_type = "application/vnd.android.package-archive"
        elif filename.endswith(".zip"):
            content_type = "application/zip"

        up_headers = {
            "Authorization": f"token {TOKEN}",
            "Content-Type": content_type
        }

        with open(filename, "rb") as f:
            up_res = requests.post(f"{upload_url}?name={filename}", headers=up_headers, data=f)
            if up_res.status_code in [200, 201]:
                print(f"   ✅ Thành công: {filename}")
            else:
                print(f"   ❌ Thất bại: {filename} ({up_res.status_code})")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Không tìm thấy GitHub Token!")
        sys.exit(1)
    update_version_json()
    rel = create_or_get_release()
    upload_assets(rel)
    print("\n🎉 HOÀN TẤT PHÁT HÀNH GÓI CÀI ĐẶT V3.3.1 LÊN GITHUB RELEASE!")
