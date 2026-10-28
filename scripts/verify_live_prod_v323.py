import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import time
from playwright.sync_api import sync_playwright

def verify_live_prod_v323():
    print("=" * 70)
    print("🌐 KIỂM THỬ TRỰC TIẾP TRÊN PRODUCTION LIVE: https://huyca.pages.dev")
    print("=" * 70)

    screenshots_dir = os.path.abspath('C:/Users/yoga/.gemini/antigravity/brain/ac3633cf-7ca4-4342-a8fb-2d22c7872b1b')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            accept_downloads=True
        )
        page = context.new_page()

        downloads = []
        page.on("download", lambda d: downloads.append(d.suggested_filename))

        # 1. Truy cập production live
        print("1. Đang truy cập https://huyca.pages.dev ...")
        page.goto("https://huyca.pages.dev", wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # 2. Chuyển sang Tab Xem Tivi
        print("2. Chuyển sang Tab Xem Tivi...")
        page.locator("#srcXemTiVi").click()
        time.sleep(2)

        # 3. Mở kênh BBC World News
        print("3. Bấm mở kênh BBC World News...")
        play_res = page.evaluate("""() => {
            const all = window.TV_CHANNELS || window.INITIAL_TV_CHANNELS || [];
            const bbc = all.find(c => c.name && c.name.toLowerCase().includes('bbc world news'));
            if (bbc) {
                window.playTvChannelDirectly(bbc);
                return { ok: true, name: bbc.name, url: bbc.url };
            }
            return { ok: false };
        }""")
        print(f"   Kết quả: {play_res}")
        assert play_res['ok'] == True, "Không tìm thấy kênh BBC World News trên Live"

        # Đợi buffer 5s
        time.sleep(5)

        # 4. Kiểm tra popup download
        print(f"4. Kiểm tra popup download: {len(downloads)} file")
        if len(downloads) > 0:
            print(f"❌ THẤT BẠI: Vẫn bị trigger download file {downloads}")
        else:
            print("✅ XUẤT SẮC: Hoàn toàn KHÔNG bị tải file manifest.mpd!")

        assert len(downloads) == 0, f"Không được tải file! Bị: {downloads}"

        # 5. Kiểm tra trạng thái Video Player trên Live
        player_state = page.evaluate("""() => {
            const video = document.getElementById('videoPlayer');
            const iframe = document.getElementById('playerIframe');
            return {
                videoVisible: video && video.style.display !== 'none',
                videoReadyState: video ? video.readyState : 0,
                videoPaused: video ? video.paused : true,
                iframeVisible: iframe && iframe.style.display !== 'none',
                title: document.getElementById('playerTitle')?.textContent || ''
            };
        }""")
        print(f"5. Trạng thái Live Player: {player_state}")
        assert player_state['videoVisible'] == True, "Video element phải hiển thị"
        assert player_state['iframeVisible'] == False, "Iframe phải ẩn hoàn toàn"
        assert 'BBC' in player_state['title']

        # Chụp ảnh chứng minh
        snap_live = os.path.join(screenshots_dir, 'live_prod_v323_bbc_world_news.png')
        page.screenshot(path=snap_live)
        print(f"📸 Đã lưu ảnh chụp Live Production: {snap_live}")

        browser.close()

    print("\n" + "=" * 70)
    print("🎉 KIỂM THỬ PRODUCTION LIVE V3.2.3 ĐẠT 100% THÀNH CÔNG!")
    print("=" * 70)

if __name__ == '__main__':
    verify_live_prod_v323()
