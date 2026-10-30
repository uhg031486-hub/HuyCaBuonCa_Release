import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://gamomephim.com/phim-moi'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as res:
    html = res.read().decode('utf-8')

slugs = list(dict.fromkeys(re.findall(r'href=["\']/phim/([a-zA-Z0-9_-]+)["\']', html)))
print('Slugs found with /phim/:', slugs[:5])
for s in slugs[:2]:
    detail_url = f'https://gamomephim.com/{s}'
    try:
        with urllib.request.urlopen(urllib.request.Request(detail_url, headers={'User-Agent': 'Mozilla/5.0'})) as d_res:
            d_html = d_res.read().decode('utf-8')
            streams = re.findall(r'https://r2\.gamomephim\.com/videos/[^\s"\'<>]+\.mp4', d_html)
            print(f'Slug: {s} -> {len(streams)} MP4 streams found: {streams}')
    except Exception as e:
        print('Error:', e)
