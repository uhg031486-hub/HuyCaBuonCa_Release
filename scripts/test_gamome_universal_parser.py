import urllib.request
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_gamome(html):
    # Match all <a href="/phim/[slug]" ... > ... </a>
    items = []
    seen = set()
    a_pattern = re.compile(r'<a[^>]+href="/phim/([^"/]+)"[^>]*>(.*?)</a>', re.DOTALL)
    for m in a_pattern.finditer(html):
        slug = m.group(1).strip()
        body = m.group(2)
        if slug in seen:
            continue
        
        # Title can be in title="...", in alt="...", or in <h3/h4...>
        title = ""
        # 1. Check title="..." in anchor or body
        t_m = re.search(r'title="([^"]+)"', m.group(0))
        if t_m:
            title = t_m.group(1).strip()
        
        # 2. If no title, check <h3...> or <h4...>
        if not title:
            h_m = re.search(r'<h[34][^>]*>(.*?)</h[34]>', body, re.DOTALL)
            if h_m:
                title = re.sub(r'<[^>]+>', '', h_m.group(1)).strip()
        
        # 3. If no title, check alt="..." on img
        if not title:
            alt_m = re.search(r'<img[^>]+alt="([^"]+)"', body)
            if alt_m:
                title = alt_m.group(1).replace("Poster phim ", "").replace("Poster ", "").strip()
        
        # Thumb / Poster
        thumb = ""
        img_m = re.search(r'<img[^>]+src="([^"]+)"', body)
        if img_m:
            thumb = img_m.group(1).strip()
        
        if slug and title:
            seen.add(slug)
            items.append({
                'slug': slug,
                'title': title,
                'thumb': thumb
            })
    return items

for url in ['https://gamomephim.com/ban-xep-hang', 'https://gamomephim.com/the-loai/trong-sinh', 'https://gamomephim.com/the-loai/guong-vo-lai-lanh', 'https://gamomephim.com/phim-moi']:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as res:
        html = res.read().decode('utf-8')
        items = parse_gamome(html)
        print(f"URL: {url} -> Parsed {len(items)} items")
        if items:
            print(f"  First item: {items[0]}")
