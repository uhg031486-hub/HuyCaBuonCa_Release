import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import time
import subprocess
import os
from playwright.sync_api import sync_playwright

def run_test():
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
            
            page.wait_for_timeout(1200)
            
            artifact_dir = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
            screen_path = os.path.join(artifact_dir, "live_transparent_player_fullscreen_look.png")
            page.screenshot(path=screen_path)
            print(f"Captured {screen_path}")
            browser.close()
    finally:
        proc.terminate()

if __name__ == "__main__":
    run_test()
