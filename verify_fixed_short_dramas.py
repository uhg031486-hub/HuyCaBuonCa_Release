import asyncio
import os
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
LIVE_URL = "https://huyca.pages.dev"

async def main():
    print("Bắt đầu kiểm thử live nguồn Phim Ngắn trên Cloudflare Pages:", LIVE_URL)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        await page.goto(LIVE_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # 1. Bấm nút nguồn PHIM NGẮN
        btn_phim_ngan = page.locator('#srcPhimNgan')
        await btn_phim_ngan.click()
        await page.wait_for_timeout(4000)

        snap1 = os.path.join(ARTIFACT_DIR, "live_proof_short_drama_reelshort_fixed.png")
        await page.screenshot(path=snap1)
        print(f"-> Đã chụp ảnh tab ReelShort: {snap1}")

        # Lấy danh sách phim hiển thị trong #mainGrid
        titles = await page.locator('#mainGrid .card-title, #mainGrid .movie-title, #mainGrid .card-info h3, #mainGrid .card').all_text_contents()
        card_count = await page.locator('#mainGrid .card').count()
        print(f"Số lượng card phim tải được trong tab ReelShort: {card_count}")
        if card_count > 0:
            first_title = await page.locator('#mainGrid .card').first.text_content()
            print(f"Thông tin card đầu tiên:\n{first_title.strip()[:100]}")

        # 2. Bấm sang tab AI Cinema
        btn_ai = page.locator("button.btn-filter:has-text('AI Cinema')")
        if await btn_ai.is_visible():
            await btn_ai.click()
            await page.wait_for_timeout(3000)
            snap2 = os.path.join(ARTIFACT_DIR, "live_proof_short_drama_ai_cinema_fixed.png")
            await page.screenshot(path=snap2)
            print(f"-> Đã chụp ảnh tab AI Cinema: {snap2}")
            ai_card_count = await page.locator('#mainGrid .card').count()
            print(f"Số lượng card phim AI Cinema: {ai_card_count}")

        # 3. Bấm mở 1 phim để kiểm tra phát video
        first_card = page.locator('#mainGrid .card').first
        if await first_card.is_visible():
            await first_card.click()
            await page.wait_for_timeout(2500)

            # Bấm Phát Tập 1
            btn_play = page.locator('#btnPlayFirst')
            if await btn_play.is_visible():
                await btn_play.click()
                await page.wait_for_timeout(4500)

                # Chụp player
                snap3 = os.path.join(ARTIFACT_DIR, "live_proof_short_drama_video_playing.png")
                await page.screenshot(path=snap3)
                print(f"-> Đã chụp ảnh Player video đang phát: {snap3}")

                # Kiểm tra trạng thái video player
                video_status = await page.evaluate("""() => {
                    const v = document.getElementById('videoPlayer');
                    return {
                        src: v ? v.src : '',
                        paused: v ? v.paused : true,
                        currentTime: v ? v.currentTime : 0,
                        duration: v ? v.duration : 0,
                        readyState: v ? v.readyState : 0
                    };
                }""")
                print("Trạng thái video element:", video_status)

        await browser.close()

asyncio.run(main())
