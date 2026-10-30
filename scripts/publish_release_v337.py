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
TAG = "v3.3.7"
TITLE = "Huy Cá v3.3.7 - Khắc Phục Triệt Để Lỗi Chạm Màn Hình Player Trên Di Động & Chuẩn Hóa Cảm Ứng Đa Nền Tảng"

BODY = """### 🚀 Bản Phát Hành Huy Cá v3.3.7 - Sửa Lỗi Cảm Ứng Màn Hình Player & Chuẩn Hóa Trải Nghiệm Di Động

#### 🌟 Các Nâng Cấp & Sửa Lỗi Trọng Yếu Trên Phiên Bản v3.3.7:
1. **Khắc Phục Hoàn Toàn Lỗi Chạm Màn Hình Player Không Hiện Thanh Điều Hướng (Controls Tàng Hình)**:
   - Điều tra và triệt tiêu nguyên nhân gốc rễ: Trên trình duyệt di động, cử chỉ chạm ngón tay (Tap) tự động phát sinh sự kiện `mousemove` và synthetic `click` liên tiếp khiến hàm toggle bị kích hoạt 2 lần trong 10ms (vừa mở đã lập tức đóng lại).
   - Thiết kế hệ thống điều khiển cảm ứng chuyên dụng `touchstart` / `touchend` đo đạc khoảng cách di chuyển (chống xung đột giữa chạm TAP và vuốt Scroll/Swipe), loại bỏ hoàn toàn sự cố "tàng hình controls".
2. **Bổ Sung Thanh Điều Khiển Tiện Ích Độc Quyền Cho Trình Phát Nhúng Embed Iframe (NguonC / Phim Rạp)**:
   - Thêm nút **Thoát (↩️)** và **Chọn Tập Phim (📑)** nổi bật trên thanh công cụ `embedHelperBar`. Người dùng trên điện thoại không còn bị kẹt cứng trong iframe mà luôn có thể điều hướng, chọn tập và quay lại một chạm.
3. **Thành Lập Tác Nhân AI Kiểm Thử Độc Lập Giả Lập Người Dùng Cuối (`end-user-qa-agent`)**:
   - Tự động kiểm thử bằng Playwright trên Viewport chuẩn iPhone 14 / Pixel (Touch Screen thật).
   - 100% các bài test: Chạm bật controls, Mở danh sách tập (Bottom Sheet), Chu kỳ Toggle, và Giao diện Embed Helper đều đạt **PASS 100%**.
4. **Trọn Bộ Cài Đặt Phát Hành v3.3.7 Chuẩn Thương Hiệu Duy Nhất Huy Cá**:
   - **Android Smart TV & TV Box**: `HuyCa_TV_v3.3.7.apk` / `HuyCa_TV_v3.3.apk`
   - **Android Mobile**: `HuyCa_Mobile_v3.3.7.apk` / `HuyCa_Mobile_v3.3.apk`
   - **LG Smart TV (webOS)**: `HuyCa_LG_webOS_v3.3.7.ipk` / `HuyCa_LG_webOS_v3.3.ipk`
   - **Windows Desktop**: `HuyCa_Windows_v3.3.7.zip` / `HuyCa_Windows_v3.3.zip`
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
        "versionCode": 31,
        "versionName": "3.3.7",
        "title": "Bản Cập Nhật Huy Cá v3.3.7",
        "changelog": "1. Khắc phục triệt để lỗi chạm màn hình video trên thiết bị di động không hiển thị thanh điều hướng/controls.\n2. Chuẩn hóa cơ chế xử lý cảm ứng (Touch & Click Ergonomics) tách biệt cử chỉ chạm TAP và vuốt, ngăn chặn hoàn toàn xung đột synthetic mousemove.\n3. Bổ sung thanh điều khiển Thoát & Chọn Tập phim nổi bật cho trình phát nhúng Embed Iframe trên điện thoại.\n4. Đồng bộ hoàn hảo trên Android TV, Mobile, LG webOS, Windows và Web.",
        "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.3.7.apk",
        "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Mobile_v3.3.7.apk",
        "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_LG_webOS_v3.3.7.ipk",
        "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Windows_v3.3.7.zip",
        "forceUpdate": False
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
    res = requests.get(url, headers=HEADERS)
    sha = res.json().get("sha") if res.status_code == 200 else None

    b64_content = base64.b64encode(json.dumps(new_version_info, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"release: nâng cấp version.json lên {TAG} (Huy Cá v3.3.7)",
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
    if res.status_code == 201:
        print(f" -> Tạo Release {TAG} thành công!")
        return res.json()
    else:
        print("Lỗi tạo release:", res.status_code, res.text)
        return None

def upload_assets(release_id):
    files_to_upload = [
        "HuyCa_TV_v3.3.7.apk",
        "HuyCa_TV_v3.3.apk",
        "HuyCa_Mobile_v3.3.7.apk",
        "HuyCa_Mobile_v3.3.apk",
        "HuyCa_LG_webOS_v3.3.7.ipk",
        "HuyCa_LG_webOS_v3.3.ipk",
        "HuyCa_Windows_v3.3.7.zip",
        "HuyCa_Windows_v3.3.zip"
    ]

    print(f"\n3. Bắt đầu tải lên {len(files_to_upload)} tệp phát hành lên Release {TAG}...")
    for filename in files_to_upload:
        if not os.path.exists(filename):
            print(f" ⚠️ Không tìm thấy file {filename}, bỏ qua.")
            continue
        size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f" -> Đang tải lên {filename} ({size_mb:.2f} MB)...")
        upload_url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets?name={filename}"
        
        # Xóa asset cũ nếu đã tồn tại
        list_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets"
        list_res = requests.get(list_url, headers=HEADERS)
        if list_res.status_code == 200:
            for item in list_res.json():
                if item.get("name") == filename:
                    print(f"    Gỡ bỏ asset cũ: {filename}...")
                    requests.delete(item.get("url"), headers=HEADERS)

        headers = {
            "Authorization": f"token {TOKEN}",
            "Content-Type": "application/octet-stream",
            "User-Agent": "Antigravity-Release-Bot"
        }
        with open(filename, "rb") as f:
            up_res = requests.post(upload_url, headers=headers, data=f)
            if up_res.status_code in (200, 201):
                print(f"    ✔ Thành công: {filename}")
            else:
                print(f"    ❌ Thất bại ({up_res.status_code}): {up_res.text}")

def main():
    if not TOKEN:
        print("❌ Không tìm thấy token GitHub.")
        return
    update_version_json()
    rel = create_or_get_release()
    if rel and "id" in rel:
        upload_assets(rel["id"])
        print(f"\n🎉 HOÀN TẤT PHÁT HÀNH TOÀN DIỆN HUY CÁ {TAG} LÊN GITHUB!")

if __name__ == "__main__":
    main()
