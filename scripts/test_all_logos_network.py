import json
import urllib.request
import sys
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

print(f"Bắt đầu kiểm tra toàn bộ 152 logos kênh TV...")

def check_logo(c):
    cid = c.get('id', '')
    name = c.get('name', '')
    grp = c.get('group', '')
    logo = c.get('logo', '')
    
    if not logo:
        return (cid, name, grp, logo, "MISSING_EMPTY", 0)
    
    if not logo.startswith('http'):
        return (cid, name, grp, logo, "RELATIVE_PATH", 0)
        
    req = urllib.request.Request(logo, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            ct = res.headers.get('content-type', '')
            return (cid, name, grp, logo, f"OK_{res.status}_{ct}", res.status)
    except Exception as e:
        return (cid, name, grp, logo, f"ERROR_{str(e)[:40]}", 0)

with ThreadPoolExecutor(max_workers=15) as ex:
    results = list(ex.map(check_logo, channels))

errors = []
relative = []
svg = []
ok = []

for r in results:
    cid, name, grp, logo, status, code = r
    if "RELATIVE_PATH" in status:
        relative.append(r)
    elif "ERROR" in status or "MISSING" in status:
        errors.append(r)
    elif "svg" in status.lower() or ".svg" in logo.lower():
        svg.append(r)
    else:
        ok.append(r)

print(f"\n--- KẾT QUẢ KIỂM TRA LOGO ---")
print(f"Tổng số: {len(channels)}")
print(f"✅ Hợp lệ (HTTP PNG/JPG/WEBP trả về 200 OK): {len(ok)}")
print(f"⚠️ Logo tương đối (data/logos/...): {len(relative)}")
print(f"⚠️ Logo dạng SVG (Glide APK không hiển thị được): {len(svg)}")
print(f"❌ Logo lỗi kết nối / 404 / hỏng: {len(errors)}")

if relative:
    print("\n--- CHI TIẾT LOGO TƯƠNG ĐỐI (data/logos/...) ---")
    for r in relative:
        print(f"[{r[2]}] {r[1]} -> {r[3]}")

if errors:
    print("\n--- CHI TIẾT LOGO LỖI / 404 ---")
    for r in errors:
        print(f"[{r[2]}] {r[1]} -> {r[3]} ({r[4]})")

if svg:
    print("\n--- CHI TIẾT LOGO DẠNG SVG (Không tương thích Glide APK) ---")
    for r in svg:
        print(f"[{r[2]}] {r[1]} -> {r[3]} ({r[4]})")
