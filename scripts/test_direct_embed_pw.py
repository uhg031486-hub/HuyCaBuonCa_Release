import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Create context with Referer header or extra HTTP headers
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            extra_http_headers={"Referer": "https://phim.nguonc.com/"}
        )
        page = await context.new_page()

        requests_log = []
        page.on("request", lambda r: requests_log.append((r.method, r.url, r.resource_type)))
        page.on("requestfailed", lambda r: print(f"FAILED: {r.method} {r.url} - {r.failure}"))
        page.on("console", lambda msg: print(f"CONSOLE: {msg.type}: {msg.text}"))

        embed_url = "https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec"
        print(f"Navigating to {embed_url}...")
        try:
            await page.goto(embed_url, wait_until="networkidle", timeout=20000)
        except Exception as e:
            print("Goto finished with:", e)

        await page.wait_for_timeout(5000)

        print("\n--- Network Requests Captured ---")
        for method, url, rtype in requests_log:
            if any(k in url for k in ['.m3u8', '.mp4', '.png', 'embed.php', 'api', 'stream', 'jwplayer']):
                print(f"[{rtype}] {method} {url[:120]}")

        # Check DOM
        title = await page.title()
        print("\nPage title:", title)
        has_video = await page.locator("video").count()
        print("Video elements count:", has_video)
        if has_video > 0:
            src = await page.locator("video").first.get_attribute("src")
            print("Video src:", src)

        has_jw = await page.evaluate("typeof window.jwplayer !== 'undefined'")
        print("jwplayer loaded:", has_jw)
        if has_jw:
            state = await page.evaluate("typeof window.jwplayer === 'function' && window.jwplayer().getState ? window.jwplayer().getState() : 'no player'")
            print("JWPlayer state:", state)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
