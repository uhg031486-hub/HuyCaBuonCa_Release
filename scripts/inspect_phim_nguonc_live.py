import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
    )
    page = browser.new_page()
    page.on('request', lambda req: print('REQ:', req.url, '\nHEADERS:', req.headers) if 'streamc' in req.url else None)
    page.on('response', lambda res: print('RESP:', res.url, res.status, '\nHEADERS:', res.headers) if 'streamc' in res.url else None)
    
    page.goto('https://phim.nguonc.com/phim/shaun-the-sheep-quai-la-ghe-nha')
    page.wait_for_timeout(3000)
    
    # Click play button or episode
    btns = page.query_selector_all('button, a')
    for b in btns:
        txt = b.inner_text().lower()
        if 'xem phim' in txt or 'tập 1' in txt or 'bản đẹp' in txt:
            print('Clicking:', txt)
            b.click()
            break
            
    page.wait_for_timeout(5000)
    browser.close()
