import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

async def run_debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})

        page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
        page.on("request", lambda req: print(f"[REQ] {req.method} {req.url}") if 'gamome' in req.url or 'proxy' in req.url else None)
        page.on("response", lambda res: print(f"[RESP] {res.status} {res.url}") if 'gamome' in res.url or 'proxy' in res.url else None)

        await page.goto("http://localhost:8080", wait_until="networkidle")
        await page.click('#srcPhimNgan')
        await page.wait_for_timeout(2000)

        await page.click('button[data-sub="short_src://gamomephim"]')
        await page.wait_for_timeout(2000)

        print("--- CLICKING BXH ---")
        await page.click('#filterBar button[data-url="gamomephim://ban-xep-hang"]')
        await page.wait_for_timeout(4000)

        cards = page.locator('#moviesContainer .movie-card')
        count = await cards.count()
        print(f"Cards count in BXH: {count}")

        # Check raw HTML in moviesContainer
        html = await page.inner_html('#moviesContainer')
        print("MoviesContainer innerHTML:", html[:500])

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_debug())
