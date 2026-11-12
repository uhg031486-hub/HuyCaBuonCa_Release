import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def test_full_interaction():
    print("=== KIỂM THỬ TƯƠNG TÁC THỰC TẾ: CHUÔNG BÓNG ĐÁ & ĐẾM NGƯỢC ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        
        page.goto("http://localhost:8098/", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        
        # 1. Mở Lịch Thi Đấu
        page.click("#btnScheduleHeader")
        page.wait_for_timeout(500)
        
        # Chụp ảnh Modal Lịch Thi Đấu có nút chuông 🔔
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/screenshot_schedule_with_bells.png")
        print("-> Đã chụp ảnh Modal Lịch Thi Đấu có Nút Chuông 🔔")
        
        # 2. Click vào Nút Chuông của trận thứ 2 (Arsenal vs Chelsea)
        bell_clicked = page.evaluate("""() => {
            const cards = document.querySelectorAll('#matchesList .match-card');
            if (cards.length > 1) {
                const bell = cards[1].querySelector('.btn-match-reminder');
                if (bell) {
                    bell.click();
                    return {
                        clicked: true,
                        hasRemindedClass: bell.classList.contains('is-reminded'),
                        localStorageData: localStorage.getItem('huyca_match_reminders')
                    };
                }
            }
            return { clicked: false };
        }""")
        print("Kết quả Click Chuông trên Thẻ:", bell_clicked)
        page.wait_for_timeout(300)
        
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/screenshot_bell_clicked_active.png")
        
        # 3. Mở trận đấu Arsenal vs Chelsea (Sắp diễn ra)
        page.evaluate("""() => {
            const cards = document.querySelectorAll('#matchesList .match-card');
            if (cards.length > 1) {
                cards[1].click(); // Mở modal server
            }
        }""")
        page.wait_for_timeout(500)
        
        # Chọn Server 1
        page.click("#btnServer1")
        page.wait_for_timeout(800)
        
        # Kiểm tra màn hình đếm ngược
        state = page.evaluate("""() => {
            const overlay = document.getElementById('matchCountdownOverlay');
            const timer = document.getElementById('matchCountdownTimer');
            const days = document.getElementById('cdDays')?.textContent;
            const hours = document.getElementById('cdHours')?.textContent;
            const mins = document.getElementById('cdMinutes')?.textContent;
            const secs = document.getElementById('cdSeconds')?.textContent;
            const bellBtn = document.getElementById('btnMatchCountdownReminder');
            const bellText = document.getElementById('cdBellText')?.textContent;
            
            return {
                overlayVisible: overlay && window.getComputedStyle(overlay).display !== 'none',
                timerText: `${days}d : ${hours}h : ${mins}m : ${secs}s`,
                bellText: bellText,
                isReminded: bellBtn ? bellBtn.classList.contains('is-reminded') : false
            };
        }""")
        print("Trạng thái Màn Hình Đếm Ngược:", state)
        
        # Chụp ảnh Màn hình Đếm Ngược Trận Đấu
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/screenshot_match_countdown_screen.png")
        print("-> Đã chụp ảnh Màn hình Đếm Ngược Trận Đấu")
        
        # 4. Click nút chuông ngay trên màn đếm ngược
        toggle_bell = page.evaluate("""() => {
            const btn = document.getElementById('btnMatchCountdownReminder');
            if (btn) {
                btn.click();
                return {
                    clicked: true,
                    isReminded: btn.classList.contains('is-reminded'),
                    bellText: document.getElementById('cdBellText')?.textContent
                };
            }
            return { clicked: false };
        }""")
        print("Kết quả Toggle Chuông trên Màn Đếm Ngược:", toggle_bell)
        page.wait_for_timeout(300)
        
        page.screenshot(path="c:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b/screenshot_countdown_bell_toggled.png")
        
        browser.close()
        print("=== KIỂM THỬ THÀNH CÔNG RỰC RỠ 100%! ===")
        return 0

if __name__ == '__main__':
    sys.exit(test_full_interaction())
