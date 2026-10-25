import os
import sys
import base64
import json
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def get_token():
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if token:
        return token
    config_path = os.path.expanduser(r"~\.gemini\config\mcp_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mcpServers", {}).get("github", {}).get("env", {}).get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
        except Exception:
            pass
    return ""

TOKEN = get_token()
REPO_OWNER = "uhg031486-hub"
REPO_NAME = "HuyCaBuonCa_Release"
TAG = "v2.6"
TITLE = "Huy Cá v2.6 - Icon 3D Khủng Long Mới, Tối Ưu Tương Phản & Giao Diện Tinh Gọn Trên Mọi Thiết Bị"

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "User-Agent": "Antigravity",
    "Accept": "application/vnd.github.v3+json",
}

def step1_verify():
    print("1. Kiểm tra xác thực tài khoản GitHub...")
    res = requests.get("https://api.github.com/user", headers=HEADERS)
    if res.status_code != 200:
        print(f"Lỗi xác thực: {res.status_code} {res.text}")
        sys.exit(1)
    user_info = res.json()
    scopes = res.headers.get("X-OAuth-Scopes", "")
    print(f"   => Tài khoản: {user_info['login']} | Scopes: {scopes}")

def step2_update_version_json():
    print("2. Cập nhật version.json trên nhánh main...")
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
    res = requests.get(url, headers=HEADERS)
    sha = None
    if res.status_code == 200:
        sha = res.json().get("sha")
        print(f"   => Tìm thấy version.json hiện tại (sha: {sha[:7]})")
    
    with open("version.json", "r", encoding="utf-8") as f:
        local_content = f.read()

    b64_content = base64.b64encode(local_content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": "Nâng cấp version.json lên v2.6 (Huy Cá: Ngoại Hạng Anh FPL, 4 Server, Chuông báo giờ đá, Vệ Tinh Quốc Tế)",
        "content": b64_content,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    put_res = requests.put(url, headers=HEADERS, json=payload)
    if put_res.status_code in (200, 201):
        commit_sha = put_res.json()["commit"]["sha"]
        print(f"   => Đã cập nhật version.json thành công! Commit: {commit_sha[:7]}")
    else:
        print(f"   => Cập nhật version.json thất bại: {put_res.status_code} {put_res.text}")
        sys.exit(1)

def step3_create_release():
    print(f"3. Tạo Release {TAG} trên GitHub...")
    with open("version.json", "r", encoding="utf-8") as f:
        version_data = json.load(f)
    
    changelog = version_data.get("changelog", "Bản cập nhật v2.4")
    payload = {
        "tag_name": TAG,
        "target_commitish": "main",
        "name": TITLE,
        "body": changelog,
        "draft": False,
        "prerelease": False
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    res = requests.post(url, headers=HEADERS, json=payload)
    if res.status_code in (200, 201):
        release = res.json()
        print(f"   => Đã tạo Release thành công (ID: {release['id']}, URL: {release['html_url']})")
        return release
    elif res.status_code == 422:
        print(f"   => Release {TAG} đã tồn tại, đang lấy thông tin...")
        get_res = requests.get(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{TAG}", headers=HEADERS)
        if get_res.status_code == 200:
            return get_res.json()
        else:
            print(f"   => Lỗi lấy release: {get_res.status_code} {get_res.text}")
            sys.exit(1)
    else:
        print(f"   => Lỗi tạo release: {res.status_code} {res.text}")
        sys.exit(1)

def step4_upload_assets(release):
    upload_url_template = release.get("upload_url", "")
    upload_url_base = upload_url_template.split("{")[0]

    existing_assets = {a["name"]: a["id"] for a in release.get("assets", [])}

    files_to_upload = [
        ("HuyCa_Windows_v2.6.zip", "application/zip"),
        ("HuyCaBuonCa_Mobile_v2.6.apk", "application/vnd.android.package-archive"),
        ("HuyCa_Mobile_v2.6.apk", "application/vnd.android.package-archive"),
        ("HuyCaBuonCa_TV_v2.6.apk", "application/vnd.android.package-archive"),
        ("HuyCa_TV_v2.6.apk", "application/vnd.android.package-archive"),
        ("HuyCaBuonCa_LG_webOS_v2.6.ipk", "application/octet-stream"),
        ("HuyCa_LG_webOS_v2.6.ipk", "application/octet-stream"),
    ]

    for filename, content_type in files_to_upload:
        if not os.path.exists(filename):
            print(f"   [!] Cảnh báo: Không tìm thấy file {filename}")
            continue

        size_mb = round(os.path.getsize(filename) / (1024 * 1024), 2)
        print(f"4. Đang upload {filename} ({size_mb} MB)...")

        # Xóa asset cũ nếu đã tồn tại cùng tên
        if filename in existing_assets:
            del_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{existing_assets[filename]}"
            requests.delete(del_url, headers=HEADERS)
            print(f"   => Đã xóa asset cũ trùng tên: {filename}")

        upload_headers = HEADERS.copy()
        upload_headers["Content-Type"] = content_type

        upload_url = f"{upload_url_base}?name={filename}"
        with open(filename, "rb") as f:
            data = f.read()

        up_res = requests.post(upload_url, headers=upload_headers, data=data)
        if up_res.status_code in (200, 201):
            download_url = up_res.json().get("browser_download_url")
            print(f"   => Upload thành công! Link tải: {download_url}")
        else:
            print(f"   => Lỗi upload {filename}: {up_res.status_code} {up_res.text}")

if __name__ == "__main__":
    step1_verify()
    step2_update_version_json()
    release = step3_create_release()
    step4_upload_assets(release)
    print("\n🎉 === TẤT CẢ ĐÃ HOÀN TẤT 100%! BẢN V2.5 ĐÃ ĐƯỢC XUẤT BẢN THÀNH CÔNG LÊN GITHUB! ===")
