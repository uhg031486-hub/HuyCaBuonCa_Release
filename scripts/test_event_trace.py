import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

server_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8091", "--directory", "HuyCa_Web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

        page.on("console", lambda msg: print(f"[LOG] {msg.text}"))

        page.goto("http://localhost:8091/index.html", wait_until="networkidle")
        time.sleep(1)

        # Mở phim
        page.locator('.movie-card').first.click()
        time.sleep(1)
        page.click('#btnPlayFirst')
        time.sleep(2)

        # Gắn theo dõi mọi sự kiện trên window trong capture phase
        page.evaluate("""() => {
            const events = ['touchstart', 'touchend', 'touchmove', 'touchcancel', 'pointerdown', 'pointerup', 'mousedown', 'mouseup', 'click'];
            events.forEach(evt => {
                window.addEventListener(evt, (e) => {
                    console.log(`EVENT: ${evt} | target: <${e.target.tagName} id="${e.target.id}" class="${e.target.className}"> | defaultPrevented: ${e.defaultPrevented}`);
                }, true);
            });
        }""")

        time.sleep(5.5)
        print("\n--- GOI page.touchscreen.tap(195, 400) ---")
        page.touchscreen.tap(195, 400)
        time.sleep(1)

        browser.close()
finally:
    server_proc.terminate()
