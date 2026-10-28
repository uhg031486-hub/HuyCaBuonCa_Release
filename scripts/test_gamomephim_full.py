import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch_category(genre_slug, page=1):
    url = f"https://gamomephim.com/the-loai/{genre_slug}"
    if page > 1:
        url += f"?page={page}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
        
    pattern = r'<a[^>]+title="([^"]+)"[^>]+href="/phim/([^"]+)".*?<img[^>]+src="([^"]+)"'
    matches = re.findall(pattern, html, re.DOTALL)
    results = []
    seen = set()
    for title, slug, thumb in matches:
        if slug not in seen:
            seen.add(slug)
            results.append({
                'title': title.strip(),
                'slug': slug.strip(),
                'thumb': thumb.strip()
            })
    return results

def fetch_movie_detail(slug):
    url = f"https://gamomephim.com/{slug}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
        
    # Lấy description
    desc_match = re.search(r'description\\\":\\\"([^\\\"]+)\\\"', html)
    desc = desc_match.group(1) if desc_match else ""
    
    # Lấy stream mp4
    streams = re.findall(r'https://r2\.gamomephim\.com/videos/[^\s"\'<>]+\.mp4', html)
    # Loai bo dau escape nguoc
    clean_streams = [s.replace('\\', '') for s in streams]
    clean_streams = list(set(clean_streams))
    
    tm_stream = next((s for s in clean_streams if '-tm.mp4' in s), None)
    sub_stream = next((s for s in clean_streams if '-sub.mp4' in s), None)
    
    return {
        'desc': desc,
        'tm_stream': tm_stream,
        'sub_stream': sub_stream,
        'all_streams': clean_streams
    }

print("Testing fetch category 'hien-dai':")
movies = fetch_category('hien-dai', 1)
print(f"Total movies found: {len(movies)}")
for m in movies[:3]:
    print(f"- {m['title']} (slug: {m['slug']})")

if movies:
    test_slug = movies[0]['slug']
    print(f"\nTesting movie detail for '{test_slug}':")
    detail = fetch_movie_detail(test_slug)
    print("TM stream:", detail['tm_stream'])
    print("SUB stream:", detail['sub_stream'])
