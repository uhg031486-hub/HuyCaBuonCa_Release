import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://gamomephim.com/phim-moi"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=10) as res:
    html = res.read().decode('utf-8', errors='ignore')

# Tìm các thẻ chứa class phim hoặc card
cards = re.findall(r'<div[^>]*class="[^"]*group[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
print("Cards count with group:", len(cards))

# Tìm tất cả link xem phim
links = re.findall(r'<a[^>]+href=["\'](/[^"\'\s>]+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
film_candidates = []
for h, c in links:
    if not any(x in h for x in ['dien-vien', 'tim-kiem', 'the-loai', 'phim-moi', 'ban-xep-hang', 'site.', 'gioi-thieu', 'dieu-khoan', 'chinh-sach', 'lien-he', 'login', 'register']):
        film_candidates.append((h, c))

print("Total film candidates:", len(film_candidates))
for h, c in film_candidates[:15]:
    imgs = re.findall(r'src=["\']([^"\']+)["\']', c)
    titles = re.findall(r'<h\d[^>]*>([^<]+)</h\d>', c)
    t = titles[0].strip() if titles else re.sub(r'<[^>]+>', '', c).strip()
    print(f"HREF: {h} | TITLE: {t} | IMG: {imgs[0] if imgs else 'None'}")
