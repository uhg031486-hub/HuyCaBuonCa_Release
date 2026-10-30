import sys
import urllib.request
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://phimnguonc.com/'
})
resp = urllib.request.urlopen(req)
html = resp.read().decode('utf-8', errors='ignore')

# 1. Base href
base_tag = '<base href="https://embed17.streamc.xyz/">'

# 2. Ad-block script
shield = """
<script>
window.open = function() { console.log('Blocked window.open'); return null; };
window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'stream-guard-hello') {
        window.postMessage({
            type: 'stream-parent-state',
            version: 'guard-5',
            id: e.data.id,
            helperVersion: 'guard-5',
            parentAdblock: 'clear',
            seq: Date.now(),
            supported: true,
            suspected: false
        }, '*');
    }
});
</script>
"""

# 3. Disable ads in bootstrap
html_mod = html.replace('<head>', '<head>' + base_tag + shield)
html_mod = re.sub(r'"ads":\s*\{\s*"enabled":\s*true', '"ads":{"enabled":false', html_mod)
html_mod = re.sub(r'"tvc":\s*\{\s*"enabled":\s*true', '"tvc":{"enabled":false', html_mod)

with open('HuyCa_Web/clean_test.html', 'w', encoding='utf-8') as f:
    f.write(html_mod)
print('Successfully wrote HuyCa_Web/clean_test.html, length:', len(html_mod))
