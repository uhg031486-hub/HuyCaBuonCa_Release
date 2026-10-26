import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
DIST_DIR = r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Cinematic\dist"

server_process = subprocess.Popen(
    [sys.executable, "-m", "http.server", "4174", "--directory", DIST_DIR],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

try:
    time.sleep(2)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.goto("http://localhost:4174", wait_until="networkidle")
        time.sleep(2)

        # Click nút "XEM NGAY" trên Hero Banner trực tiếp
        hero_play = page.locator("button:has-text('XEM NGAY')").first
        if hero_play.is_visible():
            hero_play.click()
            time.sleep(2)
            player_path = os.path.join(ARTIFACT_DIR, "cinematic_player_modal.png")
            page.screenshot(path=player_path)
            print(f"-> Đã chụp Player: {player_path}")

            # Click nút Minimize để chuyển sang Floating Mini Player (In-App PiP)
            mini_btn = page.locator("button[title*='Thu nhỏ']").first
            if mini_btn.is_visible():
                mini_btn.click()
                time.sleep(2)
                pip_path = os.path.join(ARTIFACT_DIR, "cinematic_floating_pip.png")
                page.screenshot(path=pip_path)
                print(f"-> Đã chụp Floating PiP: {pip_path}")

        context.close()
        browser.close()
finally:
    server_process.terminate()
