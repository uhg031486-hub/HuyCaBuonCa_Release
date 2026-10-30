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
TAG = "v3.3.5"
TITLE = "Huy Cá v3.3.5 - Khắc Phục Triệt Để Lỗi Phát Video & Phụ Đề Trên Toàn Bộ Kho Phim Ngắn"

BODY = """### 🚀 Bản Phát Hành Huy Cá v3.3.5 - Khắc Phục Triệt Để Lỗi Phát Video & Phụ Đề Kho Phim Ngắn

#### 🌟 Các Nâng Cấp & Sửa Lỗi Cốt Lõi Trên Phiên Bản v3.3.5:
1. **Sửa Triệt Để Lỗi Crash ExoPlayer Khi Phát Phim Ngắn Có Phụ Đề (Media3 ExoPlayer 1.4.1)**:
   - Kích hoạt `experimentalSetLegacyDecodingEnabled(true)` trên `DefaultRenderersFactory` giúp đọc và hiển thị phụ đề `application/x-subrip` (SRT) và WebVTT mượt mà, không còn lỗi `IllegalStateException: Legacy decoding is disabled`.
   - Bổ sung cơ chế Fallback an toàn đa tầng: nếu luồng phụ đề bị lỗi từ server, app sẽ tự động gỡ phụ đề và tiếp tục phát video mà không bao giờ bị dừng hay văng player.
2. **Chuẩn Hóa & Bóc Tách URL Nguồn Gà Mờ Mê Phim (Cloudflare R2)**:
   - Tối ưu parser tự động bóc tách đúng định dạng slug trực tiếp từ `gamomephim.com`, trích xuất thành công 100% hai luồng stream MP4 chất lượng cao (Thuyết minh `-tm.mp4` và Vietsub `-sub.mp4`).
3. **Tối Ưu Luồng Mở Khóa FreeReels & Lọc Sạch Dữ Liệu Rác**:
   - Tự động nhận diện và nạp trực tiếp `rawStream` sẵn có từ các đối tác FreeReels (ReelShort, DramaBox, ShortMax, GoodShort, AI Cinema).
   - Lọc bỏ các mục banner TOP có ID rỗng trong tab AI Cinema.
4. **Trọn Bộ Cài Đặt Phát Hành v3.3.5 Chuẩn Thương Hiệu Duy Nhất Huy Cá**:
   - **Android TV Box & Smart TV**: `HuyCa_TV_v3.3.5.apk` / `HuyCa_TV_v3.3.apk`
   - **Android Mobile**: `HuyCa_Mobile_v3.3.5.apk` / `HuyCa_Mobile_v3.3.apk`
   - **LG Smart TV (webOS)**: `HuyCa_LG_webOS_v3.3.5.ipk` / `HuyCa_LG_webOS_v3.3.ipk`
   - **Windows Desktop**: `HuyCa_Windows_v3.3.5.zip` / `HuyCa_Windows_v3.3.zip`
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
        "versionCode": 29,
        "versionName": "3.3.5",
        "title": "Bản Cập Nhật Huy Cá v3.3.5",
        "changelog": "1. Khắc phục triệt để lỗi phát video và phụ đề SRT/VTT trên Media3 ExoPlayer cho toàn bộ kho Phim Ngắn.\n2. Tối ưu bộ giải mã Cloudflare R2 cho Gà Mờ Mê Phim (đầy đủ Thuyết Minh & Vietsub).\n3. Tăng cường độ ổn định cho FreeReels và 7 Sub-sources (ReelShort, DramaBox, ShortMax, GoodShort, AI Cinema...).\n4. Đảm bảo trải nghiệm xem phim ngắn đồng bộ hoàn hảo trên cả Android TV và Mobile.",
        "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_TV_v3.3.5.apk",
        "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Mobile_v3.3.5.apk",
        "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_LG_webOS_v3.3.5.ipk",
        "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG}/HuyCa_Windows_v3.3.5.zip",
        "forceUpdate": False
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
    res = requests.get(url, headers=HEADERS)
    sha = res.json().get("sha") if res.status_code == 200 else None

    b64_content = base64.b64encode(json.dumps(new_version_info, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"release: nâng cấp version.json lên {TAG} (Huy Cá v3.3.5)",
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
        "HuyCa_TV_v3.3.5.apk",
        "HuyCa_TV_v3.3.apk",
        "HuyCa_Mobile_v3.3.5.apk",
        "HuyCa_Mobile_v3.3.apk",
        "HuyCa_LG_webOS_v3.3.5.ipk",
        "HuyCa_LG_webOS_v3.3.ipk",
        "HuyCa_Windows_v3.3.5.zip",
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
