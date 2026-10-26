import asyncio
import os
import sys
from playwright.async_api import async_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        await page.goto("https://huyca.pages.dev", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Bấm nguồn PHIM NGẮN
        await page.click('#srcPhimNgan')
        await page.wait_for_timeout(3500)

        # 2. Bấm vào card phim đầu tiên
        first_card = page.locator('#mainGrid .movie-card').first
        await first_card.click()
        await page.wait_for_timeout(2500)

        # Chụp ảnh modal chi tiết
        modal_snap = os.path.join(ARTIFACT_DIR, "live_proof_short_drama_detail_modal.png")
        await page.screenshot(path=modal_snap)
        print("-> Đã chụp ảnh Modal chi tiết:", modal_snap)

        # 3. Bấm nút Phát Tập 1 (btnPlayFirst)
        await page.click('#btnPlayFirst')
        await page.wait_for_timeout(5000)

        # Chụp ảnh Video Player
        player_snap = os.path.join(ARTIFACT_DIR, "live_proof_short_drama_player_active.png")
        await page.screenshot(path=player_snap)
        print("-> Đã chụp ảnh Video Player:", player_snap)

        # 4. Kiểm tra trạng thái video
        v_state = await page.evaluate("""() => {
            const v = document.getElementById('videoPlayer');
            return {
                src: v ? v.src : '',
                paused: v ? v.paused : true,
                currentTime: v ? v.currentTime : 0,
                duration: v ? v.duration : 0,
                readyState: v ? v.readyState : 0,
                networkState: v ? v.networkState : 0
            };
        }""")
        print("Trạng thái video element:", v_state)

        print("\nCác log console trong khi phát:")
        for log in console_logs[-15:]:
            print("  ", log)

        await browser.close()

asyncio.run(main())
