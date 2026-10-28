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
            token = res.split("https://")[1].split("@github.com")[0]
            if token.startswith("ghp_") or token.startswith("github_pat_"):
                return token
    except Exception as e:
        print("Lỗi đọc git remote:", e)
    return ""

TOKEN = get_token()
REPO_OWNER = "uhg031486-hub"
REPO_NAME = "HuyCaBuonCa_Release"
TAG = "v2.8"
TITLE = "Huy Cá v2.8 - Lịch Thi Đấu Bóng Đá Real-Time ESPN, Tự Động Cập Nhật Tỉ Số & Đa Server Phát Sóng Trực Tiếp"

BODY = """### ⚽ Bản Cập Nhật Huy Cá v2.8 - Lịch Thi Đấu Bóng Đá Real-Time & Đa Server Trực Tiếp

#### 🌟 Các Điểm Nổi Bật Trên Phiên Bản v2.8:
1. **Kích Hoạt Bảng Lịch Thi Đấu Bóng Đá Thời Gian Thực (Real-Time)**:
   - Tích hợp cổng dữ liệu thể thao mở chính thức toàn cầu **ESPN Official Sports Scoreboard API** (`site.api.espn.com`).
   - Tự động cập nhật liên tục các trận đấu theo múi giờ Việt Nam (GMT+7) `HH:mm • dd/MM`.
   - Bao quát toàn bộ các giải đấu danh giá nhất hành tinh:
     * 🏴󠁧󠁢󠁥󠁮󠁧󠁿 **Ngoại Hạng Anh** (Premier League)
     * 🏆 **Cúp C1 Châu Âu** (UEFA Champions League)
     * 🇪🇸 **La Liga Tây Ban Nha**
     * 🇮🇹 **Serie A Ý**
2. **Cập Nhật Tỉ Số Trực Tiếp & Logo Câu Lạc Bộ Chuẩn HD**:
   - Trạng thái trận đấu trực quan: 🔴 Trực tiếp (kèm phút thi đấu) / ⏰ Giờ đá sắp diễn ra / 🏁 Hết giờ kết thúc trận đấu.
   - Hiển thị logo chuẩn độ phân giải cao của tất cả các câu lạc bộ (Manchester City, Arsenal, Liverpool, Real Madrid, Barcelona, Bayern Munich...).
   - Tự động ghim các trận đấu đang phát trực tiếp (🔴 LIVE) lên đầu danh sách.
3. **Đa Dạng Máy Chủ Phát Sóng Trực Tiếp (Multi-Server)**:
   - Bấm vào bất kỳ trận đấu nào để mở menu chọn 5 Server xem ngay:
     * 📡 **Server 1 (Kênh Vệ Tinh Trực Tiếp)**: True Premier Football 1 & 2 HD, Astro SuperSport 1 & 2 HD (1080p 50fps phát trực tiếp qua ExoPlayer không quảng cáo).
     * 🇻🇳 **Server 2 (Thể Thao Việt Nam)**: VTV6 Thể Thao HD (FPT), VTV5.
     * 🟢 **Server 3 (Thập Cẩm HD)**: Bình luận viên Tiếng Việt.
     * 🔵 **Server 4 (Xôi Lạc HD)**: Bình luận viên Tiếng Việt.
     * 🟣 **Server 5 (Về Bờ HD)**: Bình luận viên Tiếng Việt.
4. **Tối Ưu Hóa Giao Diện Điều Khiển Remote TV Box (D-Pad)**:
   - Mở Popup lịch thi đấu ngay khi bấm vào danh mục `⚽ Lịch Thi Đấu & Bóng Đá` trên màn hình TV Box.
   - Hiệu ứng viền vàng 3D sang trọng, nổi bật khi lướt điều khiển Remote qua các trận đấu.
   - Đồng bộ hoàn hảo trên cả 4 nền tảng: **Android TV, Android Mobile, Windows PC, LG Smart TV (webOS)**.

#### 📦 Danh Sách Tệp Tải Về Cho Từng Nền Tảng:
* **Android TV**: `HuyCaBuonCa_TV_v2.8.apk` / `HuyCa_TV_v2.8.apk`
* **Android Mobile**: `HuyCaBuonCa_Mobile_v2.8.apk` / `HuyCa_Mobile_v2.8.apk`
* **LG Smart TV (webOS)**: `HuyCaBuonCa_LG_webOS_v2.8.ipk` / `HuyCa_LG_webOS_v2.8.ipk`
* **Windows PC**: `HuyCaBuonCa_Windows_v2.8.zip` / `HuyCa_Windows_v2.8.zip`
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
        "HuyCaBuonCa_TV_v2.8.apk",
        "HuyCa_TV_v2.8.apk",
        "HuyCaBuonCa_Mobile_v2.8.apk",
        "HuyCa_Mobile_v2.8.apk",
        "HuyCaBuonCa_LG_webOS_v2.8.ipk",
        "HuyCa_LG_webOS_v2.8.ipk",
        "HuyCaBuonCa_Windows_v2.8.zip",
        "HuyCa_Windows_v2.8.zip"
    ]

    for fname in files:
        if not os.path.exists(fname):
            print(f"  [!] Bỏ qua {fname} (không tìm thấy file)")
            continue

        if fname in existing_assets:
            print(f"  [*] Xóa asset cũ: {fname}...")
            del_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{existing_assets[fname]}"
            requests.delete(del_url, headers=HEADERS)

        print(f"  [+] Đang tải lên asset: {fname} ({round(os.path.getsize(fname)/(1024*1024), 2)} MB)...")
        content_type = "application/octet-stream"
        if fname.endswith(".apk"):
            content_type = "application/vnd.android.package-archive"
        elif fname.endswith(".zip"):
            content_type = "application/zip"

        headers = {
            "Authorization": f"token {TOKEN}",
            "User-Agent": "Antigravity",
            "Content-Type": content_type
        }
        with open(fname, "rb") as f:
            up_res = requests.post(f"{upload_url}?name={fname}", headers=headers, data=f)
            if up_res.status_code in [200, 201]:
                print(f"      -> Tải lên thành công {fname}!")
            else:
                print(f"      -> Thất bại: {up_res.status_code} - {up_res.text}")

def main():
    if not TOKEN:
        print("Lỗi: Không tìm thấy GitHub Token!")
        sys.exit(1)

    print("=== BẮT ĐẦU XUẤT BẢN RELEASE v2.8 LÊN GITHUB ===")
    release = create_or_get_release()
    if release:
        print("3. Tải lên danh sách tài nguyên phiên bản v2.8...")
        upload_assets(release)
        print("\n=== XUẤT BẢN THÀNH CÔNG RELEASE v2.8 ===")
        print("Link Release:", release.get("html_url"))

if __name__ == "__main__":
    main()
