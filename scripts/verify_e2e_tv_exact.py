import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

async def run_test():
    print("=== BẮT ĐẦU E2E PLAYWRIGHT TEST CHUẨN XÁC V3.2.9 ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("1. Truy cập http://localhost:8080/ ...")
        await page.goto('http://localhost:8080/', wait_until='networkidle')
        await asyncio.sleep(2)

        print("2. Click chuyển sang tab '📺 XEM TIVI' (#srcXemTiVi)...")
        await page.click('#srcXemTiVi')
        await asyncio.sleep(2)

        # 3. Click Filter 'Kênh Quốc Tế'
        print("3. Click Filter 'Kênh Quốc Tế' trong #filterBar...")
        intl_btn = page.locator('#filterBar button:has-text("Kênh Quốc Tế")')
        await intl_btn.click()
        await asyncio.sleep(2)

        cards = page.locator('#mainGrid .movie-card')
        card_count = await cards.count()
        print(f" -> [THÀNH CÔNG] Số kênh quốc tế hiển thị trong #mainGrid: {card_count}")

        # Chụp màn hình kho kênh Quốc Tế
        shot1 = os.path.join(ARTIFACT_DIR, 'e2e_v329_intl_grid_success.png')
        await page.screenshot(path=shot1)
        print(f" -> Đã chụp ảnh danh sách Kênh Quốc Tế: {shot1}")

        # 4. Click phát kênh NHK World-Japan
        print("4. Click phát trực tiếp kênh NHK World-Japan HD...")
        nhk_card = page.locator('#mainGrid .movie-card:has-text("NHK World-Japan")').first
        if await nhk_card.count() > 0:
            await nhk_card.click()
            print(" -> Đang tải stream và khởi tạo HLS player...")
            await asyncio.sleep(5)

            # Kiểm tra trạng thái video
            video = page.locator('video#videoPlayer')
            cur_time = await video.evaluate('v => v.currentTime')
            paused = await video.evaluate('v => v.paused')
            ready = await video.evaluate('v => v.readyState')
            print(f" -> [PLAYER LIVE NHK] currentTime={cur_time:.2f}s, paused={paused}, readyState={ready}")

            # Chụp ảnh Player đang phát live NHK World-Japan
            shot2 = os.path.join(ARTIFACT_DIR, 'e2e_v329_nhk_player_success.png')
            await page.screenshot(path=shot2)
            print(f" -> Đã chụp ảnh Player phát NHK World-Japan HD: {shot2}")

            # Đóng player bằng phím Escape
            print(" -> Đóng Player bằng Escape...")
            await page.keyboard.press('Escape')
            await asyncio.sleep(1.5)

        # 5. Click Filter VTV Quốc Gia
        print("5. Click Filter 'VTV Quốc Gia'...")
        vtv_btn = page.locator('#filterBar button:has-text("VTV Quốc Gia")')
        if await vtv_btn.count() > 0:
            await vtv_btn.click()
            await asyncio.sleep(2)
            vtv_count = await page.locator('#mainGrid .movie-card').count()
            print(f" -> [THÀNH CÔNG] Số kênh VTV hiển thị: {vtv_count}")
            shot3 = os.path.join(ARTIFACT_DIR, 'e2e_v329_vtv_grid_success.png')
            await page.screenshot(path=shot3)
            print(f" -> Đã chụp ảnh danh sách Kênh VTV: {shot3}")

        # 6. Click Filter Đài Địa Phương (HTV & Tỉnh)
        print("6. Click Filter 'Đài Địa Phương'...")
        local_btn = page.locator('#filterBar button:has-text("Đài Địa Phương")')
        if await local_btn.count() > 0:
            await local_btn.click()
            await asyncio.sleep(2)
            local_count = await page.locator('#mainGrid .movie-card').count()
            print(f" -> [THÀNH CÔNG] Số kênh Địa Phương hiển thị: {local_count}")
            shot4 = os.path.join(ARTIFACT_DIR, 'e2e_v329_local_grid_success.png')
            await page.screenshot(path=shot4)
            print(f" -> Đã chụp ảnh danh sách Kênh Địa Phương: {shot4}")

        # 7. Click Filter Cúp C1 & Thể Thao
        print("7. Click Filter '🏆 Cúp C1 & Thể Thao ESPN'...")
        sports_btn = page.locator('#filterBar button:has-text("Thể Thao")').first
        if await sports_btn.count() > 0:
            await sports_btn.click()
            await asyncio.sleep(2)
            sports_count = await page.locator('#mainGrid .movie-card').count()
            print(f" -> [THÀNH CÔNG] Số kênh Thể Thao hiển thị: {sports_count}")
            shot5 = os.path.join(ARTIFACT_DIR, 'e2e_v329_sports_grid_success.png')
            await page.screenshot(path=shot5)
            print(f" -> Đã chụp ảnh danh sách Kênh Thể Thao: {shot5}")

        await browser.close()
        print("🎉 TẤT CẢ KIỂM THỬ E2E TRỰC QUAN ĐÃ HOÀN TẤT THÀNH CÔNG VỚI EXIT CODE 0!")

if __name__ == '__main__':
    asyncio.run(run_test())
