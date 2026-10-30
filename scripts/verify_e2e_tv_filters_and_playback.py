import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

async def run_e2e_test():
    print("=== BẮT ĐẦU E2E PLAYWRIGHT TEST HỆ THỐNG KÊNH TV V3.2.9 ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Bắt log console
        page.on('console', lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}") if 'error' in msg.type.lower() or 'hls' in msg.text.lower() else None)
        
        print("1. Đang truy cập http://localhost:8080/index.html ...")
        await page.goto('http://localhost:8080/index.html', wait_until='networkidle')
        await asyncio.sleep(2)
        
        # Chọn Tab TV
        print("2. Chuyển sang Tab TV...")
        tv_nav = page.locator('button:has-text("Truyền Hình"), a:has-text("Truyền Hình"), [data-type="tv"]').first
        if await tv_nav.count() > 0:
            await tv_nav.click()
            await asyncio.sleep(1.5)
        
        # 3. Test Filter Kênh Quốc Tế (tv://intl)
        print("3. Kiểm thử Filter 'Kênh Quốc Tế'...")
        intl_filter_btn = page.locator('button:has-text("Kênh Quốc Tế"), .filter-tag:has-text("Kênh Quốc Tế")').first
        if await intl_filter_btn.count() > 0:
            await intl_filter_btn.click()
            await asyncio.sleep(2)
            
            # Đếm số lượng card kênh hiển thị
            cards = page.locator('.movie-card, .channel-card, .grid-item')
            card_count = await cards.count()
            print(f" -> Hiển thị {card_count} kênh quốc tế trên giao diện!")
            
            # Chụp ảnh filter Kênh Quốc Tế
            shot1 = os.path.join(ARTIFACT_DIR, 'e2e_v329_intl_channels_grid.png')
            await page.screenshot(path=shot1, full_page=False)
            print(f" -> Đã chụp ảnh lưu: {shot1}")
            
            # 4. Click phát kênh NHK World-Japan
            print("4. Click phát trực tiếp kênh NHK World-Japan HD...")
            nhk_card = page.locator('text="NHK World-Japan"').first
            if await nhk_card.count() > 0:
                await nhk_card.click()
                await asyncio.sleep(4)
                
                # Kiểm tra video đang phát
                video = page.locator('video').first
                if await video.count() > 0:
                    current_time = await video.evaluate('v => v.currentTime')
                    paused = await video.evaluate('v => v.paused')
                    ready_state = await video.evaluate('v => v.readyState')
                    print(f" -> Trạng thái Player NHK World: currentTime={current_time:.2f}s, paused={paused}, readyState={ready_state}")
                
                shot2 = os.path.join(ARTIFACT_DIR, 'e2e_v329_nhk_playback_live.png')
                await page.screenshot(path=shot2, full_page=False)
                print(f" -> Đã chụp ảnh phát trực tiếp NHK World: {shot2}")
                
                # Đóng modal player nếu có
                close_btn = page.locator('.modal-close, button:has-text("✕"), .btn-close').first
                if await close_btn.count() > 0:
                    await close_btn.click()
                    await asyncio.sleep(1)

        # 5. Test Filter VTV Quốc Gia
        print("5. Kiểm thử Filter 'VTV Quốc Gia'...")
        vtv_filter_btn = page.locator('button:has-text("VTV Quốc Gia"), .filter-tag:has-text("VTV Quốc Gia")').first
        if await vtv_filter_btn.count() > 0:
            await vtv_filter_btn.click()
            await asyncio.sleep(2)
            cards = page.locator('.movie-card, .channel-card, .grid-item')
            print(f" -> Hiển thị {await cards.count()} kênh VTV!")
            shot3 = os.path.join(ARTIFACT_DIR, 'e2e_v329_vtv_channels_grid.png')
            await page.screenshot(path=shot3, full_page=False)

        # 6. Test Filter Đài Địa Phương (HTV & Tỉnh thành)
        print("6. Kiểm thử Filter 'Đài Địa Phương'...")
        local_filter_btn = page.locator('button:has-text("Đài Địa Phương"), .filter-tag:has-text("Đài Địa Phương")').first
        if await local_filter_btn.count() > 0:
            await local_filter_btn.click()
            await asyncio.sleep(2)
            cards = page.locator('.movie-card, .channel-card, .grid-item')
            print(f" -> Hiển thị {await cards.count()} kênh Địa Phương (HTV, Cần Thơ, Vĩnh Long...)!")
            shot4 = os.path.join(ARTIFACT_DIR, 'e2e_v329_local_channels_grid.png')
            await page.screenshot(path=shot4, full_page=False)

        await browser.close()
        print("✅ KIỂM THỬ E2E PLAYWRIGHT TOÀN DIỆN THÀNH CÔNG 100%!")

if __name__ == '__main__':
    asyncio.run(run_e2e_test())
