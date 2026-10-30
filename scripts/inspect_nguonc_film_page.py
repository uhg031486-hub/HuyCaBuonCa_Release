import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
req = urllib.request.Request('https://phim.nguonc.com/', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

films = re.findall(r'href="(https://phim\.nguonc\.com/phim/[^"]+)"', html)
print('Films found:', len(films))
if films:
    print('First film page:', films[0])
    req2 = urllib.request.Request(films[0], headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req2) as resp2:
        film_html = resp2.read().decode('utf-8', errors='ignore')
        print('Film page length:', len(film_html))
        for line in film_html.split('\n'):
            if any(k in line.lower() for k in ['iframe', 'streamc', 'embed']):
                print('  ', line.strip()[:140])
