import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== BẮT ĐẦU KIỂM THỬ GIẢI PHÁP PHÁT PHIM NGUỒN C ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--autoplay-policy=no-user-gesture-required'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        # Tiêm script parent helper vào mọi trang
        await context.add_init_script("""
            window.addEventListener('message', (e) => {
                if (e.data && e.data.type === 'stream-guard-hello') {
                    console.log('[Parent] Nhận stream-guard-hello, phản hồi stream-parent-state...');
                    const frames = document.querySelectorAll('iframe');
                    frames.forEach(fr => {
                        try {
                            fr.contentWindow.postMessage({
                                type: 'stream-parent-state',
                                version: 'guard-5',
                                id: e.data.id,
                                helperVersion: 'guard-5',
                                parentAdblock: 'clear',
                                seq: Date.now(),
                                supported: true,
                                suspected: false
                            }, '*');
                        } catch(err) {}
                    });
                }
            });
        """)

        page = await context.new_page()

        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        print("1. Mở trang https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Mở phim Hậu Cung Như Ý Truyện
        print("2. Tìm kiếm 'nhu y truyen'...")
        await page.locator("#btnSearch").click()
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(3000)

        await page.locator("#searchResultsGrid .movie-card").first.click()
        await page.wait_for_timeout(2000)

        # Bấm Tập 1
        print("3. Bấm phát Tập 1...")
        ep1 = page.locator("#episodesGrid .btn-episode").first
        await ep1.click()

        print("4. Đợi trình phát nạp và kiểm tra trạng thái video...")
        await page.wait_for_timeout(10000)

        # Khảo sát iframe
        target_frame = None
        for f in page.frames:
            if "streamc" in f.url:
                target_frame = f
                break

        if target_frame:
            print(f"✅ Tìm thấy iframe: {target_frame.url}")
            
            # Kiểm tra lỗi trong iframe
            verif_err = await target_frame.evaluate("""() => {
                const el = document.getElementById('verification');
                return {
                    visible: el && !el.hidden && el.classList.contains('is-error'),
                    msg: document.getElementById('verification-message')?.textContent || ''
                };
            }""")
            print(f"Trạng thái verification trong iframe: {verif_err}")

            # Kiểm tra JWPlayer hoặc Video element
            player_state = await target_frame.evaluate("""() => {
                const vid = document.querySelector('video');
                const jw = (typeof window.jwplayer === 'function') ? window.jwplayer() : null;
                return {
                    hasVideo: !!vid,
                    currentTime: vid ? vid.currentTime : 0,
                    paused: vid ? vid.paused : true,
                    duration: vid ? vid.duration : 0,
                    jwState: jw && jw.getState ? jw.getState() : 'no_jw',
                    guardStatus: window.streamGuard ? window.streamGuard.status() : null
                };
            }""")
            print(f"Chi tiết trình phát trong iframe: {player_state}")

            # Chụp ảnh iframe
            await page.screenshot(path="scripts/test_solution_player.png")
            print("Đã chụp ảnh màn hình lưu vào scripts/test_solution_player.png")
        else:
            print("❌ Không tìm thấy iframe streamc!")

        print("\n--- NHẬT KÝ CONSOLE (MỚI NHẤT) ---")
        for log in console_logs[-15:]:
            print(log)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
