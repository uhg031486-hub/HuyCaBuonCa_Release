import sys
import shutil
import os

sys.stdout.reconfigure(encoding='utf-8')

src_json = 'HuyCa_Web/data/tv_channels.json'
src_js = 'HuyCa_Web/data/tv_channels.js'

destinations = [
    # Mobile Android
    ('HuyCaBuonCa_Mobile/app/src/main/assets/tv_channels.json', None),
    # TV Android
    ('HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json', None),
    # LG webOS
    ('HuyCaBuonCa_LG_webOS/data/tv_channels.json', 'HuyCaBuonCa_LG_webOS/data/tv_channels.js'),
    # Windows Desktop
    ('HuyCa_Windows/www/data/tv_channels.json', 'HuyCa_Windows/www/data/tv_channels.js'),
    # Samsung Tizen
    ('HuyCa_Samsung_Tizen/data/tv_channels.json', 'HuyCa_Samsung_Tizen/data/tv_channels.js'),
]

print("=== BẮT ĐẦU ĐỒNG BỘ KHO KÊNH TV V3.2.9 RA TẤT CẢ NỀN TẢNG ===")

for dest_json, dest_js in destinations:
    if dest_json:
        os.makedirs(os.path.dirname(dest_json), exist_ok=True)
        shutil.copy2(src_json, dest_json)
        print(f" -> Đã đồng bộ JSON: {dest_json}")
    if dest_js:
        os.makedirs(os.path.dirname(dest_js), exist_ok=True)
        shutil.copy2(src_js, dest_js)
        print(f" -> Đã đồng bộ JS: {dest_js}")

print("✅ Hoàn tất đồng bộ toàn bộ 5 nền tảng: Web, Mobile, Android TV, LG webOS, Windows, Samsung Tizen!")
