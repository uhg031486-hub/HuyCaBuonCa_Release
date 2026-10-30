import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://gamomephim.com/phim/noi-som-khong-som"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=10) as res:
    html = res.read().decode('utf-8', errors='ignore')

# Tìm tất cả chuỗi URL https:// trong toàn bộ html
urls = re.findall(r'https://[^\s"\'<>\\]+', html)
unique_domains = set(re.findall(r'https://([^/]+)', html))
print("Domains found:", unique_domains)

# In ra các URLs có chứa video hoặc r2 hoặc media hoặc stream
media_urls = [u for u in urls if any(k in u.lower() for k in ['video', 'stream', 'part', 'media', 'play', 'mp4', 'm3u8', 'cdn'])]
print("Media URLs:", len(media_urls))
for u in media_urls[:10]:
    print(" ->", u)

# In các đoạn __next_f có chứa từ khóa video
next_f = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
print("next_f blocks:", len(next_f))
for i, block in enumerate(next_f):
    if any(k in block.lower() for k in ['video', 'mp4', 'm3u8', 'part', 'episodes', 'source']):
        print(f"\nBlock {i} matches:")
        # unescape
        clean = block.replace('\\"', '"').replace('\\\\', '\\')
        for match in re.findall(r'"[^"]*(?:video|mp4|m3u8|part)[^"]*"', clean, re.IGNORECASE)[:10]:
            print("  ", match)
