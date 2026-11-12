import asyncio
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

async def verify_live_tv():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        context = await b.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Web0S; SmartTV; LargeScreen) AppleWebKit/537.36 Chrome/108.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        print("Connecting to live production on TV mode: https://huyca.pages.dev ...")
        await page.goto('https://huyca.pages.dev', wait_until='networkidle')

        # Test TV mode detection
        mode = await page.evaluate("() => document.body.className")
        print('Live TV Mode class:', mode)
        assert 'mode-tv' in mode, "Must be mode-tv"

        # Test D-Pad Right
        await page.keyboard.press('ArrowRight')
        focused = await page.evaluate("() => { const el = document.querySelector('.focused'); return el ? el.className : null; }")
        print('Focused class after D-Pad Right:', focused)
        assert focused is not None and 'focused' in focused, "Item must be focused"

        # Test video player controls
        await page.evaluate("""() => {
            const p = document.getElementById('playerContainer');
            p.style.display = 'flex';
            const v = document.getElementById('videoPlayer');
            Object.defineProperty(v, 'duration', { value: 3000, configurable: true, writable: true });
            v.currentTime = 100;
        }""")
        await page.keyboard.press('ArrowRight')
        cur = await page.evaluate("() => document.getElementById('videoPlayer').currentTime")
        print('CurrentTime after TV remote Right (+10s):', cur)
        assert cur == 110, 'Must seek +10s'

        await page.keyboard.press('ArrowLeft')
        cur2 = await page.evaluate("() => document.getElementById('videoPlayer').currentTime")
        print('CurrentTime after TV remote Left (-10s):', cur2)
        assert cur2 == 100, 'Must seek -10s'

        await b.close()
        print('>>> LIVE PROD TV REMOTE VERIFICATION: 100% OK! <<<')

if __name__ == "__main__":
    asyncio.run(verify_live_tv())
