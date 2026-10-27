import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import time
import subprocess
import os
from playwright.sync_api import sync_playwright

def run_test():
    print("Starting local server...")
    web_dir = os.path.join(os.path.dirname(__file__), "HuyCa_Web")
    proc = subprocess.Popen([sys.executable, "-m", "http.server", "8899", "--directory", web_dir],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto("http://localhost:8899/index.html")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)
            
            print("Invoking window.playVideo with movie...")
            page.evaluate("""() => {
                const dummyMovie = {
                    name: 'Sự Trỗi Dậy Của Nữ Hoàng Trắng(Phiên bản lồng tiếng)',
                    originName: 'Rise of White Queen',
                    year: '2026'
                };
                window.playVideo(
                    'https://vtvgolivepre-vtv02.vtvdigital.vn/hls/vtv/live/vtv5__vtv1080p-h264/index.m3u8',
                    dummyMovie.name,
                    'Tập 1',
                    dummyMovie,
                    null,
                    0,
                    0,
                    false
                );
                // Collapse sidebar like user view
                const sb = document.getElementById('playerSidebar');
                if (sb) sb.classList.add('collapsed');
                // Ensure overlay visible
                const ov = document.getElementById('playerOverlay');
                if (ov) ov.classList.remove('controls-hidden');
            }""")
            
            page.wait_for_selector("#playerContainer", state="visible", timeout=5000)
            page.wait_for_timeout(1200)
            
            artifact_dir = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
            
            # Screenshot 1: Cinema Pro Fullscreen with Dock
            screen_path = os.path.join(artifact_dir, "live_cinema_pro_fullscreen.png")
            page.screenshot(path=screen_path)
            print(f"Captured {screen_path}")
            
            # Check center: verify NO .btn-center-pill or .btn-center-round exist
            old_pills = page.locator(".btn-center-pill").count()
            old_rounds = page.locator(".btn-center-round").count()
            print(f"Old center pills count: {old_pills}, old center rounds count: {old_rounds}")
            assert old_pills == 0, "Old center pills should be removed!"
            assert old_rounds == 0, "Old center rounds should be removed!"
            
            # Check bottom dock buttons exist
            play_btn = page.locator("#btnPlayPause").count()
            rewind_btn = page.locator("#btnCenterRewind").count()
            forward_btn = page.locator("#btnCenterForward").count()
            vol_slider = page.locator("#volumeSlider").count()
            print(f"Cinema dock controls -> play: {play_btn}, -10s: {rewind_btn}, +10s: {forward_btn}, vol: {vol_slider}")
            assert play_btn > 0, "Play button must exist in bottom dock"
            assert rewind_btn > 0, "Rewind 10s must exist in bottom dock"
            assert forward_btn > 0, "Forward 10s must exist in bottom dock"
            
            # Click Pause to test pause SVG toggle
            page.click("#btnPlayPause")
            page.wait_for_timeout(500)
            screen_paused = os.path.join(artifact_dir, "live_cinema_pro_paused.png")
            page.screenshot(path=screen_paused)
            print(f"Captured {screen_paused}")
            
            browser.close()
            print("ALL CINEMA PRO VERIFICATION TESTS PASSED SUCCESSFULLY!")
    finally:
        proc.terminate()

if __name__ == "__main__":
    run_test()
