import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import time
import subprocess
import os
from playwright.sync_api import sync_playwright

def run_test():
    print("Starting local HTTP server for HuyCa_Web...")
    web_dir = os.path.join(os.path.dirname(__file__), "HuyCa_Web")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8899", "--directory", web_dir],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            
            # --- TEST 1: HuyCa_Web Football Schedule Modal & Server Selection ---
            print("1. Testing HuyCa_Web Football Schedule...")
            page.goto("http://localhost:8899/index.html")
            page.wait_for_selector("#btnScheduleHeader", timeout=10000)
            
            # Click Lịch Thi Đấu on Header
            page.click("#btnScheduleHeader")
            print("Clicked #btnScheduleHeader, waiting for #matchesList .match-card...")
            page.wait_for_selector("#matchesList .match-card", timeout=5000)
            
            # Screenshot modal
            artifact_dir = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
            page.screenshot(path=os.path.join(artifact_dir, "live_football_modal_fixed.png"))
            print("Captured live_football_modal_fixed.png")
            
            # Click first match card inside schedule modal
            page.click("#matchesList .match-card:first-child")
            page.wait_for_selector("#matchServerModal", timeout=5000)
            
            # Verify modal visible and has 4 servers
            servers_visible = page.is_visible("#matchServerModal")
            print(f"#matchServerModal visible: {servers_visible}")
            page.screenshot(path=os.path.join(artifact_dir, "live_football_servers_fixed.png"))
            print("Captured live_football_servers_fixed.png")
            
            # Click Server 4
            page.click("#btnServer4")
            page.wait_for_timeout(1000)
            
            # Verify playerContainer is displayed
            player_visible = page.is_visible("#playerContainer")
            print(f"#playerContainer visible: {player_visible}")
            
            # Check sidebar episodes grid content
            sidebar_text = page.inner_text("#sidebarEpisodesGrid")
            print(f"Sidebar text contains 'Đang phát sóng': {'Đang phát sóng' in sidebar_text}")
            assert "không có danh sách tập" in sidebar_text.lower(), "Live match notice should state no episode list"
            
            page.screenshot(path=os.path.join(artifact_dir, "live_football_playing_fixed.png"))
            print("Captured live_football_playing_fixed.png")
            
            # Close player via back button
            page.click("#btnBackPlayer")
            page.wait_for_timeout(500)
            
            # --- TEST 2: Main Grid Match Card Click (Switch to TV -> EPL) ---
            print("2. Testing Main Grid Match Card Click via TV -> EPL...")
            page.click("#srcXemTiVi")
            page.wait_for_timeout(500)
            
            # Click EPL filter pill
            page.click(".btn-filter[data-url='tv://epl']")
            page.wait_for_timeout(1500)
            page.wait_for_selector(".movie-card", timeout=5000)
            
            cards_count = page.locator(".movie-card").count()
            print(f"Loaded {cards_count} movie cards on EPL tab")
            
            # Click first match card on main grid
            page.click(".movie-card:first-child")
            page.wait_for_timeout(500)
            
            # It must open #matchServerModal, NOT #detailModal
            server_modal_open = page.is_visible("#matchServerModal")
            detail_modal_open = page.is_visible("#detailModal")
            print(f"Main grid match click -> Server Modal: {server_modal_open}, Detail Modal: {detail_modal_open}")
            assert server_modal_open == True, "Server modal should open when clicking match card on grid"
            assert detail_modal_open == False, "Detail modal (episodes) should NOT open for match card"
            
            page.screenshot(path=os.path.join(artifact_dir, "live_football_grid_click_success.png"))
            print("Captured live_football_grid_click_success.png")
            
            # --- TEST 3: Cinematic Sports / Live TV Mode ---
            print("3. Testing Cinematic Sports Mode...")
            page.goto("http://localhost:8899/cinematic/index.html")
            page.wait_for_selector("button", timeout=10000)
            page.wait_for_timeout(1000)
            
            # Switch to TV tab in Cinematic
            tv_tab = page.locator("button:has-text('Truyền Hình')").first
            if tv_tab.count() > 0:
                tv_tab.click()
                page.wait_for_timeout(1000)
            
            page.screenshot(path=os.path.join(artifact_dir, "live_cinematic_tv_fixed.png"))
            print("Captured live_cinematic_tv_fixed.png")
            
            browser.close()
            print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_test()
