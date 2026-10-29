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
TAG = "v3.3.3"
TITLE = "Huy Cá v3.3.3 - Nâng Cấp Toàn Diện Kho Phim Ngắn: Đầy Đủ 17 Bộ Lọc Gà Mờ Mê Phim, Phân Trang Vô Cực & Sửa Triệt Để Phụ Đề"

BODY = """### 🚀 Bản Phát Hành Huy Cá v3.3.3 - Nâng Cấp Toàn Diện Kho Phim Ngắn & Phụ Đề Đa Nền Tảng

#### 🌟 Các Cải Tiến Đột Phá Trên Phiên Bản v3.3.3:
1. **Khắc Phục Toàn Diện Nguồn Gà Mờ Mê Phim (GaMoMePhim)**:
   - **Bổ sung đầy đủ 17 bộ lọc chuyên sâu**: Phim Mới Cập Nhật, Bảng Xếp Hạng Thịnh Hành, Cưới Trước Yêu Sau, Gương Vỡ Lại Lành & Ngược Tâm, Yêu Thầm & Ngọt Sủng, Tiểu Kịch Hiện Đại, Trọng Sinh & Báo Thù, Xuyên Không, Cổ Trang, Hài Hước, Trà Xanh Nam, Chữa Lành, Thanh Xuân Vườn Trường, Dân Quốc, Niên Đại Thập Niên...
   - **Bộ Parser Vạn Năng (Universal Parser)**: Nhận diện chính xác 100% cấu trúc thẻ của mọi chuyên mục, bao gồm cả Bảng Xếp Hạng không chứa thuộc tính `title` trước đây.
   - **Cơ chế Phân Trang Vô Cực (Infinite Fallback)**: Với các thể loại ít phim (Trọng Sinh, Dân Quốc...), khi người dùng cuộn xuống trang 2 trở đi, hệ thống tự động gối đầu và nạp tiếp các phim mới nhất từ kho phim, đảm bảo không bao giờ bị nghẽn hay ngừng nạp.

2. **Khắc Phục Triệt Để Luồng Phụ Đề Phim Ngắn (Subtitles)**:
   - **Bản Web**: Tự động chuyển đổi SRT sang WebVTT Blob URL cho thẻ `<track>` HTML5 kết hợp bộ Cues Realtime Parser hiển thị phụ đề to rõ, chuẩn phụ đề tiếng Việt.
   - **Android TV & Mobile (ExoPlayer Media3)**: Áp dụng cơ chế kết hợp `MergingMediaSource` + `SingleSampleMediaSource` tích hợp trực tiếp luồng phụ đề SubRip vào video, hiển thị sắc nét viền đen trên `SubtitleView`.

3. **Đồng Bộ Hoàn Hảo Toàn Bộ Bộ Lọc Đa Nền Tảng**:
   - Đồng bộ đầy đủ 7 Sub-Sources phim ngắn trên Android TV, Mobile, webOS và Web.
   - Đồng bộ 18 bộ lọc Kênh Truyền Hình (XEMTIVI) chuẩn xác.

4. **Trọn Bộ Cài Đặt Phát Hành v3.3.3**:
   - **Android TV Box & Smart TV**: `HuyCa_TV_v3.3.3.apk` / `HuyCa_TV_v3.3.apk`
   - **Android Mobile**: `HuyCa_Mobile_v3.3.3.apk` / `HuyCa_Mobile_v3.3.apk`
   - **LG Smart TV (webOS)**: `HuyCa_LG_webOS_v3.3.3.ipk` / `HuyCa_LG_webOS_v3.3.ipk`
   - **Windows Desktop**: `HuyCa_Windows_v3.3.3.zip` / `HuyCa_Windows_v3.3.zip`
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
        "versionCode": 27,
        "versionName": "3.3.3",
        "title": "Bản Cập Nhật Huy Cá v3.3.3",
        "changelog": "1. Bổ sung đầy đủ 17 bộ lọc chuyên sâu cho kho Phim Ngắn Gà Mờ Mê Phim.\n2. Phân trang vô cực thông minh: Cuộn kéo phim mượt mà không bao giờ thiếu phim.\n3. Khắc phục triệt để hiển thị phụ đề tiếng Việt phim ngắn.\n4. Đồng bộ hoàn hảo đa nền tảng.",
        "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.3.3.apk",
        "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Mobile_v3.3.3.apk",
        "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_LG_webOS_v3.3.3.ipk",
        "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Windows_v3.3.3.zip",
        "forceUpdate": False
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
    res = requests.get(url, headers=HEADERS)
    sha = res.json().get("sha") if res.status_code == 200 else None

    b64_content = base64.b64encode(json.dumps(new_version_info, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"release: nâng cấp version.json lên {TAG} (Huy Cá v3.3.3)",
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
        "HuyCa_TV_v3.3.3.apk",
        "HuyCa_TV_v3.3.apk",
        "HuyCa_Mobile_v3.3.3.apk",
        "HuyCa_Mobile_v3.3.apk",
        "HuyCa_LG_webOS_v3.3.3.ipk",
        "HuyCa_LG_webOS_v3.3.ipk",
        "HuyCa_Windows_v3.3.3.zip",
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
    print("\n🎉 HOÀN TẤT PHÁT HÀNH GÓI CÀI ĐẶT V3.3.3 LÊN GITHUB RELEASE!")
