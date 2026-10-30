import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== RED GATE: Kiểm tra lỗi hiện tại trên https://huyca.pages.dev ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("1. Mở trang https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # 2. Bấm nút Tìm Kiếm
        print("2. Mở hộp thoại Tìm Kiếm...")
        await page.locator("#btnSearch").click()
        await page.wait_for_timeout(1000)

        # 3. Nhập từ khóa 'nhu y truyen'
        print("3. Nhập từ khóa 'nhu y truyen'...")
        search_input = page.locator("#searchInput")
        await search_input.fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(4000)

        # 4. Tìm và click vào phim Hậu Cung Như Ý Truyện
        movie_cards = page.locator("#searchResultsGrid .movie-card")
        count = await movie_cards.count()
        print(f"4. Tìm thấy {count} kết quả phim.")
        if count == 0:
            print("❌ Không tìm thấy phim trong kết quả tìm kiếm.")
            await page.screenshot(path="scripts/red_gate_search_empty.png")
            await browser.close()
            return 1

        # Lọc đúng thẻ phim chứa 'Như Ý Truyện'
        target_card = None
        for i in range(count):
            c = movie_cards.nth(i)
            t = await c.locator(".card-title").inner_text()
            if "Như Ý Truyện" in t or "nhu y truyen" in t.lower():
                target_card = c
                print(f"   Chọn phim: '{t}'")
                break

        if not target_card:
            target_card = movie_cards.first

        await target_card.click()
        await page.wait_for_timeout(3000)

        # 5. Kiểm tra danh sách tập trong modal
        ep_count = await page.locator("#episodesGrid .btn-episode").count()
        print(f"5. Số lượng tập hiển thị trong Modal chi tiết: {ep_count}")

        # 6. Click Tập 40 (hoặc tập đầu tiên)
        ep40 = page.locator("#episodesGrid .btn-episode").filter(has_text="40").first
        if await ep40.count() > 0:
            print("6. Bấm chọn Tập 40...")
            await ep40.click()
        else:
            print("6. Bấm nút Tập đầu tiên...")
            await page.locator("#btnPlayFirst").click()

        await page.wait_for_timeout(6000)

        # 7. Kiểm tra trạng thái phát video
        has_video = await page.evaluate("""() => {
            const v = document.getElementById('videoPlayer');
            return v && !v.paused && v.currentTime > 0;
        }""")
        print(f"7. Trình phát native videoPlayer đang chạy: {has_video}")

        # 8. Kiểm tra iframe
        iframe = page.locator("#playerIframe")
        iframe_visible = await iframe.is_visible()
        iframe_src = await iframe.get_attribute("src") if iframe_visible else "None"
        print(f"8. Iframe nhúng hiển thị: {iframe_visible}, src: {iframe_src}")

        # 9. Kiểm tra sidebar episodes
        sidebar_eps = await page.locator("#sidebarEpisodesGrid .btn-sidebar-ep").count()
        print(f"9. Số tập trong Sidebar khi đang phát: {sidebar_eps}")

        await page.screenshot(path="scripts/red_gate_current_failure.png")
        print("📸 Đã lưu ảnh chụp Red Gate tại scripts/red_gate_current_failure.png")

        await browser.close()

        # Đánh giá: Trên bản v3.2.4 hiện tại, phim NguonC bị đẩy vào iframe chứa domain streamc.xyz (không native) và sidebar không có tập!
        if not has_video or sidebar_eps == 0 or iframe_visible:
            print("\n❌ [RED GATE CONFIRMED] Xác nhận lỗi trên phiên bản v3.2.4 hiện tại:")
            print(f"   - Phim phát qua native player: {has_video} (Kỳ vọng: True)")
            print(f"   - Phim bị nhúng iframe ngoài: {iframe_visible} (Kỳ vọng: False - nhúng iframe ngoài bị lỗi DNS & Anti-Adblock)")
            print(f"   - Số tập sidebar: {sidebar_eps} (Kỳ vọng: > 0)")
            return 0  # Trả về 0 cho script test để xác nhận Red Gate đã thành công bắt lỗi
        else:
            print("\n⚠️ Không phát hiện lỗi.")
            return 1

if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(code)
