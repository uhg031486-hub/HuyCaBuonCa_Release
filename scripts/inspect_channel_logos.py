import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

print(f"Total channels in HuyCaBuonCa_TV: {len(channels)}")

relative = []
svg = []
no_logo = []
valid_http = []

for c in channels:
    logo = c.get('logo', '')
    cid = c.get('id', '')
    name = c.get('name', '')
    grp = c.get('group', '')
    if not logo:
        no_logo.append((cid, name, grp))
    elif not logo.startswith('http'):
        relative.append((cid, name, grp, logo))
    elif '.svg' in logo:
        svg.append((cid, name, grp, logo))
    else:
        valid_http.append((cid, name, grp, logo))

print(f"\n1. Relative logos ({len(relative)}):")
for r in relative:
    print(f"  - [{r[2]}] {r[1]} -> {r[3]}")

print(f"\n2. SVG logos ({len(svg)}):")
for s in svg:
    print(f"  - [{s[2]}] {s[1]} -> {s[3]}")

print(f"\n3. Empty logos ({len(no_logo)}):")
for n in no_logo:
    print(f"  - [{n[2]}] {n[1]}")

print(f"\n4. Valid HTTP logos: {len(valid_http)}")
