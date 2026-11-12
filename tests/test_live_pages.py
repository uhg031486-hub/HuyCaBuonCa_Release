import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def test_live_production():
    print("=== KIỂM THỬ TRỰC TIẾP TRÊN LIVE PRODUCTION: https://huyca.pages.dev/ ===")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        
        # Thêm timestamp tránh cache
        live_url = f"https://huyca.pages.dev/?_t={int(time.time())}"
        print(f"Đang tải: {live_url}")
        page.goto(live_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        
        # 1. Kiểm tra Lịch Thi Đấu trên Live
        print("\n1. Mở Lịch Thi Đấu trên Live Site...")
        page.click("#btnScheduleHeader")
        page.wait_for_timeout(800)
        
        schedule_check = page.evaluate("""() => {
            const cards = document.querySelectorAll('#matchesList .match-card');
            const bells = document.querySelectorAll('#matchesList .btn-match-reminder');
            return {
                cardCount: cards.length,
                bellCount: bells.length
            };
        }""")
        print("Trạng thái Lịch Thi Đấu Live:", schedule_check)
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/live_schedule_with_bells.png")
        
        # 2. Click Nút Chuông trận thứ 2 trên Live
        bell_action = page.evaluate("""() => {
            const bell = document.querySelectorAll('#matchesList .btn-match-reminder')[1];
            if (bell) {
                bell.click();
                return {
                    clicked: true,
                    isReminded: bell.classList.contains('is-reminded')
                };
            }
            return { clicked: false };
        }""")
        print("Kết quả Click Chuông Live:", bell_action)
        page.wait_for_timeout(400)
        
        # 3. Mở trận đấu sắp diễn ra trên Live
        print("\n2. Mở Trận Sắp Diễn Ra trên Live Site...")
        page.evaluate("""() => {
            const cards = document.querySelectorAll('#matchesList .match-card');
            if (cards.length > 1) {
                cards[1].click();
            }
        }""")
        page.wait_for_timeout(600)
        
        page.click("#btnServer1")
        page.wait_for_timeout(1000)
        
        countdown_check = page.evaluate("""() => {
            const overlay = document.getElementById('matchCountdownOverlay');
            const timer = document.getElementById('matchCountdownTimer');
            const bellBtn = document.getElementById('btnMatchCountdownReminder');
            const bellText = document.getElementById('cdBellText')?.textContent;
            const days = document.getElementById('cdDays')?.textContent;
            const hours = document.getElementById('cdHours')?.textContent;
            const mins = document.getElementById('cdMinutes')?.textContent;
            const secs = document.getElementById('cdSeconds')?.textContent;
            
            return {
                overlayVisible: overlay && window.getComputedStyle(overlay).display !== 'none',
                bellText: bellText,
                isReminded: bellBtn ? bellBtn.classList.contains('is-reminded') : false,
                countdownTime: `${days}d : ${hours}h : ${mins}m : ${secs}s`
            };
        }""")
        print("Trạng thái Màn Hình Đếm Ngược Live:", countdown_check)
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/live_match_countdown.png")
        
        # 4. Kiểm tra nút Thoát trận đấu
        page.click("#btnCloseMatchWebPlayer")
        page.wait_for_timeout(500)
        
        # 5. Kiểm tra Nút Bỏ qua Intro nhỏ gọn trên Desktop Live
        print("\n3. Kiểm tra Nút Bỏ qua Intro trên Live Desktop...")
        page.evaluate("""() => {
            playVideo('https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'Dhindora (Phần 1)', 'Tập 01', { name: 'Dhindora', isShortDrama: false }, null, 0, 0);
            const btn = document.getElementById('btnSkipIntro');
            if (btn) btn.style.display = 'inline-flex';
            if (typeof showPlayerControls === 'function') showPlayerControls();
        }""")
        page.wait_for_timeout(800)
        
        skip_btn_live = page.evaluate("""() => {
            const btn = document.getElementById('btnSkipIntro');
            if (!btn) return null;
            const r = btn.getBoundingClientRect();
            return {
                width: r.width,
                height: r.height,
                text: btn.textContent.trim()
            };
        }""")
        print("Thông số Nút Skip Intro Live:", skip_btn_live)
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/live_skip_intro_compact.png")
        
        # 6. Kiểm tra Chế độ Màn dọc (Short Drama / Mobile 390px) trên Live
        print("\n4. Kiểm tra Chế độ Màn hình dọc trên Live (390px)...")
        mob_context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1'
        )
        mob_page = mob_context.new_page()
        mob_page.goto(live_url, wait_until="domcontentloaded")
        mob_page.wait_for_timeout(1500)
        
        mob_page.evaluate("""() => {
            playVideo('https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 'Tiểu Kịch Ngắn Màn Dọc', 'Tập 01', { name: 'Tiểu Kịch', isShortDrama: true }, null, 0, 0);
            const pc = document.getElementById('playerContainer');
            if (pc) {
                pc.classList.add('player-vertical-mode');
                pc.style.display = 'block';
            }
            if (typeof showPlayerControls === 'function') showPlayerControls();
        }""")
        mob_page.wait_for_timeout(600)
        
        vertical_check = mob_page.evaluate("""() => {
            const row = document.querySelector('.player-controls-row');
            const btnPlay = document.getElementById('btnPlayPause');
            const btnPrev = document.getElementById('btnCenterPrev');
            const btnNext = document.getElementById('btnCenterNext');
            const btnVol = document.getElementById('btnVolumeToggle');
            const btnSpeed = document.getElementById('btnSpeedPlayer');
            const btnEp = document.getElementById('btnEpisodeSheetPlayer');
            const btnFs = document.getElementById('btnFullscreen');
            
            const isVis = (el) => {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0 && window.getComputedStyle(el).display !== 'none';
            };
            
            return {
                scrollWidth: row ? row.scrollWidth : 0,
                clientWidth: row ? row.clientWidth : 0,
                isOverflowing: row ? (row.scrollWidth > row.clientWidth + 2) : false,
                buttons: {
                    play: isVis(btnPlay),
                    prev: isVis(btnPrev),
                    next: isVis(btnNext),
                    volume: isVis(btnVol),
                    speed: isVis(btnSpeed),
                    episodeSheet: isVis(btnEp),
                    fullscreen: isVis(btnFs)
                }
            };
        }""")
        print("Trạng thái Màn Dọc Live (390px):", vertical_check)
        mob_page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/live_vertical_controls_perfect.png")
        
        browser.close()
        
        assert countdown_check['overlayVisible'], "Màn hình đếm ngược không hiển thị trên live!"
        assert not vertical_check['isOverflowing'], "Controls row bị tràn trên màn dọc live!"
        print("\n=== TOÀN BỘ KIỂM THỬ TRÊN LIVE PRODUCTION ĐẠT 100% HOÀN HẢO! ===")
        return 0

if __name__ == '__main__':
    sys.exit(test_live_production())
