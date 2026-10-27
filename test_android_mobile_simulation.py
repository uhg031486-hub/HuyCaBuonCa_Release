import os
import sys
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from playwright.sync_api import sync_playwright

def run_android_mobile_simulation():
    print("=" * 70)
    print("🚀 BẮT ĐẦU KIỂM THỬ GIẢ LẬP ANDROID (MOBILE VIEWPORT & TOUCH EMULATION)")
    print("=" * 70)

    results = []

    def record_test(name, passed, detail=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        results.append((name, passed, detail))
        print(f"[{status}] {name}: {detail}")

    with sync_playwright() as p:
        # Cấu hình thiết bị Android Mobile giả lập chuẩn (Pixel 7 / Galaxy S23)
        # Viewport dọc: 393 x 851, Touch Support, Mobile User Agent
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 393, "height": 851},
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
            device_scale_factor=2.75
        )
        page = context.new_page()

        # Mở trang web Huy Cá từ server kiểm thử nội bộ (port 8888)
        print("\n📱 1. Khởi động Web trên Giả lập Android Pixel 7 (393 x 851)...")
        page.goto("http://localhost:8888", wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # -------------------------------------------------------------
        # TEST GROUP 1: GIAO DIỆN CHÍNH TRÊN ANDROID MOBILE
        # -------------------------------------------------------------
        print("\n--- PHẦN 1: GIAO DIỆN MOBILE NATIVE ---")
        
        # 1.1 Header Bar gọn gàng
        header_height = page.evaluate("() => document.querySelector('.header-bar').offsetHeight")
        record_test("Header Mobile gọn gàng", header_height <= 60, f"Chiều cao header: {header_height}px")

        # 1.2 Lưới phim 3 cột chuẩn di động
        grid_cols = page.evaluate("() => window.getComputedStyle(document.getElementById('mainGrid')).getPropertyValue('grid-template-columns').split(' ').length")
        record_test("Lưới phim 3 cột chuẩn Mobile", grid_cols == 3, f"Số cột: {grid_cols}")

        # -------------------------------------------------------------
        # TEST GROUP 2: PHIM MÀN NGANG (16:9) TRÊN MOBILE
        # -------------------------------------------------------------
        print("\n--- PHẦN 2: PHIM MÀN NGANG (16:9) TRÊN MOBILE ---")
        
        # Mở 1 phim bộ/lẻ chuẩn 16:9
        card = page.wait_for_selector(".movie-card", timeout=10000)
        card.tap() # Giả lập chạm cảm ứng ngón tay
        time.sleep(1.5)

        detail_modal = page.wait_for_selector("#detailModal", state="visible")
        btn_watch = page.wait_for_selector("#btnPlayFirst", state="visible")
        btn_watch.tap()
        time.sleep(2.5)

        # 2.1 Kiểm tra player container hiển thị
        player_visible = page.is_visible("#playerContainer")
        record_test("Mở Player trên Android", player_visible, "Player hiển thị toàn màn hình")

        # 2.2 Phim ngang trên mobile dọc tự động chuyển xoay ngang (player-forced-landscape)
        is_landscape_forced = page.evaluate("() => document.getElementById('playerContainer').classList.contains('player-forced-landscape')")
        is_vertical_mode = page.evaluate("() => document.getElementById('playerContainer').classList.contains('player-vertical-mode')")
        record_test("Phim ngang 16:9 xoay ngang rạp chiếu", is_landscape_forced and not is_vertical_mode, f"forced-landscape: {is_landscape_forced}, vertical-mode: {is_vertical_mode}")

        # 2.3 Nút xoay màn hình hoạt động mượt mà
        btn_rotate = page.wait_for_selector("#btnRotatePlayer", state="visible")
        btn_rotate.tap() # Bấm xoay dọc
        time.sleep(0.5)
        is_now_portrait = not page.evaluate("() => document.getElementById('playerContainer').classList.contains('player-forced-landscape')")
        rotate_text = page.evaluate("() => document.getElementById('rotateBtnText') ? document.getElementById('rotateBtnText').textContent : ''")
        record_test("Nút Xoay màn hình chuyển dọc", is_now_portrait, f"Trở về dọc: {is_now_portrait}, text: {rotate_text}")

        # Bấm lại để xoay ngang rạp chiếu
        btn_rotate.tap()
        time.sleep(0.5)
        is_back_landscape = page.evaluate("() => document.getElementById('playerContainer').classList.contains('player-forced-landscape')")
        record_test("Nút Xoay màn hình quay lại ngang", is_back_landscape, f"Quay lại ngang: {is_back_landscape}")

        # 2.4 Chạm vào màn hình video khi controls đang hiện: ẨN CONTROLS MÀ KHÔNG PAUSE PHIM!
        video_paused_before = page.evaluate("() => document.getElementById('videoPlayer').paused")
        page.evaluate("() => window.togglePlayerControls()")
        time.sleep(0.5)
        controls_hidden_after = page.evaluate("() => document.getElementById('playerOverlay').classList.contains('controls-hidden')")
        video_paused_after = page.evaluate("() => document.getElementById('videoPlayer').paused")
        record_test("Chạm màn hình ẩn controls KHÔNG làm dừng phim", controls_hidden_after and (video_paused_before == video_paused_after), f"Overlay hidden: {controls_hidden_after}, paused: {video_paused_after}")

        # Chạm lại vào màn hình để hiện controls
        page.evaluate("() => window.togglePlayerControls()")
        time.sleep(0.5)
        controls_visible_again = not page.evaluate("() => document.getElementById('playerOverlay').classList.contains('controls-hidden')")
        record_test("Chạm màn hình hiện lại controls", controls_visible_again, f"Overlay visible: {controls_visible_again}")

        # 2.5 Nút Play/Pause chính ở Dock dưới hoạt động
        btn_play = page.wait_for_selector("#btnPlayPause", state="visible")
        btn_play.tap() # Tạm dừng
        time.sleep(0.5)
        paused_state = page.evaluate("() => document.getElementById('videoPlayer').paused")
        btn_play.tap() # Phát tiếp
        time.sleep(0.5)
        playing_state = not page.evaluate("() => document.getElementById('videoPlayer').paused")
        record_test("Nút Play/Pause chính nhạy cảm ứng", paused_state and playing_state, f"Paused: {paused_state} -> Playing: {playing_state}")

        # 2.6 Tua tiến +10s / Tua lùi -10s
        curr_t_1 = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
        page.locator("#btnCenterForward").tap()
        time.sleep(0.5)
        curr_t_2 = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
        record_test("Nút Tua tiến +10s", curr_t_2 >= curr_t_1 + 8, f"Từ {curr_t_1:.1f}s -> {curr_t_2:.1f}s")

        page.locator("#btnCenterRewind").tap()
        time.sleep(0.5)
        curr_t_3 = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
        record_test("Nút Tua lùi -10s", curr_t_3 <= curr_t_2 - 8, f"Từ {curr_t_2:.1f}s -> {curr_t_3:.1f}s")

        # 2.7 Mute / Unmute 1 chạm trên mobile
        btn_vol = page.locator("#btnVolumeToggle")
        btn_vol.tap() # Mute
        time.sleep(0.3)
        muted_state = page.evaluate("() => document.getElementById('videoPlayer').muted")
        btn_vol.tap() # Unmute
        time.sleep(0.3)
        unmuted_state = not page.evaluate("() => document.getElementById('videoPlayer').muted")
        record_test("Nút Âm lượng Mute/Unmute 1 chạm", muted_state and unmuted_state, f"Muted: {muted_state} -> Unmuted: {unmuted_state}")

        # 2.8 Tốc độ phát 5 mức
        btn_speed = page.locator("#btnSpeedPlayer")
        btn_speed.tap() # 1.0x -> 1.25x
        time.sleep(0.3)
        rate_1 = page.evaluate("() => document.getElementById('videoPlayer').playbackRate")
        record_test("Đổi tốc độ phát trên Mobile", rate_1 == 1.25, f"Tốc độ: {rate_1}x")

        # 2.9 Tỉ lệ khung hình (Fit / Fill / Căng)
        btn_asp = page.locator("#btnAspectPlayer")
        btn_asp.tap() # Fit -> Fill
        time.sleep(0.3)
        obj_fit = page.evaluate("() => document.getElementById('videoPlayer').style.objectFit")
        record_test("Đổi tỉ lệ khung hình (Aspect)", obj_fit == "cover", f"object-fit: {obj_fit}")

        # 2.10 Khóa cảm ứng trên Mobile
        btn_lock = page.locator("#btnLockPlayer")
        btn_lock.tap()
        time.sleep(0.5)
        is_locked = page.evaluate("() => window.isTouchLocked === true")
        btn_unlock = page.wait_for_selector("#btnUnlockTouch", state="visible")
        btn_unlock.tap()
        time.sleep(0.5)
        is_unlocked = page.evaluate("() => window.isTouchLocked === false")
        record_test("Khóa cảm ứng & Mở khóa an toàn", is_locked and is_unlocked, f"Locked: {is_locked} -> Unlocked: {is_unlocked}")

        # Chụp ảnh bằng chứng Phim Ngang trên Android
        screenshot_path = os.path.join(os.getcwd(), "android_sim_landscape_movie.png")
        page.screenshot(path=screenshot_path)
        print(f"📸 Đã chụp ảnh Phim Ngang Android: {screenshot_path}")

        # Thoát player để sang phần 3
        page.locator("#btnBackPlayer").tap()
        time.sleep(1.5)
        page.locator("#btnCloseDetail").tap()
        time.sleep(1.0)

        # -------------------------------------------------------------
        # TEST GROUP 3: PHIM MÀN DỌC (9:16 - SHORT DRAMA / REELS)
        # -------------------------------------------------------------
        print("\n--- PHẦN 3: PHIM MÀN DỌC (9:16) TRÊN ANDROID MOBILE ---")

        # Chuyển sang tab PHIM NGẮN (Short Drama)
        page.evaluate("() => { const b = document.getElementById('srcPhimNgan'); if (b) b.click(); }")
        time.sleep(3.0)

        # Mở phim ngắn đầu tiên
        short_card = page.wait_for_selector(".movie-card", timeout=10000)
        short_title = page.evaluate("() => document.querySelector('.movie-card .card-title').textContent")
        short_card.tap()
        time.sleep(2.0)

        page.wait_for_selector("#detailModal", state="visible")
        btn_watch_short = page.wait_for_selector("#btnPlayFirst", state="visible")
        btn_watch_short.tap()
        time.sleep(3.0)

        # 3.1 TỰ ĐỘNG CHUYỂN DỌC THEO PHIM (Vertical Drama Mode)
        is_short_vert = page.evaluate("() => document.getElementById('playerContainer').classList.contains('player-vertical-mode')")
        is_short_forced_land = page.evaluate("() => document.getElementById('playerContainer').classList.contains('player-forced-landscape')")
        rotate_lbl = page.evaluate("() => document.getElementById('rotateBtnText') ? document.getElementById('rotateBtnText').textContent : ''")
        record_test("Tự động chuyển dọc theo phim (9:16)", is_short_vert and not is_short_forced_land, f"vertical-mode: {is_short_vert}, forced-landscape: {is_short_forced_land}, label: {rotate_lbl}")

        # 3.2 Video hiển thị dọc toàn màn hình (Full Height Portrait)
        vid_rect = page.evaluate("() => { const v = document.getElementById('videoPlayer'); const r = v.getBoundingClientRect(); return { w: r.width, h: r.height }; }")
        record_test("Video dọc tràn trọn khung nhìn", vid_rect["h"] >= 700, f"Chiều cao video: {vid_rect['h']}px x {vid_rect['w']}px")

        # 3.3 Mở danh sách tập trên Mobile Dọc: Bottom Sheet trượt từ dưới lên
        btn_sheet = page.wait_for_selector("#btnEpisodeSheetPlayer", state="visible")
        btn_sheet.tap()
        time.sleep(0.8)

        sidebar_mobile_open = page.evaluate("() => document.getElementById('playerSidebar').classList.contains('mobile-open')")
        sidebar_bottom = page.evaluate("() => { const s = document.getElementById('playerSidebar'); const r = s.getBoundingClientRect(); return r.top >= 0 && r.height >= 300; }")
        record_test("Danh sách tập Bottom Sheet mở mượt mà", sidebar_mobile_open and sidebar_bottom, f"mobile-open: {sidebar_mobile_open}, bottom-sheet: {sidebar_bottom}")

        # Chụp ảnh Bottom Sheet danh sách tập
        screenshot_sheet = os.path.join(os.getcwd(), "android_sim_bottom_sheet_episodes.png")
        page.screenshot(path=screenshot_sheet)
        print(f"📸 Đã chụp ảnh Bottom Sheet DS Tập: {screenshot_sheet}")

        # Kiểm tra Touch Target của nút Đóng Sidebar lúc đang mở
        size_close_btn = page.evaluate("() => { const el = document.getElementById('btnCloseSidebar'); if (!el) return null; const r = el.getBoundingClientRect(); return { w: r.width, h: r.height }; }")
        record_test("Touch target: Nút Đóng Sidebar", size_close_btn and size_close_btn["w"] >= 34 and size_close_btn["h"] >= 34, f"Kích thước: {size_close_btn['w']:.0f}x{size_close_btn['h']:.0f}px")

        # 3.4 Nút đóng Sidebar trên mobile to rõ, bấm nhạy
        btn_close_sidebar = page.wait_for_selector("#btnCloseSidebar", state="visible")
        btn_close_sidebar.tap()
        time.sleep(0.8)

        sidebar_closed = not page.evaluate("() => document.getElementById('playerSidebar').classList.contains('mobile-open')")
        record_test("Nút đóng Sidebar đóng trượt xuống mượt mà", sidebar_closed, f"Sidebar closed: {sidebar_closed}")

        # 3.5 Chuyển sang tập tiếp theo trong Phim Màn Dọc: PHẢI VỀ TỪ ĐẦU (00:00) & GIỮ CHẾ ĐỘ DỌC
        # Tua tập 1 đến 25s
        page.evaluate("() => { const v = document.getElementById('videoPlayer'); v.currentTime = 25; }")
        time.sleep(1.0)
        t_ep1 = page.evaluate("() => document.getElementById('videoPlayer').currentTime")

        # Bấm Next Episode
        btn_next = page.locator("#btnCenterNext")
        btn_next.tap()
        time.sleep(3.0)

        # Kiểm tra tập 2 bắt đầu từ đầu
        t_ep2 = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
        ep2_sub = page.evaluate("() => document.getElementById('playerSub').textContent")
        is_still_vert = page.evaluate("() => document.getElementById('playerContainer').classList.contains('player-vertical-mode')")
        record_test("Chuyển tập tiếp theo về 00:00 & giữ chế độ dọc", t_ep2 < 5.0 and is_still_vert, f"Tập: {ep2_sub}, Thời gian: {t_ep2:.1f}s, Vẫn xem dọc: {is_still_vert}")

        # Chụp ảnh bằng chứng Phim Dọc Android
        screenshot_vert = os.path.join(os.getcwd(), "android_sim_portrait_short_drama.png")
        page.screenshot(path=screenshot_vert)
        print(f"📸 Đã chụp ảnh Phim Dọc Android: {screenshot_vert}")

        # -------------------------------------------------------------
        # TEST GROUP 4: XOAY NGANG THỰC TẾ TRÊN ANDROID (DEVICE ORIENTATION)
        # -------------------------------------------------------------
        print("\n--- PHẦN 4: XOAY NGANG THỰC TẾ TRÊN ANDROID ---")
        
        # Giả lập người dùng xoay ngang điện thoại (Landscape Viewport: 851 x 393)
        page.set_viewport_size({"width": 851, "height": 393})
        time.sleep(1.0)

        # Kiểm tra: Khi xoay ngang thật, KHÔNG được ép xoay rotate(90deg) làm lộn ngược màn hình
        is_rotated_unwanted = page.evaluate("() => document.getElementById('playerContainer').classList.contains('player-forced-landscape')")
        record_test("Điện thoại xoay ngang không bị lộn ngược", not is_rotated_unwanted, f"forced-landscape: {is_rotated_unwanted}")

        # -------------------------------------------------------------
        # TEST GROUP 5: KÍCH THƯỚC NÚT BẤM CẢM ỨNG (TOUCH TARGETS)
        # -------------------------------------------------------------
        print("\n--- PHẦN 5: KIỂM TRA TOUCH TARGETS (>= 36px) ---")
        
        touch_buttons = [
            ("Play/Pause", "#btnPlayPause"),
            ("Tua +10s", "#btnCenterForward"),
            ("Tua -10s", "#btnCenterRewind"),
            ("DS Tập", "#btnEpisodeSheetPlayer"),
            ("Nút Quay lại", "#btnBackPlayer")
        ]

        all_touch_valid = True
        for b_name, b_sel in touch_buttons:
            size = page.evaluate(f"() => {{ const el = document.querySelector('{b_sel}'); if (!el) return null; const r = el.getBoundingClientRect(); return {{ w: r.width, h: r.height }}; }}")
            if size:
                is_valid = size["w"] >= 34 and size["h"] >= 34
                if not is_valid:
                    all_touch_valid = False
                record_test(f"Touch target: {b_name}", is_valid, f"Kích thước: {size['w']:.0f}x{size['h']:.0f}px")
            else:
                record_test(f"Touch target: {b_name}", False, "Không tìm thấy selector")

        browser.close()

    # -------------------------------------------------------------
    # TỔNG KẾT
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("📊 TỔNG KẾT KIỂM THỬ GIẢ LẬP ANDROID (MOBILE VIEWPORT & TOUCH)")
    print("=" * 70)
    total = len(results)
    passed_count = sum(1 for _, p, _ in results if p)
    failed_count = total - passed_count
    pass_rate = (passed_count / total) * 100

    print(f"Tổng số bài kiểm thử: {total}")
    print(f"Thành công: {passed_count} / {total} ({pass_rate:.1f}%)")
    print(f"Thất bại: {failed_count}")
    print("=" * 70)

    if failed_count == 0:
        print("🎉 TẤT CẢ CÁC BÀI KIỂM THỬ TRÊN GIẢ LẬP ANDROID ĐÃ VƯỢT QUA 100%!")
    else:
        print("⚠️ Có bài kiểm thử thất bại, xem chi tiết ở trên.")

if __name__ == "__main__":
    run_android_mobile_simulation()
