import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
LIVE_URL = "https://huyca.pages.dev/cinematic/"

print("Đang kiểm thử URL Live Cloudflare Pages:", LIVE_URL)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # Desktop Full HD
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    page.goto(LIVE_URL, wait_until="networkidle")
    time.sleep(3)

    live_desktop_path = os.path.join(ARTIFACT_DIR, "live_cinematic_desktop_1920.png")
    page.screenshot(path=live_desktop_path)
    print("-> Đã chụp Live Desktop:", live_desktop_path)

    # Click play to test Live Player
    play_btn = page.locator("button:has-text('XEM NGAY')").first
    if play_btn.is_visible():
        play_btn.click()
        time.sleep(2)
        live_player_path = os.path.join(ARTIFACT_DIR, "live_cinematic_player.png")
        page.screenshot(path=live_player_path)
        print("-> Đã chụp Live Player:", live_player_path)

    context.close()

    # Mobile 375px
    context_m = browser.new_context(
        viewport={"width": 375, "height": 812},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        is_mobile=True,
        has_touch=True
    )
    page_m = context_m.new_page()
    page_m.goto(LIVE_URL, wait_until="networkidle")
    time.sleep(3)

    live_mobile_path = os.path.join(ARTIFACT_DIR, "live_cinematic_mobile_375.png")
    page_m.screenshot(path=live_mobile_path)
    print("-> Đã chụp Live Mobile:", live_mobile_path)

    context_m.close()
    browser.close()

print("Hoàn tất kiểm thử Live Cloudflare Pages!")
