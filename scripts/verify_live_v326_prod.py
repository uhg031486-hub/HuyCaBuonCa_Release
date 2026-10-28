import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== KIỂM THỬ XÁC MINH TOÀN DIỆN TRÊN PRODUCTION LIVE (v3.2.6) ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        console_errors = []
        proxy_fallbacks = []
        page.on("console", lambda m: console_errors.append(f"[{m.type}] {m.text}"))
        page.on("console", lambda m: proxy_fallbacks.append(m.text) if "proxy fallback" in m.text else None)

        print("1. Truy cập https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Kiểm tra thẻ script app.js có đúng v=3.2.6
        script_src = await page.locator("script[src*='app.js']").get_attribute("src")
        print(f"Script app.js version: {script_src}")
        assert "3.2.6" in script_src, f"LỖI: Chưa cập nhật script sang v3.2.6! (Hiện tại: {script_src})"

        # 2. Tìm kiếm phim Nguồn C
        print("2. Tìm kiếm 'nhu y truyen'...")
        await page.locator("#btnSearch").click()
        await page.wait_for_timeout(500)
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(3000)

        card = page.locator("#searchResultsGrid .movie-card").first
        await card.click()

        # Đợi modal tải xong chi tiết và hiển thị nút Xem Trực Tiếp
        print("Đợi nút '↗️ XEM TRỰC TIẾP' xuất hiện trong modal...")
        direct_btn = page.locator("#btnDirectPlayDetail")
        await direct_btn.wait_for(state="visible", timeout=10000)
        has_direct_btn = await direct_btn.is_visible()
        print(f"Nút '↗️ XEM TRỰC TIẾP' trong Modal: {has_direct_btn}")
        assert has_direct_btn, "LỖI: Nút '↗️ XEM TRỰC TIẾP' chưa xuất hiện trên modal!"

        # Chụp ảnh modal chi tiết
        await page.screenshot(path="scripts/live_prod_v326_detail_modal.png")
        print("Đã lưu ảnh: scripts/live_prod_v326_detail_modal.png")

        # 3. Mở Tập 1
        print("3. Bấm Tập 1...")
        ep1 = page.locator("#episodesGrid .btn-episode").first
        await ep1.click()
        await page.wait_for_timeout(4000)

        # Kiểm tra Embed Helper Toolbar
        popout_btn = page.locator("#btnPopoutPlayer")
        tab_btn = page.locator("#btnOpenEmbedNewTab")
        switch_btn = page.locator("#btnSwitchEmbedMirror")
        reload_btn = page.locator("#btnReloadEmbed")

        assert await popout_btn.is_visible(), "LỖI: Thiếu nút Pop-out Player!"
        assert await tab_btn.is_visible(), "LỖI: Thiếu nút Mở Tab Mới!"
        assert await switch_btn.is_visible(), "LỖI: Thiếu nút Đổi Server!"
        assert await reload_btn.is_visible(), "LỖI: Thiếu nút Tải Lại!"
        print("✓ Toàn bộ Embed Toolbar (Đổi Server, Cửa Sổ Riêng, Mở Tab Mới, Tải Lại) hiển thị xuất sắc!")

        # Kiểm tra proxy fallback rác & toast lỗi
        print(f"Số lượng log proxy fallback rác: {len(proxy_fallbacks)}")
        assert len(proxy_fallbacks) == 0, f"LỖI: Vẫn còn log proxy fallback rác: {proxy_fallbacks}"

        toast_el = page.locator("#toast")
        toast_visible = await toast_el.is_visible() if await toast_el.count() > 0 else False
        toast_text = await toast_el.inner_text() if toast_visible else ""
        print(f"Toast hiển thị: {toast_visible}, Nội dung: '{toast_text}'")
        assert not (toast_visible and "Không thể tải" in toast_text), "LỖI: Vẫn xuất hiện toast báo lỗi sai!"

        # Chụp ảnh Player Tập 1
        await page.screenshot(path="scripts/live_prod_v326_ep1_player.png")
        print("Đã lưu ảnh Player Tập 1: scripts/live_prod_v326_ep1_player.png")

        # 4. Thử tính năng Đổi Server
        print("4. Bấm Đổi Server sang Server dự phòng...")
        src_1 = await page.locator("#playerIframe").get_attribute("src")
        await switch_btn.click()
        await page.wait_for_timeout(1500)
        src_2 = await page.locator("#playerIframe").get_attribute("src")
        print(f"  Domain trước: {src_1.split('/')[2]}")
        print(f"  Domain sau:   {src_2.split('/')[2]}")
        assert src_1 != src_2, "LỖI: Đổi server không thay đổi domain iframe!"

        # Chụp ảnh sau khi đổi server
        await page.screenshot(path="scripts/live_prod_v326_switched_server.png")
        print("Đã lưu ảnh: scripts/live_prod_v326_switched_server.png")

        # 5. Thử chuyển sang Tập 40 từ Sidebar
        print("5. Chọn Tập 40...")
        side_ep40 = page.locator("#sidebarEpisodesGrid .btn-episode").nth(39)
        if await side_ep40.count() > 0:
            await side_ep40.click()
            await page.wait_for_timeout(3000)
            src_ep40 = await page.locator("#playerIframe").get_attribute("src")
            print(f"Iframe Tập 40 src: {src_ep40}")
            await page.screenshot(path="scripts/live_prod_v326_ep40_player.png")
            print("Đã lưu ảnh: scripts/live_prod_v326_ep40_player.png")

        print("\n🎉 TOÀN BỘ KIỂM THỬ TRÊN PRODUCTION HOÀN TOÀN THÀNH CÔNG (EXIT CODE = 0)!")
        await browser.close()
        return 0

if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(code)
