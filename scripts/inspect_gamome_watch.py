import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://gamomephim.com/noi-som-khong-som"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=10) as res:
    html = res.read().decode('utf-8', errors='ignore')

print("WATCH PAGE HTML length:", len(html))

mp4s = re.findall(r'https://[^\s"\'<>]+\.mp4', html)
m3u8s = re.findall(r'https://[^\s"\'<>]+\.m3u8', html)
r2_urls = re.findall(r'https://r2\.gamomephim\.com/[^\s"\'<>]+', html)

print("MP4s found:", len(mp4s))
for m in mp4s:
    print(" -> MP4:", m)

print("M3U8s found:", len(m3u8s))
for m in m3u8s:
    print(" -> M3U8:", m)

iframes = re.findall(r'<iframe[^>]*src=["\']([^"\']+)["\']', html)
print("Iframes:", iframes)
