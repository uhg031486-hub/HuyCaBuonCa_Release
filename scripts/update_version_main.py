import subprocess
import requests
import base64

res = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
token = res.split("https://")[1].split("@github.com")[0]

REPO_OWNER = "uhg031486-hub"
REPO_NAME = "HuyCaBuonCa_Release"

headers = {
    "Authorization": f"token {token}",
    "User-Agent": "Antigravity",
    "Accept": "application/vnd.github.v3+json",
}

url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/version.json"
r = requests.get(url, headers=headers)
sha = r.json().get("sha") if r.status_code == 200 else None

with open("version.json", "r", encoding="utf-8") as f:
    content = f.read()

payload = {
    "message": "Nâng cấp version.json lên v2.7 (Kho Phim Ngắn Gà Mờ Mê Phim & Icon chuẩn đẹp)",
    "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    "branch": "main"
}
if sha:
    payload["sha"] = sha

put_res = requests.put(url, headers=headers, json=payload)
print("Update version.json on main status:", put_res.status_code)
