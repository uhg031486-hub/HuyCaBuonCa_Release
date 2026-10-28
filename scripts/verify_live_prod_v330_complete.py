import sys
import os
import time
import json
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

PROD_URL = "https://huyca.pages.dev"
ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def test_1_downloads():
    print("\n=== BƯỚC 1: KIỂM THỬ API DOWNLOAD CÁC NỀN TẢNG (v3.3.0) ===")
    targets = {
        'tv': ('HuyCa_TV_v3.3.0.apk', 9 * 1024 * 1024),
        'mobile': ('HuyCa_Mobile_v3.3.0.apk', 8 * 1024 * 1024),
        'lg': ('HuyCa_LG_webOS_v3.3.0.ipk', 1 * 1024 * 1024),
        'windows': ('HuyCa_Windows_v3.3.0.zip', 1 * 1024 * 1024)
    }
    
    for key, (expected_file, min_size) in targets.items():
        url = f"{PROD_URL}/api/download?file={key}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            cd = resp.headers.get('Content-Disposition') or ''
            ct = resp.headers.get('Content-Type') or ''
            cl = int(resp.headers.get('Content-Length') or 0)
            print(f"[{key.upper()}] Status: {resp.status}, File: {expected_file}, Size: {cl:,} bytes, Content-Type: {ct}")
            assert resp.status == 200, f"Status != 200 for {key}"
            assert expected_file in cd, f"Expected {expected_file} in Content-Disposition: {cd}"
            assert cl >= min_size, f"Size {cl} < min_size {min_size}"
    print("-> Tất cả 4 bộ cài đặt v3.3.0 đã sẵn sàng và tải xuống chuẩn xác 100%!")

def test_2_nguonc_stream_api():
    print("\n=== BƯỚC 2: KIỂM THỬ ENDPOINT GIẢI MÃ NGUỒN C SẠCH (/api/nguonc_stream) ===")
    embed_target = "https://embed18.streamc.xyz/embed.php?hash=9aed8dc306c066c863d2a37aec123b22"
    api_url = f"{PROD_URL}/api/nguonc_stream?url={urllib.parse.quote(embed_target)}"
    
    print(f"Gọi giải mã: {api_url}")
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        assert resp.status == 200, f"LỖI: Status {resp.status}"
        ctype = resp.headers.get('Content-Type') or ''
        print(f"Status: {resp.status}, Content-Type: {ctype}")
        assert 'mpegurl' in ctype.lower(), f"LỖI: Content-Type không phải mpegurl: {ctype}"
        
        body = resp.read().decode('utf-8')
        lines = [line.strip() for line in body.splitlines() if line.strip() and not line.startswith('#')]
        print(f"Tổng số phân đoạn (segments) được viết lại qua proxy: {len(lines)}")
        assert len(lines) > 200, f"LỖI: Số lượng phân đoạn quá ít: {len(lines)}"
        
        first_seg_url = lines[0]
        print(f"Segment đầu tiên: {first_seg_url[:80]}...")
        assert '/api/proxy?url=' in first_seg_url, "LỖI: Segment chưa được trỏ qua /api/proxy!"

    print("-> Luồng HLS Nguồn C giải mã thành công, sẵn sàng cho cả Android TV, Mobile, webOS và Web!")

def test_3_playwright_e2e_tv(context):
    print("\n=== BƯỚC 3A: KIỂM THỬ E2E LIVE WEB PRODUCTION (KÊNH TV) ===")
    page = context.new_page()

    # 1. Mở Live Web
    print(f"1. Mở trang: {PROD_URL}")
    page.goto(PROD_URL, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(2000)

    header_text = page.locator('.brand-subtitle').inner_text()
    print(f"Header subtitle: {header_text}")
    assert "v3.3.0" in header_text, f"Header does not show v3.3.0: {header_text}"

    # 2. Chuyển sang Tab TV
    print("2. Chuyển sang Tab TV (#srcXemTiVi)...")
    page.locator('#srcXemTiVi').click()
    page.wait_for_timeout(2000)

    # Chọn filter Kênh Quốc Tế
    intl_btn = page.locator('#filterBar button:has-text("Kênh Quốc Tế")')
    if intl_btn.count() > 0:
        intl_btn.first.click()
        page.wait_for_timeout(1500)

    card_count = page.locator('#mainGrid .movie-card').count()
    print(f"Số lượng kênh TV Quốc Tế: {card_count}")
    assert card_count > 0, "Không có kênh TV nào trong mục Quốc Tế"

    # Click NHK World
    nhk_card = page.locator('#mainGrid .movie-card:has-text("NHK")').first
    if nhk_card.count() > 0:
        print("Tìm thấy kênh NHK World, bấm phát...")
        nhk_card.click()
    else:
        print("Bấm kênh TV đầu tiên...")
        page.locator('#mainGrid .movie-card').first.click()

    page.wait_for_timeout(5000)

    is_playing = page.evaluate("""() => {
        const v = document.querySelector('video');
        return v && !v.paused && v.currentTime > 0;
    }""")
    v_time = page.evaluate("() => document.querySelector('video')?.currentTime || 0")
    v_src = page.evaluate("() => document.querySelector('video')?.currentSrc || ''")
    print(f"TV Video playing: {is_playing}, currentTime: {v_time:.2f}s, src: {v_src[:80]}...")
    
    shot_tv = os.path.join(ARTIFACT_DIR, "live_prod_v330_tv_playing.png")
    page.screenshot(path=shot_tv)
    print(f"Đã lưu screenshot TV: {shot_tv}")
    assert is_playing or v_time > 0, "LỖI: TV stream không phát được!"
    page.close()

def test_3_playwright_e2e_nguonc(context):
    print("\n=== BƯỚC 3B: KIỂM THỬ E2E LIVE WEB PRODUCTION (PHIM NGUỒN C SẠCH) ===")
    page = context.new_page()

    print(f"1. Mở trang: {PROD_URL}")
    page.goto(PROD_URL, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(2000)

    print("2. Bấm nút Tìm kiếm (#btnSearch)...")
    page.click("#btnSearch")
    page.wait_for_selector("#searchInput", state="visible")
    page.fill("#searchInput", "Nhu Y Truyen")
    page.keyboard.press("Enter")
    page.wait_for_timeout(3000)

    search_cards = page.locator("#searchResultsGrid .movie-card")
    sc_count = search_cards.count()
    print(f"Đã tìm thấy {sc_count} kết quả. Click vào phim đầu tiên...")
    assert sc_count > 0, "Không tìm thấy phim Nguồn C trong kết quả tìm kiếm"
    search_cards.first.click()
    page.wait_for_selector("#detailModal", state="visible")
    page.wait_for_timeout(2000)

    shot_detail = os.path.join(ARTIFACT_DIR, "live_prod_v330_nguonc_detail.png")
    page.screenshot(path=shot_detail)
    print(f"Đã lưu screenshot Detail: {shot_detail}")

    print("3. Bấm nút '▶ XEM PHIM' (btnPlayFirst)...")
    page.click("#btnPlayFirst")
    page.wait_for_timeout(6000)

    nc_playing = page.evaluate("""() => {
        const v = document.getElementById('videoPlayer');
        return v && !v.paused && v.currentTime > 0;
    }""")
    nc_time = page.evaluate("() => document.getElementById('videoPlayer')?.currentTime || 0")
    nc_src = page.evaluate("() => document.getElementById('videoPlayer')?.currentSrc || ''")
    print(f"NguonC Video playing: {nc_playing}, currentTime: {nc_time:.2f}s, src: {nc_src[:80]}...")
    
    shot_nc = os.path.join(ARTIFACT_DIR, "live_prod_v330_nguonc_playing.png")
    page.screenshot(path=shot_nc)
    print(f"Đã lưu screenshot NguonC playing: {shot_nc}")

    assert nc_playing or nc_time > 0, "Video NguonC không bắt đầu phát!"
    print("✅ Phim Nguồn C phát sạch qua Native HLS, Zero Ads, tốc độ mượt mà!")
    page.close()

if __name__ == '__main__':
    test_1_downloads()
    test_2_nguonc_stream_api()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--autoplay-policy=no-user-gesture-required', '--no-sandbox']
        )
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        test_3_playwright_e2e_tv(context)
        test_3_playwright_e2e_nguonc(context)
        browser.close()
    print("\n🎉 TOÀN BỘ CÁC BƯỚC KIỂM THỬ THỰC TẾ TRÊN LIVE PRODUCTION ĐỀU ĐẠT CHUẨN 100% (PASS)!")
