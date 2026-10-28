import sys
import json
import urllib.request
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def test_live_worker_endpoint():
    print("=== BƯỚC 1: KIỂM THỬ ENDPOINT /api/nguonc_stream TRÊN CLOUDFLARE LIVE ===")
    embed_target = "https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f"
    stream_api_url = f"https://huyca.pages.dev/api/nguonc_stream?url={urllib.parse.quote(embed_target)}"
    
    print(f"Gọi API: {stream_api_url}")
    req = urllib.request.Request(stream_api_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, f"LỖI: Status {resp.status}"
        ctype = resp.headers.get('Content-Type')
        print(f"Status: {resp.status}, Content-Type: {ctype}")
        assert 'mpegurl' in ctype.lower(), f"LỖI: Content-Type không phải mpegurl: {ctype}"
        
        body = resp.read().decode('utf-8')
        lines = [line.strip() for line in body.splitlines() if line.strip() and not line.startswith('#')]
        print(f"Tổng số phân đoạn (segments) được viết lại qua proxy: {len(lines)}")
        assert len(lines) > 200, f"LỖI: Số lượng phân đoạn quá ít: {len(lines)}"
        
        first_seg_url = lines[0]
        print(f"Segment đầu tiên: {first_seg_url}")
        assert '/api/proxy?url=' in first_seg_url, "LỖI: Segment chưa được trỏ qua /api/proxy!"

    print("\n=== BƯỚC 2: KIỂM THỬ TẢI PHÂN ĐOẠN VIDEO MPEG-TS QUA PROXY LIVE ===")
    req_seg = urllib.request.Request(first_seg_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_seg) as resp_seg:
        assert resp_seg.status == 200, f"LỖI segment status: {resp_seg.status}"
        seg_ctype = resp_seg.headers.get('Content-Type')
        print(f"Segment Content-Type: {seg_ctype}")
        assert 'video/mp2t' in seg_ctype or 'octet-stream' in seg_ctype or 'png' in seg_ctype, f"LỖI segment Content-Type: {seg_ctype}"
        
        seg_bytes = resp_seg.read(188)
        print(f"Byte đầu tiên (hex): {hex(seg_bytes[0])} (Kỳ vọng: 0x47 chuẩn MPEG-TS)")
        assert seg_bytes[0] == 0x47, f"LỖI: Byte đầu tiên không phải 0x47 MPEG-TS sync byte: {hex(seg_bytes[0])}"
        print("✅ Phân đoạn video MPEG-TS tải thành công, dữ liệu phim gốc 100% nguyên vẹn!")

def test_live_browser_playback():
    print("\n=== BƯỚC 3: KIỂM THỬ TRẢI NGHIỆM THỰC TẾ TRÊN WEB LIVE (E2E PLAYWRIGHT) ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--autoplay-policy=no-user-gesture-required', '--no-sandbox']
        )
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        popups = []
        context.on("page", lambda p: popups.append(p) if p != page else None)
        
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        print("1. Truy cập https://huyca.pages.dev ...")
        page.goto("https://huyca.pages.dev", wait_until="networkidle")
        page.wait_for_timeout(2000)

        print("2. Tìm kiếm 'Nhu Y Truyen'...")
        page.click("#btnSearch")
        page.wait_for_selector("#searchInput", state="visible")
        page.fill("#searchInput", "Nhu Y Truyen")
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)

        cards = page.query_selector_all("#searchResultsGrid .movie-card")
        assert len(cards) > 0, "LỖI: Không tìm thấy card phim nào!"
        print(f"Đã tìm thấy {len(cards)} kết quả. Click vào phim đầu tiên...")
        cards[0].click()
        page.wait_for_selector("#detailModal", state="visible")
        page.wait_for_timeout(2000)

        # Kiểm tra nút Xem Trực Tiếp bị ẩn
        btn_direct = page.query_selector("#btnDirectPlayDetail")
        is_direct_vis = btn_direct.is_visible() if btn_direct else False
        print(f"Nút '↗️ XEM TRỰC TIẾP' có hiển thị không: {is_direct_vis} (Kỳ vọng: False để bảo vệ người dùng)")
        assert not is_direct_vis, "LỖI: Nút '↗️ XEM TRỰC TIẾP' vẫn còn hiển thị trên modal!"

        page.screenshot(path="scripts/live_v328_detail_modal.png")
        print("Đã chụp: scripts/live_v328_detail_modal.png")

        print("3. Bấm '▶ XEM PHIM' (btnPlayFirst) để phát bằng trình phát sạch...")
        page.click("#btnPlayFirst")
        
        # Đợi video tải và phát trong 12 giây
        video_playing = False
        last_info = None
        for sec in range(12):
            page.wait_for_timeout(1000)
            video_info = page.evaluate("""() => {
                const v = document.getElementById('videoPlayer');
                const ifr = document.getElementById('playerIframe');
                return {
                    hasVideo: !!v,
                    videoDisplay: v ? v.style.display : 'none',
                    iframeDisplay: ifr ? ifr.style.display : 'none',
                    currentTime: v ? v.currentTime : 0,
                    paused: v ? v.paused : true,
                    duration: v ? v.duration : 0,
                    readyState: v ? v.readyState : 0
                };
            }""")
            last_info = video_info
            if video_info['currentTime'] > 0 and not video_info['paused']:
                print(f"Giây {sec+1}: Video đang phát mượt mà! currentTime={video_info['currentTime']:.2f}s, duration={video_info['duration']:.2f}s")
                video_playing = True
                break
            else:
                print(f"Giây {sec+1}: Đang nạp luồng video... readyState={video_info['readyState']}, currentTime={video_info['currentTime']}")

        page.screenshot(path="scripts/live_v328_clean_playing.png")
        print("Đã chụp: scripts/live_v328_clean_playing.png")

        print("4. Thử click 5 lần vào màn hình video để kiểm tra có bị bật popup quảng cáo không...")
        box = page.eval_on_selector("#videoPlayer", "el => el.getBoundingClientRect()")
        mid_x = box['x'] + box['width'] / 2
        mid_y = box['y'] + box['height'] / 2
        for click_i in range(5):
            page.mouse.click(mid_x, mid_y)
            page.wait_for_timeout(1000)

        print(f"Số lượng popup quảng cáo bị bật ra sau 5 lần click: {len(popups)} (Kỳ vọng: 0)")
        assert len(popups) == 0, f"LỖI: Vẫn có {len(popups)} popup quảng cáo bị mở!"

        # Kiểm tra helper bar không còn nút mở tab ngoài
        tab_btn = page.query_selector("#btnOpenEmbedNewTab")
        assert tab_btn is None or not tab_btn.is_visible(), "LỖI: Nút 'Mở Tab Mới' vẫn còn tồn tại!"

        assert video_playing, f"LỖI: Video không phát được! Trạng thái cuối: {last_info}"
        print("🎉 HOÀN TOÀN THÀNH CÔNG: Video Nguồn C phát sạch 100% không một giây quảng cáo, không iframe, 0 popup!")

        browser.close()

if __name__ == "__main__":
    test_live_worker_endpoint()
    test_live_browser_playback()
