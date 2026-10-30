import urllib.request
import re

url = 'https://gamomephim.com/ban-xep-hang'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=10) as res:
        code = res.status
        html = res.read().decode('utf-8')
        print(f"Status: {code}, Length: {len(html)}")
        # Check movie cards pattern
        matches = re.findall(r'<a[^>]+href="([^"]+)"[^>]*title="([^"]+)"', html)
        print(f"Matches count: {len(matches)}")
        for m in matches[:5]:
            print("  Match:", m)
        # Check what classes are in html
        cards = re.findall(r'class="([^"]*movie[^"]*)"', html)
        print(f"Movie classes: {set(cards)}")
except Exception as e:
    print("Error:", e)

# Also check homepage or navigation to see where BXH points to
try:
    req = urllib.request.Request('https://gamomephim.com', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=10) as res:
        home_html = res.read().decode('utf-8')
        bxh_links = [m for m in re.findall(r'href="([^"]*)"[^>]*>([^<]*[Xx]ếp [Hh]ạng[^<]*)<', home_html)]
        print("BXH links on homepage:", bxh_links)
except Exception as e:
    print("Home error:", e)
