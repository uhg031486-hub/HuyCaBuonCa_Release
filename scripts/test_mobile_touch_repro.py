import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Khởi động HTTP server local nếu chưa có
server_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8088", "--directory", "HuyCa_Web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)

print("=== BẮT ĐẦU TEST TÁI HIỆN LỖI CHẠM MÀN HÌNH PLAYER TRÊN MOBILE WEB ===")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Giả lập điện thoại di động
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()

        print("1. Truy cập HuyCa_Web trên Mobile...")
        page.goto("http://localhost:8088/index.html", wait_until="networkidle")
        time.sleep(2)

        # Chờ lưới phim xuất hiện
        page.wait_for_selector('.movie-card')
        first_card = page.locator('.movie-card').first
        print(f" -> Đã thấy phim: {first_card.inner_text().splitlines()[0] if first_card.inner_text() else 'Card'}")
        
        # Click vào phim đầu tiên
        first_card.click()
        time.sleep(1.5)

        # Bấm xem tập đầu
        page.wait_for_selector('#btnPlayFirst')
        print("2. Bấm '▶️ XEM TẬP ĐẦU'...")
        page.click('#btnPlayFirst')
        time.sleep(2)

        # Kiểm tra player đã mở chưa
        player_container = page.locator('#playerContainer')
        is_player_visible = player_container.is_visible()
        print(f" -> Trình phát video hiển thị: {is_player_visible}")

        # Kiểm tra trạng thái ban đầu của overlay
        overlay = page.locator('#playerOverlay')
        print(" -> Trạng thái overlay ban đầu:", overlay.get_attribute("class"))

        # Đợi 5.5 giây cho overlay tự động ẩn (hide timeout = 4.5s)
        print("3. Đợi 5.5s để overlay tự động ẩn khi đang xem...")
        time.sleep(5.5)

        overlay_class_after_wait = overlay.get_attribute("class") or ""
        print(f" -> Class của overlay sau 5.5s: '{overlay_class_after_wait}'")
        page.screenshot(path="scripts/mobile_player_controls_hidden.png")
        print(" -> Đã chụp: scripts/mobile_player_controls_hidden.png")

        # 4. GIẢ LẬP NGƯỜI DÙNG CUỐI: Chạm (TAP) vào màn hình video chính
        print("\n4. THỰC HIỆN THAO TÁC NGƯỜI DÙNG CUỐI: Chạm (Tap) ngón tay vào giữa màn hình video...")
        # Thử chạm qua touchscreen tap
        page.touchscreen.tap(195, 400)
        time.sleep(1)

        overlay_class_after_tap = overlay.get_attribute("class") or ""
        print(f" -> Class của overlay sau khi TAP: '{overlay_class_after_tap}'")

        # Kiểm tra opacity và pointer-events theo tính toán CSS
        is_hidden = "controls-hidden" in overlay_class_after_tap or "hide" in overlay_class_after_tap
        print(f" -> Overlay có còn bị 'controls-hidden' (tàng hình) không? {is_hidden}")

        page.screenshot(path="scripts/mobile_player_after_tap.png")
        print(" -> Đã chụp: scripts/mobile_player_after_tap.png")

        # Thử click vào #playerMainArea
        print("\n5. Thử click trực tiếp vào #playerMainArea...")
        page.locator('#playerMainArea').click(position={'x': 195, 'y': 400})
        time.sleep(1)
        overlay_class_after_click = overlay.get_attribute("class") or ""
        print(f" -> Class của overlay sau click #playerMainArea: '{overlay_class_after_click}'")

        # Thử chạm vào chính thẻ <video>
        print("\n6. Thử chạm (tap) vào thẻ <video>...")
        video_el = page.locator('#videoPlayer')
        if video_el.count() > 0:
            video_el.tap()
            time.sleep(1)
            overlay_class_after_video_tap = overlay.get_attribute("class") or ""
            print(f" -> Class của overlay sau khi tap thẻ <video>: '{overlay_class_after_video_tap}'")

        browser.close()
finally:
    server_proc.terminate()
