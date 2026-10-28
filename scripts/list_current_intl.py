import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

intl_list = [c for c in channels if c.get('group') == 'Quốc Tế']
print(f"Tổng số kênh Quốc Tế hiện tại: {len(intl_list)}")

for i, c in enumerate(intl_list):
    print(f"{i+1}. [{c.get('id')}] {c.get('name')}: {c.get('url')}")
