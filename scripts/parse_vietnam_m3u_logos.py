import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = [
    'https://raw.githubusercontent.com/FancyCoolerGuy2283/Vietnam/main/Vietnam.m3u',
    'https://raw.githubusercontent.com/kienthuanhp/Vietnam-IPTV/main/iptv.m3u',
    'https://raw.githubusercontent.com/thung65/Iptv-vietnam/main/FPT_PLAY.m3u'
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as res:
            content = res.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'tvg-logo="([^"]+)".*?,\s*([^\r\n]+)', content)
            print(f"=== {url.split('/')[-1]} ({len(matches)} logos found) ===")
            for logo, name in matches[:15]:
                print(f"  {name.strip()}: {logo}")
    except Exception as e:
        print(f"Error {url}: {e}")
