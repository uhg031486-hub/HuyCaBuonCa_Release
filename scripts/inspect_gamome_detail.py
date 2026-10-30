import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://gamomephim.com/phim/noi-som-khong-som"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=10) as res:
    html = res.read().decode('utf-8', errors='ignore')

print("Detail HTML length:", len(html))

# Tìm tất cả URLs trong trang chi tiết
mp4s = re.findall(r'https://[^\s"\'<>]+\.mp4', html)
m3u8s = re.findall(r'https://[^\s"\'<>]+\.m3u8', html)
r2_urls = re.findall(r'https://r2\.gamomephim\.com/[^\s"\'<>]+', html)

print("MP4s found:", len(mp4s), mp4s[:3])
print("M3U8s found:", len(m3u8s), m3u8s[:3])
print("R2 URLs found:", len(r2_urls), r2_urls[:5])

# Tìm nút xem hoặc player iframe/video tag
video_tags = re.findall(r'<video[^>]*>(.*?)</video>', html, re.DOTALL)
print("Video tags:", len(video_tags))
iframes = re.findall(r'<iframe[^>]*src=["\']([^"\']+)["\']', html)
print("Iframes:", iframes)

# Tìm các nút xem tập hoặc các link /xem-phim/
watch_links = re.findall(r'href=["\'](/xem-phim/[^"\'\s>]+)["\']', html)
print("Watch links:", watch_links)
