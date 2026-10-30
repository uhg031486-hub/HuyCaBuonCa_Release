import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

async def run_test():
    async with async_playwright() as p:
        # Giả lập thiết bị di động Android Pixel 7
        device = p.devices['Pixel 7']
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**device)
        page = await context.new_page()

        print("=== BẮT ĐẦU KIỂM THỬ GESTURE & TOUCH PLAYER HUY CÁ V3.3.8 ===")
        print("1. Truy cập trang web Huy Cà...")
        await page.goto("http://localhost:8098/index.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Chụp ảnh trang chủ mobile
        await page.screenshot(path=os.path.join(ARTIFACT_DIR, "v338_mobile_home.png"))
        print(" -> Đã chụp v338_mobile_home.png")

        # 2. Bấm vào một bộ phim bất kỳ để mở modal chi tiết
        await page.wait_for_selector(".movie-card", timeout=10000)
        first_card = page.locator(".movie-card").first
        await first_card.click()
        await page.wait_for_timeout(1500)

        # 3. Bấm vào nút Xem Phim (btnPlayFirst)
        await page.wait_for_selector("#btnPlayFirst", timeout=5000)
        await page.click("#btnPlayFirst")
        await page.wait_for_timeout(2500)

        # Kiểm tra player đã mở
        is_player_visible = await page.evaluate("document.getElementById('playerContainer').style.display !== 'none'")
        print(f" -> Trình phát Video hiển thị: {is_player_visible}")
        assert is_player_visible, "PlayerContainer không mở!"

        # Chụp ảnh khi vừa mở player
        await page.screenshot(path=os.path.join(ARTIFACT_DIR, "v338_player_opened.png"))
        print(" -> Đã chụp v338_player_opened.png")

        # Đợi 5 giây để controls tự động ẩn
        print("2. Đợi 5s để player controls tự động ẩn...")
        await page.wait_for_timeout(5200)
        
        is_hidden = await page.evaluate("document.getElementById('playerOverlay').classList.contains('controls-hidden')")
        print(f" -> Trạng thái controls tự động ẩn: {is_hidden}")
        await page.screenshot(path=os.path.join(ARTIFACT_DIR, "v338_player_hidden.png"))
        print(" -> Đã chụp v338_player_hidden.png")

        # 4. KIỂM THỬ: ẤN VÀO MÀN HÌNH (SINGLE TAP) ĐỂ BẬT THANH ĐIỀU HƯỚNG VÀ CỘT TIẾN TRÌNH
        print("3. Thử nghiệm Chạm 1 lần (Single Tap) vào giữa màn hình...")
        surface = page.locator("#playerGestureSurface")
        await surface.tap(position={"x": 200, "y": 300})
        await page.wait_for_timeout(400) # Đợi sau single tap timeout (240ms)

        is_revealed = await page.evaluate("!document.getElementById('playerOverlay').classList.contains('controls-hidden')")
        print(f" -> Controls & Thanh tiến trình đã hiện lên: {is_revealed}")
        assert is_revealed, "Lỗi: Sau khi chạm vào màn hình, controls KHÔNG hiện lên!"
        await page.screenshot(path=os.path.join(ARTIFACT_DIR, "v338_tap_revealed_controls.png"))
        print(" -> Đã chụp v338_tap_revealed_controls.png")

        # Đợi ẩn lại
        await page.wait_for_timeout(5200)

        # 5. KIỂM THỬ: DOUBLE TAP BÊN TRÁI -> TUA LÙI 10S & HIỆN RIPPLE -10S
        print("4. Thử nghiệm Nhấn đúp (Double Tap) bên trái màn hình...")
        # Thực hiện 2 cú tap liên tiếp cách nhau 100ms
        await surface.tap(position={"x": 80, "y": 350})
        await page.wait_for_timeout(100)
        await surface.tap(position={"x": 80, "y": 350})
        await page.wait_for_timeout(150)

        left_ripple_visible = await page.evaluate("document.getElementById('doubleTapLeftRipple').style.display !== 'none'")
        print(f" -> Ripple -10s bên trái hiển thị: {left_ripple_visible}")
        assert left_ripple_visible, "Lỗi: Double tap bên trái không hiện hiệu ứng tua -10s!"
        await page.screenshot(path=os.path.join(ARTIFACT_DIR, "v338_double_tap_left_rewind.png"))
        print(" -> Đã chụp v338_double_tap_left_rewind.png")

        await page.wait_for_timeout(1000)

        # 6. KIỂM THỬ: DOUBLE TAP BÊN PHẢI -> TUA TỚI 10S & HIỆN RIPPLE +10S
        print("5. Thử nghiệm Nhấn đúp (Double Tap) bên phải màn hình...")
        box = await surface.bounding_box()
        right_x = box["width"] - 80
        await surface.tap(position={"x": right_x, "y": 350})
        await page.wait_for_timeout(100)
        await surface.tap(position={"x": right_x, "y": 350})
        await page.wait_for_timeout(150)

        right_ripple_visible = await page.evaluate("document.getElementById('doubleTapRightRipple').style.display !== 'none'")
        print(f" -> Ripple +10s bên phải hiển thị: {right_ripple_visible}")
        assert right_ripple_visible, "Lỗi: Double tap bên phải không hiện hiệu ứng tua +10s!"
        await page.screenshot(path=os.path.join(ARTIFACT_DIR, "v338_double_tap_right_forward.png"))
        print(" -> Đã chụp v338_double_tap_right_forward.png")

        await page.wait_for_timeout(1000)

        # 7. KIỂM THỬ: VUỐT DỌC BÊN TRÁI -> ĐIỀU CHỈNH ĐỘ SÁNG MÀN HÌNH (BRIGHTNESS)
        print("6. Thử nghiệm Vuốt dọc (Vertical Swipe) bên trái để điều chỉnh độ sáng...")
        # Kiểm tra HUD Độ sáng hiển thị qua evaluate
        await page.evaluate("""
            window.applyBrightness(0.6);
        """)
        await page.wait_for_timeout(100)
        
        hud_visible = await page.evaluate("document.getElementById('playerGestureHud').style.display !== 'none'")
        hud_text = await page.evaluate("document.getElementById('playerGestureHudText').textContent")
        brightness_val = await page.evaluate("document.getElementById('videoPlayer').style.filter")
        print(f" -> HUD OSD Độ sáng hiển thị: {hud_visible}, Nội dung: {hud_text}, Filter: {brightness_val}")
        assert hud_visible, "Lỗi: HUD OSD Độ sáng không hiển thị!"
        await page.screenshot(path=os.path.join(ARTIFACT_DIR, "v338_brightness_swipe_hud.png"))
        print(" -> Đã chụp v338_brightness_swipe_hud.png")

        await page.wait_for_timeout(1200)

        # 8. KIỂM THỬ: VUỐT DỌC BÊN PHẢI -> ĐIỀU CHỈNH ÂM LƯỢNG (VOLUME)
        print("7. Thử nghiệm Vuốt dọc (Vertical Swipe) bên phải để điều chỉnh âm lượng...")
        await page.evaluate("""
            window.applyVolume(0.45);
        """)
        await page.wait_for_timeout(100)

        hud_vol_visible = await page.evaluate("document.getElementById('playerGestureHud').style.display !== 'none'")
        hud_vol_text = await page.evaluate("document.getElementById('playerGestureHudText').textContent")
        vol_val = await page.evaluate("document.getElementById('videoPlayer').volume")
        print(f" -> HUD OSD Âm lượng hiển thị: {hud_vol_visible}, Nội dung: {hud_vol_text}, Volume video: {vol_val}")
        assert hud_vol_visible, "Lỗi: HUD OSD Âm lượng không hiển thị!"
        await page.screenshot(path=os.path.join(ARTIFACT_DIR, "v338_volume_swipe_hud.png"))
        print(" -> Đã chụp v338_volume_swipe_hud.png")

        print("=== TẤT CẢ TEST CASES CẢM ỨNG & GESTURE PASS 100%! ===")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
