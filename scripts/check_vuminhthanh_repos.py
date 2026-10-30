import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

for repo in ["vuminhthanh12/Logo", "vuminhthanh12/vuminhthanh12"]:
    url = f"https://api.github.com/repos/{repo}/contents"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as res:
            items = json.loads(res.read().decode('utf-8'))
            print(f"=== {repo} ({len(items)} files) ===")
            for item in sorted(items, key=lambda x: x['name']):
                print(f"  {item['name']} -> {item['download_url']}")
    except Exception as e:
        print(f"Error {repo}:", e)
