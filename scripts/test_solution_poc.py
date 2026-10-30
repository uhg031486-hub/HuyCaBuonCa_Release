import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

server_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8097", "--directory", "HuyCa_Web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()

        page.goto("http://localhost:8097/index.html", wait_until="domcontentloaded")
        time.sleep(1.5)

        page.locator('.movie-card').first.click()
        time.sleep(1)
        page.click('#btnPlayFirst')
        time.sleep(2)

        # Ẩn controls đi
        page.evaluate("() => document.getElementById('playerOverlay').classList.add('controls-hidden')")

        # THỬ NGHIỆM GIẢI PHÁP:
        # Ngăn mousemove kích hoạt resetOverlayTimer trên touch device
        # Và khi chạm màn hình: Toggle hiển thị controls một cách dứt khoát
        page.evaluate("""() => {
            const overlay = document.getElementById('playerOverlay');
            const pArea = document.getElementById('playerMainArea');

            // Giải pháp 1: Lắng nghe pointerup / touchend trực tiếp với cơ chế chống xung đột
            let lastTouchTime = 0;
            window.addEventListener('touchstart', () => { lastTouchTime = Date.now(); }, true);

            // Ghi đè hàm toggle controls thông minh
            window.showControlsOnTouch = () => {
                overlay.classList.remove('controls-hidden');
                overlay.classList.remove('hide');
                console.log('SHOW CONTROLS SUCCESS! Class is now:', overlay.className);
            };

            pArea.addEventListener('touchend', (e) => {
                if (e.target.closest('button, input, .player-top, .player-bottom-bar, .player-sidebar')) return;
                e.preventDefault();
                const isHidden = overlay.classList.contains('controls-hidden');
                if (isHidden) {
                    window.showControlsOnTouch();
                } else {
                    overlay.classList.add('controls-hidden');
                }
            });
        }""")

        overlay = page.locator('#playerOverlay')
        print("Trạng thái overlay trước khi tap:", overlay.get_attribute("class"))

        print("\n--- GỌI page.touchscreen.tap(195, 400) với giải pháp mới ---")
        page.touchscreen.tap(195, 400)
        time.sleep(1)
        print("Trạng thái overlay SAU TAP:", overlay.get_attribute("class"))

        browser.close()
finally:
    server_proc.terminate()
