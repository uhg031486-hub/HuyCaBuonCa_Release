import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

url = "https://gamomephim.com/the-loai/hien-dai"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as r:
    html = r.read().decode('utf-8', errors='ignore')
    # Tìm đoạn quanh /phim/
    idx = html.find('/phim/')
    if idx != -1:
        print("Snippet around /phim/:\n", html[idx-100:idx+400])
    
    # Tìm chuỗi có chứa ban-tinh-ca
    idx2 = html.find('ban-tinh-ca')
    if idx2 != -1:
        print("\nSnippet around ban-tinh-ca:\n", html[idx2-100:idx2+400])
