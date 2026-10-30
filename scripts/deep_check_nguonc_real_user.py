import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== KIỂM TRA CHUYÊN SÂU: TẠI SAO NGƯỜI DÙNG KHÔNG XEM ĐƯỢC NGUỒN C ===")
    async with async_playwright() as p:
        # Launch browser without headless or with realistic arguments
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        console_errors = []
        network_fails = []
        
        page.on("console", lambda m: console_errors.append(f"[{m.type}] {m.text}"))
        page.on("requestfailed", lambda r: network_fails.append(f"FAILED: {r.method} {r.url} - {r.failure}"))

        print("1. Mở https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # Mở phim Hậu Cung Như Ý Truyện
        print("2. Tìm kiếm và mở phim Hậu Cung Như Ý Truyện...")
        await page.locator("#btnSearch").click()
        await page.wait_for_timeout(1000)
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(3000)

        card = page.locator("#searchResultsGrid .movie-card").first
        await card.click()
        await page.wait_for_timeout(2000)

        # Thử cả Tập 1 và Tập 40
        for ep_text, ep_idx in [("Tập 1", 0), ("Tập 40", 39)]:
            print(f"\n==============================================")
            print(f"👉 ĐANG THỬ NGHIỆM {ep_text}...")
            print(f"==============================================")
            
            # Chọn tập
            ep_btns = page.locator("#episodesGrid .btn-episode")
            count = await ep_btns.count()
            print(f"Tổng số nút tập: {count}")
            
            target_btn = ep_btns.filter(has_text=f"Tập {ep_idx + 1}" if ep_idx > 0 else "Tập 1").first
            if await target_btn.count() == 0:
                target_btn = ep_btns.nth(ep_idx)
            
            await target_btn.click()
            print(f"Đã click {ep_text}. Đợi 10 giây xem trình phát xử lý thế nào...")
            await page.wait_for_timeout(10000)

            # Chụp ảnh toàn màn hình player
            shot_path = f"scripts/debug_player_{ep_idx + 1}.png"
            await page.screenshot(path=shot_path)
            print(f"Đã lưu ảnh màn hình: {shot_path}")

            # Khảo sát iframe
            iframe_el = page.locator("#playerIframe")
            iframe_src = await iframe_el.get_attribute("src")
            print(f"Iframe src: {iframe_src}")

            # Tìm frame con
            target_frame = None
            for f in page.frames:
                if "streamc" in f.url or "embed" in f.url:
                    target_frame = f
                    break
            
            if target_frame:
                print(f"Tìm thấy iframe content! URL = {target_frame.url}")
                try:
                    frame_title = await target_frame.title()
                    print(f"  Frame Title: {frame_title}")
                    
                    # Chụp riêng ảnh của iframe
                    frame_shot = f"scripts/debug_iframe_{ep_idx + 1}.png"
                    frame_body = target_frame.locator("body")
                    if await frame_body.count() > 0:
                        await frame_body.screenshot(path=frame_shot)
                        print(f"  Đã chụp ảnh nội dung iframe: {frame_shot}")
                        
                        body_html = await frame_body.inner_html()
                        print(f"  Iframe HTML preview (500 chars):\n{body_html[:500]}")
                        
                        # Kiểm tra xem có popup hay thông báo gì không
                        verif = target_frame.locator("#verification")
                        if await verif.count() > 0:
                            v_text = await verif.inner_text()
                            v_hidden = await verif.is_hidden()
                            print(f"  #verification (hidden={v_hidden}): {v_text}")

                        # Kiểm tra jwplayer
                        jw_info = await target_frame.evaluate("""() => {
                            if (typeof window.jwplayer === 'function') {
                                try {
                                    const p = window.jwplayer('player') || window.jwplayer();
                                    return {
                                        loaded: true,
                                        state: p.getState ? p.getState() : 'unknown',
                                        position: p.getPosition ? p.getPosition() : 0,
                                        duration: p.getDuration ? p.getDuration() : 0,
                                        muted: p.getMute ? p.getMute() : false
                                    };
                                } catch(e) {
                                    return { loaded: true, error: e.message };
                                }
                            }
                            return { loaded: false };
                        }""")
                        print(f"  JWPlayer info: {jw_info}")

                        # Kiểm tra có thẻ video nào trong iframe không
                        videos = target_frame.locator("video")
                        v_count = await videos.count()
                        print(f"  Thẻ <video> trong iframe: {v_count}")
                        if v_count > 0:
                            v_src = await videos.first.get_attribute("src")
                            v_paused = await videos.first.evaluate("v => v.paused")
                            v_time = await videos.first.evaluate("v => v.currentTime")
                            print(f"  Thẻ video: paused={v_paused}, currentTime={v_time}, src={v_src[:80] if v_src else 'None'}")
                except Exception as e:
                    print(f"  Lỗi khi khảo sát frame: {e}")
            else:
                print("❌ KHÔNG TÌM THẤY frame NguonC nào!")

            # Mở lại modal để thử tập tiếp theo
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)

        print("\n--- TỔNG KẾT NETWORK FAILS ---")
        for fail in network_fails[:15]:
            print(fail)

        print("\n--- TỔNG KẾT CONSOLE ERRORS ---")
        for err in console_errors[:15]:
            print(err)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
