import os
import sys
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
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f).get("mcpServers", {}).get("github", {}).get("env", {}).get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    return ""

TOKEN = get_token()
REPO = "uhg031486-hub/HuyCaBuonCa_Release"
TAG = "v2.4"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "User-Agent": "Antigravity",
    "Accept": "application/vnd.github.v3+json",
}

res = requests.get(f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}", headers=HEADERS)
if res.status_code != 200:
    print(f"Lỗi lấy release {TAG}: {res.status_code} {res.text}")
    sys.exit(1)

release = res.json()
upload_url_base = release["upload_url"].split("{")[0]

filename = "HuyCa_Windows_v2.4.zip"

# Xóa asset cũ nếu có
for a in release.get("assets", []):
    if a["name"] == filename:
        asset_id = a["id"]
        print(f"Đang xóa asset cũ trên GitHub (ID: {asset_id})...")
        del_res = requests.delete(f"https://api.github.com/repos/{REPO}/releases/assets/{asset_id}", headers=HEADERS)
        print(f"Kết quả xóa: {del_res.status_code}")

size_mb = round(os.path.getsize(filename) / (1024 * 1024), 2)
print(f"Đang tải lên {filename} ({size_mb} MB)...")

with open(filename, "rb") as f:
    data = f.read()

up_headers = HEADERS.copy()
up_headers["Content-Type"] = "application/zip"

up_res = requests.post(f"{upload_url_base}?name={filename}", headers=up_headers, data=data)
if up_res.status_code in (200, 201):
    dl_url = up_res.json().get("browser_download_url")
    print(f"🎉 TẢI LÊN THÀNH CÔNG! Link: {dl_url}")
else:
    print(f"Lỗi upload: {up_res.status_code} {up_res.text}")
    sys.exit(1)
