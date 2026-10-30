import sys
import urllib.request
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://phimnguonc.com/'
})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# Insert base href and shield script
injected = """
<base href="https://embed17.streamc.xyz/">
<script>
window.open = function() { console.log('INTERCEPTED window.open'); return null; };
</script>
"""
html_mod = html.replace('<head>', '<head>' + injected)

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
    )
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    page.on('console', lambda msg: print(f'[PAGE CONSOLE] {msg.type}: {msg.text}'))
    page.set_content(html_mod)
    page.wait_for_timeout(6000)
    page.screenshot(path='scripts/test_injected_embed.png')
    print('Done test. Title:', page.title())
    
    # Check jwplayer
    jw_status = page.evaluate("""() => {
        const jw = (typeof window.jwplayer === 'function') ? window.jwplayer() : null;
        const v = document.querySelector('video');
        return {
            hasJw: !!jw,
            jwState: jw ? (jw.getState ? jw.getState() : 'unknown') : 'no_jw',
            hasVideo: !!v,
            videoSrc: v ? v.src : null,
            videoPaused: v ? v.paused : null
        };
    }""")
    print('JW status:', jw_status)
    browser.close()
