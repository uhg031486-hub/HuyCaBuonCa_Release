import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl
import json
import urllib.parse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Danh sách ứng viên HTTPS cho các kênh đang bị lỗi
candidates = {
    'Bloomberg TV': [
        'https://bloomberg.com/media-manifest/streams/us.m3u8',
        'https://ciner-live.daioncdn.net/bloomberght/bloomberght.m3u8',
        'https://cdn4.skygo.mn/live/disk1/BloombergMon/HLSv3-FTA/BloombergMon.m3u8'
    ],
    'CNN': [
        'https://tv.a2news.com/live/smil:a2cnnweb.stream.smil/playlist.m3u8',
        'https://live.cnnindonesia.com/livecnn/smil:cnntv.smil/playlist.m3u8',
        'https://live3vox.antenaplay.ro/a3free/a3free.m3u8'
    ],
    'Cartoon Network': [
        'https://shls-cartoon-net-prod-dub.shahid.net/out/v1/dc4aa87372374325a66be458f29eab0f/index.m3u8',
        'https://drk6xq0vhn.gpcdn.net/live/cn_sd_abr/index.m3u8',
        'https://live02-seg.msf.cdn.mediaset.net/live/ch-la/la-clr.isml/index.m3u8' # Cartoonito
    ],
    'Discovery': [
        'https://svs.itworkscdn.net/asharqdiscoverylive/asharqd.smil/playlist_dvr.m3u8',
        'https://streaming.aurora.enhanced.live/live/mpc/enl0eG1mLmVncmVzcy5mZDJ2eHI=/out/v1/IT_SIMULCAST/DISCOVERYCHANNEL/CMAF/index.m3u8'
    ],
    'Fashion TV': [
        'https://cdn2.invivo.bg/Codefashion_5500/index.m3u8',
        'https://fashiontv-fashntv-1-nl.samsung.wurl.tv/playlist.m3u8',
        'https://fashiontv_paris-samsunguk.amagi.tv/playlist.m3u8'
    ],
    'TRT World': [
        'https://tv-trtworld.medya.trt.com.tr/master_1080.m3u8',
        'https://trt.daioncdn.net/trt-world/master.m3u8'
    ],
    'KBS World': [
        'https://freem3u.xyz/api/live/play.m3u8?vid=213',
        'https://kbs-world-latam.amagi.tv/playlist.m3u8'
    ],
    'HBO': [
        'https://amg00793-amg00793c41-rakuten-it-5445.playouts.now.amagi.tv/playlist.m3u8', # Rakuten Action Movies
        'https://linear-1087.frequency.stream/mt/studio/1087/hls/master/playlist.m3u8' # Movie Central 24/7
    ],
    'Cinemax': [
        'https://linear-1087.frequency.stream/mt/studio/1087/hls/master/playlist.m3u8', # Movie Central Action
        'https://rakuten-actionmovies-1-eu.rakuten.wurl.tv/playlist.m3u8' # Rakuten Action Movies
    ],
    'AXN': [
        'https://rakuten-actionmovies-1-eu.rakuten.wurl.tv/playlist.m3u8',
        'https://linear-1087.frequency.stream/mt/studio/1087/hls/master/playlist.m3u8'
    ]
}

print("Kiểm tra CORS và trạng thái qua Proxy lẫn Direct:")
good_streams = {}

for ch, urls in candidates.items():
    good_streams[ch] = []
    for u in urls:
        # 1. Thử qua Live Proxy
        proxy_u = f"https://huyca.pages.dev/api/proxy?url={urllib.parse.quote(u)}"
        proxy_ok = False
        try:
            req = urllib.request.Request(proxy_u, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as r:
                if r.status == 200:
                    data = r.read(400).decode('utf-8', errors='ignore')
                    if '#EXTM3U' in data:
                        proxy_ok = True
        except Exception:
            pass

        # 2. Thử trực tiếp xem có CORS không
        direct_ok = False
        has_cors = False
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as r:
                if r.status == 200:
                    data = r.read(400).decode('utf-8', errors='ignore')
                    if '#EXTM3U' in data:
                        direct_ok = True
                        has_cors = r.headers.get('Access-Control-Allow-Origin') is not None
        except Exception:
            pass

        if proxy_ok or (direct_ok and has_cors):
            status_desc = "CORS OK" if (direct_ok and has_cors) else "PROXY OK"
            print(f"✅ {ch}: {status_desc} -> {u}")
            good_streams[ch].append({'url': u, 'status': status_desc})
        else:
            print(f"❌ {ch}: FAILED -> {u}")

print("\n--- TỔNG KẾT ---")
for ch, items in good_streams.items():
    print(f"{ch}: {len(items)} streams hoạt động")
