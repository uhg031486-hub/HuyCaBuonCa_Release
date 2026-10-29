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
TAG = "v3.3.2"
TITLE = "Huy Cá v3.3.2 - Nâng Cấp Toàn Diện Lịch Thi Đấu Bóng Đá: Hiển Thị Đầy Đủ 2 Biểu Tượng (Logo Đội Nhà & Đội Khách)"

BODY = """### 🚀 Bản Phát Hành Huy Cá v3.3.2 - Nâng Cấp Giao Diện Lịch Thi Đấu Bóng Đá Chuẩn Đẳng Cấp

#### 🌟 Các Cải Tiến Đột Phá Trên Phiên Bản v3.3.2:
1. **Nâng Cấp Giao Diện Lịch Thi Đấu Bóng Đá Đầy Đủ 2 Biểu Tượng (Head-to-Head Versus)**:
   - Khắc phục triệt để tình trạng thẻ trận đấu trước đây chỉ hiển thị duy nhất 1 logo (đội nhà).
   - Thiết kế lại thẻ trận đấu chuyên nghiệp:
     - **Cột Đội Nhà (Home Team)**: Khung tròn chứa logo đội nhà sắc nét + Tên đội nhà in đậm rõ ràng.
     - **Khu Vực Trung Tâm**: Chữ **VS** màu vàng kim rực rỡ (hoặc Tỷ số trận đấu nếu đang đá LIVE / Hết giờ FT) + Thời gian thi đấu chi tiết (`19:30 • 31/10`).
     - **Cột Đội Khách (Away Team)**: Khung tròn chứa logo đội khách sắc nét + Tên đội khách in đậm rõ ràng.
     - **Header**: Tên giải đấu (`🏆 UEFA Champions League`, `🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh`, `🇪🇸 La Liga`...) + Tag trạng thái (`EPL` / `🔴 LIVE`).
     - **Footer**: `⚡ 4 Server Trực Tiếp` + Nút `🔔 Nhắc Tôi` / `🔔 Đã Đặt`.
   - Bổ sung logo 2 đội bóng trực tiếp vào Modal chọn 4 Server phát sóng (Thập Cẩm HD, Xôi Lạc HD, Về Bờ HD, Vệ Tinh Trực Tiếp).
   - Bổ sung logo chuẩn ESPN độ phân giải cao cho toàn bộ kho trận đấu thời gian thực và fallback.

2. **Kế Thừa Hoàn Hảo Toàn Bộ Tính Năng Từ v3.3.1**:
   - Khắc phục 100% lỗi "ngồi nhầm lớp" trong Anime và Phim Ngắn.
   - Thanh chọn Server Phụ Đề / Thuyết Minh / Lồng Tiếng trên Android TV và Mobile.
   - Kho truyền hình trực tiếp 100+ kênh sạch không quảng cáo.

3. **Đồng Bộ Hoàn Hảo Trên Cả 5 Nền Tảng**:
   - **Android TV Box & Smart TV**: `HuyCa_TV_v3.3.2.apk` / `HuyCa_TV_v3.3.apk`
   - **Android Mobile**: `HuyCa_Mobile_v3.3.2.apk` / `HuyCa_Mobile_v3.3.apk`
   - **LG Smart TV (webOS)**: `HuyCa_LG_webOS_v3.3.2.ipk` / `HuyCa_LG_webOS_v3.3.ipk`
   - **Windows Desktop**: `HuyCa_Windows_v3.3.2.zip` / `HuyCa_Windows_v3.3.zip`
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
        "versionCode": 26,
        "versionName": "3.3.2",
        "title": "Bản Cập Nhật Huy Cá v3.3.2",
        "changelog": "1. Nâng cấp lịch thi đấu bóng đá: Hiển thị đầy đủ 2 biểu tượng (logo Đội Nhà & Đội Khách), chữ VS và giờ thi đấu chuẩn quốc tế.\n2. Tối ưu giao diện thẻ trận đấu và modal chọn 4 Server trực tiếp.\n3. Đồng bộ hoàn hảo đa nền tảng.",
        "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.3.2.apk",
        "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Mobile_v3.3.2.apk",
        "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_LG_webOS_v3.3.2.ipk",
        "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Windows_v3.3.2.zip",
        "forceUpdate": False
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
    res = requests.get(url, headers=HEADERS)
    sha = res.json().get("sha") if res.status_code == 200 else None

    b64_content = base64.b64encode(json.dumps(new_version_info, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"release: nâng cấp version.json lên {TAG} (Huy Cá v3.3.2)",
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
        "HuyCa_TV_v3.3.2.apk",
        "HuyCa_TV_v3.3.apk",
        "HuyCa_Mobile_v3.3.2.apk",
        "HuyCa_Mobile_v3.3.apk",
        "HuyCa_LG_webOS_v3.3.2.ipk",
        "HuyCa_LG_webOS_v3.3.ipk",
        "HuyCa_Windows_v3.3.2.zip",
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
    print("\n🎉 HOÀN TẤT PHÁT HÀNH GÓI CÀI ĐẶT V3.3.2 LÊN GITHUB RELEASE!")
