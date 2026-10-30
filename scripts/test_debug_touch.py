import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

server_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8089", "--directory", "HuyCa_Web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)

print("=== DEBUG CHI TIẾT SỰ KIỆN CLICK / TOUCH TRÊN MOBILE ===")

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

        page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))

        page.goto("http://localhost:8089/index.html", wait_until="networkidle")
        time.sleep(1)

        # Inject debugger listeners vào window
        page.evaluate("""() => {
            window.addEventListener('touchstart', (e) => console.log('window touchstart target:', e.target.tagName, e.target.id, e.target.className), true);
            window.addEventListener('touchend', (e) => console.log('window touchend target:', e.target.tagName, e.target.id, e.target.className), true);
            window.addEventListener('click', (e) => console.log('window click target:', e.target.tagName, e.target.id, e.target.className), true);
            
            const pArea = document.getElementById('playerMainArea');
            if (pArea) {
                pArea.addEventListener('click', (e) => {
                    console.log('playerMainArea CLICK fired! target:', e.target.tagName, e.target.id, e.target.className);
                });
                pArea.addEventListener('touchstart', (e) => {
                    console.log('playerMainArea TOUCHSTART fired! target:', e.target.tagName, e.target.id);
                });
            }
        }""")

        # Mở phim
        page.locator('.movie-card').first.click()
        time.sleep(1)
        page.click('#btnPlayFirst')
        time.sleep(2)

        # Chờ 5.5s để controls ẩn
        print("Đợi 5.5s...")
        time.sleep(5.5)

        print("\n--- THỰC HIỆN TAP TẠI TỌA ĐỘ (195, 422) ---")
        page.touchscreen.tap(195, 422)
        time.sleep(1)

        print("\n--- THỰC HIỆN EVALUATE document.elementFromPoint(195, 422) ---")
        el_info = page.evaluate("""() => {
            const el = document.elementFromPoint(195, 422);
            return el ? { tag: el.tagName, id: el.id, className: el.className, zIndex: window.getComputedStyle(el).zIndex } : null;
        }""")
        print("Element at (195, 422):", el_info)

        print("\n--- THỰC HIỆN CLICK TRỰC TIẾP QUA DISPATCH MOUSE/TOUCH ---")
        page.evaluate("""() => {
            const el = document.elementFromPoint(195, 422);
            if (el) {
                console.log('Dispatching click to elementFromPoint:', el.tagName, el.id);
                el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
            }
        }""")
        time.sleep(1)

        overlay_class = page.locator('#playerOverlay').get_attribute("class")
        print("Overlay class after dispatch click:", overlay_class)

        browser.close()
finally:
    server_proc.terminate()
