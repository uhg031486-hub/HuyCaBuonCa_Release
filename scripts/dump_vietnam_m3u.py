import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://raw.githubusercontent.com/FancyCoolerGuy2283/Vietnam/main/Vietnam.m3u'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as res:
    content = res.read().decode('utf-8', errors='ignore')

matches = re.findall(r'tvg-logo="([^"]+)".*?,\s*([^\r\n]+)', content)
print(f"Total {len(matches)} logos in Vietnam.m3u:")
for logo, name in matches:
    print(f"{name.strip()} ===> {logo}")
