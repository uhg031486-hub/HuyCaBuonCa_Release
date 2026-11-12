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
TAG = "v3.4.1"
TITLE = "Huy Cá v3.4.1 - Tích Hợp Kho Phim Dài AI & Phim Ngắn Gộp Trọn Bộ (Full 1-3 Giờ)"

BODY = """### 🚀 Bản Phát Hành Huy Cá v3.4.1 - Kho Phim Dài AI & Tiểu Kịch Gộp Trọn Bộ (Full 1-3 Giờ)

#### 🌟 Các Tính Năng Mới Trên Phiên Bản v3.4.1:
1. **Tích Hợp `YouTubeAIClient` — Kho Phim Dài AI & Tiểu Kịch Gộp Trọn Bộ (Full 1-3 Giờ)**:
   - Bổ sung bộ máy tìm kiếm và trích xuất trực tiếp các bộ phim dài AI (1–4 giờ+) và phim ngắn tiểu kịch gộp trọn bộ thuyết minh Tiếng Việt trên YouTube (`sp=EgIYAg%3D%3D` >20 phút, lọc bỏ livestream).
   - Nâng cấp toàn diện mục **🤖 Nguồn AI Cinema (`short_src://aicinema`)** với 5 danh mục phim dài:
     * `🤖 Phim Dài AI Trọn Bộ (Full 1-3 Giờ)` (`yt_ai://ai_all`)
     * `⚔️ AI 3D Tu Tiên & Huyền Huyễn (Full)` (`yt_ai://ai_tutien`)
     * `🎨 AI Hoạt Hình & Xuyên Không Hệ Thống` (`yt_ai://ai_manhwa`)
     * `🌌 AI Khoa Học Viễn Tưởng & Tương Lai` (`yt_ai://ai_scifi`)
     * `📺 Phim Ngắn Gộp Trọn Bộ (Full 1-3 Giờ)` (`yt_ai://short_full`)
   - Bổ sung tab **📺 Phim Ngắn Gộp Trọn Bộ (Full 1-3h)** ngay trong **💎 Nguồn FreeReels** và **🎙️ Nguồn Gà Mờ Mê Phim** để người dùng xem trọn bộ từ đầu đến cuối không lo khóa tập.
2. **Tích Hợp Tìm Kiếm Toàn Cục & Trình Phát 16:9 Không Quảng Cáo**:
   - Hỗ trợ tìm kiếm phim dài AI & phim ngắn trọn bộ ngay trong ô Tìm Kiếm toàn cục.
   - Tối ưu trình phát `youtube-nocookie.com/embed` với thanh công cụ `↩️ Thoát`, `📑 Chọn Tập`, `🗔 Cửa Sổ Riêng` trên Web/Windows/LG webOS và `WebView` kèm `Referer` chuẩn trên Android Mobile & Android TV.

#### 📦 Trọn Bộ Cài Đặt Phát Hành v3.4.1 Chuẩn Thương Hiệu Duy Nhất Huy Cá:
- **Android Smart TV & TV Box**: `HuyCa_TV_v3.4.1.apk` / `HuyCa_TV_v3.4.apk`
- **Android Mobile**: `HuyCa_Mobile_v3.4.1.apk` / `HuyCa_Mobile_v3.4.apk`
- **LG Smart TV (webOS)**: `HuyCa_LG_webOS_v3.4.1.ipk` / `HuyCa_LG_webOS_v3.4.ipk`
- **Windows Desktop**: `HuyCa_Windows_v3.4.1.zip` / `HuyCa_Windows_v3.4.zip`
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
        "versionCode": 35,
        "versionName": "3.4.1",
        "title": "Bản Cập Nhật Huy Cá v3.4.1 - Kho Phim Dài AI & Phim Ngắn Gộp Trọn Bộ (Full 1-3 Giờ)",
        "changelog": "1. Tích hợp kho Phim Dài AI Trọn Bộ (Full 1-3 Giờ): AI 3D Tu Tiên, AI Manhwa Xuyên Không Hệ Thống, AI Khoa Học Viễn Tưởng.\n2. Bổ sung mục Phim Ngắn Gộp Trọn Bộ (Full 1-3 Giờ Thuyết Minh) xem liền mạch từ đầu đến cuối không khóa tập.\n3. Hỗ trợ tìm kiếm phim dài AI & phim trọn bộ trên toàn hệ thống (Web, Mobile, Android TV, LG webOS, Windows).",
        "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.4.1.apk",
        "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Mobile_v3.4.1.apk",
        "tvApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.4.1.apk",
        "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_LG_webOS_v3.4.1.ipk",
        "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Windows_v3.4.1.zip",
        "isMaintenanceLocked": False,
        "maintenanceMessage": "Hệ thống đang bảo trì định kỳ. Vui lòng quay lại sau!"
    }

    with open("version.json", "w", encoding="utf-8") as vf:
        json.dump(new_version_info, vf, indent=2, ensure_ascii=False)

    content_str = json.dumps(new_version_info, indent=2, ensure_ascii=False)
    b64_content = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")

    for branch in ["main", "master"]:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json?ref={branch}"
        res = requests.get(url, headers=HEADERS)
        sha = res.json().get("sha") if res.status_code == 200 else None

        put_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
        payload = {
            "message": f"chore(release): bump version.json to {TAG} on {branch}",
            "content": b64_content,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha

        put_res = requests.put(put_url, headers=HEADERS, json=payload)
        if put_res.status_code in [200, 201]:
            print(f" -> Đã cập nhật version.json trên nhánh '{branch}' thành công!")
        else:
            print(f" -> Lỗi cập nhật version.json trên nhánh '{branch}':", put_res.status_code, put_res.text)

def create_or_get_release():
    print(f"2. Tạo hoặc lấy thông tin GitHub Release cho tag {TAG}...")
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{TAG}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        print(" -> Release đã tồn tại, sử dụng release này.")
        return res.json()
    
    create_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    payload = {
        "tag_name": TAG,
        "target_commitish": "master",
        "name": TITLE,
        "body": BODY,
        "draft": False,
        "prerelease": False
    }
    create_res = requests.post(create_url, headers=HEADERS, json=payload)
    if create_res.status_code in [200, 201]:
        print(" -> Đã tạo GitHub Release mới thành công!")
        return create_res.json()
    else:
        print(" -> Lỗi tạo Release:", create_res.status_code, create_res.text)
        return None

def upload_asset(release, file_path, custom_name=None):
    asset_name = custom_name if custom_name else os.path.basename(file_path)
    if not os.path.exists(file_path):
        print(f" ⚠️ Không tìm thấy file: {file_path}, bỏ qua.")
        return

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f" -> Đang tải lên {asset_name} ({size_mb:.2f} MB)...")

    for asset in release.get("assets", []):
        if asset["name"] == asset_name:
            print(f"    Xóa asset cũ trùng tên: {asset['name']} (id: {asset['id']})...")
            del_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{asset['id']}"
            requests.delete(del_url, headers=HEADERS)

    upload_url_template = release["upload_url"]
    upload_url = upload_url_template.split("{")[0] + f"?name={asset_name}"

    headers = {
        "Authorization": f"token {TOKEN}",
        "User-Agent": "Antigravity-Release-Bot",
        "Content-Type": "application/octet-stream"
    }

    with open(file_path, "rb") as f:
        upload_res = requests.post(upload_url, headers=headers, data=f)

    if upload_res.status_code in [200, 201]:
        print(f"    ✅ Thành công tải lên: {asset_name}")
    else:
        print(f"    ❌ Lỗi tải lên {asset_name}:", upload_res.status_code, upload_res.text)

def main():
    if not TOKEN:
        print("Không tìm thấy token hợp lệ trong git remote.")
        return

    update_version_json()
    rel = create_or_get_release()
    if not rel:
        print("Không thể tiếp tục vì không có thông tin Release.")
        return

    assets = [
        "HuyCa_TV_v3.4.1.apk",
        "HuyCa_TV_v3.4.apk",
        "HuyCa_Mobile_v3.4.1.apk",
        "HuyCa_Mobile_v3.4.apk",
        "HuyCa_LG_webOS_v3.4.1.ipk",
        "HuyCa_LG_webOS_v3.4.ipk",
        "HuyCa_Windows_v3.4.1.zip",
        "HuyCa_Windows_v3.4.zip"
    ]

    print("\n3. Bắt đầu tải lên các tệp phát hành chuẩn thương hiệu Huy Cá...")
    for f in assets:
        upload_asset(rel, f)

    print("\n🎉 HOÀN TẤT XUẤT BẢN GITHUB RELEASE V3.4.1!")
    print(f"🔗 Link Release: https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/tag/{TAG}")

if __name__ == "__main__":
    main()
