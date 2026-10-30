import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            extra_http_headers={"Referer": "https://phim.nguonc.com/"}
        )
        page = await context.new_page()

        async def handle_response(response):
            if "embed.php" in response.url and response.request.method == "POST":
                print("POST embed.php status:", response.status)
                try:
                    text = await response.text()
                    print("POST embed.php body:", text[:500])
                except Exception as e:
                    print("Could not read text:", e)
            elif "eyJ" in response.url:
                print("Token URL status:", response.status, response.url[:80])
                try:
                    text = await response.text()
                    print("Token URL body:", text[:500])
                except Exception as e:
                    print("Could not read text:", e)

        page.on("response", handle_response)

        embed_url = "https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec"
        await page.goto(embed_url, wait_until="networkidle", timeout=25000)
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
