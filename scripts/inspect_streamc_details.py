import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://phim.nguonc.com/'
})
with urllib.request.urlopen(req) as r:
    html = r.read().decode('utf-8', errors='ignore')

scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html)
print('Found scripts in embed.php:', scripts)

inline_scripts = re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', html, re.DOTALL)
print(f'Found {len(inline_scripts)} inline scripts')
for i, s in enumerate(inline_scripts):
    print(f"\n--- Inline script {i} (first 300 chars) ---")
    print(s[:300])
