import os
import sys
import subprocess
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def get_token():
    try:
        res = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
        if "@github.com" in res and "https://" in res:
            # https://TOKEN@github.com/...
            token = res.split("https://")[1].split("@github.com")[0]
            if token.startswith("ghp_") or token.startswith("github_pat_"):
                return token
    except Exception as e:
        print("Lỗi đọc git remote:", e)
    return ""

TOKEN = get_token()
REPO_OWNER = "uhg031486-hub"
REPO_NAME = "HuyCaBuonCa_Release"
TAG = "v2.7"
TITLE = "Huy Cá v2.7 - Tích Hợp Kho Phim Ngắn Mới (Gà Mờ Mê Phim Thuyết Minh & Vietsub), Tinh Chỉnh Icon Chuẩn Đẹp Tự Nhiên"

BODY = """### 🎉 Bản Cập Nhật Huy Cá v2.7 - Kho Phim Ngắn Mới & Tinh Chỉnh Biểu Tượng Ứng Dụng

#### 🌟 Các Điểm Nổi Bật Trên Phiên Bản v2.7:
1. **Tích Hợp Kho Phim Ngắn / Tiểu Kịch Mới (Gà Mờ Mê Phim)**:
   - Bổ sung nguồn Gà Mờ Mê Phim trực tiếp vào nút **"📱 PHIM NGẮN"** trên cả 4 nền tảng (Android TV, Android Mobile, Windows PC, LG webOS).
   - Kho tiểu kịch đồ sộ với hàng trăm bộ phim ngắn hot nhất thị trường (Tổng tài, Trọng sinh, Hào môn, Cung đấu, Chiến thần...).
   - Đầy đủ cả 2 bản: **🎙️ Thuyết Minh Tiếng Việt** và **🇻🇳 Vietsub**, chất lượng Full HD sắc nét, phát mượt mà không quảng cáo.
   - Trọn bộ phim được mở khóa 100% không giới hạn, không cần tài khoản hay nạp xu.
2. **Tinh Chỉnh Biểu Tượng Ứng Dụng (Icon) Chuẩn Đẹp Tự Nhiên**:
   - Đưa icon 3D Khủng Long Bạo Chúa về kích thước vừa vặn, cân đối, tỉ lệ tự nhiên trên tất cả các thiết bị.
   - Không còn bị phóng to bè viền hay vỡ hình, tạo cảm giác sang trọng và hài hòa trên launcher TV cũng như màn hình điện thoại.
3. **Hoàn Thiện Bộ 3 Nguồn Phim Ngắn Đa Năng**:
   - **Gà Mờ Mê Phim**: Thuyết minh tiếng Việt chuẩn, trọn bộ Full HD.
   - **FreeReels Dọc**: Màn hình dọc nguyên bản 9:16 mở khóa 100% tất cả các tập.
   - **Tiểu Kịch Vietsub (KKPhim HD)**: Phim ngắn chất lượng cao tuyển chọn.

#### 📦 Danh Sách Tệp Tải Về Cho Từng Nền Tảng:
* **Android TV**: `HuyCaBuonCa_TV_v2.7.apk` / `HuyCa_TV_v2.7.apk`
* **Android Mobile**: `HuyCaBuonCa_Mobile_v2.7.apk` / `HuyCa_Mobile_v2.7.apk`
* **LG Smart TV (webOS)**: `HuyCaBuonCa_LG_webOS_v2.7.ipk` / `HuyCa_LG_webOS_v2.7.ipk`
* **Windows PC**: `HuyCaBuonCa_Windows_v2.7.zip` / `HuyCa_Windows_v2.7.zip`
"""

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "User-Agent": "Antigravity",
    "Accept": "application/vnd.github.v3+json",
}

def create_or_get_release():
    print(f"1. Kiểm tra Release {TAG} trên GitHub...")
    rel_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{TAG}"
    res = requests.get(rel_url, headers=HEADERS)
    if res.status_code == 200:
        print("  -> Release đã tồn tại!")
        return res.json()
    
    print(f"2. Tạo mới Release {TAG}...")
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
        print("  -> Tạo Release thành công!")
        return create_res.json()
    else:
        print(f"  -> Lỗi tạo Release: {create_res.status_code} - {create_res.text}")
        return None

def upload_assets(release):
    upload_url = release.get("upload_url", "").replace("{?name,label}", "")
    existing_assets = {a["name"]: a["id"] for a in release.get("assets", [])}

    files = [
        "HuyCaBuonCa_TV_v2.7.apk",
        "HuyCa_TV_v2.7.apk",
        "HuyCaBuonCa_Mobile_v2.7.apk",
        "HuyCa_Mobile_v2.7.apk",
        "HuyCaBuonCa_LG_webOS_v2.7.ipk",
        "HuyCa_LG_webOS_v2.7.ipk",
        "HuyCaBuonCa_Windows_v2.7.zip",
        "HuyCa_Windows_v2.7.zip"
    ]

    for fname in files:
        if not os.path.exists(fname):
            print(f"  [!] Bỏ qua {fname} (không tìm thấy file)")
            continue

        if fname in existing_assets:
            print(f"  [-] Xóa asset cũ {fname} (id: {existing_assets[fname]})...")
            del_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{existing_assets[fname]}"
            requests.delete(del_url, headers=HEADERS)

        size_mb = round(os.path.getsize(fname) / (1024 * 1024), 2)
        print(f"  [+] Đang tải lên {fname} ({size_mb} MB)...")
        headers = {
            "Authorization": f"token {TOKEN}",
            "User-Agent": "Antigravity",
            "Content-Type": "application/octet-stream"
        }
        params = {"name": fname}
        with open(fname, "rb") as f:
            up_res = requests.post(upload_url, headers=headers, params=params, data=f)
            if up_res.status_code in [200, 201]:
                print(f"      -> Thành công tải lên {fname}!")
            else:
                print(f"      -> Thất bại: {up_res.status_code} - {up_res.text}")

if __name__ == "__main__":
    rel = create_or_get_release()
    if rel:
        upload_assets(rel)
        print("\n🎉 Hoàn tất toàn bộ quy trình xuất bản GitHub Release v2.7!")
        print(f"URL: {rel.get('html_url')}")
