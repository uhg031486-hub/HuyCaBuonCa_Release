import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
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
        page = await context.new_page()

        # Monitor all requests and responses
        page.on("request", lambda req: print(f"REQ: {req.method} {req.url} (resource: {req.resource_type})"))
        page.on("response", lambda res: print(f"RES: {res.status} {res.url} (ok: {res.ok})") if res.status != 200 else None)
        page.on("requestfailed", lambda req: print(f"FAIL: {req.method} {req.url} -> {req.failure}"))
        page.on("console", lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))

        print("Navigating to https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Search nhu y truyen
        await page.locator("#btnSearch").click()
        await page.wait_for_timeout(500)
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(3000)

        await page.locator("#searchResultsGrid .movie-card").first.click()
        await page.wait_for_timeout(2000)

        # Click Tập 1
        ep1 = page.locator("#episodesGrid .btn-episode").first
        print(f"Clicking: {await ep1.inner_text()}")
        await ep1.click()

        print("Waiting 12 seconds for player to load inside iframe...")
        await page.wait_for_timeout(12000)

        for f in page.frames:
            if "streamc" in f.url:
                print(f"\n--- IFRAME FOUND: {f.url} ---")
                try:
                    logs = await f.evaluate("""() => {
                        return {
                            bootstrapText: document.getElementById('stream-bootstrap')?.textContent,
                            verificationText: document.getElementById('verification-message')?.textContent,
                            verificationHidden: document.getElementById('verification')?.hidden,
                            errorClasses: document.getElementById('verification')?.className,
                            bodyText: document.body?.innerText?.slice(0, 500)
                        };
                    }""")
                    print("Iframe state:", logs)
                except Exception as e:
                    print("Could not evaluate in frame:", e)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
