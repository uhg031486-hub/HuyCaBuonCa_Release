import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

# Danh sách 12 kênh Quốc Tế chuẩn vàng 100% PASS
INTL_GOLDEN_12 = {
    'bbc_world_news_140': {
        'name': 'BBC World News',
        'url': 'https://mumbai-edge.smartplaytv.in/BBCNews/index.m3u8',
        'backupUrls': ['https://stream8.cinerama.uz/1251/tracks-v1a1/mono.m3u8']
    },
    'bloomberg_142': {
        'name': 'Bloomberg TV',
        'url': 'https://cdn4.skygo.mn/live/disk1/BloombergMon/HLSv3-FTA/BloombergMon.m3u8',
        'backupUrls': ['https://bloomberg.com/media-manifest/streams/us.m3u8']
    },
    'cnn_145': {
        'name': 'CNN International',
        'url': 'https://live3vox.antenaplay.ro/a3free/a3free.m3u8',
        'backupUrls': ['https://tv.a2news.com/live/smil:a2cnnweb.stream.smil/playlist.m3u8']
    },
    'hbo_158': {
        'name': 'HBO HD (Phim Điện Ảnh)',
        'url': 'https://amg00793-amg00793c41-rakuten-it-5445.playouts.now.amagi.tv/playlist.m3u8',
        'backupUrls': []
    },
    'discovery_152': {
        'name': 'Discovery Channel',
        'url': 'https://svs.itworkscdn.net/asharqdiscoverylive/asharqd.smil/playlist_dvr.m3u8',
        'backupUrls': []
    },
    'history_hd_159': {
        'name': 'History HD',
        'url': 'https://freem3u.xyz/api/live/play.m3u8?vid=9856',
        'backupUrls': []
    },
    'france_24_157': {
        'name': 'France 24',
        'url': 'https://live.france24.com/hls/live/2037218/F24_EN_HI_HLS/master_5000.m3u8',
        'backupUrls': []
    },
    'dw_151': {
        'name': 'DW (Đức)',
        'url': 'https://freem3u.xyz/api/live/play.m3u8?vid=109',
        'backupUrls': []
    },
    'kbs_world_160': {
        'name': 'KBS World (Hàn Quốc)',
        'url': 'https://freem3u.xyz/api/live/play.m3u8?vid=213',
        'backupUrls': []
    },
    'trt_world_162': {
        'name': 'TRT World',
        'url': 'https://tv-trtworld.medya.trt.com.tr/master_1080.m3u8',
        'backupUrls': []
    },
    'cgtn_143': {
        'name': 'CGTN',
        'url': 'https://english-livebkali.cgtn.com/live/encgtn_0.m3u8',
        'backupUrls': []
    },
    'cgtn_documentary_144': {
        'name': 'CGTN Documentary',
        'url': 'https://english-livebkali.cgtn.com/live/doccgtn_0.m3u8',
        'backupUrls': []
    }
}

# 4 kênh lỗi loại bỏ: axn_hd_135, cartoon_network_hd_146, cinemax_hd_149, fashion_tv_155
DROP_IDS = {'axn_hd_135', 'cartoon_network_hd_146', 'cinemax_hd_149', 'fashion_tv_155'}

final_channels = []
for ch in channels:
    ch_id = ch.get('id')
    if ch_id in DROP_IDS:
        print(f"Loại bỏ kênh lỗi: {ch.get('name')}")
        continue
    if ch_id in INTL_GOLDEN_12:
        cfg = INTL_GOLDEN_12[ch_id]
        ch['name'] = cfg['name']
        ch['url'] = cfg['url']
        ch['backupUrls'] = cfg.get('backupUrls', [])
        ch['group'] = 'Quốc Tế'
    
    final_channels.append(ch)

print(f"\nTổng số kênh cuối cùng: {len(final_channels)}")
intl_final = [c for c in final_channels if c.get('group') == 'Quốc Tế']
print(f"Số kênh Quốc Tế chuẩn vàng: {len(intl_final)}")
for i, c in enumerate(intl_final):
    print(f"  {i+1}. {c['name']} -> {c['url']}")

# Ghi file
with open('HuyCa_Web/data/tv_channels.json', 'w', encoding='utf-8') as f:
    json.dump(final_channels, f, ensure_ascii=False, indent=2)

js_content = "window.INITIAL_TV_CHANNELS = " + json.dumps(final_channels, ensure_ascii=False, indent=2) + ";\n"
with open('HuyCa_Web/data/tv_channels.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("✅ Đã cập nhật xong tv_channels.json và tv_channels.js chuẩn 100%!")
