import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

sources = [
    'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/vn.m3u',
    'https://raw.githubusercontent.com/vthanhtivi/vthanhtivi/main/vthanhtivi.m3u',
    'https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8',
    'https://raw.githubusercontent.com/Yan-One/Live-IPTV/master/IPTV.m3u',
]

for src in sources:
    try:
        print(f"Reading {src}...")
        req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            lines = r.read().decode('utf-8', errors='ignore').splitlines()
            print(f"Loaded {len(lines)} lines")
            curr_name = ""
            for line in lines:
                if line.startswith('#EXTINF:'):
                    curr_name = line
                elif line.startswith('http') and curr_name:
                    for kw in ['BBC', 'CNN', 'BLOOMBERG', 'DISCOVERY', 'HBO', 'CARTOON', 'ANIMAL', 'AXN', 'CINEMAX']:
                        if kw in curr_name.upper():
                            print(f"{curr_name} -> {line}")
                            break
    except Exception as e:
        print(f"Err {src}: {e}")
