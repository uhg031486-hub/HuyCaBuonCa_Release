import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

async def verify_live_prod():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        live_url = "https://937b0fc9.huyca.pages.dev"
        print(f"Connecting to live production: {live_url} ...")
        await page.goto(live_url, wait_until="networkidle")

        # Check attributes and styles on live prod
        result = await page.evaluate("""() => {
            const playerCont = document.getElementById('playerContainer');
            playerCont.style.display = 'flex';
            playerCont.classList.remove('hide');

            const overlay = document.getElementById('playerOverlay');
            overlay.classList.remove('hide', 'controls-hidden');
            overlay.style.opacity = '1';
            overlay.style.display = 'flex';

            const seekBar = document.getElementById('seekBar');
            seekBar.focus();

            const st = window.getComputedStyle(seekBar);
            return {
                hasClassFocusable: seekBar.classList.contains('focusable'),
                tabIndex: seekBar.getAttribute('tabindex'),
                boxShadow: st.boxShadow,
                outline: st.outline,
                borderColor: st.borderColor,
                hasCyan: st.outline.includes('0, 229, 255') || st.boxShadow.includes('0, 229, 255') || st.borderColor.includes('0, 229, 255')
            };
        }""")
        print("Live Prod Result:", result)

        artifact_dir = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
        shot_path = os.path.join(artifact_dir, "live_prod_clean_seekbar.png")
        await page.screenshot(path=shot_path)
        print("Captured live production screenshot:", shot_path)

        await browser.close()

        assert not result.get('hasClassFocusable'), "Live prod seekBar still has class focusable"
        assert result.get('tabIndex') == '-1', "Live prod seekBar does not have tabindex='-1'"
        assert not result.get('hasCyan'), "Live prod seekBar still has cyan outline/glow"
        print(">>> LIVE PROD VERIFICATION SUCCESS: 100% CLEAN! <<<")

if __name__ == "__main__":
    asyncio.run(verify_live_prod())
