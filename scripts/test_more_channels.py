import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open('scripts/iptv_found.json', 'r', encoding='utf-8') as f:
    found = json.load(f)

# Kiểm tra thêm các kênh: HBO, Cinemax, AXN, Fashion TV, CBeebies
extra_checks = {
    'HBO': [
        'http://88.212.15.50/live/test_hbo2_hd_hevc/playlist.m3u8',
        'http://45.171.64.30:6060/play/a00i/index.m3u8',
        'http://170.83.16.50/HBO/index.m3u8',
        'https://shls-hbo-prod-dub.shahid.net/out/v1/hbo/index.m3u8'
    ],
    'Cinemax': [
        'http://88.212.15.50/live/test_cinemax_hd_hevc/playlist.m3u8',
        'http://170.83.16.50/CINEMAX/index.m3u8'
    ],
    'AXN': [
        'http://170.83.16.50/AXN/index.m3u8',
        'http://5.57.74.130:8000/play/a0at/index.m3u8'
    ],
    'Fashion TV': [
        'https://fashiontv-fashntv-1-nl.samsung.wurl.tv/playlist.m3u8',
        'https://fashiontv_paris-samsunguk.amagi.tv/playlist.m3u8',
        'https://cdn2.invivo.bg/Codefashion_5500/index.m3u8'
    ],
    'BBC Cbeebies': [
        'https://vs-hls-pushb-uk-live.akamaized.net/x=4/i=urn:bbc:pips:service:cbeebies/iptv_hd_abr_v1.m3u8',
        'http://193.46.58.239:8080/CbeebiesHD/index.m3u8'
    ],
    'SCTV15': [
        'https://s1.hplus.com.vn/hls/sctv15/index.m3u8',
        'https://live.tv360.vn/live/sctv15.m3u8'
    ],
    'SCTV22': [
        'https://s1.hplus.com.vn/hls/sctv22/index.m3u8'
    ]
}

results = {}
for ch, urls in extra_checks.items():
    results[ch] = []
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=4) as res:
                content = res.read(500).decode('utf-8', errors='ignore')
                if '#EXTM3U' in content and 'SAMPLE-AES' not in content:
                    print(f"✅ {ch} OK: {u}")
                    results[ch].append(u)
                else:
                    print(f"⚠️ {ch} DRM: {u}")
        except Exception as e:
            # print(f"❌ {ch} FAIL: {u} ({e})")
            pass

print("Done extra checks.")
for k, v in results.items():
    print(f"{k}: {v}")
