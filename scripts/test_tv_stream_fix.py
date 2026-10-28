import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import time
from playwright.sync_api import sync_playwright

def test_tv_channel_no_download_and_plays():
    print("🚀 Bắt đầu bài test kiểm thử mở kênh BBC World News và các kênh TV...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Giả lập Desktop hoặc Mobile đều không được có download popup
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            accept_downloads=True
        )
        page = context.new_page()

        # Bắt sự kiện download nếu có
        downloads_triggered = []
        page.on("download", lambda download: downloads_triggered.append(download.suggested_filename))

        # Điều hướng đến ứng dụng local web
        # Khởi động bằng file:/// hoặc localhost
        web_path = os.path.abspath('HuyCa_Web/index.html')
        page.goto(f'file:///{web_path.replace(os.sep, "/")}')
        page.wait_for_load_state('networkidle')

        print("1. Kiểm tra tải trang Huy Cà...")
        assert page.title() != "", "Trang web phải tải thành công"

        # Chuyển sang tab Truyền Hình TV
        btn_tv = page.locator('#srcTruyenHinh')
        if btn_tv.is_visible():
            btn_tv.click()
            time.sleep(1)

        # Mở modal hoặc bấm trực tiếp kênh BBC World News
        print("2. Tìm kiếm và mở kênh BBC World News...")
        # Dùng hàm JS trong trang để play kênh BBC World News trực tiếp như user click
        play_result = page.evaluate("""() => {
            const allChannels = window.TV_CHANNELS || window.INITIAL_TV_CHANNELS || [];
            const bbc = allChannels.find(c => c.name && c.name.toLowerCase().includes('bbc world news'));
            if (!bbc) return { found: false };
            
            // Bấm mở phát kênh
            if (typeof window.playTvChannelDirectly === 'function') {
                window.playTvChannelDirectly(bbc);
            } else if (typeof window.playVideo === 'function') {
                window.playVideo(bbc.url, bbc.name, 'Trực Tiếp', bbc, null, 0, 0, true);
            }
            return {
                found: true,
                channelName: bbc.name,
                url: bbc.url
            };
        }""")

        print(f"   Kết quả tìm kênh: {play_result}")
        assert play_result['found'] == True, "Phải tìm thấy kênh BBC World News trong danh sách TV"

        # Đợi 3 giây xem có download nào bị kích hoạt không
        time.sleep(3)

        # Kiểm tra download popup
        print(f"3. Kiểm tra số lượng download bị trigger: {len(downloads_triggered)}")
        if len(downloads_triggered) > 0:
            print(f"❌ THẤT BẠI: Đã kích hoạt download các file: {downloads_triggered}")
        else:
            print("✅ XUẤT SẮC: Không có bất kỳ file download nào bị kích hoạt!")

        assert len(downloads_triggered) == 0, f"Không được kích hoạt download file! Bị download: {downloads_triggered}"

        # Kiểm tra iframe src vs video src
        iframe_src = page.evaluate("() => document.getElementById('playerIframe')?.src || ''")
        video_src = page.evaluate("() => document.getElementById('videoPlayer')?.src || ''")
        iframe_display = page.evaluate("() => document.getElementById('playerIframe')?.style.display || ''")
        video_display = page.evaluate("() => document.getElementById('videoPlayer')?.style.display || ''")

        print(f"4. Trạng thái Player:")
        print(f"   - iframe_display: '{iframe_display}', iframe_src: '{iframe_src}'")
        print(f"   - video_display: '{video_display}', video_src: '{video_src}'")

        assert '.mpd' not in iframe_src, "iframe.src tuyệt đối không được gán link .mpd"
        assert iframe_display != 'block', "iframe không được hiển thị khi phát stream TV"

        browser.close()
        print("🎉 TẤT CẢ CÁC BƯỚC KIỂM THỬ BAN ĐẦU HOÀN THÀNH!")

if __name__ == '__main__':
    test_tv_channel_no_download_and_plays()
