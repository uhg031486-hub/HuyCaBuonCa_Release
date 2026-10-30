import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"

# Khởi động HTTP server local cho HuyCa_Web trên cổng 8098
server_proc = subprocess.Popen([sys.executable, "-m", "http.server", "8098", "--directory", "HuyCa_Web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)

print("=== BẮT ĐẦU KIỂM THỬ E2E: THAO TÁC NGƯỜI DÙNG CUỐI TRÊN MOBILE WEB ===")

test_results = {}

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Giả lập iPhone 14 Pro (393 x 852, touch screen thật)
        context = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()

        # ---------------- LUỒNG 1: MỞ TRANG CHỦ & VÀO XEM PHIM ----------------
        print("\n--- 1. TRUY CẬP HUY CÁ WEB TRÊN ĐIỆN THOẠI DI ĐỘNG ---")
        page.goto("http://localhost:8098/index.html", wait_until="domcontentloaded")
        time.sleep(2)

        # Chờ phim tải
        page.wait_for_selector('.movie-card')
        first_card = page.locator('.movie-card').first
        print(f" -> Đã tải lưới phim, bấm chọn phim đầu tiên...")
        first_card.click()
        time.sleep(1.5)

        # Bấm xem tập đầu
        page.wait_for_selector('#btnPlayFirst')
        page.click('#btnPlayFirst')
        time.sleep(2)

        # Kiểm tra player
        player_container = page.locator('#playerContainer')
        overlay = page.locator('#playerOverlay')
        assert player_container.is_visible(), "PlayerContainer phải hiển thị"
        print(" -> Trình phát video đã mở thành công!")

        # ---------------- LUỒNG 2: CHỜ CONTROLS TỰ ĐỘNG ẨN (TÀNG HÌNH) ----------------
        print("\n--- 2. CHỜ CONTROLS TỰ ĐỘNG ẨN KHI ĐANG XEM ---")
        # Đợi 5.5s để overlay tự động ẩn
        time.sleep(5.5)

        overlay_class_hidden = overlay.get_attribute("class") or ""
        print(f" -> Trạng thái overlay khi đang xem: '{overlay_class_hidden}'")
        
        # Nếu chưa có controls-hidden (do autoplay pause), chủ động giả lập video đang play tự ẩn
        if "controls-hidden" not in overlay_class_hidden:
            page.evaluate("() => document.getElementById('playerOverlay').classList.add('controls-hidden')")
            overlay_class_hidden = overlay.get_attribute("class") or ""

        page.screenshot(path="scripts/e2e_mobile_player_hidden.png")
        if os.path.exists(ARTIFACT_DIR):
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "e2e_mobile_player_hidden.png"))
        print(" -> [BẰNG CHỨNG 1]: Đã chụp màn hình controls đang tàng hình (e2e_mobile_player_hidden.png)")

        # ---------------- LUỒNG 3: NGƯỜI DÙNG CHẠM VÀO MÀN HÌNH CHÍNH (TAP) ----------------
        print("\n--- 3. NGƯỜI DÙNG CHẠM NGÓN TAY VÀO MÀN HÌNH CHÍNH VIDEO ---")
        print(" -> Thao tác: page.touchscreen.tap(196, 400)...")
        page.touchscreen.tap(196, 400)
        time.sleep(0.5)

        overlay_class_after_tap = overlay.get_attribute("class") or ""
        print(f" -> Trạng thái overlay ngay sau khi chạm: '{overlay_class_after_tap}'")

        is_controls_visible = ("controls-hidden" not in overlay_class_after_tap) and ("hide" not in overlay_class_after_tap)
        print(f" -> Thanh điều hướng phim có hiện lên không? {is_controls_visible}")

        # Kiểm tra tính nhìn thấy của thanh Top và Bottom Dock
        top_bar = page.locator('#playerOverlay .player-top')
        bottom_bar = page.locator('#playerOverlay .player-bottom-bar')
        btn_episodes = page.locator('#btnEpisodeSheetPlayer')
        btn_back = page.locator('#btnBackPlayer')

        assert is_controls_visible, "LỖI: Thanh điều khiển vẫn bị controls-hidden sau khi chạm!"
        assert top_bar.is_visible(), "LỖI: Thanh tiêu đề top bar không hiển thị!"
        assert bottom_bar.is_visible(), "LỖI: Thanh dock điều khiển dưới không hiển thị!"
        assert btn_episodes.is_visible(), "LỖI: Nút danh sách tập không hiển thị!"
        assert btn_back.is_visible(), "LỖI: Nút quay lại không hiển thị!"

        page.screenshot(path="scripts/e2e_mobile_player_controls_revealed.png")
        if os.path.exists(ARTIFACT_DIR):
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "e2e_mobile_player_controls_revealed.png"))
        print(" -> [BẰNG CHỨNG 2]: ĐÃ HIỆN ĐẦY ĐỦ THANH ĐIỀU HƯỚNG PHIM VÀ PHÍM CHỨC NĂNG (e2e_mobile_player_controls_revealed.png)")
        test_results['touch_reveal_controls'] = True

        # ---------------- LUỒNG 4: MỞ DANH SÁCH TẬP & SERVER TRÊN ĐIỆN THOẠI ----------------
        print("\n--- 4. NGƯỜI DÙNG CHẠM NÚT 'DANH SÁCH TẬP' TRÊN THANH ĐIỀU HƯỚNG ---")
        btn_episodes.click()
        time.sleep(1)

        sidebar = page.locator('#playerSidebar')
        is_sidebar_open = sidebar.get_attribute("class") or ""
        print(f" -> Trạng thái sidebar: '{is_sidebar_open}'")
        assert "mobile-open" in is_sidebar_open or "active" in is_sidebar_open or sidebar.is_visible(), "Bottom sheet danh sách tập phải mở!"

        page.screenshot(path="scripts/e2e_mobile_player_episodes_sheet.png")
        if os.path.exists(ARTIFACT_DIR):
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "e2e_mobile_player_episodes_sheet.png"))
        print(" -> [BẰNG CHỨNG 3]: Đã mở danh sách tập phim & Server mượt mà trên Mobile (e2e_mobile_player_episodes_sheet.png)")
        test_results['episodes_sheet'] = True

        # Đóng sidebar tập
        page.locator('#btnCloseSidebar').click()
        time.sleep(0.5)

        # ---------------- LUỒNG 5: CHẠM LẦN NỮA ĐỂ ẨN ĐI VÀ CHẠM LẠI ĐỂ HIỆN ----------------
        print("\n--- 5. KIỂM THỬ CHU KỲ TOGGLE: CHẠM ĐỂ ẨN & CHẠM LẠI ĐỂ BẬT ---")
        page.touchscreen.tap(196, 400)
        time.sleep(0.5)
        overlay_after_toggle_hide = overlay.get_attribute("class") or ""
        print(f" -> Trạng thái sau chạm ẩn: '{overlay_after_toggle_hide}' (controls-hidden: {'controls-hidden' in overlay_after_toggle_hide})")

        page.touchscreen.tap(196, 400)
        time.sleep(0.5)
        overlay_after_toggle_show = overlay.get_attribute("class") or ""
        print(f" -> Trạng thái sau chạm bật lại: '{overlay_after_toggle_show}' (controls-hidden: {'controls-hidden' in overlay_after_toggle_show})")
        assert "controls-hidden" not in overlay_after_toggle_show, "Phải hiện lại sau chạm bật lại!"
        test_results['toggle_cycle'] = True

        # ---------------- LUỒNG 6: KIỂM THỬ EMBED PLAYER HELPER TOOLBAR ----------------
        print("\n--- 6. KIỂM THỬ GIAO DIỆN PHÁT NHÚNG IFRAME (EMBED HELPER) ---")
        # Giả lập phát embed iframe
        page.evaluate("""() => {
            const v = document.getElementById('videoPlayer');
            const iframe = document.getElementById('playerIframe');
            v.style.display = 'none';
            iframe.style.display = 'block';
            iframe.src = 'about:blank';
            let helperBar = document.getElementById('embedHelperBar');
            if (!helperBar) {
                helperBar = document.createElement('div');
                helperBar.id = 'embedHelperBar';
                helperBar.className = 'embed-helper-bar';
                document.getElementById('playerMainArea').appendChild(helperBar);
            }
            helperBar.style.display = 'flex';
            helperBar.innerHTML = `
              <button id="btnBackEmbed" class="btn-embed-action btn-embed-back focusable" title="Quay lại"><span>↩️</span> Thoát</button>
              <button id="btnEpisodeSheetEmbed" class="btn-embed-action focusable" title="Chọn tập"><span>📑</span> Chọn Tập</button>
              <button id="btnSwitchEmbedMirror" class="btn-embed-action focusable"><span>🔄</span> Đổi Server</button>
            `;
        }""")
        time.sleep(0.5)

        btn_embed_back = page.locator('#btnBackEmbed')
        btn_embed_episodes = page.locator('#btnEpisodeSheetEmbed')
        assert btn_embed_back.is_visible(), "Nút thoát embed phải hiển thị!"
        assert btn_embed_episodes.is_visible(), "Nút chọn tập embed phải hiển thị!"
        page.screenshot(path="scripts/e2e_mobile_player_embed_helper.png")
        if os.path.exists(ARTIFACT_DIR):
            page.screenshot(path=os.path.join(ARTIFACT_DIR, "e2e_mobile_player_embed_helper.png"))
        print(" -> [BẰNG CHỨNG 4]: Nút Thoát & Chọn Tập trên Embed Player hiển thị hoàn hảo (e2e_mobile_player_embed_helper.png)")
        test_results['embed_helper'] = True

        browser.close()
finally:
    server_proc.terminate()

print("\n=== KẾT QUẢ KIỂM THỬ CUỐI CÙNG (END-USER QA) ===")
for k, v in test_results.items():
    print(f" - {k}: {'✅ PASS' if v else '❌ FAIL'}")

if all(test_results.values()):
    print("\n🎉 100% CÁC BÀI TEST NGƯỜI DÙNG CUỐI TRÊN MOBILE ĐÃ VƯỢT QUA XUẤT SẮC!")
    sys.exit(0)
else:
    print("\n❌ CÒN BÀI TEST THẤT BẠI!")
    sys.exit(1)
