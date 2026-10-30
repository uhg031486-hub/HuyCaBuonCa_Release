import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8080')
        await page.wait_for_timeout(2000)
        await page.locator('#btnSearch').click()
        await page.locator('#searchInput').fill('nhu y truyen')
        await page.locator('#btnDoSearch').click()
        await page.wait_for_timeout(3000)
        await page.locator('#searchResultsGrid .movie-card').first.click()
        await page.wait_for_timeout(2000)
        await page.locator('#episodesGrid .btn-episode').first.click()
        await page.wait_for_timeout(6000)
        for f in page.frames:
            if 'streamc' in f.url:
                txt = await f.locator('body').inner_text()
                print('Iframe inner text:\n', txt[:400])
                v = f.locator('video')
                if await v.count() > 0:
                    cur = await v.first.evaluate('e => e.currentTime')
                    dur = await v.first.evaluate('e => e.duration')
                    paused = await v.first.evaluate('e => e.paused')
                    print(f'Video in iframe: cur = {cur}, dur = {dur}, paused = {paused}')
                else:
                    print('Video tag not found in iframe!')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(check())
