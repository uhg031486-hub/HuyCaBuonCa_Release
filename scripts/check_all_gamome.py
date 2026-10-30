import requests, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

all_genres = [
    'the-loai/hien-dai',
    'the-loai/cuoi-truoc-yeu-sau',
    'the-loai/guong-vo-lai-lanh',
    'the-loai/trong-sinh',
    'the-loai/xuyen-khong',
    'the-loai/co-trang',
    'the-loai/dan-quoc',
    'the-loai/thanh-xuan',
    'the-loai/nien-dai',
    'the-loai/yeu-tham',
    'the-loai/hai-huoc',
    'the-loai/tra-xanh-nam',
    'the-loai/chua-lanh'
]

pattern = re.compile(r'<a[^>]+title="([^"]+)"[^>]+href="/phim/([^"]+)".*?<img[^>]+src="([^"]+)"', re.DOTALL)

for g in all_genres:
    r = requests.get(f'https://gamomephim.com/{g}', headers=headers, timeout=10)
    items = pattern.findall(r.text)
    r2 = requests.get(f'https://gamomephim.com/{g}?page=2', headers=headers, timeout=10)
    items_p2 = pattern.findall(r2.text)
    print(f'{g:30} -> P1: {len(items):2d} phim | P2: {len(items_p2):2d} phim')
