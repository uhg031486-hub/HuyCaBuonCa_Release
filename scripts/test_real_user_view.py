import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== TEST VỚI TRÌNH DUYỆT THƯỜNG (KHÔNG HOOK CONSOLE, KHÔNG DEVTOOLS) ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-infobars',
                '--autoplay-policy=no-user-gesture-required'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Đi tới https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Search nhu y truyen
        await page.locator("#btnSearch").click()
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(3000)

        await page.locator("#searchResultsGrid .movie-card").first.click()
        await page.wait_for_timeout(2000)

        # Click Tap 1
        print("Clicking Tap 1...")
        await page.locator("#episodesGrid .btn-episode").first.click()

        print("Đợi 8 giây...")
        await page.wait_for_timeout(8000)

        # Chụp ảnh toàn màn hình player
        await page.screenshot(path="scripts/real_user_view.png")
        print("Đã lưu scripts/real_user_view.png")

        # Kiểm tra iframe src và URL
        iframe_src = await page.locator("#playerIframe").get_attribute("src")
        print(f"Iframe src attribute: {iframe_src}")

        for i, f in enumerate(page.frames):
            print(f"Frame {i}: {f.url}")
            if "streamc" in f.url:
                body_txt = await f.locator("body").inner_text()
                print(f"  Frame {i} body text: {body_txt.strip().replace(chr(10), ' ')[:200]}")
                # Kiểm tra video
                v = f.locator("video")
                if await v.count() > 0:
                    cur = await v.first.evaluate("el => el.currentTime")
                    dur = await v.first.evaluate("el => el.duration")
                    paused = await v.first.evaluate("el => el.paused")
                    print(f"  🎬 VIDEO IN IFRAME: cur={cur}, dur={dur}, paused={paused}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
