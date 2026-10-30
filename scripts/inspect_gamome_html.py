import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://gamomephim.com/phim-moi"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=10) as res:
    html = res.read().decode('utf-8', errors='ignore')

print("HTML length:", len(html))

# Tìm các link href
links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
print("Total links:", len(links))

valid_movies = []
for href, content in links:
    if href.startswith("/") and not href.startswith("//"):
        href = href[1:]
    if any(x in href for x in ['the-loai', 'phim-moi', 'ban-xep-hang', 'site.', 'gioi-thieu', 'dieu-khoan', 'chinh-sach', 'lien-he', 'login', 'register', 'css', 'js', 'favicon', 'images']):
        continue
    if not href:
        continue
    imgs = re.findall(r'src=["\']([^"\']+)["\']', content)
    title = re.sub(r'<[^>]+>', '', content).strip()
    valid_movies.append((href, imgs[0] if imgs else "", title))

print(f"Valid movies found: {len(valid_movies)}")
for m in valid_movies[:10]:
    print(f" -> Slug: '{m[0]}', Title: '{m[2]}', Thumb: '{m[1]}'")
