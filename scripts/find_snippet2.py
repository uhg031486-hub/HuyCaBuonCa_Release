import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = "https://gamomephim.com/the-loai/hien-dai"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    html = r.read().decode('utf-8', errors='ignore')
    idx = html.find('ban-tinh-ca-nho-trong-anh-sang-le-loi')
    print(html[idx:idx+1000])
