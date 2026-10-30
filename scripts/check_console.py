import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

async def check_console():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})

        errors = []
        page.on('console', lambda msg: print(f"[{msg.type}] {msg.text}") if msg.type in ['error', 'warn'] else None)
        page.on('pageerror', lambda err: print(f"[PAGE ERROR] {err}"))

        await page.goto('http://localhost:8080')
        await page.wait_for_timeout(2000)

        # Click Phim Ngan
        print("Clicking #srcPhimNgan...")
        await page.click('#srcPhimNgan')
        await page.wait_for_timeout(2000)

        sub_btns = await page.locator('#animeSubSourcesBar button').all_inner_texts()
        print('Sub buttons:', sub_btns)

        filter_btns = await page.locator('#filterBar button').all_inner_texts()
        print('Filter buttons:', filter_btns)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(check_console())
