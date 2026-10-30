import json
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

print(f"Tổng số kênh TV: {len(channels)}")

domain_counts = {}
svg_count = 0
relative_count = 0
broken_urls = []

for c in channels:
    logo = c.get('logo', '')
    if not logo.startswith('http'):
        relative_count += 1
    else:
        if '.svg' in logo:
            svg_count += 1
        domain = logo.split('/')[2] if len(logo.split('/')) > 2 else 'other'
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

print(f"Số logo dạng tương đối (data/logos/...): {relative_count}")
print(f"Số logo dạng SVG: {svg_count}")
print("Các domain logo đang dùng:")
for d, cnt in sorted(domain_counts.items(), key=lambda x: -x[1]):
    print(f"  {d}: {cnt}")
