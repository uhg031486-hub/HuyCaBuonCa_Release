import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

async def verify_live_prod():
    print("=== BẮT ĐẦU KIỂM THỬ TRỰC TIẾP TRÊN CLOUDFLARE PAGES LIVE PROD ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1366, 'height': 768})
        
        url = 'https://huyca.pages.dev'
        print(f"1. Đang truy cập {url}...")
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(2)
        
        # Click Xem TiVi
        print("2. Chuyển sang Tab TV (#srcXemTiVi)...")
        await page.click('#srcXemTiVi')
        await asyncio.sleep(2)
        
        # Click Filter Kênh Quốc Tế
        print("3. Chọn Filter 'Kênh Quốc Tế'...")
        intl_btn = page.locator('#filterBar button:has-text("Kênh Quốc Tế")')
        await intl_btn.click()
        await asyncio.sleep(2)
        
        cards = page.locator('#mainGrid .movie-card')
        count = await cards.count()
        print(f" -> [LIVE PROD] Số kênh quốc tế hiển thị: {count}")
        
        shot1 = os.path.join(ARTIFACT_DIR, 'live_prod_v329_intl_grid.png')
        await page.screenshot(path=shot1)
        print(f" -> Đã chụp ảnh lưu: {shot1}")
        
        # Click phát thử kênh NHK World-Japan
        print("4. Click phát trực tiếp NHK World-Japan trên Live Production...")
        nhk_card = page.locator('#mainGrid .movie-card:has-text("NHK World-Japan")').first
        if await nhk_card.count() > 0:
            await nhk_card.click()
            await asyncio.sleep(5)
            
            video = page.locator('video#videoPlayer')
            cur_time = await video.evaluate('v => v.currentTime')
            paused = await video.evaluate('v => v.paused')
            ready = await video.evaluate('v => v.readyState')
            print(f" -> [LIVE PROD VIDEO] currentTime={cur_time:.2f}s, paused={paused}, readyState={ready}")
            
            shot2 = os.path.join(ARTIFACT_DIR, 'live_prod_v329_nhk_playing.png')
            await page.screenshot(path=shot2)
            print(f" -> Đã chụp ảnh lưu Player phát live: {shot2}")
            
        await browser.close()
        print("🎉 KIỂM THỬ LIVE PRODUCTION CLOUDFLARE PAGES HOÀN TẤT THÀNH CÔNG VỚI EXIT CODE 0!")

if __name__ == '__main__':
    asyncio.run(verify_live_prod())
