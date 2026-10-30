import urllib.request
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://phim.nguonc.com/'
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print('Homepage length:', len(content))
        links = re.findall(r'href="([^"]+)"', content)
        print('Links found:', len(links))
        for l in links[:15]:
            print(' ', l)
except Exception as e:
    print('Error:', e)
