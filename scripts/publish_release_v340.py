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
TAG = "v3.4.0"
TITLE = "Huy Cá v3.4.0 - Tự Động Làm Mới Kho Phim Ngắn (Tab 505 Mới Lên Sóng + Xoay Vòng Đa Nguồn)"

BODY = """### 🚀 Bản Phát Hành Huy Cá v3.4.0 - Làm Mới Toàn Diện Kho Phim Ngắn (Vertical Short Dramas)

#### 🌟 Các Nâng Cấp & Sửa Lỗi Đột Phá Trên Phiên Bản v3.4.0:
1. **Tự Động Xoay Vòng Phiên & Ưu Tiên Tab `505` (Mới Lên Sóng) + `/foryou/feed`**:
   - Bổ sung cơ chế `getRotationSeed()` và `refreshSession()` xoay vòng động theo khung giờ 4 tiếng và làm mới phiên `deviceId`/`sessionId`.
   - Mục **🔥 Đề Xuất Cho Bạn (`freereels://foryou`)** ưu tiên lấy trực tiếp từ **Tab `505` (Mới Lên Sóng)** kết hợp luồng đề xuất động **`/foryou/feed`** và **`Tab 503`** theo offset xoay vòng.
   - Bấm nút **🔄 Cập Nhật** trên thanh công cụ sẽ đổi ngay danh sách phim ngắn mới tức thì.
2. **Xoay Vòng Đa Từ Khóa Động Cho Cả 5 Nguồn Phụ (`ReelShort`, `DramaBox`, `ShortMax`, `AI Cinema`, `GoodShort`)**:
   - Tự động xoay vòng 2 từ khóa song song (`targetKw1`, `targetKw2`) và đan xen luồng phim mới theo offset động để Trang 1 luôn hiển thị các bộ phim ngắn mới mẻ.
3. **Cơ Chế Dự Phòng Tự Động Cho `🎙️ Nguồn Gà Mờ Mê Phim (Thuyết Minh)` (`fallbackGenreToFreeReels`)**:
   - Khi máy chủ gốc `gamomephim.com` gặp sự cố DNS / HTTP 530, tự động ánh xạ toàn bộ 15 thể loại sang kho phim ngắn Lồng Tiếng / Thuyết Minh & Phụ Đề tương ứng của FreeReels, đảm bảo không có danh mục nào bị trống.
4. **Thanh Tiến Trình (Seekbar) Chuẩn YouTube Tinh Gọn**:
   - Giữ nguyên giao diện thanh tiến trình đỏ sạch sẽ, không viền xanh rối mắt, hỗ trợ đầy đủ điều khiển chuột, cảm ứng và Remote TV D-Pad.

#### 📦 Trọn Bộ Cài Đặt Phát Hành v3.4.0 Chuẩn Thương Hiệu Duy Nhất Huy Cá:
- **Android Smart TV & TV Box**: `HuyCa_TV_v3.4.0.apk` / `HuyCa_TV_v3.4.apk`
- **Android Mobile**: `HuyCa_Mobile_v3.4.0.apk` / `HuyCa_Mobile_v3.4.apk`
- **LG Smart TV (webOS)**: `HuyCa_LG_webOS_v3.4.0.ipk` / `HuyCa_LG_webOS_v3.4.ipk`
- **Windows Desktop**: `HuyCa_Windows_v3.4.0.zip` / `HuyCa_Windows_v3.4.zip`
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
        "versionCode": 34,
        "versionName": "3.4.0",
        "title": "Bản Cập Nhật Huy Cá v3.4.0 - Tự Động Làm Mới Kho Phim Ngắn & Dự Phòng Toàn Diện",
        "changelog": "1. Ưu tiên luồng Phim Mới Lên Sóng (Tab 505) và đề xuất động (/foryou/feed) xoay vòng tự động cho mục Phim Ngắn.\n2. Xoay vòng đa từ khóa động cho toàn bộ 5 nguồn phụ (ReelShort, DramaBox, ShortMax, AI Cinema, GoodShort).\n3. Bổ sung cơ chế dự phòng tự động fallbackGenreToFreeReels cho toàn bộ 15 thể loại Gà Mờ Mê Phim khi máy chủ gốc gặp sự cố.\n4. Hỗ trợ làm mới danh sách phim ngắn tức thì khi bấm nút Cập Nhật.",
        "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.4.0.apk",
        "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Mobile_v3.4.0.apk",
        "tvApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.4.0.apk",
        "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_LG_webOS_v3.4.0.ipk",
        "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Windows_v3.4.0.zip",
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
        "HuyCa_TV_v3.4.0.apk",
        "HuyCa_TV_v3.4.apk",
        "HuyCa_Mobile_v3.4.0.apk",
        "HuyCa_Mobile_v3.4.apk",
        "HuyCa_LG_webOS_v3.4.0.ipk",
        "HuyCa_LG_webOS_v3.4.ipk",
        "HuyCa_Windows_v3.4.0.zip",
        "HuyCa_Windows_v3.4.zip"
    ]

    print("\n3. Bắt đầu tải lên các tệp phát hành chuẩn thương hiệu Huy Cá...")
    for f in assets:
        upload_asset(rel, f)

    print("\n🎉 HOÀN TẤT XUẤT BẢN GITHUB RELEASE V3.4.0!")
    print(f"🔗 Link Release: https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/tag/{TAG}")

if __name__ == "__main__":
    main()
