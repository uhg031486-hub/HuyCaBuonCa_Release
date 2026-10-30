import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== TEST MỞ TRỰC TIẾP EMBED TRONG TAB ĐỘC LẬP ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--autoplay-policy=no-user-gesture-required'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        embed_url = "https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f"
        print(f"Điều hướng tới: {embed_url} ...")
        await page.goto(embed_url, wait_until="networkidle")
        await page.wait_for_timeout(5000)

        # Chụp ảnh xem màn hình embed hiển thị gì
        await page.screenshot(path="scripts/direct_tab_embed.png")
        print("Đã lưu ảnh màn hình: scripts/direct_tab_embed.png")

        # Kiểm tra video element
        v = page.locator("video")
        count = await v.count()
        print(f"Số lượng thẻ <video>: {count}")
        if count > 0:
            cur = await v.first.evaluate("el => el.currentTime")
            dur = await v.first.evaluate("el => el.duration")
            paused = await v.first.evaluate("el => el.paused")
            print(f"🎬 VIDEO STATE: currentTime={cur}, duration={dur}, paused={paused}")

        # Thử click play nếu đang pause
        play_btn = page.locator(".jw-display-icon-container, #player")
        if await play_btn.count() > 0:
            print("Click vào khung player để phát...")
            await play_btn.first.click()
            await page.wait_for_timeout(3000)
            if count > 0:
                cur2 = await v.first.evaluate("el => el.currentTime")
                paused2 = await v.first.evaluate("el => el.paused")
                print(f"🎬 SAU KHI CLICK: currentTime={cur2}, paused={paused2}")
                await page.screenshot(path="scripts/direct_tab_playing.png")
                print("Đã lưu ảnh đang phát: scripts/direct_tab_playing.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
