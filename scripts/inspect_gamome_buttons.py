import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://gamomephim.com/phim/noi-som-khong-som"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=10) as res:
    html = res.read().decode('utf-8', errors='ignore')

buttons = re.findall(r'<button[^>]*>(.*?)</button>', html, re.DOTALL)
for b in buttons:
    print('BUTTON:', re.sub(r'<[^>]+>', '', b).strip())

links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
for href, content in links:
    text = re.sub(r'<[^>]+>', '', content).strip()
    if text:
        print(f"A: {href} -> {text[:30]}")
