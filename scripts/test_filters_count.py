import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

print(f"Tổng số kênh trong kho v3.2.9: {len(channels)}")

filters = {
    'tv://all': lambda c: True,
    'tv://intl': lambda c: any(k in (c.get('group') or '') for k in ['Quốc Tế', 'Hàn Quốc', 'Trung Quốc', 'Israel', 'In The Box', 'TVB', 'Vệ Tinh']) or any(k in (c.get('name') or '') for k in ['NHK', 'Al Jazeera', 'DW ', 'France 24', 'ABC News', 'CBS News', 'NBC News', 'Bloomberg', 'CNA', 'Euronews', 'Arirang', 'Red Bull']),
    'tv://vtv': lambda c: 'vtv' in (c.get('group') or '').lower() or (c.get('name') or '').lower().startswith('vtv'),
    'tv://vtvcab': lambda c: 'vtvcab' in (c.get('group') or '').lower(),
    'tv://sctv': lambda c: 'sctv' in (c.get('group') or '').lower(),
    'tv://local': lambda c: any(k in (c.get('group') or '') for k in ['Địa phương', 'HTV']) or (c.get('name') or '').lower().startswith('htv') or (c.get('name') or '').lower().startswith('thvl'),
    'tv://satellite': lambda c: 'vệ tinh' in (c.get('group') or '').lower() or any(k in (c.get('name') or '') for k in ['True Premier', 'Astro', 'Sky Sports', 'TNT Sports', 'beIN']),
    'tv://football': lambda c: any(k in (c.get('group') or '').lower() for k in ['bóng đá', 'thể thao', 'c1']) or any(k in (c.get('name') or '').lower() for k in ['k+', 'sport', 'football', 'vtv5', 'vtv6', 'htv thể thao', 'bein', 'cbs', 'eurosport', 'fifa', 'espn']),
    'tv://sports_intl': lambda c: any(k in (c.get('group') or '') for k in ['ESPN', 'Bóng Rổ', 'FOX', 'Bóng Đá Quốc Tế']) or any(k in (c.get('name') or '').lower() for k in ['sport', 'bein', 'eurosport', 'fifa', 'red bull']),
    'tv://racing_combat': lambda c: any(k in (c.get('group') or '') for k in ['Đua Xe', 'Võ Thuật', 'Mạo Hiểm', 'Đối Kháng']) or 'red bull' in (c.get('name') or '').lower(),
    'tv://movies': lambda c: 'rạp phim' in (c.get('group') or '').lower() or 'phim' in (c.get('group') or '').lower() or any(k in (c.get('name') or '').lower() for k in ['hbo', 'warner', 'cinemax']),
    'tv://radio': lambda c: 'radio' in (c.get('group') or '').lower()
}

for filter_id, fn in filters.items():
    matched = [c for c in channels if fn(c)]
    print(f"Filter [{filter_id}]: {len(matched)} kênh")
