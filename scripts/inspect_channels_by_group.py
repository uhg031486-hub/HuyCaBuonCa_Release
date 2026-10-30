import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

by_group = {}
for c in channels:
    grp = c.get('group', 'Other')
    by_group.setdefault(grp, []).append(c)

print(f"Tổng số nhóm: {len(by_group)}")
for grp, chs in sorted(by_group.items(), key=lambda x: -len(x[1])):
    print(f"\n--- NHÓM [{grp}] ({len(chs)} kênh) ---")
    for c in chs:
        logo = c.get('logo', '')
        status = "RELATIVE" if not logo.startswith('http') else ("WIKIMEDIA_400" if "wikimedia.org/wikipedia/commons/thumb" in logo else ("GENERIC" if "vbook-ext" in logo else "OK"))
        print(f"  {c['name']} (id: {c['id']}) [{status}] -> {logo}")
