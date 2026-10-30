import requests, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
pattern = re.compile(r'<a[^>]+title="([^"]+)"[^>]+href="/phim/([^"]+)".*?<img[^>]+src="([^"]+)"', re.DOTALL)

for path in ['phim-moi', 'ban-xep-hang']:
    r1 = requests.get(f'https://gamomephim.com/{path}', headers=headers, timeout=10)
    r2 = requests.get(f'https://gamomephim.com/{path}?page=2', headers=headers, timeout=10)
    r3 = requests.get(f'https://gamomephim.com/{path}?page=3', headers=headers, timeout=10)
    print(f'{path:15} -> P1: {len(pattern.findall(r1.text)):2d} | P2: {len(pattern.findall(r2.text)):2d} | P3: {len(pattern.findall(r3.text)):2d}')
