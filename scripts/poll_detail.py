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
        await page.locator('#searchResultsGrid .movie-card').first.click()
        print('Clicked card, waiting for detail...')
        for t in range(1, 8):
            await page.wait_for_timeout(1000)
            status = await page.evaluate('''() => {
                const b = document.getElementById('btnDirectPlayDetail');
                const eps = document.querySelectorAll('#episodesGrid .btn-episode').length;
                const desc = document.getElementById('detailDesc')?.textContent;
                return {
                    epCount: eps,
                    desc: desc?.slice(0, 40),
                    btnDirectDisplay: b ? b.style.display : 'no_btn',
                    btnDirectVisible: b ? (b.offsetWidth > 0 && b.offsetHeight > 0) : false
                };
            }''')
            print(f'Second {t}: {status}')
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())
