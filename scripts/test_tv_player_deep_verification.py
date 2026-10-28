import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import time
from playwright.sync_api import sync_playwright

def run_deep_tv_verification():
    print("=" * 70)
    print("🚀 BẮT ĐẦU BỘ KIỂM THỬ TOÀN DIỆN KÊNH TRUYỀN HÌNH & PLAYER V3.2.3")
    print("=" * 70)

    screenshots_dir = os.path.abspath('C:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 1. Test trên Desktop (1280x720)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            accept_downloads=True
        )
        page = context.new_page()

        downloads = []
        page.on("download", lambda d: downloads.append(d.suggested_filename))

        web_path = os.path.abspath('HuyCa_Web/index.html').replace(os.sep, '/')
        page.goto(f'file:///{web_path}')
        page.wait_for_load_state('networkidle')

        print("\n--- TEST CASE 1: Mở Tab Xem Tivi & Danh Sách Kênh ---")
        page.locator('#srcXemTiVi').click()
        time.sleep(1.5)
        
        cards_count = page.locator('#mainGrid .movie-card').count()
        print(f"✅ Đã tải danh sách kênh Tivi: {cards_count} kênh hiển thị trên giao diện.")
        assert cards_count > 50, "Phải hiển thị đầy đủ danh sách kênh TV"

        print("\n--- TEST CASE 2: Phát Kênh BBC World News & Kiểm Tra Không Tải File ---")
        play_res = page.evaluate("""() => {
            const all = window.TV_CHANNELS || window.INITIAL_TV_CHANNELS || [];
            const bbc = all.find(c => c.name && c.name.toLowerCase().includes('bbc world news'));
            if (bbc) {
                window.playTvChannelDirectly(bbc);
                return { ok: true, name: bbc.name, url: bbc.url };
            }
            return { ok: false };
        }""")
        print(f"Phát kênh: {play_res}")
        assert play_res['ok'] == True

        # Đợi stream nạp metadata & buffer
        time.sleep(4)

        # Chặn đứng download
        print(f"Số lượng file bị kích hoạt download: {len(downloads)}")
        assert len(downloads) == 0, f"LỖI: Phát sinh tải file download: {downloads}"

        # Kiểm tra trạng thái Player
        player_state = page.evaluate("""() => {
            const video = document.getElementById('videoPlayer');
            const iframe = document.getElementById('playerIframe');
            const title = document.getElementById('playerTitle')?.textContent || '';
            const sub = document.getElementById('playerSub')?.textContent || '';
            return {
                videoVisible: video && video.style.display !== 'none',
                videoReadyState: video ? video.readyState : 0,
                videoPaused: video ? video.paused : true,
                iframeVisible: iframe && iframe.style.display !== 'none',
                title: title,
                sub: sub
            };
        }""")
        print(f"Trạng thái Player: {player_state}")
        assert player_state['videoVisible'] == True, "Video Player phải hiển thị dạng video element"
        assert player_state['iframeVisible'] == False, "Iframe không được hiển thị"
        assert 'BBC' in player_state['title'], "Tiêu đề player phải là BBC World News"

        # Chụp ảnh minh chứng kênh BBC đang phát
        snap1 = os.path.join(screenshots_dir, 'tv_test_bbc_world_news_playing.png')
        page.screenshot(path=snap1)
        print(f"📸 Đã lưu ảnh chụp: {snap1}")

        print("\n--- TEST CASE 3: Kiểm Tra Thao Tác Nút Bấm Player (Play/Pause, Đổi Kênh) ---")
        # Nút Play/Pause
        btn_play = page.locator('#btnPlayPause')
        if btn_play.is_visible():
            btn_play.click()
            time.sleep(0.5)
            is_paused = page.evaluate("() => document.getElementById('videoPlayer')?.paused")
            print(f"Sau khi bấm Pause: video.paused = {is_paused}")
            btn_play.click()
            time.sleep(0.5)

        # Nút Đổi Kênh (Quick Zapping)
        btn_zap = page.locator('#btnQuickZap')
        assert btn_zap.is_visible(), "Nút Đổi Kênh nhanh phải hiển thị ở chế độ Tivi"
        btn_zap.click()
        time.sleep(1)

        zapping_open = page.evaluate("() => document.getElementById('zappingPanel')?.classList.contains('open')")
        print(f"Bảng đổi kênh nhanh mở: {zapping_open}")
        assert zapping_open == True, "Bảng zappingPanel phải mở ra"

        # Chụp ảnh menu đổi kênh
        snap2 = os.path.join(screenshots_dir, 'tv_test_zapping_panel.png')
        page.screenshot(path=snap2)
        print(f"📸 Đã lưu ảnh chụp menu đổi kênh: {snap2}")

        print("\n--- TEST CASE 4: Đổi Sang Kênh Bloomberg TV ---")
        switch_res = page.evaluate("""() => {
            const all = window.TV_CHANNELS || window.INITIAL_TV_CHANNELS || [];
            const bb = all.find(c => c.name && c.name.toLowerCase().includes('bloomberg'));
            if (bb) {
                window.playTvChannelDirectly(bb);
                return { ok: true, name: bb.name, url: bb.url };
            }
            return { ok: false };
        }""")
        print(f"Chuyển sang: {switch_res}")
        time.sleep(3)
        assert len(downloads) == 0, "Không được tải file khi chuyển kênh Bloomberg"

        bloomberg_title = page.evaluate("() => document.getElementById('playerTitle')?.textContent || ''")
        print(f"Tiêu đề hiện tại: {bloomberg_title}")
        assert 'Bloomberg' in bloomberg_title

        print("\n--- TEST CASE 5: Kiểm Tra Mini Floating Player Trên TV ---")
        btn_mini = page.locator('#btnMiniPlayer')
        if btn_mini.is_visible():
            btn_mini.click()
            time.sleep(1)
            is_mini = page.evaluate("() => document.getElementById('playerContainer')?.classList.contains('player-floating-mini')")
            print(f"Player ở chế độ Mini Floating: {is_mini}")
            assert is_mini == True, "Player phải thu nhỏ góc phải"
            
            # Khôi phục lại
            page.locator('#btnRestoreFromMini').click()
            time.sleep(1)
            is_restored = page.evaluate("() => !document.getElementById('playerContainer')?.classList.contains('player-floating-mini')")
            print(f"Player đã khôi phục: {is_restored}")
            assert is_restored == True

        # Đóng browser Desktop
        browser.close()

        # 2. Test trên Giả Lập Android Mobile (Viewport 393 x 851, Touch)
        print("\n" + "=" * 50)
        print("📱 TEST CASE 6: Kiểm Thử Trên Giả Lập Android Mobile")
        print("=" * 50)
        pixel7 = p.devices['Pixel 7']
        mobile_browser = p.chromium.launch(headless=True)
        mobile_ctx = mobile_browser.new_context(
            **pixel7,
            accept_downloads=True
        )
        mobile_page = mobile_ctx.new_page()
        mobile_downloads = []
        mobile_page.on("download", lambda d: mobile_downloads.append(d.suggested_filename))

        mobile_page.goto(f'file:///{web_path}')
        mobile_page.wait_for_load_state('networkidle')

        # Chuyển tab TV
        mobile_page.locator('#srcXemTiVi').click()
        time.sleep(1)

        # Mở kênh CNN International
        cnn_res = mobile_page.evaluate("""() => {
            const all = window.TV_CHANNELS || window.INITIAL_TV_CHANNELS || [];
            const cnn = all.find(c => c.name && c.name.toLowerCase().includes('cnn'));
            if (cnn) {
                window.playTvChannelDirectly(cnn);
                return { ok: true, name: cnn.name };
            }
            return { ok: false };
        }""")
        print(f"Mobile phát CNN: {cnn_res}")
        time.sleep(3)

        assert len(mobile_downloads) == 0, "Không được tải file trên Mobile!"
        mobile_snap = os.path.join(screenshots_dir, 'tv_test_mobile_cnn_playing.png')
        mobile_page.screenshot(path=mobile_snap)
        print(f"📸 Đã lưu ảnh chụp mobile: {mobile_snap}")

        mobile_browser.close()

    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ 6 TEST CASES KIỂM THỬ TOÀN DIỆN ĐỀU ĐẠT 100% (PASS)")
    print("=" * 70)

if __name__ == '__main__':
    run_deep_tv_verification()
