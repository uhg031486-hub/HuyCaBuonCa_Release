import requests, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

genres = ['the-loai/hien-dai', 'the-loai/cuoi-truoc-yeu-sau', 'the-loai/trong-sinh', 'the-loai/co-trang', 'the-loai/tra-xanh-nam', 'the-loai/chua-lanh']

for g in genres:
    url_p1 = f'https://gamomephim.com/{g}'
    url_p2 = f'https://gamomephim.com/{g}?page=2'
    r1 = requests.get(url_p1, headers=headers, timeout=10)
    r2 = requests.get(url_p2, headers=headers, timeout=10)
    
    # Check pagination links in r1
    page_links = re.findall(r'href=[\'"]([^\'"]*(?:page|trang|the-loai)[^\'"]*)[\'"]', r1.text, re.IGNORECASE)
    
    # Check items count
    pattern = re.compile(r'<a[^>]+title="([^"]+)"[^>]+href="/phim/([^"]+)".*?<img[^>]+src="([^"]+)"', re.DOTALL)
    m1 = pattern.findall(r1.text)
    m2 = pattern.findall(r2.text)
    
    print(f'=== {g} ===')
    print(f'P1 status: {r1.status_code}, items: {len(m1)}')
    print(f'P2 status: {r2.status_code}, items: {len(m2)}')
    if len(m1) > 0 and len(m2) > 0:
        print('P1 item[0]:', m1[0][0], m1[0][1])
        print('P2 item[0]:', m2[0][0], m2[0][1])
        if m1[0][1] == m2[0][1]:
            print('>>> WARNING: P1 and P2 items are IDENTICAL! ?page=2 did not change page!')
    print('Pagination links sample:', list(set(page_links))[:8])

# Khám phá tất cả các thể loại và menu trên trang chủ gamomephim.com
r_home = requests.get('https://gamomephim.com/', headers=headers, timeout=10)
all_genres = re.findall(r'href=[\'"](/(?:the-loai|danh-sach|chu-de|genre)[^\'"]*)[\'"]', r_home.text)
print('\n=== ALL GENRE LINKS ON GAMOMEPHIM.COM ===')
for link in set(all_genres):
    print(link)
