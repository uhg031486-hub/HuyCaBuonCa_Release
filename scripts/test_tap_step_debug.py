import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

server_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8096", "--directory", "HuyCa_Web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

        page.goto("http://localhost:8096/index.html", wait_until="domcontentloaded")
        time.sleep(1.5)

        page.locator('.movie-card').first.click()
        time.sleep(1)
        page.click('#btnPlayFirst')
        time.sleep(2)

        # Chủ động ẩn controls
        page.evaluate("() => document.getElementById('playerOverlay').classList.add('controls-hidden')")

        # Thay thế listener trên playerMainArea để debug từng bước
        page.evaluate("""() => {
            const overlay = document.getElementById('playerOverlay');
            const pArea = document.getElementById('playerMainArea');
            const video = document.getElementById('videoPlayer');

            console.log('Video paused:', video.paused);

            pArea.addEventListener('click', (e) => {
                console.log('--- DEBUG CLICK START ---');
                console.log('Target:', e.target.tagName, e.target.id, e.target.className);
                console.log('Current overlay class before toggle:', overlay.className);
                const isHidden = overlay.classList.contains('controls-hidden');
                console.log('isHidden in click listener:', isHidden);
            }, true); // capture phase
        }""")

        print("\n--- GỌI page.touchscreen.tap(195, 400) ---")
        page.touchscreen.tap(195, 400)
        time.sleep(1)

        browser.close()
finally:
    server_proc.terminate()
