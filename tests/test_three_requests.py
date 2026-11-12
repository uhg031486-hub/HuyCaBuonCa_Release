import asyncio
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        await page.goto("http://localhost:8098/index.html")

        # ======================================================================
        # TEST 1: Phim dài ở phút 21:25 (cur = 1285s)
        # 1. Nút #btnSubtitlePos PHẢI ẨN (vì phim dài hardsub)
        # 2. Nút #btnSkipIntro PHẢI ẨN (vì đã xem quá 3 phút = 180s)
        # ======================================================================
        print("\n=== TEST 1: PHIM DÀI Ở PHÚT 21:25 ===")
        test1_res = await page.evaluate("""() => {
            const playerCont = document.getElementById('playerContainer');
            playerCont.style.display = 'block';
            playerCont.classList.remove('player-vertical-mode');
            
            // Giả lập phim dài phút 21:25
            const video = document.getElementById('videoPlayer');
            Object.defineProperty(video, 'duration', { value: 3016, configurable: true });
            Object.defineProperty(video, 'currentTime', { value: 1285, configurable: true });
            
            // Kích hoạt timeupdate
            video.dispatchEvent(new Event('timeupdate'));

            // Phim dài không có soft sub -> gọi cập nhật visibility
            if (window.updateSubtitlePosVisibility) {
                window.updateSubtitlePosVisibility(false, false);
            }

            const btnSubPos = document.getElementById('btnSubtitlePos');
            const btnSkip = document.getElementById('btnSkipIntro');
            
            const isSubPosHidden = !btnSubPos || window.getComputedStyle(btnSubPos).display === 'none';
            const isSkipHidden = !btnSkip || window.getComputedStyle(btnSkip).display === 'none';

            return {
                btnSubPosExists: !!btnSubPos,
                subPosDisplay: btnSubPos ? window.getComputedStyle(btnSubPos).display : 'none',
                skipDisplay: btnSkip ? window.getComputedStyle(btnSkip).display : 'none',
                isSubPosHidden,
                isSkipHidden
            };
        }""")

        print(f"  btnSubtitlePos display: {test1_res['subPosDisplay']}")
        print(f"  btnSkipIntro display:   {test1_res['skipDisplay']}")
        assert test1_res["isSubPosHidden"], "LỖI: Nút chỉnh phụ đề vẫn hiện trên phim dài!"
        assert test1_res["isSkipHidden"], "LỖI: Nút Bỏ qua Intro vẫn hiện khi đã xem quá 3 phút!"
        print("  => PASS TEST 1: Phim dài phút 21:25 ẩn hoàn toàn cả nút phụ đề lẫn nút Bỏ qua Intro!")

        # ======================================================================
        # TEST 2: Phim ngắn có softsub
        # Nút #btnSubtitlePos PHẢI HIỆN (vì là phim ngắn có softsub)
        # Đổi nấc vị trí Vừa / Cao / Thấp hoạt động tốt
        # ======================================================================
        print("\n=== TEST 2: PHIM NGẮN CÓ SOFT SUBTITLE ===")
        test2_res = await page.evaluate("""() => {
            const playerCont = document.getElementById('playerContainer');
            playerCont.classList.add('player-vertical-mode');
            
            // Cập nhật visibility: hasSoftSub=true, isShort=true
            if (window.updateSubtitlePosVisibility) {
                window.updateSubtitlePosVisibility(true, true);
            }

            const btnSubPos = document.getElementById('btnSubtitlePos');
            return {
                subPosDisplay: btnSubPos ? window.getComputedStyle(btnSubPos).display : 'none'
            };
        }""")
        print(f"  btnSubtitlePos display: {test2_res['subPosDisplay']}")
        assert test2_res["subPosDisplay"] in ["flex", "inline-flex"], "LỖI: Nút chỉnh phụ đề không hiện trên phim ngắn có softsub!"

        # Thử click nút phụ đề để đổi nấc
        btn_sub_pos = await page.query_selector("#btnSubtitlePos")
        await btn_sub_pos.click()
        level_high = await page.evaluate("() => localStorage.getItem('huyca_short_sub_level')")
        assert level_high == "high", f"LỖI: Không chuyển được sang nấc high, đang là {level_high}"
        print(f"  => Click đổi nấc: {level_high}")
        print("  => PASS TEST 2: Nút phụ đề hiện chuẩn trên phim ngắn và chuyển nấc vị trí tốt!")

        # ======================================================================
        # TEST 3: Toàn màn hình sạch popup (Pure Window Fullscreen)
        # Nhấn nút Fullscreen -> Tràn 100% cửa sổ, không gọi native fullscreen (không có popup Esc)
        # Nhấn phím Escape -> Tự động thoát toàn màn hình
        # ======================================================================
        print("\n=== TEST 3: TOÀN MÀN HÌNH KHÔNG HIỆN POPUP ESC ===")
        test3_res = await page.evaluate("""() => {
            const btnFs = document.getElementById('btnFullscreen');
            const container = document.getElementById('playerContainer');
            
            if (btnFs) btnFs.click();
            
            const isWindowFs = container.classList.contains('player-window-fullscreen');
            const hasNativeFs = !!document.fullscreenElement;

            return {
                isWindowFs,
                hasNativeFs
            };
        }""")
        print(f"  isWindowFullscreen: {test3_res['isWindowFs']}")
        print(f"  hasNativeFullscreen (popup trigger): {test3_res['hasNativeFs']}")
        assert test3_res["isWindowFs"], "LỖI: Không bật được chế độ player-window-fullscreen!"
        assert not test3_res["hasNativeFs"], "LỖI: Vẫn gọi HTML5 native fullscreen gây hiện popup của Chrome!"

        # Chụp ảnh nghiệm thu chế độ toàn màn hình sạch
        await page.screenshot(path="tests/clean_fullscreen.png")

        # Thử nhấn phím Escape trên bàn phím
        await page.keyboard.press("Escape")
        is_exited = await page.evaluate("""() => {
            const container = document.getElementById('playerContainer');
            return !container.classList.contains('player-window-fullscreen');
        }""")
        assert is_exited, "LỖI: Nhấn phím Escape không thoát được toàn màn hình!"
        print("  => Phím Escape thoát toàn màn hình mượt mà!")
        print("  => PASS TEST 3: Toàn màn hình sạch không một popup Esc phiền toái!")

        await browser.close()
        print("\n=== TOÀN BỘ 3 YÊU CẦU ĐỀU ĐẠT CHUẨN 100% (PASS GREEN GATE) ===")
        return 0

if __name__ == "__main__":
    code = asyncio.run(run_test())
    sys.exit(code)
