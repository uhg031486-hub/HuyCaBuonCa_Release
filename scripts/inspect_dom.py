import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://localhost:8080')
        await page.wait_for_timeout(2500)
        
        # Click FREEREELS
        await page.click('button[data-source="FREEREELS"]')
        await page.wait_for_timeout(2500)

        # Print all buttons inside #animeSubSourcesBar and #filterBar
        sub_btns = await page.locator('#animeSubSourcesBar button').all_inner_texts()
        print('Sub-source buttons:', sub_btns)

        # Click GaMoMePhim
        await page.click('#animeSubSourcesBar button:has-text("Gà Mờ Mê Phim")')
        await page.wait_for_timeout(2500)

        filter_btns = await page.locator('#filterBar button').all_inner_texts()
        print(f'Total Filter buttons in GaMoMePhim: {len(filter_btns)}')
        print('Filter buttons in GaMoMePhim:', filter_btns)

        cards = await page.locator('.movie-card').count()
        print('Movie cards count:', cards)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect())
