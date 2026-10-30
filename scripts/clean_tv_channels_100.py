import sys
import json
import shutil
import os

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

print(f"Tổng số kênh hiện tại: {len(channels)}")

bad_keywords = [
    '360 hài', '360 hoạt hình', '360 k-drama', '360 phim kinh điển',
    'on golf', 'gia lai', 'thái nguyên', 'tây ninh tv', 'on vie giải trí',
    'kbs world', 'espn 6'
]

clean_channels = []
for c in channels:
    name_low = c.get('name', '').lower()
    url_low = c.get('url', '').lower()
    if any(k in name_low for k in bad_keywords):
        print(f" -> Loại bỏ kênh chết: {c.get('name')}")
        continue
    if 'barinaslive1' in url_low:
        print(f" -> Loại bỏ link boldmss chết: {c.get('name')}")
        continue
    clean_channels.append(c)

print(f"Số lượng kênh sau khi làm sạch hoàn toàn: {len(clean_channels)}")

# Ghi ra Web
with open('HuyCa_Web/data/tv_channels.json', 'w', encoding='utf-8') as f:
    json.dump(clean_channels, f, ensure_ascii=False, indent=2)

js_content = f"// Kho Kênh Truyền Hình Huy Cá v3.2.9 - Tự động đồng bộ đa nền tảng\nwindow.CHANNELS_DATA = {json.dumps(clean_channels, ensure_ascii=False, indent=2)};\n"
with open('HuyCa_Web/data/tv_channels.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

# Đồng bộ đa nền tảng
destinations = [
    ('HuyCaBuonCa_Mobile/app/src/main/assets/tv_channels.json', None),
    ('HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json', None),
    ('HuyCaBuonCa_LG_webOS/data/tv_channels.json', 'HuyCaBuonCa_LG_webOS/data/tv_channels.js'),
    ('HuyCa_Windows/www/data/tv_channels.json', 'HuyCa_Windows/www/data/tv_channels.js'),
    ('HuyCa_Samsung_Tizen/data/tv_channels.json', 'HuyCa_Samsung_Tizen/data/tv_channels.js'),
]

for dest_json, dest_js in destinations:
    if dest_json:
        os.makedirs(os.path.dirname(dest_json), exist_ok=True)
        shutil.copy2('HuyCa_Web/data/tv_channels.json', dest_json)
    if dest_js:
        os.makedirs(os.path.dirname(dest_js), exist_ok=True)
        shutil.copy2('HuyCa_Web/data/tv_channels.js', dest_js)

print("✅ Đã cập nhật và đồng bộ kho kênh siêu sạch v3.2.9!")
