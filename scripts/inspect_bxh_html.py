import urllib.request
import re

for test_url in ['https://gamomephim.com/ban-xep-hang', 'https://gamomephim.com/the-loai/trong-sinh']:
    req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=10) as res:
        html = res.read().decode('utf-8')
        print(f"=== URL: {test_url} ===")
        # Find all <a> with /phim/
        phim_links = re.findall(r'<a[^>]+href="([^"]*phim[^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL)
        print(f"Found {len(phim_links)} links with /phim/")
        for link, content in phim_links[:3]:
            # clean content
            c = re.sub(r'\s+', ' ', content).strip()
            print(f"  Href: {link} -> Content: {c[:100]}")
