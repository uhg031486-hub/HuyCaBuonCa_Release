import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Navigating to https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle")

        # Open search and select Như Ý Truyện
        await page.locator("#btnSearch").click()
        await page.wait_for_timeout(1000)
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(4000)

        card = page.locator("#searchResultsGrid .movie-card").first
        await card.click()
        await page.wait_for_timeout(3000)

        # Click Tập 40
        await page.locator("#episodesGrid .btn-episode").filter(has_text="40").first.click()
        print("Clicked Ep 40. Waiting 8s...")
        await page.wait_for_timeout(8000)

        print("\nFrames in page:")
        for i, frame in enumerate(page.frames):
            print(f"Frame {i}: url={frame.url[:80]}")
            if "streamc" in frame.url:
                try:
                    title = await frame.title()
                    print(f"  Title: {title}")
                    body_text = await frame.locator("body").inner_text()
                    print(f"  Body text:\n{body_text[:300]}")
                    
                    jw_exists = await frame.evaluate("typeof window.jwplayer !== 'undefined'")
                    print(f"  JWPlayer loaded: {jw_exists}")
                    if jw_exists:
                        jw_state = await frame.evaluate("typeof window.jwplayer === 'function' ? window.jwplayer().getState() : 'N/A'")
                        print(f"  JWPlayer state: {jw_state}")
                except Exception as e:
                    print(f"  Frame eval error: {e}")

        await page.screenshot(path="scripts/inspect_iframe_live.png")
        print("\nScreenshot saved to scripts/inspect_iframe_live.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
