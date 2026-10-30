import urllib.request
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://phim.nguonc.com/'
}

for asset in ['/assets/cdn-start-messages-r25.a68e59ca53a35043.js', '/assets/guard-messages-r25.7935ef4ddf515ec5.js']:
    url = 'https://embed14.streamc.xyz' + asset
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(f'{asset}: length={len(content)}')
            for kw in ['adblock', 'guard', 'chặn quảng cáo', 'ads.js', 'verification']:
                matches = [m.start() for m in re.finditer(kw, content, re.IGNORECASE)]
                if matches:
                    print(f'  contains {kw}: {len(matches)} times (first at {matches[0]})')
                    # print snippet around first match
                    snip = content[max(0, matches[0]-60):min(len(content), matches[0]+120)]
                    print(f'    snippet: {snip}')
    except Exception as e:
        print(f'{asset} error: {e}')
