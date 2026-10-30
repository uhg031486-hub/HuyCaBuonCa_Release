import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

server_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8090", "--directory", "HuyCa_Web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

        page.goto("http://localhost:8090/index.html", wait_until="networkidle")
        time.sleep(1)

        # Hook vào togglePlayerControls và resetOverlayTimer
        page.evaluate("""() => {
            const origToggle = window.togglePlayerControls;
            window.togglePlayerControls = function() {
                const overlay = document.getElementById('playerOverlay');
                console.log('>>> togglePlayerControls CALLED! Current class:', overlay ? overlay.className : 'null', 'isTouchLocked:', window.isTouchLocked);
                const ret = origToggle.apply(this, arguments);
                console.log('>>> togglePlayerControls FINISHED! New class:', overlay ? overlay.className : 'null');
                return ret;
            };

            const origReset = window.resetOverlayTimer;
            window.resetOverlayTimer = function() {
                console.log('>>> resetOverlayTimer CALLED!');
                return origReset.apply(this, arguments);
            };
        }""")

        # Mở phim
        page.locator('.movie-card').first.click()
        time.sleep(1)
        page.click('#btnPlayFirst')
        time.sleep(2)

        print("Đợi 5.5s để overlay tự ẩn...")
        time.sleep(5.5)

        print("\n--- BẮT ĐẦU page.touchscreen.tap(195, 400) ---")
        page.touchscreen.tap(195, 400)
        time.sleep(1)

        print("\n--- BẮT ĐẦU page.locator('#playerMainArea').tap() ---")
        page.locator('#playerMainArea').tap()
        time.sleep(1)

        browser.close()
finally:
    server_proc.terminate()
