import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

chs = json.load(open('HuyCa_Web/data/tv_channels.json', encoding='utf-8'))
print(f"Tổng số kênh: {len(chs)}")

groups = {}
for c in chs:
    g = c.get('group', 'Chưa phân loại')
    groups[g] = groups.get(g, 0) + 1

for g, count in sorted(groups.items(), key=lambda x: -x[1]):
    print(f"Group: [{g}] -> {count} kênh")

print("\n--- CHI TIẾT KÊNH QUỐC TẾ ---")
for c in chs:
    g = c.get('group', '')
    if any(k in g.lower() for k in ['quốc tế', 'vệ tinh', 'hàn quốc', 'nhật']):
        print(f" - [{g}] {c['name']} -> {c['url'][:60]}...")
