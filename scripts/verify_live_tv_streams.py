import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

test_map = {
    'BBC World News': [
        'https://mumbai-edge.smartplaytv.in/BBCNews/index.m3u8',
        'http://103.151.60.162:2122/play/a0fl/index.m3u8?hls',
        'https://stream8.cinerama.uz/1251/tracks-v1a1/mono.m3u8',
        'https://tvsen1.aynaott.com/shn6jGTk/index.m3u8'
    ],
    'Bloomberg': [
        'https://bloomberg.com/media-manifest/streams/us.m3u8',
        'https://bloomberg.com/media-manifest/streams/eu.m3u8',
        'https://bloomberg.com/media-manifest/streams/phoenix-us.m3u8'
    ],
    'CNN': [
        'https://tv.a2news.com/live/smil:a2cnnweb.stream.smil/playlist.m3u8',
        'https://nw18live.cdn.jio.com/bpk-tv/CNN_News18_NW18_MOB/output01/index.m3u8'
    ],
    'Cartoon Network': [
        'https://shls-cartoon-net-prod-dub.shahid.net/out/v1/dc4aa87372374325a66be458f29eab0f/index.m3u8',
        'https://drk6xq0vhn.gpcdn.net/live/cn_sd_abr/index.m3u8'
    ],
    'Discovery': [
        'https://svs.itworkscdn.net/asharqdiscoverylive/asharqd.smil/playlist_dvr.m3u8'
    ],
    'Animal Planet': [
        'https://drk6xq0vhn.gpcdn.net/live/animal_planet_sd_abr/index.m3u8'
    ]
}

verified_streams = {}

for ch_name, urls in test_map.items():
    verified_streams[ch_name] = []
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as res:
                content = res.read(500).decode('utf-8', errors='ignore')
                if '#EXTM3U' in content and 'SAMPLE-AES' not in content:
                    print(f"✅ {ch_name} LIVE OK: {u}")
                    verified_streams[ch_name].append(u)
                else:
                    print(f"⚠️ {ch_name} has DRM or non-m3u8: {u}")
        except Exception as e:
            print(f"❌ {ch_name} FAILED ({e}): {u}")

print("\n--- TỔNG KẾT KÊNH SỐNG KHÔNG DRM ---")
for k, v in verified_streams.items():
    print(f"{k}: {len(v)} links OK -> {v[0] if v else 'NONE'}")
