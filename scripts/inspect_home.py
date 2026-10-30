import requests, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r = requests.get('https://gamomephim.com/', headers=headers, timeout=10)
print('Home status:', r.status_code)

nav_links = re.findall(r'<a[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>', r.text)
for href, label in nav_links:
    clean_label = re.sub(r'<[^>]+>', '', label).strip()
    if clean_label and len(clean_label) < 40:
        print(f'{clean_label:30} -> {href}')
