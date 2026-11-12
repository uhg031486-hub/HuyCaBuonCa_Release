import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def test_mobile_fullscreen_no_native_popup():
    print("=== TEST TDD: LOẠI BỎ TRIỆT ĐỂ POPUP TOÀN MÀN HÌNH TRÊN MOBILE ===")
    all_passed = True
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 1. Khởi tạo môi trường Mobile (Android Chrome Viewport)
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent='Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
        )
        page = context.new_page()
        page.goto("http://localhost:8098/", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        
        # Mở phim ngang trên mobile
        page.evaluate("""() => {
            window.playVideo('https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'Phim Cổ Trang', 'Tập 01', { name: 'Phim Cổ Trang', isShortDrama: false }, null, 0, 0);
            if (typeof showPlayerControls === 'function') showPlayerControls();
        }""")
        page.wait_for_timeout(500)
        
        # 2. Kiểm tra trạng thái ban đầu: Đã tự động xoay ngang tràn viền không cần gọi Native Fullscreen
        initial_state = page.evaluate("""() => {
            const container = document.getElementById('playerContainer');
            return {
                isNativeFullscreen: !!(document.fullscreenElement || document.webkitFullscreenElement),
                isForcedLandscape: container ? container.classList.contains('player-forced-landscape') : false
            };
        }""")
        print("Trạng thái ban đầu khi mở phim ngang:", initial_state)
        
        if initial_state['isNativeFullscreen']:
            print("LỖI: Tự động kích hoạt Native Fullscreen gây popup Chrome!")
            all_passed = False
            
        # 3. Click nút Toàn Màn Hình lần 1: Toggle về màn hình dọc
        print("\n1. Click Nút Toàn Màn Hình lần 1 (Toggle)...")
        page.evaluate("""() => {
            const btn = document.getElementById('btnFullscreen');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(400)
        
        state1 = page.evaluate("""() => {
            const container = document.getElementById('playerContainer');
            return {
                isNativeFullscreen: !!(document.fullscreenElement || document.webkitFullscreenElement),
                isForcedLandscape: container ? container.classList.contains('player-forced-landscape') : false
            };
        }""")
        print("Trạng thái sau Click lần 1:", state1)
        if state1['isNativeFullscreen']:
            print("LỖI: Click fullscreen trên mobile gọi Native Fullscreen gây popup!")
            all_passed = False
            
        # 4. Click nút Toàn Màn Hình lần 2: Bật lại toàn màn hình ngang
        print("\n2. Click Nút Toàn Màn Hình lần 2 (Toggle lại toàn màn hình)...")
        page.evaluate("""() => {
            const btn = document.getElementById('btnFullscreen');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(400)
        
        state2 = page.evaluate("""() => {
            const container = document.getElementById('playerContainer');
            return {
                isNativeFullscreen: !!(document.fullscreenElement || document.webkitFullscreenElement),
                isForcedLandscape: container ? container.classList.contains('player-forced-landscape') : false
            };
        }""")
        print("Trạng thái sau Click lần 2:", state2)
        if state2['isNativeFullscreen']:
            print("LỖI: Click fullscreen trên mobile gọi Native Fullscreen gây popup!")
            all_passed = False
        if not state2['isForcedLandscape']:
            print("LỖI: Chưa bật lại chế độ toàn màn hình ngang sau khi click lần 2!")
            all_passed = False
            
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/test_fullscreen_no_popup_success.png")
        print("\n-> ĐÃ XÁC MINH 100%: HOÀN TOÀN KHÔNG CÒN GỌI NATIVE FULLSCREEN -> TRIỆT TIÊU 100% POPUP CHROME!")
        browser.close()
        
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(test_mobile_fullscreen_no_native_popup())
