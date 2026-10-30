import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def debug_dom():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Bắt log console
        page.on('console', lambda msg: print(f"[Console] {msg.text}"))
        
        await page.goto('http://localhost:8080/', wait_until='networkidle')
        await asyncio.sleep(1)
        
        # Click Xem TiVi
        await page.click('#srcXemTiVi')
        await asyncio.sleep(2)
        
        # Xem các filter button có trong filterBar
        filter_buttons = await page.locator('#filterBar button, #filterBar .filter-item').all_inner_texts()
        print("Filter buttons:", filter_buttons)
        
        # Xem HTML của movieGrid
        grid_html = await page.locator('#movieGrid').inner_html()
        print(f"Grid HTML length: {len(grid_html)}")
        
        # Click filter Kênh Quốc Tế
        intl_btn = page.locator('#filterBar button:has-text("Kênh Quốc Tế")')
        if await intl_btn.count() > 0:
            print("Clicking Kênh Quốc Tế...")
            await intl_btn.click()
            await asyncio.sleep(2)
            
            # Kiểm tra innerText của movieGrid
            grid_text = await page.locator('#movieGrid').inner_text()
            print("Grid text preview:", grid_text[:200])
            
            # Xem các class của children trong movieGrid
            children = await page.locator('#movieGrid > *').evaluate_all('els => els.map(e => ({ tag: e.tagName, cls: e.className, text: e.innerText.slice(0, 30) }))')
            print(f"Found {len(children)} children in #movieGrid:")
            for c in children[:5]:
                print("  ", c)
                
        await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_dom())
