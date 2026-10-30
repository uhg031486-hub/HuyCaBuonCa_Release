import sys
import json
import urllib.request
import time

sys.stdout.reconfigure(encoding='utf-8')

# 1. Tìm URL sống cho NBC News
print("Đang kiểm tra các link NBC News...")
nbc_candidates = [
    "https://d1si3n1st4nkgb.cloudfront.net/10502/88896001/hls/master.m3u8",
    "https://nbcnews-hls.tubi.video/live/nbcnews/master.m3u8",
    "https://nbcnews2.akamaized.net/hls/live/723426/NBCNewsPlay/master.m3u8",
    "https://dai.google.com/linear/hls/event/nbcnews/master.m3u8",
    "https://stitcher-ipv4.pluto.tv/v1/stitch/hls/channel/5d9bc37f09ef5a0009623e10/master.m3u8?deviceType=web"
]
best_nbc = None
for url in nbc_candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.5) as r:
            if r.status in [200, 206]:
                print(f" -> NBC SỐNG: {url}")
                best_nbc = url
                break
    except Exception as e:
        print(f" -> NBC Lỗi: {e} ({url[:40]})")

# 2. Tìm URL sống cho HTV Thể Thao
print("\nĐang kiểm tra các link HTV Thể Thao...")
htv_sport_candidates = [
    "https://dethich.pw/htvtt/index.m3u8",
    "https://dethich.pw/htvthethao/index.m3u8",
    "http://125hvt.ddns.net:21585/htvtt/playlist.m3u8",
    "http://118.69.170.218:8000/live/htvtt/playlist.m3u8",
    "https://hls.htv.com.vn/live/htvthethao/index.m3u8"
]
best_htv_sport = None
for url in htv_sport_candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.5) as r:
            if r.status in [200, 206]:
                print(f" -> HTV Thể Thao SỐNG: {url}")
                best_htv_sport = url
                break
    except Exception as e:
        print(f" -> HTV Thể Thao Lỗi: {e} ({url[:40]})")

# 3. Tìm các kênh Phim Điện Ảnh chất lượng cao thay thế nhóm Rạp Phim chết
print("\nĐang tìm kiếm các kênh phim điện ảnh thay thế...")
movie_replacements = [
    {
        "id": "movie_warner_tv",
        "name": "Warner TV Asia HD (Điện Ảnh Hollywood)",
        "group": "Rạp Phim",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Warner_TV_2016.svg/512px-Warner_TV_2016.svg.png",
        "url": "https://cdn4.skygo.mn/live/disk1/Warner/HLSv3-FTA/Warner.m3u8"
    },
    {
        "id": "movie_hbo_rakuten",
        "name": "HBO Rakuten Cinema HD (Phim Điện Ảnh)",
        "group": "Rạp Phim",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/HBO_logo.svg/512px-HBO_logo.svg.png",
        "url": "https://amg00793-amg00793c41-rakuten-it-5445.playouts.now.amagi.tv/playlist.m3u8"
    },
    {
        "id": "movie_cartoonito",
        "name": "Cartoonito / Boomerang HD (Hoạt Hình Quốc Tế)",
        "group": "Rạp Phim",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Cartoonito_2021.svg/512px-Cartoonito_2021.svg.png",
        "url": "http://cdn4.skygo.mn/live/disk1/Boomerang/HLSv3-FTA/Boomerang.m3u8"
    },
    {
        "id": "movie_history_hit",
        "name": "History Hit HD (Phim Tài Liệu & Điện Ảnh)",
        "group": "Rạp Phim",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/History_Hit_logo.png/512px-History_Hit_logo.png",
        "url": "https://lds-timeline-rakuten.amagi.tv/playlist.m3u8"
    }
]

for m in movie_replacements:
    try:
        req = urllib.request.Request(m['url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.5) as r:
            print(f" -> Phim {m['name']} SỐNG ({r.status})")
    except Exception as e:
        print(f" -> Phim {m['name']} Lỗi: {e}")
