import asyncio
from playwright.async_api import async_playwright
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== GREEN FEEDBACK LOOP: KIỂM THỬ LOCAL v3.2.6 ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-web-security']
        )
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})

        console_errors = []
        proxy_fallbacks = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("console", lambda m: proxy_fallbacks.append(m.text) if "proxy fallback" in m.text else None)

        file_url = f"file:///{os.path.abspath('HuyCa_Web/index.html').replace(os.sep, '/')}"
        print(f"1. Mở file cục bộ: {file_url} ...")
        await page.goto(file_url, wait_until="load")
        await page.wait_for_timeout(2000)

        # 2. Tìm kiếm và mở phim Hậu Cung Như Ý Truyện
        print("2. Tìm kiếm phim Nguồn C (Như Ý Truyện)...")
        await page.locator("#btnSearch").click()
        await page.wait_for_timeout(500)
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(3000)

        card = page.locator("#searchResultsGrid .movie-card").first
        await card.click()
        await page.wait_for_timeout(2000)

        # Kiểm tra nút Xem Trực Tiếp trong Modal
        direct_btn = page.locator("#btnDirectPlayDetail")
        has_direct_btn = await direct_btn.is_visible()
        print(f"Nút Xem Trực Tiếp trong Modal hiển thị: {has_direct_btn}")
        assert has_direct_btn, "LỖI: Nút Direct Play trong Modal chưa hiển thị!"

        # Chụp ảnh modal chi tiết
        await page.screenshot(path="scripts/local_v326_detail_modal.png")
        print("Đã lưu ảnh modal chi tiết: scripts/local_v326_detail_modal.png")

        # 3. Bấm Tập 1 để mở Player
        print("3. Bấm Tập 1 để kiểm tra Player...")
        ep1 = page.locator("#episodesGrid .btn-episode").first
        await ep1.click()
        await page.wait_for_timeout(4000)

        # Kiểm tra Embed Helper Toolbar
        popout_btn = page.locator("#btnPopoutPlayer")
        has_popout = await popout_btn.is_visible()
        print(f"Nút Pop-out Player hiển thị: {has_popout}")
        assert has_popout, "LỖI: Nút Popout Player chưa hiển thị!"

        tab_btn = page.locator("#btnOpenEmbedNewTab")
        has_tab = await tab_btn.is_visible()
        print(f"Nút Mở Tab Mới hiển thị: {has_tab}")
        assert has_tab, "LỖI: Nút Mở Tab Mới chưa hiển thị!"

        switch_btn = page.locator("#btnSwitchEmbedMirror")
        has_switch = await switch_btn.is_visible()
        print(f"Nút Đổi Server hiển thị: {has_switch}")
        assert has_switch, "LỖI: Nút Đổi Server chưa hiển thị!"

        # Kiểm tra proxy fallback rác
        print(f"Proxy fallback logs count: {len(proxy_fallbacks)}")
        assert len(proxy_fallbacks) == 0, f"LỖI: Vẫn còn log proxy fallback rác: {proxy_fallbacks}"

        # Chụp ảnh Player
        await page.screenshot(path="scripts/local_v326_player.png")
        print("Đã lưu ảnh Player: scripts/local_v326_player.png")

        # Thử bấm Đổi Server
        print("4. Thử bấm Đổi Server Embed...")
        iframe_before = await page.locator("#playerIframe").get_attribute("src")
        await switch_btn.click()
        await page.wait_for_timeout(1000)
        iframe_after = await page.locator("#playerIframe").get_attribute("src")
        print(f"  Iframe trước: {iframe_before}")
        print(f"  Iframe sau:   {iframe_after}")
        assert iframe_before != iframe_after, "LỖI: Đổi server không đổi URL iframe!"

        print("\n✅ KIỂM THỬ LOCAL GREEN HOÀN TOÀN THÀNH CÔNG (100% PASS)!")
        await browser.close()
        return 0

if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(code)
