import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

server_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8093", "--directory", "HuyCa_Web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

        page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))

        page.goto("http://localhost:8093/index.html", wait_until="domcontentloaded")
        time.sleep(1.5)

        # Mở phim
        page.locator('.movie-card').first.click()
        time.sleep(1)
        page.click('#btnPlayFirst')
        time.sleep(2)

        # Gắn log trực tiếp vào click của playerMainArea
        page.evaluate("""() => {
            const pArea = document.getElementById('playerMainArea');
            const overlay = document.getElementById('playerOverlay');
            pArea.addEventListener('click', (e) => {
                console.log('>>> playerMainArea CLICK event caught! target:', e.target.tagName, e.target.id, 'class:', e.target.className);
                console.log('>>> overlay current class:', overlay.className);
                console.log('>>> isTouchLocked:', window.isTouchLocked);
                console.log('>>> closest button:', !!e.target.closest('button'));
                console.log('>>> closest player-top:', !!e.target.closest('.player-top'));
                console.log('>>> closest player-bottom-bar:', !!e.target.closest('.player-bottom-bar'));
            }, false);
        }""")

        print("Đợi 5.5s...")
        time.sleep(5.5)

        print("\n--- BẮT ĐẦU page.touchscreen.tap(195, 400) ---")
        page.touchscreen.tap(195, 400)
        time.sleep(0.5)

        overlay_class = page.locator('#playerOverlay').get_attribute("class")
        print("Overlay class NGAY SAU TAP:", overlay_class)

        time.sleep(1.5)
        overlay_class_after_1s = page.locator('#playerOverlay').get_attribute("class")
        print("Overlay class SAU 1.5s:", overlay_class_after_1s)

        browser.close()
finally:
    server_proc.terminate()
