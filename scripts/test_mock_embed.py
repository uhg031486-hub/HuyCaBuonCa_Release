import asyncio
from playwright.async_api import async_playwright
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    target_embed = "https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec"
    
    req = urllib.request.Request(target_embed, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://phim.nguonc.com/'
    })
    with urllib.request.urlopen(req) as resp:
        original_html = resp.read().decode('utf-8', errors='ignore')

    injection = """
    <script>
    window.streamSandbox = {
        error: (stage, msg) => console.log('STREAM_SANDBOX_ERROR:', stage, msg),
        pipeline: (p) => console.log('STREAM_SANDBOX_PIPELINE:', JSON.stringify(p)),
        bootstrap: (b) => console.log('STREAM_SANDBOX_BOOTSTRAP:', JSON.stringify(b))
    };
    window.addEventListener('error', (e) => console.log('WINDOW_ERROR:', e.message));
    </script>
    """
    
    modified_html = original_html.replace('<head>', '<head>\n<base href="https://embed14.streamc.xyz/">\n' + injection)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        async def handle_route(route):
            request = route.request
            headers = {**request.headers}
            if "streamc.xyz" in request.url:
                headers['Referer'] = 'https://phim.nguonc.com/'
                headers['Origin'] = 'https://embed14.streamc.xyz'
            elif "hihihoho4.top" in request.url:
                headers['Referer'] = 'https://embed14.streamc.xyz/'
                headers['Origin'] = 'https://embed14.streamc.xyz'
                
            if request.url == "https://huyca.local/embed":
                await route.fulfill(status=200, content_type="text/html", body=modified_html)
            else:
                await route.continue_(headers=headers)

        await page.route("**/*", handle_route)
        page.on("console", lambda msg: print(f"CONSOLE {msg.type}: {msg.text}"))

        await page.goto("https://huyca.local/embed", wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
