import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== ĐIỀU TRA CHÍNH XÁC HÀNH VI QUẢNG CÁO TRÊN NGUỒN C ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        opened_pages = []
        context.on("page", lambda new_p: opened_pages.append(new_p))

        page = await context.new_page()

        print("1. Mở http://localhost:8080 ...")
        await page.goto("http://localhost:8080", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Mở phim Như Ý Truyện
        print("2. Tìm kiếm 'nhu y truyen'...")
        await page.locator("#btnSearch").click()
        await page.wait_for_timeout(500)
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(3000)

        await page.locator("#searchResultsGrid .movie-card").first.click()
        await page.wait_for_timeout(2500)

        # Click Tập 1
        print("3. Click Tập 1...")
        await page.locator("#episodesGrid .btn-episode").first.click()
        await page.wait_for_timeout(6000)

        print("4. Thử click 5 lần vào các vị trí trên Player...")
        for i in range(5):
            print(f"  Click {i+1} vào giữa player...")
            await page.mouse.click(640, 360)
            await page.wait_for_timeout(1500)

        print(f"\n=> TỔNG SỐ TRANG QUẢNG CÁO POPUP BỊ MỞ: {len(opened_pages)}")
        for idx, pg in enumerate(opened_pages):
            try:
                print(f"  Popup {idx+1}: URL = {pg.url}, Title = {await pg.title()}")
            except Exception as e:
                print(f"  Popup {idx+1}: {e}")

        # Chụp ảnh Player hiện tại
        await page.screenshot(path="scripts/ads_test_player.png")
        print("Đã lưu ảnh: scripts/ads_test_player.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
