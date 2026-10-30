import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

async def run_inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})

        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))

        await page.goto("http://localhost:8080", wait_until="networkidle")

        # Evaluate GaMoMePhimClient directly
        res = await page.evaluate("""async () => {
            try {
                const proxyUrl = window.GaMoMePhimClient.getProxyUrl('https://gamomephim.com/ban-xep-hang');
                console.log('Proxy URL computed:', proxyUrl);
                const list = await window.GaMoMePhimClient.getDramaList('gamomephim://ban-xep-hang', 1);
                return { proxyUrl, count: list.length, first: list[0] };
            } catch (e) {
                return { error: e.message, stack: e.stack };
            }
        }""")
        print("Direct evaluate result:", res)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_inspect())
