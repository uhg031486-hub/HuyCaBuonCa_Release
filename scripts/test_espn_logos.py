import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

for lg in ['eng.1', 'uefa.champions', 'esp.1']:
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lg}/scoreboard"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            events = data.get('events', [])
            print(f"=== ESPN {lg}: {len(events)} matches ===")
            for ev in events[:2]:
                print(f"Match: {ev.get('name')}")
                comps = ev.get('competitions', [{}])[0].get('competitors', [])
                for c in comps:
                    side = c.get('homeAway')
                    name = c.get('team', {}).get('displayName')
                    logo = c.get('team', {}).get('logo')
                    print(f"  [{side}] {name} => Logo: {logo}")
    except Exception as e:
        print(f"Error {lg}:", e)
