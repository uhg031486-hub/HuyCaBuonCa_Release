# -*- coding: utf-8 -*-
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"

results = []

def record(test_name, success, detail=""):
    results.append({"name": test_name, "success": success, "detail": detail})
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"[{status}] {test_name}: {detail}")

def run_simulation():
    print("================================================================")
    print("🚀 BẮT ĐẦU GIẢ LẬP KIỂM THỬ TOÀN DIỆN MỌI TÍNH NĂNG HUY CÁ")
    print("================================================================")

    server_proc = subprocess.Popen([sys.executable, "test_server.py"])
    time.sleep(2)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            # Lắng nghe lỗi console và pageerror
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: console_errors.append(str(err)))

            print("\n--- PHẦN 1: TẢI TRANG CHỦ & KIỂM TRA ĐẦU TRANG (HEADER) ---")
            page.goto("http://localhost:8888/index.html")
            page.wait_for_timeout(2500)

            # 1.1 Kiểm tra tiêu đề trang
            title = page.title()
            record("1.1 Page Title", "Huy Cá" in title or "Huy" in title, f"Title: {title}")

            # 1.2 Kiểm tra Đồng hồ Header
            clock_el = page.query_selector("#clockDisplay")
            clock_text = clock_el.text_content() if clock_el else ""
            record("1.2 Header Clock", len(clock_text.strip()) >= 4, f"Clock: {clock_text}")

            # 1.3 Kiểm tra Nút Cài Đặt App (Install Modal)
            btn_install = page.query_selector("#btnInstallApp")
            if btn_install:
                btn_install.click()
                page.wait_for_timeout(600)
                modal_install = page.query_selector("#installPlatformModal")
                is_modal_vis = modal_install.evaluate("el => window.getComputedStyle(el).display !== 'none'")
                record("1.3 Modal Cài Đặt App", is_modal_vis, "Mở thành công modal cài đặt đa nền tảng")
                # Đóng modal
                btn_close_inst = page.query_selector("#btnCloseInstallModalTop")
                if btn_close_inst: btn_close_inst.click()
                page.wait_for_timeout(400)
            else:
                record("1.3 Modal Cài Đặt App", False, "Không tìm thấy nút #btnInstallApp")

            # 1.4 Kiểm tra Nút Tìm Kiếm (Search Modal)
            btn_search = page.query_selector("#btnSearch")
            if btn_search:
                btn_search.click()
                page.wait_for_timeout(600)
                search_modal = page.query_selector("#searchModal")
                is_search_open = search_modal.evaluate("el => window.getComputedStyle(el).display !== 'none'")
                record("1.4 Mở Modal Tìm Kiếm", is_search_open, "Modal tìm kiếm mở thành công")

                # Gõ từ khóa tìm kiếm và bấm TÌM KIẾM
                search_input = page.query_selector("#searchInput")
                search_input.fill("chiến")
                page.wait_for_timeout(300)
                page.query_selector("#btnDoSearch").click()
                try:
                    page.wait_for_selector("#searchResultsGrid .movie-card", timeout=8000)
                except Exception:
                    page.wait_for_timeout(1000)
                search_results = page.query_selector_all("#searchResultsGrid .movie-card")
                record("1.4 Kết quả tìm kiếm", len(search_results) > 0, f"Tìm thấy {len(search_results)} phim với từ khóa 'chiến'")

                # Đóng search modal
                page.query_selector("#btnCloseSearch").click()
                page.wait_for_timeout(400)
            else:
                record("1.4 Modal Tìm Kiếm", False, "Không tìm thấy nút #btnSearch")

            # 1.5 Kiểm tra Nút Lịch Thi Đấu Bóng Đá (Schedule Modal)
            btn_sched = page.query_selector("#btnScheduleHeader")
            if btn_sched:
                btn_sched.click()
                page.wait_for_timeout(800)
                sched_modal = page.query_selector("#scheduleModal")
                is_sched_open = sched_modal.evaluate("el => window.getComputedStyle(el).display !== 'none'")
                record("1.5 Mở Lịch Thi Đấu Bóng Đá", is_sched_open, "Modal lịch thi đấu mở thành công")

                matches = page.query_selector_all(".match-card, .btn-match-play")
                record("1.5 Danh sách trận đấu bóng đá", len(matches) > 0, f"Hiển thị {len(matches)} mục trận đấu")

                page.query_selector("#btnCloseSchedule").click()
                page.wait_for_timeout(400)
            else:
                record("1.5 Modal Lịch Thi Đấu", False, "Không tìm thấy nút #btnScheduleHeader")

            print("\n--- PHẦN 2: CHUYỂN ĐỔI CÁC TAB NỘI DUNG CHÍNH ---")
            # 2.1 Tab Anime
            tab_anime = page.query_selector("#srcAnimeHay")
            if tab_anime:
                tab_anime.click()
                page.wait_for_timeout(2000)
                anime_cards = page.query_selector_all("#mainGrid .movie-card")
                record("2.1 Chuyển Tab Anime", len(anime_cards) > 0, f"Tải {len(anime_cards)} phim anime thành công")

            # 2.2 Tab Xem Tivi
            tab_tv = page.query_selector("#srcXemTiVi")
            if tab_tv:
                tab_tv.click()
                page.wait_for_timeout(2000)
                tv_cards = page.query_selector_all("#mainGrid .movie-card")
                record("2.2 Chuyển Tab Xem Tivi", len(tv_cards) > 0, f"Tải {len(tv_cards)} kênh truyền hình thành công")

            # 2.3 Tab Phim Ngắn (Short Dramas)
            tab_short = page.query_selector("#srcPhimNgan")
            if tab_short:
                tab_short.click()
                try:
                    page.wait_for_selector("#mainGrid .movie-card", timeout=8000)
                except Exception:
                    page.wait_for_timeout(1000)
                short_cards = page.query_selector_all("#mainGrid .movie-card")
                record("2.3 Chuyển Tab Phim Ngắn", len(short_cards) > 0, f"Tải {len(short_cards)} tập phim ngắn thành công")

            # 2.4 Quay lại Tab Phim (KKPhim) & Bộ lọc
            tab_phim = page.query_selector("#srcKKPhim")
            if tab_phim:
                tab_phim.click()
                page.wait_for_timeout(2000)
                movie_cards = page.query_selector_all("#mainGrid .movie-card")
                record("2.4 Quay lại Tab Phim", len(movie_cards) > 0, f"Tải {len(movie_cards)} phim chính thành công")

            # 2.5 Nút Tải Thêm Phim (Pagination)
            btn_load_more = page.query_selector("#btnLoadMore")
            if btn_load_more:
                count_before = len(page.query_selector_all("#mainGrid .movie-card"))
                btn_load_more.click()
                page.wait_for_timeout(2500)
                count_after = len(page.query_selector_all("#mainGrid .movie-card"))
                record("2.5 Nút Tải Thêm Phim", count_after > count_before, f"Số phim tăng từ {count_before} -> {count_after}")

            print("\n--- PHẦN 3: MODAL CHI TIẾT PHIM (DETAIL MODAL) ---")
            first_card = page.wait_for_selector("#mainGrid .movie-card", timeout=8000)
            first_card.click()
            page.wait_for_timeout(1500)

            detail_modal = page.query_selector("#detailModal")
            detail_title = page.query_selector("#detailTitle").text_content()
            detail_open = detail_modal.evaluate("el => window.getComputedStyle(el).display !== 'none'")
            record("3.1 Mở Modal Chi Tiết Phim", detail_open and len(detail_title) > 0, f"Phim: {detail_title}")

            # 3.2 Nút Yêu Thích trong Chi Tiết
            btn_fav_detail = page.query_selector("#btnDetailFav")
            if btn_fav_detail:
                btn_fav_detail.click()
                page.wait_for_timeout(400)
                record("3.2 Nút Yêu Thích Chi Tiết", True, "Bấm yêu thích thành công")

            # 3.3 Danh sách tập phim trong Detail Modal
            detail_episodes = page.query_selector_all("#episodesGrid .btn-episode")
            record("3.3 Danh Sách Tập trong Detail", len(detail_episodes) > 0, f"Có {len(detail_episodes)} tập phim trong danh sách")

            print("\n--- PHẦN 4: TRÌNH PHÁT VIDEO ĐIỆN ẢNH (CINEMA PRO PLAYER) ---")
            # Bấm nút Xem Tập Đầu
            btn_play_first = page.query_selector("#btnPlayFirst")
            btn_play_first.click()
            page.wait_for_timeout(3500)

            player_container = page.query_selector("#playerContainer")
            is_player_open = player_container.evaluate("el => window.getComputedStyle(el).display !== 'none'")
            record("4.1 Khởi động Trình Phát Video", is_player_open, "Player Container hiển thị thành công")

            # 4.2 Tạm Dừng / Tiếp Tục (Play / Pause)
            btn_pp = page.query_selector("#btnPlayPause")
            btn_pp.click()
            page.wait_for_timeout(600)
            is_paused_1 = page.evaluate("() => document.getElementById('videoPlayer').paused")
            record("4.2 Nút Tạm Dừng (Pause)", is_paused_1, "Video đã tạm dừng")

            btn_pp.click()
            page.wait_for_timeout(600)
            is_paused_2 = page.evaluate("() => document.getElementById('videoPlayer').paused")
            record("4.2 Nút Tiếp Tục (Play)", not is_paused_2, "Video đã tiếp tục phát")

            # 4.3 Tua đi +10s và Tua lại -10s
            time_start = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            btn_fwd = page.query_selector("#btnCenterForward")
            btn_fwd.click()
            page.wait_for_timeout(500)
            time_fwd = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            record("4.3 Tua Đi +10s", time_fwd > time_start + 5, f"Tua từ {time_start:.1f}s -> {time_fwd:.1f}s")

            btn_rwd = page.query_selector("#btnCenterRewind")
            btn_rwd.click()
            page.wait_for_timeout(500)
            time_rwd = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            record("4.3 Tua Lại -10s", time_rwd < time_fwd, f"Tua về {time_rwd:.1f}s")

            # 4.4 Thay đổi tốc độ phát (Speed Changer)
            btn_speed = page.query_selector("#btnSpeedPlayer")
            spd1 = btn_speed.text_content()
            btn_speed.click()
            page.wait_for_timeout(400)
            spd2 = btn_speed.text_content()
            rate = page.evaluate("() => document.getElementById('videoPlayer').playbackRate")
            record("4.4 Nút Tốc Độ Phát (Speed)", spd2 != spd1 and rate > 1.0, f"Tốc độ: {spd1} -> {spd2} (playbackRate={rate})")

            # 4.5 Nút Tỉ lệ khung hình (Aspect Ratio)
            btn_aspect = page.query_selector("#btnAspectPlayer")
            badge_aspect = page.query_selector("#aspectBadgeText")
            asp_init = badge_aspect.text_content()
            btn_aspect.click()
            page.wait_for_timeout(400)
            asp_next = badge_aspect.text_content()
            fit_mode = page.evaluate("() => document.getElementById('videoPlayer').style.objectFit")
            record("4.5 Nút Tỉ Lệ Khung Hình", asp_next != asp_init and fit_mode == "cover", f"Tỉ lệ: {asp_init} -> {asp_next} (objectFit={fit_mode})")

            # 4.6 Nút Khóa cảm ứng và Mở khóa
            btn_lock = page.query_selector("#btnLockPlayer")
            btn_lock.click()
            page.wait_for_timeout(500)
            is_locked = page.evaluate("() => Boolean(window.isTouchLocked)")
            btn_unlock = page.query_selector("#btnUnlockTouch")
            is_unlock_visible = btn_unlock.evaluate("el => window.getComputedStyle(el).display !== 'none'")
            record("4.6 Khóa Cảm Ứng (Touch Lock)", is_locked and is_unlock_visible, "Đã khóa và hiện nút mở khóa")

            btn_unlock.click()
            page.wait_for_timeout(500)
            is_unlocked = page.evaluate("() => !Boolean(window.isTouchLocked)")
            record("4.6 Mở Khóa Cảm Ứng", is_unlocked, "Đã mở khóa cảm ứng thành công")

            # 4.7 Sidebar Danh Sách Tập & Server trong Player
            sidebar_el = page.query_selector("#playerSidebar")
            is_init_open = sidebar_el.evaluate("el => !el.classList.contains('collapsed')")
            record("4.7 Drawer Danh Sách Tập Ban Đầu", is_init_open, "Drawer danh sách tập mở sẵn trên màn hình rộng")

            btn_sidebar_toggle = page.query_selector("#btnEpisodeSheetPlayer")
            btn_sidebar_toggle.click()
            page.wait_for_timeout(500)
            is_sidebar_closed = sidebar_el.evaluate("el => el.classList.contains('collapsed')")
            record("4.7 Thu Nhỏ Drawer Danh Sách Tập", is_sidebar_closed, "Đã thu nhỏ drawer danh sách tập để xem toàn cảnh")

            btn_sidebar_toggle.click()
            page.wait_for_timeout(500)
            is_sidebar_reopen = sidebar_el.evaluate("el => !el.classList.contains('collapsed')")
            record("4.7 Mở Lại Drawer Danh Sách Tập", is_sidebar_reopen, "Đã mở lại drawer danh sách tập thành công")

            # 4.8 Nút Tập Tiếp Theo: Reset về 00:00
            page.evaluate("() => { document.getElementById('videoPlayer').currentTime = 40; }")
            page.wait_for_timeout(1000)
            btn_next_ep = page.query_selector("#btnCenterNext")
            btn_next_ep.click()
            page.wait_for_timeout(3500)
            ep2_time = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            ep2_sub = page.evaluate("() => document.getElementById('playerSub').textContent")
            record("4.8 Chuyển Tập Tiếp Theo về 00:00", ep2_time < 5.0, f"Tập 2: '{ep2_sub}' phát từ {ep2_time:.2f}s (chuẩn đầu tập)")

            # 4.9 Nút Tập Trước: Reset về 00:00
            page.evaluate("() => { document.getElementById('videoPlayer').currentTime = 50; }")
            page.wait_for_timeout(1000)
            btn_prev_ep = page.query_selector("#btnCenterPrev")
            btn_prev_ep.click()
            page.wait_for_timeout(3500)
            ep1_retime = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            ep1_resub = page.evaluate("() => document.getElementById('playerSub').textContent")
            record("4.9 Chuyển Tập Trước về 00:00", ep1_retime < 5.0, f"Tập 1: '{ep1_resub}' phát từ {ep1_retime:.2f}s (chuẩn đầu tập)")

            # 4.10 Thu Nhỏ Hình Trong Hình (Mini Player / PiP)
            btn_pip = page.query_selector("#btnPipPlayer")
            btn_pip.click()
            page.wait_for_timeout(800)
            is_pip = player_container.evaluate("el => el.classList.contains('player-floating-mini')")
            record("4.10 Bật Chế Độ Thu Nhỏ (Mini Player)", is_pip, "Player chuyển sang cửa sổ nổi góc dưới")

            # Phóng to lại
            page.query_selector("#playerMainArea").click(position={"x": 50, "y": 50})
            page.wait_for_timeout(800)
            is_restored = player_container.evaluate("el => !el.classList.contains('player-floating-mini')")
            record("4.10 Phóng To Toàn Màn Hình từ Mini", is_restored, "Đã trở lại toàn màn hình mượt mà")

            print("\n--- PHẦN 5: PHÍM TẮT BÀN PHÍM (KEYBOARD SHORTCUTS) ---")
            # 5.1 Phím Space: Tạm dừng / Tiếp tục
            page.keyboard.press("Space")
            page.wait_for_timeout(600)
            kb_paused = page.evaluate("() => document.getElementById('videoPlayer').paused")
            record("5.1 Phím Space (Play/Pause)", kb_paused, "Phím Space tạm dừng video thành công")

            page.keyboard.press("Space")
            page.wait_for_timeout(600)

            # 5.2 Phím M: Tắt / Bật tiếng (Mute)
            page.keyboard.press("KeyM")
            page.wait_for_timeout(400)
            is_muted = page.evaluate("() => document.getElementById('videoPlayer').muted")
            record("5.2 Phím M (Mute/Unmute)", is_muted, "Phím M tắt tiếng thành công")
            page.keyboard.press("KeyM")

            # 5.3 Phím ArrowRight / ArrowLeft
            cur_t = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            page.keyboard.press("ArrowRight")
            page.wait_for_timeout(400)
            fwd_t = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            record("5.3 Phím Mũi Tên Phải (Tua +10s)", fwd_t > cur_t + 4, f"Tua từ {cur_t:.1f}s -> {fwd_t:.1f}s")

            # 5.4 Thoát Player bằng Nút Quay Lại
            btn_back = page.query_selector("#btnBackPlayer")
            btn_back.click()
            page.wait_for_timeout(1000)
            is_player_closed = player_container.evaluate("el => window.getComputedStyle(el).display === 'none'")
            record("5.4 Nút Thoát Trình Phát (Back)", is_player_closed, "Thoát trình phát thành công")

            # Chụp ảnh báo cáo tổng thể
            screenshot_path = f"{ARTIFACT_DIR}\\simulation_final_report.png"
            page.screenshot(path=screenshot_path)
            print(f"\nĐã lưu ảnh chụp màn hình kiểm thử: {screenshot_path}")

            print("\n--- PHẦN 6: KIỂM TRA LỖI CONSOLE & RUNTIME ---")
            js_critical_errors = [
                e for e in console_errors
                if any(kw in e for kw in ['Uncaught', 'TypeError', 'ReferenceError', 'SyntaxError', 'RangeError'])
            ]
            record("6.1 Không Có Lỗi JS Crash / Exception", len(js_critical_errors) == 0, f"Số lỗi JS nghiêm trọng: {len(js_critical_errors)}")
            if len(js_critical_errors) > 0:
                print("Chi tiết lỗi JS nghiêm trọng:", js_critical_errors[:5])

            browser.close()

    finally:
        server_proc.terminate()

    total = len(results)
    passed = sum(1 for r in results if r["success"])
    failed = total - passed
    print("\n================================================================")
    print(f"📊 KẾT QUẢ TỔNG HỢP: {passed}/{total} BÀI KIỂM THỬ THÀNH CÔNG ({passed/total*100:.1f}%)")
    print(f"   Thành công: {passed} | Thất bại: {failed}")
    print("================================================================")

if __name__ == "__main__":
    run_simulation()
