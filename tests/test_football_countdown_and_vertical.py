import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def run_tests():
    print("=== BẮT ĐẦU TEST TDD: ĐẾM NGƯỢC TRẬN ĐẤU, CHUÔNG THÔNG BÁO & MÀN DỌC ===")
    all_passed = True
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        
        page.goto("http://localhost:8098/", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        
        # -------------------------------------------------------------
        # TEST 1: KIỂM TRA LỊCH THI ĐẤU CÓ NÚT CHUÔNG THÔNG BÁO 🔔
        # -------------------------------------------------------------
        print("\n--- TEST 1: Kiểm tra Nút Chuông 🔔 trong Lịch Thi Đấu ---")
        page.click("#btnScheduleHeader")
        page.wait_for_timeout(500)
        
        cards_info = page.evaluate("""() => {
            const cards = document.querySelectorAll('#matchesList .match-card');
            const results = [];
            cards.forEach(c => {
                const bell = c.querySelector('.btn-match-reminder, .match-bell-btn');
                const teams = c.querySelector('.match-teams')?.textContent || '';
                results.push({
                    hasBell: !!bell,
                    teams: teams
                });
            });
            return {
                totalCards: cards.length,
                results: results
            };
        }""")
        print("Kết quả Lịch Thi Đấu:", cards_info)
        
        if cards_info['totalCards'] == 0:
            print("LỖI: Không tìm thấy thẻ trận đấu nào trong Lịch Thi Đấu!")
            all_passed = False
        else:
            has_bells = any(r['hasBell'] for r in cards_info['results'])
            if not has_bells:
                print("RED GATE XÁC NHẬN: Chưa có nút chuông 🔔 trên các thẻ trận đấu!")
                all_passed = False
            else:
                print("Đã có nút chuông thông báo trên thẻ trận đấu!")
        
        # Đóng modal lịch
        page.click("#btnCloseSchedule")
        page.wait_for_timeout(300)
        
        # -------------------------------------------------------------
        # TEST 2: KIỂM TRA MỞ TRẬN SẮP DIỄN RA -> HIỆN ĐẾM NGƯỢC & CHUÔNG
        # -------------------------------------------------------------
        print("\n--- TEST 2: Mở Trận Sắp Diễn Ra -> Giao diện Đếm Ngược ---")
        countdown_result = page.evaluate("""() => {
            // Giả lập mở trận Chelsea vs Manchester United sắp diễn ra vào ngày mai
            const tomorrowKickoff = Date.now() + (24 * 3600 * 1000);
            const futureMatch = {
                id: 'test_che_mun',
                tournament: '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh',
                teamA: 'Chelsea',
                teamB: 'Manchester United',
                teamALogo: 'https://resources.premierleague.com/premierleague/badges/70/t8.png',
                teamBLogo: 'https://resources.premierleague.com/premierleague/badges/70/t1.png',
                time: 'Ngày Mai • 20:30',
                timeStr: '20:30 • Ngày Mai',
                kickoffTime: tomorrowKickoff,
                isLive: false,
                isFinished: false
            };
            
            if (typeof playMatchViaServer === 'function') {
                playMatchViaServer(1, futureMatch);
            }
            
            const overlay = document.getElementById('matchCountdownOverlay');
            const iframe = document.getElementById('matchIframe');
            const bellBtn = document.getElementById('btnMatchCountdownReminder');
            const timerEl = document.getElementById('matchCountdownTimer');
            
            return {
                overlayExists: !!overlay,
                overlayVisible: overlay ? (window.getComputedStyle(overlay).display !== 'none') : false,
                iframeSrc: iframe ? iframe.src : '',
                hasBellBtn: !!bellBtn,
                hasTimer: !!timerEl
            };
        }""")
        print("Kết quả Màn hình Đếm Ngược:", countdown_result)
        
        if not countdown_result['overlayVisible']:
            print("RED GATE XÁC NHẬN: Màn hình Đếm Ngược chưa hiển thị khi mở trận sắp có!")
            all_passed = False
        else:
            print("Màn hình Đếm Ngược đã hiển thị hoàn hảo!")
            
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/test_football_countdown.png")
        
        browser.close()
        
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(run_tests())
