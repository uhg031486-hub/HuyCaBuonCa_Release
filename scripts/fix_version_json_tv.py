import subprocess
import requests
import json
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

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

headers = {
    "Authorization": f"token {TOKEN}",
    "User-Agent": "Antigravity-Release-Bot",
    "Accept": "application/vnd.github.v3+json",
}

# 1. Kiểm tra các release gần nhất
rel_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
res = requests.get(rel_url, headers=headers)
if res.status_code == 200:
    rels = res.json()
    print(f"Tổng số releases: {len(rels)}")
    for r in rels[:3]:
        print(f"Tag: {r.get('tag_name')} | Name: {r.get('name')}")
        assets = [a['name'] for a in r.get('assets', [])]
        print(f"  Assets: {assets}")

# 2. Cập nhật version.json với ĐẦY ĐỦ CẢ tvApkUrl VÀ apkUrl
new_version_info = {
    "versionCode": 26,
    "versionName": "3.3.2",
    "title": "Bản Cập Nhật Huy Cá v3.3.2",
    "changelog": "1. Khắc phục triệt để lịch thi đấu bóng đá: Hiển thị đầy đủ 2 biểu tượng (logo Đội Nhà & Đội Khách), chữ VS vàng kim và giờ thi đấu chuẩn quốc tế.\n2. Tối ưu bảng chọn 4 Server phát sóng trực tiếp (Thập Cẩm, Xôi Lạc, Về Bờ, Vệ Tinh).\n3. Sửa lỗi nhận diện bản cập nhật tự động cho Smart TV v2.8.",
    "tvApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/v3.3.2/HuyCa_TV_v3.3.2.apk",
    "apkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/v3.3.2/HuyCa_TV_v3.3.2.apk",
    "mobileApkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/v3.3.2/HuyCa_Mobile_v3.3.2.apk",
    "lgIpkUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/v3.3.2/HuyCa_LG_webOS_v3.3.2.ipk",
    "windowsZipUrl": f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/v3.3.2/HuyCa_Windows_v3.3.2.zip",
    "forceUpdate": False
}

v_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
v_res = requests.get(v_url, headers=headers)
sha = v_res.json().get("sha") if v_res.status_code == 200 else None

b64_content = base64.b64encode(json.dumps(new_version_info, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
payload = {
    "message": "fix(updater): bổ sung tvApkUrl và apkUrl cho bản cập nhật Smart TV v2.8 -> v3.3.2",
    "content": b64_content,
    "branch": "main"
}
if sha:
    payload["sha"] = sha

put_res = requests.put(v_url, headers=headers, json=payload)
if put_res.status_code in [200, 201]:
    print(f"✅ ĐÃ CẬP NHẬT THÀNH CÔNG version.json TRÊN NHÁNH MAIN! SHA: {put_res.json().get('commit', {}).get('sha', '')[:7]}")
else:
    print(f"❌ Thất bại: {put_res.status_code} - {put_res.text}")
