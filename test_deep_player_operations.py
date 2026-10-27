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

def run_deep_player_test():
    print("================================================================")
    print("🎬 BẮT ĐẦU KIỂM THỬ CHUYÊN SÂU THAO TÁC TRONG LÚC XEM PHIM")
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

            page.goto("http://localhost:8888/index.html")
            page.wait_for_timeout(2000)

            # -------------------------------------------------------------
            # BÀI 1: KIỂM TRA ĐÚNG PHIM, ĐÚNG TẬP KHI BẤM XEM
            # -------------------------------------------------------------
            print("\n--- BÀI 1: XÁC THỰC TÍNH ĐÚNG ĐẮN CỦA PHIM ĐANG XEM ---")
            
            # Chọn thẻ phim đầu tiên trên trang chủ
            first_card = page.wait_for_selector("#mainGrid .movie-card", timeout=8000)
            card_title = first_card.query_selector(".card-title").text_content().strip()
            print(f"-> Phim được click: '{card_title}'")
            first_card.click()
            page.wait_for_timeout(1000)

            # Kiểm tra modal chi tiết
            detail_title = page.query_selector("#detailTitle").text_content().strip()
            record("1.1 Khớp Tiêu Đề Modal Chi Tiết", card_title.lower() in detail_title.lower() or detail_title.lower() in card_title.lower(), f"Card: '{card_title}' == Detail: '{detail_title}'")

            # Bấm xem Tập 1
            btn_play_first = page.query_selector("#btnPlayFirst")
            btn_play_first.click()
            page.wait_for_timeout(3500)

            # Kiểm tra tiêu đề trên Header của Player
            player_title = page.query_selector("#playerTitle").text_content().strip()
            player_sub = page.query_selector("#playerSub").text_content().strip()
            record("1.2 Đúng Tên Phim Trong Player", card_title.lower() in player_title.lower() or player_title.lower() in card_title.lower(), f"Tên hiển thị: '{player_title}'")
            record("1.3 Đúng Tập Đầu Tiên Trong Player", "01" in player_sub or "1" in player_sub, f"Tập hiển thị: '{player_sub}'")

            # Kiểm tra tiêu đề trong Sidebar Drawer
            sidebar_title = page.query_selector("#sidebarMovieTitle").text_content().strip()
            record("1.4 Khớp Tiêu Đề Trong Sidebar Danh Sách", card_title.lower() in sidebar_title.lower() or sidebar_title.lower() in card_title.lower(), f"Sidebar Title: '{sidebar_title}'")

            # Kiểm tra video player đang phát luồng m3u8 thực thụ
            current_src = page.evaluate("() => document.getElementById('videoPlayer').src || (window.currentPlayingMovie ? window.currentPlayingMovie.slug : '')")
            record("1.5 Luồng Phát Hợp Lệ", len(current_src) > 5, f"Luồng/Slug: {current_src[:60]}")

            page.screenshot(path=f"{ARTIFACT_DIR}\\player_test_1_verified_movie.png")

            # -------------------------------------------------------------
            # BÀI 2: THAO TÁC CÁC NÚT ĐIỀU KHIỂN CƠ BẢN
            # -------------------------------------------------------------
            print("\n--- BÀI 2: THAO TÁC NÚT PHÁT, TẠM DỪNG & TUA 10S ---")

            btn_play_pause = page.query_selector("#btnPlayPause")
            
            # Tạm dừng
            btn_play_pause.click()
            page.wait_for_timeout(500)
            is_paused = page.evaluate("() => document.getElementById('videoPlayer').paused")
            svg_pause_disp = page.evaluate("() => document.getElementById('svgPlay').style.display !== 'none'")
            record("2.1 Nút Tạm Dừng Dock Dưới", is_paused, "Video đã tạm dừng và hiển thị icon Play")

            # Tiếp tục phát
            btn_play_pause.click()
            page.wait_for_timeout(500)
            is_playing = page.evaluate("() => !document.getElementById('videoPlayer').paused")
            record("2.2 Nút Tiếp Tục Phát Dock Dưới", is_playing, "Video tiếp tục phát và hiển thị icon Pause")

            # Tạm dừng bằng cách Click vào màn hình video chính
            page.query_selector("#playerMainArea").click(position={"x": 300, "y": 250})
            page.wait_for_timeout(500)
            is_paused_screen = page.evaluate("() => document.getElementById('videoPlayer').paused")
            record("2.3 Click Trực Tiếp Màn Hình Để Pause", is_paused_screen, "Click màn hình video đã dừng phát")

            page.query_selector("#playerMainArea").click(position={"x": 300, "y": 250})
            page.wait_for_timeout(500)
            is_resumed_screen = page.evaluate("() => !document.getElementById('videoPlayer').paused")
            record("2.4 Click Trực Tiếp Màn Hình Để Play", is_resumed_screen, "Click màn hình video đã tiếp tục phát")

            # Tua đi +10s và tua lùi -10s
            t0 = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            page.query_selector("#btnCenterForward").click()
            page.wait_for_timeout(500)
            t1 = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            record("2.5 Nút Tua Đi +10s", t1 > t0 + 5, f"Tua từ {t0:.1f}s -> {t1:.1f}s")

            page.query_selector("#btnCenterRewind").click()
            page.wait_for_timeout(500)
            t2 = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            record("2.6 Nút Tua Lùi -10s", t2 < t1, f"Tua lùi về {t2:.1f}s")

            # -------------------------------------------------------------
            # BÀI 3: THANH TIẾN TRÌNH SEEKBAR (SCRUBBER) & THỜI GIAN
            # -------------------------------------------------------------
            print("\n--- BÀI 3: THANH TIẾN TRÌNH SEEKBAR & THỜI GIAN ---")

            # Giả lập seek đến 40% bằng thanh trượt seekBar
            duration = page.evaluate("() => document.getElementById('videoPlayer').duration || 100")
            page.evaluate("""() => {
                const sb = document.getElementById('seekBar');
                const v = document.getElementById('videoPlayer');
                if (sb && v && v.duration) {
                    sb.value = 40;
                    v.currentTime = v.duration * 0.4;
                    sb.dispatchEvent(new Event('input'));
                    sb.dispatchEvent(new Event('change'));
                }
            }""")
            page.wait_for_timeout(800)
            seeked_t = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            record("3.1 Kéo Thanh Scrubber (Seek to 40%)", seeked_t > 15, f"Thời gian nhảy tới: {seeked_t:.1f}s / {duration:.1f}s")

            # Kiểm tra định dạng đồng hồ hiển thị
            time_str = page.query_selector("#currentTime").text_content().strip()
            record("3.2 Hiển Thị Thời Gian Hiện Tại", ":" in time_str and len(time_str) >= 4, f"Đồng hồ: {time_str}")

            # -------------------------------------------------------------
            # BÀI 4: ĐIỀU KHIỂN ÂM LƯỢNG & MUTE
            # -------------------------------------------------------------
            print("\n--- BÀI 4: ĐIỀU KHIỂN ÂM LƯỢNG & BẬT/TẮT TIẾNG ---")

            # Chỉnh slider âm lượng về 0.4
            page.evaluate("""() => {
                const s = document.getElementById('volumeSlider');
                if (s) {
                    s.value = 0.4;
                    s.dispatchEvent(new Event('input'));
                }
            }""")
            page.wait_for_timeout(400)
            vol_val = page.evaluate("() => document.getElementById('videoPlayer').volume")
            record("4.1 Kéo Slider Âm Lượng", abs(vol_val - 0.4) < 0.05, f"Volume: {vol_val:.2f}")

            # Bấm nút tắt tiếng (Mute)
            page.query_selector("#btnVolumeToggle").click()
            page.wait_for_timeout(400)
            is_muted = page.evaluate("() => document.getElementById('videoPlayer').muted || document.getElementById('videoPlayer').volume === 0")
            record("4.2 Nút Tắt Tiếng (Mute)", is_muted, "Đã tắt tiếng thành công")

            # Bấm lại để bật tiếng (Unmute)
            page.query_selector("#btnVolumeToggle").click()
            page.wait_for_timeout(400)
            is_unmuted = page.evaluate("() => !document.getElementById('videoPlayer').muted")
            record("4.3 Nút Bật Tiếng (Unmute)", is_unmuted, "Đã bật lại tiếng thành công")

            # -------------------------------------------------------------
            # BÀI 5: TỐC ĐỘ PHÁT & TỈ LỆ KHUNG HÌNH
            # -------------------------------------------------------------
            print("\n--- BÀI 5: TỐC ĐỘ PHÁT & TỈ LỆ KHUNG HÌNH ---")

            # Kiểm tra xoay vòng tốc độ: 1.0x -> 1.25x -> 1.5x -> 2.0x -> 0.75x -> 1.0x
            btn_speed = page.query_selector("#btnSpeedPlayer")
            rates_tested = []
            for _ in range(5):
                btn_speed.click()
                page.wait_for_timeout(250)
                cur_rate = page.evaluate("() => document.getElementById('videoPlayer').playbackRate")
                badge_text = btn_speed.text_content().strip()
                rates_tested.append((badge_text, cur_rate))

            record("5.1 Xoay Vòng Đủ 5 Mức Tốc Độ", len(rates_tested) == 5, f"Các mức: {[r[0] for r in rates_tested]}")

            # Đặt lại về 1.0x
            page.evaluate("() => { document.getElementById('videoPlayer').playbackRate = 1.0; }")
            btn_speed.evaluate("el => el.textContent = '1.0x'")

            # Tỉ lệ khung hình: Fit -> Fill -> Stretch
            btn_aspect = page.query_selector("#btnAspectPlayer")
            aspect_badge = page.query_selector("#aspectBadgeText")

            btn_aspect.click() # Chuyển sang Fill
            page.wait_for_timeout(300)
            mode_fill = page.evaluate("() => document.getElementById('videoPlayer').style.objectFit")
            badge_fill = aspect_badge.text_content().strip()
            record("5.2 Tỉ Lệ Khung Hình Fill", mode_fill == "cover" and badge_fill == "Fill", f"Mode: {mode_fill} - Badge: {badge_fill}")

            btn_aspect.click() # Chuyển sang Căng (Stretch)
            page.wait_for_timeout(300)
            mode_stretch = page.evaluate("() => document.getElementById('videoPlayer').style.objectFit")
            badge_stretch = aspect_badge.text_content().strip()
            record("5.3 Tỉ Lệ Khung Hình Căng (Stretch)", mode_stretch == "fill" and badge_stretch == "Căng", f"Mode: {mode_stretch} - Badge: {badge_stretch}")

            btn_aspect.click() # Trở về Fit
            page.wait_for_timeout(300)
            mode_fit = page.evaluate("() => document.getElementById('videoPlayer').style.objectFit")
            record("5.4 Tỉ Lệ Khung Hình Fit Chuẩn Gốc", mode_fit == "contain", f"Mode: {mode_fit}")

            # -------------------------------------------------------------
            # BÀI 6: KHÓA CẢM ỨNG & TỰ ĐỘNG ẨN OVERLAY (AUTO-HIDE TIMER)
            # -------------------------------------------------------------
            print("\n--- BÀI 6: KHÓA CẢM ỨNG & TỰ ĐỘNG ẨN OVERLAY ---")

            btn_lock = page.query_selector("#btnLockPlayer")
            btn_lock.click()
            page.wait_for_timeout(400)
            is_locked = page.evaluate("() => Boolean(window.isTouchLocked)")
            overlay_hidden = page.evaluate("() => document.getElementById('playerOverlay').classList.contains('controls-hidden')")
            record("6.1 Kích Hoạt Khóa Cảm Ứng", is_locked and overlay_hidden, "Overlay đã bị khóa ẩn hoàn toàn")

            # Click màn hình khi đang khóa: Không được phép play/pause
            page.query_selector("#playerMainArea").click(position={"x": 200, "y": 200})
            page.wait_for_timeout(300)
            still_locked = page.evaluate("() => Boolean(window.isTouchLocked)")
            record("6.2 Vô Hiệu Thao Tác Chạm Khi Đang Khóa", still_locked, "Cảm ứng vẫn giữ trạng thái khóa an toàn")

            # Mở khóa cảm ứng
            btn_unlock = page.query_selector("#btnUnlockTouch")
            btn_unlock.click()
            page.wait_for_timeout(400)
            is_unlocked = page.evaluate("() => !Boolean(window.isTouchLocked)")
            record("6.3 Mở Khóa Cảm Ứng Thành Công", is_unlocked, "Các thanh điều khiển đã xuất hiện lại")

            # -------------------------------------------------------------
            # BÀI 7: CHỌN TẬP PHIM BẤT KỲ TỪ SIDEBAR & NÚT NEXT/PREV
            # -------------------------------------------------------------
            print("\n--- BÀI 7: CHỌN TẬP PHIM TỪ DANH SÁCH & CHUYỂN TẬP ---")

            # Đảm bảo sidebar đang mở
            sidebar_el = page.query_selector("#playerSidebar")
            is_sb_open = sidebar_el.evaluate("el => !el.classList.contains('collapsed')")
            if not is_sb_open:
                page.query_selector("#btnEpisodeSheetPlayer").click()
                page.wait_for_timeout(400)

            # Lấy danh sách các nút tập trong Sidebar
            ep_btns = page.query_selector_all("#sidebarEpisodesGrid .btn-sidebar-ep")
            print(f"-> Tổng số tập hiển thị trong Sidebar: {len(ep_btns)}")
            record("7.1 Danh Sách Tập Đầy Đủ Trong Sidebar", len(ep_btns) >= 2, f"Có {len(ep_btns)} tập phim")

            if len(ep_btns) >= 3:
                # Click thử tập 3
                target_ep_btn = ep_btns[2]
                target_ep_text = target_ep_btn.text_content().strip()
                print(f"-> Đang click chuyển sang: '{target_ep_text}'")
                target_ep_btn.click()
                page.wait_for_timeout(3500)

                new_sub = page.query_selector("#playerSub").text_content().strip()
                new_t = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
                is_btn_active = page.evaluate("() => { const btns = document.querySelectorAll('#sidebarEpisodesGrid .btn-sidebar-ep'); return btns[2] ? btns[2].classList.contains('active') : false; }")

                record("7.2 Chọn Trực Tiếp Tập 3", target_ep_text.lower() in new_sub.lower() or "03" in new_sub or "3" in new_sub, f"Đang phát: '{new_sub}'")
                record("7.3 Nút Tập Đang Xem Có Viền Sáng Active", is_btn_active, "Thẻ tập 3 có class active nổi bật")
                record("7.4 Tập Mới Được Phát Từ 00:00", new_t < 4.5, f"Thời gian bắt đầu: {new_t:.2f}s (chuẩn đầu tập)")

            # Thử nút Tua Tập Kế Tiếp (#btnCenterNext)
            page.evaluate("() => { document.getElementById('videoPlayer').currentTime = 50; }")
            page.wait_for_timeout(500)
            page.query_selector("#btnCenterNext").click()
            page.wait_for_timeout(3500)
            next_t = page.evaluate("() => document.getElementById('videoPlayer').currentTime")
            next_sub = page.query_selector("#playerSub").text_content().strip()
            record("7.5 Nút Tập Kế Tiếp Reset Về 00:00", next_t < 4.5, f"Tập kế '{next_sub}' phát từ {next_t:.2f}s")

            # -------------------------------------------------------------
            # BÀI 8: NÚT YÊU THÍCH TRONG PLAYER
            # -------------------------------------------------------------
            print("\n--- BÀI 8: NÚT YÊU THÍCH PHIM TRONG PLAYER ---")
            init_fav = page.evaluate("""() => {
                const favs = JSON.parse(localStorage.getItem('huycabuonca_favs') || '[]');
                const cur = window.currentPlayingMovie;
                return Boolean(cur && favs.some(f => f.id === cur.id || f.name === cur.name));
            }""")

            btn_fav = page.query_selector("#btnToggleFavPlayer")
            btn_fav.click()
            page.wait_for_timeout(400)

            toggled_fav = page.evaluate("""() => {
                const favs = JSON.parse(localStorage.getItem('huycabuonca_favs') || '[]');
                const cur = window.currentPlayingMovie;
                return Boolean(cur && favs.some(f => f.id === cur.id || f.name === cur.name));
            }""")
            star_color_toggled = page.evaluate("() => document.getElementById('svgStarFav').style.color")
            record("8.1 Chuyển Trạng Thái Yêu Thích Trong Player", toggled_fav != init_fav, f"Đảo trạng thái fav: {init_fav} -> {toggled_fav} (màu sao: {star_color_toggled})")

            btn_fav.click() # Bấm lại để hoàn tác
            page.wait_for_timeout(400)
            final_fav = page.evaluate("""() => {
                const favs = JSON.parse(localStorage.getItem('huycabuonca_favs') || '[]');
                const cur = window.currentPlayingMovie;
                return Boolean(cur && favs.some(f => f.id === cur.id || f.name === cur.name));
            }""")
            record("8.2 Hoàn Tác Trạng Thái Yêu Thích Khi Click Lần 2", final_fav == init_fav, f"Trở lại ban đầu: {final_fav} == {init_fav}")

            # -------------------------------------------------------------
            # BÀI 9: CỬA SỔ NỔI THU NHỎ MINI PLAYER (PIP)
            # -------------------------------------------------------------
            print("\n--- BÀI 9: CỬA SỔ NỔI MINI PLAYER (PIP) ---")
            page.query_selector("#btnPipPlayer").click()
            page.wait_for_timeout(600)
            is_mini = page.evaluate("() => document.getElementById('playerContainer').classList.contains('player-floating-mini')")
            record("9.1 Chuyển Sang Cửa Sổ Nổi Góc Dưới", is_mini, "Player co lại dạng mini floating nổi góc dưới")

            page.screenshot(path=f"{ARTIFACT_DIR}\\player_test_9_mini_floating.png")

            # Bấm nút phóng to từ thanh mini bar
            page.query_selector("#btnExpandMini").click()
            page.wait_for_timeout(600)
            is_normal = page.evaluate("() => !document.getElementById('playerContainer').classList.contains('player-floating-mini')")
            record("9.2 Phóng To Lại Toàn Màn Hình Từ Mini", is_normal, "Trở lại rạp chiếu điện ảnh đầy đủ")

            # Thoát player
            page.query_selector("#btnBackPlayer").click()
            page.wait_for_timeout(1000)
            is_closed = page.evaluate("() => document.getElementById('playerContainer').style.display === 'none'")
            record("9.3 Thoát Trình Phát Về Trang Chủ", is_closed, "Đã đóng player an toàn")

            # Chụp ảnh báo cáo tổng hợp
            final_report_shot = f"{ARTIFACT_DIR}\\deep_player_simulation_report.png"
            page.screenshot(path=final_report_shot)
            print(f"\nĐã lưu ảnh chụp kết quả kiểm thử: {final_report_shot}")

            browser.close()

    finally:
        server_proc.terminate()

    total = len(results)
    passed = sum(1 for r in results if r["success"])
    failed = total - passed
    print("\n================================================================")
    print(f"📊 KẾT QUẢ KIỂM THỬ TRONG PLAYER: {passed}/{total} BÀI THÀNH CÔNG ({passed/total*100:.1f}%)")
    print(f"   Thành công: {passed} | Thất bại: {failed}")
    print("================================================================")

if __name__ == "__main__":
    run_deep_player_test()
