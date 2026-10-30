import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    responses = {}
    page.on('response', lambda res: responses.update({res.url: (res.status, res.headers)}))

    # Test 1: Iframe WITH sandbox
    print("--- 1. Testing WITH sandbox ---")
    page.set_content("""
    <html><body>
    <iframe src="https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f"
            sandbox="allow-scripts allow-same-origin allow-forms allow-presentation">
    </iframe>
    </body></html>
    """)
    page.wait_for_timeout(4000)
    for url, (status, headers) in responses.items():
        if 'streamc.xyz' in url:
            print(f"WITH SANDBOX: {url} -> {status} (XFO: {headers.get('x-frame-options')})")

    responses.clear()

    # Test 2: Iframe WITHOUT sandbox (with referrerpolicy="origin")
    print("\n--- 2. Testing WITHOUT sandbox (referrerpolicy='origin') ---")
    page.set_content("""
    <html><body>
    <iframe src="https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f"
            allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
            allowfullscreen
            referrerpolicy="origin">
    </iframe>
    </body></html>
    """)
    page.wait_for_timeout(4000)
    for url, (status, headers) in responses.items():
        if 'streamc.xyz' in url:
            print(f"WITHOUT SANDBOX: {url} -> {status} (XFO: {headers.get('x-frame-options')})")

    browser.close()
