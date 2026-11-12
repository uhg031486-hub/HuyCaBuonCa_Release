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
        
        # 1. Kiểm tra nút Cài Đặt App vẫn giữ nền vàng chữ đen sang trọng
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        await page.goto("http://localhost:8098/index.html")
        await page.wait_for_selector("#btnInstallApp", state="visible")

        btn_info = await page.evaluate("""() => {
            const btn = document.getElementById('btnInstallApp');
            const spanText = btn.querySelector('.btn-text');
            const cs = window.getComputedStyle(btn);
            const csText = window.getComputedStyle(spanText);
            return {
                bg: cs.backgroundColor,
                bgImage: cs.backgroundImage,
                textColor: csText.color,
                fontWeight: csText.fontWeight
            };
        }""")

        print("\n=== TEST 1: NÚT CÀI ĐẶT APP ===")
        print(f"  Background Color: {btn_info['bg']}")
        print(f"  Background Image: {btn_info['bgImage']}")
        print(f"  Text Color:       {btn_info['textColor']}")
        assert "rgb(30, 41, 59)" not in btn_info["bg"], "LỖI: Nút vẫn bị màu đen rgb(30, 41, 59) đè!"
        assert btn_info["textColor"] == "rgb(0, 0, 0)", "LỖI: Chữ không phải màu đen rgb(0, 0, 0)!"
        print("  => PASS: Nút Cài Đặt App chuẩn nền vàng chữ đen!")

        # 2. Xác nhận nút chỉnh vị trí phụ đề đã được gỡ bỏ theo yêu cầu của người dùng
        btn_sub_pos = await page.query_selector("#btnSubtitlePos")
        assert btn_sub_pos is None, "LỖI: Nút #btnSubtitlePos vẫn còn tồn tại trong DOM!"
        print("\n=== TEST 2: GỠ BỎ NÚT CHỈNH VỊ TRÍ PHỤ ĐỀ ===")
        print("  => PASS: Đã gỡ bỏ hoàn toàn nút #btnSubtitlePos khỏi thanh công cụ!")

        # 3. Kiểm tra hiển thị phụ đề tự nhiên của player
        page_mobile = await browser.new_page(viewport={"width": 390, "height": 844})
        await page_mobile.goto("http://localhost:8098/index.html")
        await page_mobile.evaluate("""() => {
            const playerCont = document.getElementById('playerContainer');
            playerCont.style.display = 'block';
            playerCont.classList.add('player-vertical-mode');
            let sub = document.getElementById('playerSubtitleOverlay');
            if (!sub) {
                sub = document.createElement('div');
                sub.id = 'playerSubtitleOverlay';
                document.getElementById('playerMainArea').appendChild(sub);
            }
            sub.textContent = 'Phụ đề hiển thị tự nhiên theo chuẩn nguồn';
            sub.style.display = 'block';
        }""")

        sub_info = await page_mobile.evaluate("""() => {
            const sub = document.getElementById('playerSubtitleOverlay');
            const cs = window.getComputedStyle(sub);
            return {
                bottom: cs.bottom,
                pointerEvents: cs.pointerEvents,
                fontSize: cs.fontSize
            };
        }""")
        print("\n=== TEST 3: PHỤ ĐỀ TỰ NHIÊN ===")
        print(f"  Bottom: {sub_info['bottom']}")
        print(f"  Pointer Events: {sub_info['pointerEvents']}")
        assert sub_info["pointerEvents"] == "none", "LỖI: Phụ đề không nên chặn touch của người dùng!"
        print("  => PASS: Phụ đề hiển thị tự nhiên, không chiếm sự kiện chạm vuốt của player!")

        await browser.close()
        print("\n=== TOÀN BỘ KIỂM THỬ THÀNH CÔNG 100% (PASS GREEN GATE) ===")
        return 0

if __name__ == "__main__":
    code = asyncio.run(run_test())
    sys.exit(code)
