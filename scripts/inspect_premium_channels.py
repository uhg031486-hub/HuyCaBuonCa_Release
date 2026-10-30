import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

verified = json.load(open('scripts/intl_verified_streams.json', encoding='utf-8'))
interesting = ['Animax', 'Cinemax', 'HBO', 'Warner', 'National Geographic', 'Sky News', 'Euronews', 'Red Bull TV']

for ch in verified:
    if any(k in ch.get('target', '') for k in interesting):
        print(f"[{ch.get('target')}] {ch.get('name')}")
        print(f"   URL: {ch.get('url')}")
        print(f"   LOGO: {ch.get('logo')}\n")
