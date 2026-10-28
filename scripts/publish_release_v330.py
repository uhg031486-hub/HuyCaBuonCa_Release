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
TAG = "v3.3.0"
TITLE = "Huy Cá v3.3.0 - Nâng Cấp Toàn Diện Kho Kênh TV Quốc Tế, VTV, HTV & Giải Mã Luồng Nguồn C Không Quảng Cáo Đa Nền Tảng"

BODY = """### 🚀 Bản Phát Hành Huy Cá v3.3.0 - Nâng Cấp Toàn Diện Kho Kênh TV & Nguồn C Đa Nền Tảng

#### 🌟 Các Tính Năng Đột Phá Trên Phiên Bản v3.3.0:
1. **Khắc Phục Hoàn Toàn Lỗi Xem Phim Nguồn C Trên Android TV & Mobile**:
   - Tích hợp giao thức giải mã Native HLS / MPEG-TS thông qua endpoint proxy sạch, triệt tiêu 100% bẫy mở popup và tab quảng cáo ngoài.
   - Cấu hình ExoPlayer nhận diện chính xác `MimeTypes.APPLICATION_M3U8` và xử lý buffer thông minh, phát mượt mà không giật lag.
2. **Nâng Cấp Kho Kênh Truyền Hình Quốc Tế Đỉnh Cao (1080p / 720p)**:
   - **Tin tức & Thời sự toàn cầu**: NHK World-Japan HD (Nhật Bản), ABC News Live HD (Mỹ), CBS News 24/7 HD (Mỹ), NBC News NOW HD (Mỹ), Reuters TV HD (Hãng tin quốc tế), CNA Singapore HD (Châu Á), DW English HD (Đức), France 24 English HD (Pháp), Al Jazeera English HD, Euronews HD.
   - **Kinh tế tài chính**: Bloomberg Originals HD, CNBC Europe HD.
   - **Thể thao & Vệ tinh**: TNT Sports 1 HD (Cúp C1 & Ngoại Hạng Anh), beIN SPORTS XTRA HD, NBC Sports NOW HD, Red Bull TV HD, Arirang World TV HD.
   - **Điện ảnh & Hoạt hình**: Warner TV Asia HD, HBO Cinema HD, Cartoonito / Boomerang HD, History Hit HD.
3. **Trọn Bộ Kênh Trong Nước Chuẩn HD 100% Live**:
   - VTV1 đến VTV10, trọn bộ HTV1, HTV2, HTV3, HTV7, HTV9, HTV Thể Thao HD nguồn CDN HTTPS sạch.
   - Các đài địa phương: Cần Thơ 1, Cần Thơ 3, An Giang, Vĩnh Long, Hà Tĩnh...
4. **Đồng Bộ Hoàn Hảo Trên Cả 5 Nền Tảng**:
   - **Android TV Box & Smart TV**: `HuyCa_TV_v3.3.0.apk` / `HuyCa_TV_v3.3.apk`
   - **Android Mobile**: `HuyCa_Mobile_v3.3.0.apk` / `HuyCa_Mobile_v3.3.apk`
   - **LG Smart TV (webOS)**: `HuyCa_LG_webOS_v3.3.0.ipk` / `HuyCa_LG_webOS_v3.3.ipk`
   - **Windows Desktop**: `HuyCa_Windows_v3.3.0.zip` / `HuyCa_Windows_v3.3.zip`
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
        "versionCode": 24,
        "versionName": "3.3.0",
        "title": "Bản Cập Nhật Huy Cá v3.3.0",
        "changelog": "1. Khắc phục triệt để lỗi xem phim Nguồn C trên Android TV & Mobile.\n2. Bổ sung kho kênh quốc tế đỉnh cao: NHK World, ABC News, CBS News, CNA, Reuters, Al Jazeera, DW, France 24...\n3. Trọn bộ HTV1-HTV9 và HTV Thể Thao HD sạch 100%.\n4. Đồng bộ hoàn hảo đa nền tảng.",
        "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.3.0.apk",
        "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Mobile_v3.3.0.apk",
        "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_LG_webOS_v3.3.0.ipk",
        "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Windows_v3.3.0.zip",
        "forceUpdate": False
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
    res = requests.get(url, headers=HEADERS)
    sha = res.json().get("sha") if res.status_code == 200 else None

    b64_content = base64.b64encode(json.dumps(new_version_info, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"release: nâng cấp version.json lên {TAG} (Huy Cá v3.3.0)",
        "content": b64_content,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    put_res = requests.put(url, headers=HEADERS, json=payload)
    if put_res.status_code in (200, 201):
        print(f" -> Đã cập nhật version.json thành công trên GitHub (sha: {put_res.json().get('commit', {}).get('sha', '')[:7]})")
    else:
        # Thử lại với branch master nếu branch main lỗi
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
        "HuyCa_TV_v3.3.0.apk",
        "HuyCa_TV_v3.3.apk",
        "HuyCa_Mobile_v3.3.0.apk",
        "HuyCa_Mobile_v3.3.apk",
        "HuyCa_LG_webOS_v3.3.0.ipk",
        "HuyCa_LG_webOS_v3.3.ipk",
        "HuyCa_Windows_v3.3.0.zip",
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
    print("\n🎉 HOÀN TẤT PHÁT HÀNH GÓI CÀI ĐẶT V3.3.0 LÊN GITHUB RELEASE!")
