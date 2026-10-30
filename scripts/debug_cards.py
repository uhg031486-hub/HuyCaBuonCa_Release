import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://huyca.pages.dev')
        await page.wait_for_timeout(2000)
        await page.locator('#btnSearch').click()
        await page.locator('#searchInput').fill('nhu y truyen')
        await page.locator('#btnDoSearch').click()
        await page.wait_for_timeout(3000)
        cards = page.locator('#searchResultsGrid .movie-card')
        count = await cards.count()
        print('Total search results:', count)
        for i in range(count):
            txt = await cards.nth(i).inner_text()
            lines = " | ".join(txt.splitlines())
            print(f'Card {i}: {lines}')
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())
