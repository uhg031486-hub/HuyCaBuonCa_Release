import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Tải file JS của streamc để xem API endpoint lấy m3u8
js_urls = [
    'https://embed14.streamc.xyz/assets/cdn-start-messages-r25.a68e59ca53a35043.js',
    'https://embed14.streamc.xyz/assets/player-messages-r25.f8deeb2bf0fe759c.js',
    'https://embed14.streamc.xyz/assets/guard-messages-r25.7935ef4ddf515ec5.js'
]

for u in js_urls:
    try:
        print(f"\nFetching {u}...")
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://embed14.streamc.xyz/'})
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            content = r.read().decode('utf-8', errors='ignore')
            print(f"Loaded {len(content)} bytes")
            # Tìm kiếm m3u8, api, fetch, stream, player
            import re
            apis = re.findall(r'[\'\"`](https?://[^\'\"`]+|/api/[^\'\"`]+|/player/[^\'\"`]+)[\'\"`]', content)
            print("Found endpoints:", apis[:10])
            # Xem cách nó phát hiện adblock
            ad_matches = re.findall(r'adblock|chặn quảng cáo|ads\.js', content, re.IGNORECASE)
            print("Adblock matches:", set(ad_matches))
    except Exception as e:
        print("Err:", e)
