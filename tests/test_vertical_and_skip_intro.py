import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def run_tests():
    print("=== BẮT ĐẦU KIỂM THỬ TDD: THANH ĐIỀU HƯỚNG MÀN DỌC & NÚT SKIP INTRO ===")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # -------------------------------------------------------------
        # TEST 1: KIỂM THỬ TRÊN MÀN HÌNH DỌC (MOBILE VIEWPORT 390 x 844)
        # -------------------------------------------------------------
        print("\n--- TEST 1: Mobile Viewport 390x844 (Chế độ màn dọc) ---")
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1'
        )
        page = context.new_page()
        page.goto("http://localhost:8098/", wait_until="domcontentloaded")
        
        # Mở phim bằng playVideo
        page.evaluate("""() => {
            if (typeof playVideo === 'function') {
                playVideo('https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'Kiểm Thử Phim Ngắn Màn Dọc', 'Tập 01', { name: 'Phim Ngắn Dọc', isShortDrama: true }, null, 0, 0);
                const pc = document.getElementById('playerContainer');
                if (pc) {
                    pc.classList.add('player-vertical-mode');
                    pc.style.display = 'block';
                }
            }
        }""")
        page.wait_for_timeout(1000)
        
        # Đảm bảo controls hiển thị
        page.evaluate("() => { if (typeof showPlayerControls === 'function') showPlayerControls(); }")
        page.wait_for_timeout(300)
        
        # Đo đạc controls-row trên màn hình dọc 390px
        row_metrics = page.evaluate("""() => {
            const row = document.querySelector('.player-controls-row');
            const overlay = document.querySelector('.player-overlay');
            const bottomBar = document.querySelector('.player-bottom-bar');
            
            const btnPlay = document.getElementById('btnPlayPause');
            const btnPrev = document.getElementById('btnCenterPrev');
            const btnNext = document.getElementById('btnCenterNext');
            const btnVol = document.getElementById('btnVolumeToggle');
            const timeDisplay = document.querySelector('.player-time-display');
            const btnSpeed = document.getElementById('btnSpeedPlayer');
            const btnEp = document.getElementById('btnEpisodeSheetPlayer');
            const btnAspect = document.getElementById('btnAspectPlayer');
            const btnFs = document.getElementById('btnFullscreen');
            
            const isVisible = (el) => {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0 && window.getComputedStyle(el).display !== 'none';
            };
            
            return {
                rowClientWidth: row ? row.clientWidth : 0,
                rowScrollWidth: row ? row.scrollWidth : 0,
                overlayPaddingLeft: overlay ? window.getComputedStyle(overlay).paddingLeft : '',
                overlayPaddingRight: overlay ? window.getComputedStyle(overlay).paddingRight : '',
                bottomBarPaddingLeft: bottomBar ? window.getComputedStyle(bottomBar).paddingLeft : '',
                bottomBarPaddingRight: bottomBar ? window.getComputedStyle(bottomBar).paddingRight : '',
                buttonsVisible: {
                    play: isVisible(btnPlay),
                    prev: isVisible(btnPrev),
                    next: isVisible(btnNext),
                    volume: isVisible(btnVol),
                    time: isVisible(timeDisplay),
                    speed: isVisible(btnSpeed),
                    episodeSheet: isVisible(btnEp),
                    aspect: isVisible(btnAspect),
                    fullscreen: isVisible(btnFs)
                }
            };
        }""")
        
        print("Thông số Controls Row trên Mobile Dọc (390px):", row_metrics)
        
        # Kiểm tra tràn chiều ngang:
        is_overflowing = row_metrics['rowScrollWidth'] > (row_metrics['rowClientWidth'] + 2)
        print(f"Kiểm tra tràn: scrollWidth={row_metrics['rowScrollWidth']}, clientWidth={row_metrics['rowClientWidth']}, Tràn={is_overflowing}")
        
        # Kiểm tra hiển thị đầy đủ các nút cốt lõi:
        btns = row_metrics['buttonsVisible']
        missing = [k for k, v in btns.items() if not v]
        if missing:
            print(f"CẢNH BÁO: Các nút bị ẩn/mất: {missing}")
        else:
            print("100% CÁC NÚT TRỌNG YẾU ĐỀU HIỂN THỊ ĐẦY ĐỦ!")
            
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/test_vertical_controls_390.png")
        
        # -------------------------------------------------------------
        # TEST 2: KIỂM THỬ NÚT BỎ QUA INTRO VỪA PHẢI, NHỎ GỌN TINH TẾ
        # -------------------------------------------------------------
        print("\n--- TEST 2: Kiểm thử Nút Bỏ Qua Intro trên màn hình Desktop ---")
        desktop_context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page_desk = desktop_context.new_page()
        page_desk.goto("http://localhost:8098/", wait_until="domcontentloaded")
        
        page_desk.evaluate("""() => {
            if (typeof playVideo === 'function') {
                playVideo('https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'Dhindora (Phim Dài)', 'Tập 01', { name: 'Dhindora', isShortDrama: false }, null, 0, 0);
                const pc = document.getElementById('playerContainer');
                if (pc) pc.style.display = 'block';
            }
        }""")
        page_desk.wait_for_timeout(1000)
        
        # Kích hoạt hiện nút Bỏ qua Intro
        page_desk.evaluate("""() => {
            const btn = document.getElementById('btnSkipIntro');
            if (btn) btn.style.display = 'inline-flex';
            if (typeof showPlayerControls === 'function') showPlayerControls();
        }""")
        page_desk.wait_for_timeout(300)
        
        btn_metrics = page_desk.evaluate("""() => {
            const btn = document.getElementById('btnSkipIntro');
            const row = document.querySelector('.player-controls-row');
            if (!btn) return null;
            const r = btn.getBoundingClientRect();
            const cs = window.getComputedStyle(btn);
            
            // Kiểm tra nút có nằm trong row không hay nổi ở góc
            const isInsideRow = row && row.contains(btn);
            
            return {
                width: r.width,
                height: r.height,
                fontSize: cs.fontSize,
                padding: cs.padding,
                isInsideRow: isInsideRow,
                position: cs.position,
                bottom: cs.bottom,
                right: cs.right,
                text: btn.textContent.trim()
            };
        }""")
        print("Thông số Nút Bỏ qua Intro:", btn_metrics)
        
        page_desk.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/test_skip_intro_desktop.png")
        
        browser.close()
        
        # Đánh giá PASS / FAIL cho Red Gate
        passed = True
        if is_overflowing:
            print("RED GATE THẤT BẠI: Controls Row vẫn bị tràn trên màn dọc!")
            passed = False
        if missing:
            print(f"RED GATE THẤT BẠI: Có nút bị mất trên màn dọc: {missing}")
            passed = False
        if btn_metrics and btn_metrics['height'] > 36:
            print(f"RED GATE THẤT BẠI: Nút Skip Intro quá to ({btn_metrics['height']}px > 36px)!")
            passed = False
        if btn_metrics and btn_metrics['isInsideRow']:
            print("RED GATE THẤT BẠI: Nút Skip Intro vẫn nằm chình ình trong controls row!")
            passed = False
            
        return 0 if passed else 1

if __name__ == '__main__':
    code = run_tests()
    sys.exit(code)
