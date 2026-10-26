import asyncio
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://huyca.pages.dev", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Bấm srcPhimNgan
        await page.click('#srcPhimNgan')
        await page.wait_for_timeout(3500)

        res = await page.evaluate("""() => {
            const grid = document.getElementById('mainGrid');
            const cards = grid ? grid.querySelectorAll('.movie-card') : [];
            const titles = Array.from(cards).map(c => {
                const titleEl = c.querySelector('.card-title') || c.querySelector('h3') || c;
                return titleEl.innerText.trim();
            });
            return {
                cardCount: cards.length,
                firstFive: titles.slice(0, 5),
                gridInnerExcerpt: grid ? grid.innerHTML.substring(0, 200) : ''
            };
        }""")
        print("ReelShort check:", res)

        # Bấm sang AI Cinema
        await page.click("button.btn-filter:has-text('AI Cinema')")
        await page.wait_for_timeout(3500)

        res_ai = await page.evaluate("""() => {
            const grid = document.getElementById('mainGrid');
            const cards = grid ? grid.querySelectorAll('.movie-card') : [];
            const titles = Array.from(cards).map(c => {
                const titleEl = c.querySelector('.card-title') || c.querySelector('h3') || c;
                return titleEl.innerText.trim();
            });
            return {
                cardCount: cards.length,
                firstFive: titles.slice(0, 5)
            };
        }""")
        print("AI Cinema check:", res_ai)

        await browser.close()

asyncio.run(main())
