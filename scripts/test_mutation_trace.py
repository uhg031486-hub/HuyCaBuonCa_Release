import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

server_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8092", "--directory", "HuyCa_Web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

        page.goto("http://localhost:8092/index.html", wait_until="networkidle")
        time.sleep(1)

        # Mở phim
        page.locator('.movie-card').first.click()
        time.sleep(1)
        page.click('#btnPlayFirst')
        time.sleep(2)

        # Inject mutation observer theo dõi class của #playerOverlay
        page.evaluate("""() => {
            const overlay = document.getElementById('playerOverlay');
            if (overlay) {
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach(m => {
                        if (m.attributeName === 'class') {
                            console.log('MUTATION class changed to:', overlay.className, 'at', performance.now());
                            console.trace('Stack trace of class change:');
                        }
                    });
                });
                observer.observe(overlay, { attributes: true });
                console.log('Observer attached to #playerOverlay, current class:', overlay.className);
            }

            const pArea = document.getElementById('playerMainArea');
            if (pArea) {
                pArea.addEventListener('click', (e) => {
                    console.log('--- CLICK on playerMainArea at', performance.now(), 'target:', e.target.tagName, e.target.id);
                });
            }
        }""")

        print("Đợi 5.5s...")
        time.sleep(5.5)

        print("\n--- THỰC HIỆN TAP (195, 400) ---")
        page.touchscreen.tap(195, 400)
        time.sleep(2)

        browser.close()
finally:
    server_proc.terminate()
