import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

for idx, c in enumerate(channels, 1):
    print(f"{idx:3d}. [{c.get('group')}] {c.get('name')} (id: {c.get('id')}) -> {c.get('logo')}")
