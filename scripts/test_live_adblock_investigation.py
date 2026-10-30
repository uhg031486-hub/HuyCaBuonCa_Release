import sys
import asyncio
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== ĐIỀU TRA CHI TIẾT TRẢI NGHIỆM THỰC TẾ CỦA NGƯỜI DÙNG TRÊN WEB ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        popups = []
        context.on("page", lambda p: popups.append(p))

        page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
        
        # Bắt các request quảng cáo bị trigger
        ads_requests = []
        page.on("request", lambda req: ads_requests.append(req.url) if any(kw in req.url for kw in ["ad", "banner", "pop", "shopee", "bet", "88", "track"]) else None)

        print("1. Truy cập https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        print("2. Mở Search Modal và tìm kiếm 'Nhu Y Truyen'...")
        await page.click("#btnSearch")
        await page.wait_for_selector("#searchInput", state="visible")
        await page.fill("#searchInput", "Nhu Y Truyen")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)

        # Chụp ảnh kết quả tìm kiếm
        await page.screenshot(path="scripts/live_investigate_search.png")
        print("Đã lưu: scripts/live_investigate_search.png")

        cards = await page.query_selector_all("#searchResultsGrid .movie-card")
        print(f"Số lượng phim tìm thấy trong Search Results: {len(cards)}")
        if not cards:
            print("❌ Không thấy card phim nào trong search results!")
            await browser.close()
            return

        print("3. Click vào phim đầu tiên trong search results...")
        await cards[0].click()
        await page.wait_for_selector("#detailModal", state="visible")
        await page.wait_for_timeout(2000)

        # Kiểm tra các nút trên modal
        btn_direct = await page.query_selector("#btnDirectPlayDetail")
        btn_direct_visible = await btn_direct.is_visible() if btn_direct else False
        btn_play = await page.query_selector("#btnPlayFirst")
        print(f"Nút '↗️ XEM TRỰC TIẾP' có hiển thị không: {btn_direct_visible}")
        await page.screenshot(path="scripts/live_investigate_modal.png")
        print("Đã lưu: scripts/live_investigate_modal.png")

        print("4. Bấm nút '▶ XEM PHIM' (btnPlayFirst) để phát trong web player...")
        await btn_play.click()
        await page.wait_for_timeout(4000)

        # Chụp ảnh player
        await page.screenshot(path="scripts/live_investigate_player.png")
        print("Đã lưu: scripts/live_investigate_player.png")

        # Kiểm tra iframe sandbox
        iframe_el = await page.query_selector("#playerIframe")
        sandbox_val = await iframe_el.get_attribute("sandbox") if iframe_el else None
        iframe_src = await iframe_el.get_attribute("src") if iframe_el else None
        print(f"Iframe src: {iframe_src}")
        print(f"Iframe sandbox: {sandbox_val}")

        # Kiểm tra các frame
        stream_frame = None
        for fr in page.frames:
            if "streamc" in fr.url:
                stream_frame = fr
                break
        
        print(f"Stream frame tìm thấy: {stream_frame.url if stream_frame else 'None'}")

        print("5. Thử click trực tiếp vào vùng giữa video player xem có bị popup không...")
        # Lấy bounding box của iframe
        if iframe_el:
            box = await iframe_el.bounding_box()
            if box:
                mid_x = box['x'] + box['width'] / 2
                mid_y = box['y'] + box['height'] / 2
                print(f"Clicking at ({mid_x}, {mid_y})...")
                for c in range(3):
                    await page.mouse.click(mid_x, mid_y)
                    await page.wait_for_timeout(1500)

        print(f"Tổng số popups sau khi click video trong iframe: {len(popups)}")

        # 6. Bây giờ kiểm tra nút '↗️ XEM TRỰC TIẾP' trên Modal hoặc '↗️ Mở Tab Mới' trên Toolbar!
        # Hãy xem toolbar embedHelperBar
        helper_bar = await page.query_selector("#embedHelperBar")
        helper_visible = await helper_bar.is_visible() if helper_bar else False
        print(f"Toolbar embedHelperBar có hiển thị không: {helper_visible}")

        popout_btn = await page.query_selector("#btnPopoutPlayer")
        tab_btn = await page.query_selector("#btnOpenEmbedNewTab")
        print(f"Nút Cửa Sổ Riêng có hiển thị không: {await popout_btn.is_visible() if popout_btn else False}")
        print(f"Nút Mở Tab Mới có hiển thị không: {await tab_btn.is_visible() if tab_btn else False}")
        if tab_btn:
            tab_href = await tab_btn.get_attribute("href")
            print(f"Link Mở Tab Mới là gì: {tab_href}")

        await browser.close()
        print("=== HOÀN TẤT ĐIỀU TRA ===")

if __name__ == "__main__":
    asyncio.run(main())
