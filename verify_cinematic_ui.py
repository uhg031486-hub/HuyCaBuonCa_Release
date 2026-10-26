import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
DIST_DIR = r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Cinematic\dist"

print("Khởi chạy HTTP server cho HuyCa_Cinematic dist trên cổng 4173...")
server_process = subprocess.Popen(
    [sys.executable, "-m", "http.server", "4173", "--directory", DIST_DIR],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

try:
    time.sleep(2)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1. Test Desktop 1920x1080 (Chuẩn Full HD Cinematic)
        print("Đang kiểm thử Desktop 1920x1080...")
        context_desktop = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context_desktop.new_page()
        page.goto("http://localhost:4173", wait_until="networkidle")
        time.sleep(2)

        desktop_screenshot_path = os.path.join(ARTIFACT_DIR, "cinematic_desktop_1920.png")
        page.screenshot(path=desktop_screenshot_path, full_page=False)
        print(f"-> Đã lưu ảnh Desktop: {desktop_screenshot_path}")

        # Hover lên thẻ phim đầu tiên để kiểm tra hiệu ứng phóng to & quick play
        first_card = page.locator(".group\\/section .group").first
        if first_card.is_visible():
            first_card.hover()
            time.sleep(1)
            hover_screenshot_path = os.path.join(ARTIFACT_DIR, "cinematic_card_hover.png")
            page.screenshot(path=hover_screenshot_path, full_page=False)
            print(f"-> Đã lưu ảnh Card Hover: {hover_screenshot_path}")

        # Bấm xem chi tiết (Detail Modal)
        print("Đang kiểm tra Detail Modal...")
        first_card.click()
        time.sleep(1)
        modal_screenshot_path = os.path.join(ARTIFACT_DIR, "cinematic_detail_modal.png")
        page.screenshot(path=modal_screenshot_path, full_page=False)
        print(f"-> Đã lưu ảnh Detail Modal: {modal_screenshot_path}")

        # Bấm phát phim để kiểm tra Player
        play_btn = page.locator("text=PHÁT PHIM").first
        if play_btn.is_visible():
            play_btn.click()
            time.sleep(2)
            player_screenshot_path = os.path.join(ARTIFACT_DIR, "cinematic_player_modal.png")
            page.screenshot(path=player_screenshot_path, full_page=False)
            print(f"-> Đã lưu ảnh Player: {player_screenshot_path}")

            # Bấm thu nhỏ (Mini Player / Floating In-App PiP)
            mini_btn = page.locator("button[title*='Thu nhỏ']").first
            if mini_btn.is_visible():
                mini_btn.click()
                time.sleep(1.5)
                pip_screenshot_path = os.path.join(ARTIFACT_DIR, "cinematic_floating_pip.png")
                page.screenshot(path=pip_screenshot_path, full_page=False)
                print(f"-> Đã lưu ảnh In-App Floating PiP: {pip_screenshot_path}")

        context_desktop.close()

        # 2. Test Mobile 375x812 (iPhone X/13)
        print("Đang kiểm thử Mobile 375x812...")
        context_mobile = browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page_m = context_mobile.new_page()
        page_m.goto("http://localhost:4173", wait_until="networkidle")
        time.sleep(2)

        mobile_screenshot_path = os.path.join(ARTIFACT_DIR, "cinematic_mobile_375.png")
        page_m.screenshot(path=mobile_screenshot_path, full_page=False)
        print(f"-> Đã lưu ảnh Mobile: {mobile_screenshot_path}")

        context_mobile.close()

        # 3. Test 4K Ultra HD (3840x2160)
        print("Đang kiểm thử 4K 3840x2160...")
        context_4k = browser.new_context(viewport={"width": 3840, "height": 2160})
        page_4k = context_4k.new_page()
        page_4k.goto("http://localhost:4173", wait_until="networkidle")
        time.sleep(2)

        screenshot_4k_path = os.path.join(ARTIFACT_DIR, "cinematic_4k_ultra.png")
        page_4k.screenshot(path=screenshot_4k_path, full_page=False)
        print(f"-> Đã lưu ảnh 4K: {screenshot_4k_path}")

        context_4k.close()

        browser.close()

    print("Hoàn tất toàn bộ kiểm thử Playwright!")

finally:
    server_process.terminate()
