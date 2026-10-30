import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})

        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))

        await page.goto("http://localhost:8080", wait_until="networkidle")

        # Click Tab FREEREELS
        await page.click('#srcPhimNgan')
        await page.wait_for_timeout(2000)

        # Select Gà Mờ Mê Phim
        await page.click('button[data-sub="short_src://gamomephim"]')
        await page.wait_for_timeout(2500)

        # Count cards before
        c0 = await page.locator('#moviesContainer .movie-card').count()
        print(f"Cards initially loaded for GaMoMePhim (Phim Mới): {c0}")

        # Click BXH
        print("Clicking BXH...")
        btn = page.locator('#filterBar button[data-url="gamomephim://ban-xep-hang"]')
        print("Btn exists:", await btn.count())
        await btn.click()
        await page.wait_for_timeout(5000)

        c_bxh = await page.locator('#moviesContainer .movie-card').count()
        print(f"Cards in BXH after 5s: {c_bxh}")

        # Check first card title if any
        if c_bxh > 0:
            first_title = await page.locator('#moviesContainer .movie-card h3').first.inner_text()
            print("First movie title in BXH:", first_title)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
