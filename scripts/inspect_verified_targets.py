import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

verified = json.load(open('scripts/intl_verified_streams.json', encoding='utf-8'))
targets = {}
for ch in verified:
    tgt = ch.get('target', 'Other')
    if tgt not in targets:
        targets[tgt] = []
    targets[tgt].append(ch)

print(f"Tổng số luồng verified: {len(verified)}")
for tgt, list_ch in sorted(targets.items()):
    print(f" - [{tgt}]: {len(list_ch)} luồng (VD: {list_ch[0]['name']})")
