import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import subprocess
import re

# Lấy dữ liệu gốc từ git HEAD của HuyCa_Web
p = subprocess.run(['git', 'show', 'HEAD:data/tv_channels.js'], cwd='HuyCa_Web', stdout=subprocess.PIPE, text=True, encoding='utf-8')
text = p.stdout
json_match = re.search(r'=\s*(\[.*\]);?\s*$', text, re.DOTALL)
channels = json.loads(json_match.group(1))

print(f"Tổng số kênh từ git HEAD: {len(channels)}")

# Bản đồ thay thế link stream chuẩn HLS m3u8 không DRM
REPLACEMENTS = {
    'bbc world news': {
        'name': 'BBC World News',
        'url': 'https://mumbai-edge.smartplaytv.in/BBCNews/index.m3u8',
        'backupUrls': [
            'https://stream8.cinerama.uz/1251/tracks-v1a1/mono.m3u8',
            'https://tvsen1.aynaott.com/shn6jGTk/index.m3u8',
            'http://103.151.60.162:2122/play/a0fl/index.m3u8?hls'
        ]
    },
    'bloomberg': {
        'name': 'Bloomberg TV',
        'url': 'https://bloomberg.com/media-manifest/streams/us.m3u8',
        'backupUrls': [
            'https://bloomberg.com/media-manifest/streams/eu.m3u8',
            'https://bloomberg.com/media-manifest/streams/phoenix-us.m3u8'
        ]
    },
    'cnn': {
        'name': 'CNN International',
        'url': 'https://tv.a2news.com/live/smil:a2cnnweb.stream.smil/playlist.m3u8',
        'backupUrls': [
            'https://nw18live.cdn.jio.com/bpk-tv/CNN_News18_NW18_MOB/output01/index.m3u8'
        ]
    },
    'cartoon network': {
        'name': 'Cartoon Network HD',
        'url': 'https://shls-cartoon-net-prod-dub.shahid.net/out/v1/dc4aa87372374325a66be458f29eab0f/index.m3u8',
        'backupUrls': [
            'https://drk6xq0vhn.gpcdn.net/live/cn_sd_abr/index.m3u8'
        ]
    },
    'discovery': {
        'name': 'Discovery Channel',
        'url': 'https://svs.itworkscdn.net/asharqdiscoverylive/asharqd.smil/playlist_dvr.m3u8',
        'backupUrls': []
    },
    'animal planet': {
        'name': 'Animal Planet',
        'url': 'https://drk6xq0vhn.gpcdn.net/live/animal_planet_sd_abr/index.m3u8',
        'backupUrls': []
    },
    'hbo': {
        'name': 'HBO HD',
        'url': 'http://88.212.15.50/live/test_hbo2_hd_hevc/playlist.m3u8',
        'backupUrls': []
    },
    'cinemax': {
        'name': 'Cinemax HD',
        'url': 'http://88.212.15.50/live/test_cinemax_hd_hevc/playlist.m3u8',
        'backupUrls': []
    },
    'axn': {
        'name': 'AXN HD',
        'url': 'http://170.83.16.50/AXN/index.m3u8',
        'backupUrls': []
    },
    'fashion tv': {
        'name': 'Fashion TV',
        'url': 'https://cdn2.invivo.bg/Codefashion_5500/index.m3u8',
        'backupUrls': []
    }
}

clean_channels = []
replaced_count = 0
dropped_drm_count = 0

for ch in channels:
    c_name = ch.get('name', '').lower()
    c_url = ch.get('url', '')

    # Tìm xem có trong danh sách thay thế m3u8 không
    matched_rep = None
    for k, rep in REPLACEMENTS.items():
        if k in c_name:
            matched_rep = rep
            break

    if matched_rep:
        ch['name'] = matched_rep['name']
        ch['url'] = matched_rep['url']
        if 'backupUrls' in matched_rep:
            ch['backupUrls'] = matched_rep['backupUrls']
        clean_channels.append(ch)
        replaced_count += 1
        print(f"✅ Đã nâng cấp kênh {ch['name']} sang HLS m3u8: {ch['url']}")
        continue

    # Nếu vẫn dính MPD hoặc Live_DASHDRM chưa có link thay thế -> bỏ để không lỗi người dùng
    if '.mpd' in c_url or 'Live_DASHDRM' in c_url or 'live_dzones' in c_url:
        print(f"Bỏ kênh DRM không phát được: {ch.get('name')}")
        dropped_drm_count += 1
        continue

    clean_channels.append(ch)

print(f"\nTổng số kênh cuối cùng: {len(clean_channels)}")
print(f"Đã nâng cấp {replaced_count} kênh quốc tế.")
print(f"Đã dọn dẹp {dropped_drm_count} kênh DRM.")

# Ghi ra tv_channels.json và tv_channels.js
with open('HuyCa_Web/data/tv_channels.json', 'w', encoding='utf-8') as f:
    json.dump(clean_channels, f, ensure_ascii=False, indent=2)

js_content = "window.INITIAL_TV_CHANNELS = " + json.dumps(clean_channels, ensure_ascii=False, indent=2) + ";\n"
with open('HuyCa_Web/data/tv_channels.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Đã ghi xong file!")
