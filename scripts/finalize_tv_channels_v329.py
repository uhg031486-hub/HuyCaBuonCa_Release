import sys
import json
import shutil
import os

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

print(f"Tổng số kênh ban đầu: {len(channels)}")

# 1. Danh sách kênh cần loại bỏ dứt điểm do link chết vĩnh viễn
to_remove_ids = {
    'sports_intl_espn_4', 
    'on_kids', 
    'kr_cjb_sbs', 
    'cn_cctv_7', 
    'sports_racing_rally_tv',
    'intl_bloomberg_tv',
    'cinema_360_comedy',
    'cinema_360_kdrama',
    'cinema_360_classics',
    'cinema_360_animation'
}

channels = [c for c in channels if c.get('id') not in to_remove_ids and not any(r in c.get('name', '').lower() for r in ['cctv7', 'cjb sbs', 'on kids', 'rally tv 1080p', 'espn 4 latin'])]

# 2. Cập nhật các kênh cần sửa link chuẩn
url_fixes = {
    'intl_nbc_news_now': {
        'url': 'https://d1si3n1st4nkgb.cloudfront.net/10502/88896001/hls/master.m3u8?ads.xumo_channelId=88896001',
        'name': 'NBC News NOW HD (Hoa Kỳ)'
    },
    'htv_the_thao_hd': {
        'url': 'https://dethich.pw/htvthethao/index.m3u8',
        'name': 'HTV Thể Thao HD (Trực Tiếp Thể Thao)'
    },
    'intl_cnn': {
        'url': 'https://d2sybdl23b9psq.cloudfront.net/v1/master/3722c60a815c199d9c0ef36c5b73da68a62b09d1/cc-bocx3i7bjz0dg/CNNFAST_GB.m3u8',
        'name': 'CNN International HD (Tin Tức Toàn Cầu)'
    }
}

for c in channels:
    cid = c.get('id')
    if cid in url_fixes:
        c['url'] = url_fixes[cid]['url']
        c['name'] = url_fixes[cid]['name']
    elif 'htv thể thao' in c.get('name', '').lower():
        c['url'] = 'https://dethich.pw/htvthethao/index.m3u8'
    elif 'nbc news' in c.get('name', '').lower():
        c['url'] = 'https://d1si3n1st4nkgb.cloudfront.net/10502/88896001/hls/master.m3u8?ads.xumo_channelId=88896001'
    elif 'cnn' in c.get('name', '').lower() and 'antenaplay' in c.get('url', ''):
        c['url'] = 'https://d2sybdl23b9psq.cloudfront.net/v1/master/3722c60a815c199d9c0ef36c5b73da68a62b09d1/cc-bocx3i7bjz0dg/CNNFAST_GB.m3u8'

# 3. Thêm các kênh Quốc Tế & Rạp Phim cao cấp đã xác minh 100%
premium_additions = [
    {
        "id": "intl_reuters_tv",
        "name": "Reuters TV HD (Hãng Tin Quốc Tế)",
        "group": "Quốc Tế",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Reuters_Logo.svg/512px-Reuters_Logo.svg.png",
        "url": "https://amg00453-reuters-amg00453c1-rakuten-uk-2110.playouts.now.amagi.tv/playlist/amg00453-reuters-reuters-rakutenuk/playlist.m3u8"
    },
    {
        "id": "intl_cnbc_europe",
        "name": "CNBC Europe HD (Tài Chính & Chứng Khoán)",
        "group": "Quốc Tế",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/CNBC_logo.svg/512px-CNBC_logo.svg.png",
        "url": "https://amg01079-nbcuuk-amg01079c2-samsung-gb-1258.playouts.now.amagi.tv/playlist.m3u8"
    },
    {
        "id": "sports_sat_nbc_sports_now",
        "name": "NBC Sports NOW HD (Thể Thao Mỹ)",
        "group": "📡 Kênh Vệ Tinh Quốc Tế",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/NBC_Sports_2023.svg/512px-NBC_Sports_2023.svg.png",
        "url": "https://d4whmvwm0rdvi.cloudfront.net/10007/99993008/hls/master.m3u8?ads.xumo_channelId=99993008"
    },
    {
        "id": "movie_warner_tv_hd",
        "name": "Warner TV Asia HD (Điện Ảnh Hollywood)",
        "group": "Rạp Phim",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Warner_TV_2016.svg/512px-Warner_TV_2016.svg.png",
        "url": "https://cdn4.skygo.mn/live/disk1/Warner/HLSv3-FTA/Warner.m3u8"
    },
    {
        "id": "movie_hbo_rakuten_hd",
        "name": "HBO Cinema HD (Phim Chiếu Rạp Bom Tấn)",
        "group": "Rạp Phim",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/HBO_logo.svg/512px-HBO_logo.svg.png",
        "url": "https://amg00793-amg00793c41-rakuten-it-5445.playouts.now.amagi.tv/playlist.m3u8"
    },
    {
        "id": "movie_cartoonito_hd",
        "name": "Cartoonito / Boomerang HD (Hoạt Hình Quốc Tế)",
        "group": "Rạp Phim",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Cartoonito_2021.svg/512px-Cartoonito_2021.svg.png",
        "url": "http://cdn4.skygo.mn/live/disk1/Boomerang/HLSv3-FTA/Boomerang.m3u8"
    },
    {
        "id": "movie_history_hit_hd",
        "name": "History Hit HD (Phim Tài Liệu Lịch Sử)",
        "group": "Rạp Phim",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/History_Hit_logo.png/512px-History_Hit_logo.png",
        "url": "https://lds-timeline-rakuten.amagi.tv/playlist.m3u8"
    }
]

existing_urls = {c.get('url') for c in channels}
for p in premium_additions:
    if p['url'] not in existing_urls:
        channels.append(p)
        existing_urls.add(p['url'])

print(f"Tổng số kênh sau khi tối ưu hóa hoàn chỉnh: {len(channels)}")

# Ghi ra Web data
with open('HuyCa_Web/data/tv_channels.json', 'w', encoding='utf-8') as f:
    json.dump(channels, f, ensure_ascii=False, indent=2)

js_content = f"// Kho Kênh Truyền Hình Huy Cá v3.2.9 - Tự động đồng bộ đa nền tảng\nwindow.CHANNELS_DATA = {json.dumps(channels, ensure_ascii=False, indent=2)};\n"
with open('HuyCa_Web/data/tv_channels.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("✅ Đã cập nhật xong dữ liệu HuyCa_Web!")

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
        print(f" -> Đã đồng bộ JSON: {dest_json}")
    if dest_js:
        os.makedirs(os.path.dirname(dest_js), exist_ok=True)
        shutil.copy2('HuyCa_Web/data/tv_channels.js', dest_js)
        print(f" -> Đã đồng bộ JS: {dest_js}")

print("🎉 Hoàn tất đồng bộ toàn diện v3.2.9!")
