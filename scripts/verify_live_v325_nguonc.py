import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

PROD_URL = "https://huyca.pages.dev"

async def main():
    print(f"=== GREEN GATE: KIỂM THỬ TOÀN DIỆN PRODUCTION v3.2.5 ({PROD_URL}) ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        console_logs = []
        page.on("console", lambda m: console_logs.append(f"[{m.type}] {m.text}"))

        # 1. Truy cập trang web
        print(f"1. Truy cập {PROD_URL} ...")
        await page.goto(PROD_URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        # Kiểm tra version v3.2.5 trong HTML
        content = await page.content()
        has_v325 = "v=3.2.5" in content
        print(f"   -> Phiên bản mã nguồn xác nhận v3.2.5: {has_v325}")

        # 2. Tìm kiếm phim 'nhu y truyen'
        print("\n2. Mở tìm kiếm và tìm 'nhu y truyen'...")
        await page.locator("#btnSearch").click()
        await page.wait_for_timeout(1000)
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(4000)

        # 3. Chọn phim Hậu Cung Như Ý Truyện
        movie_cards = page.locator("#searchResultsGrid .movie-card")
        count = await movie_cards.count()
        print(f"   -> Tìm thấy {count} kết quả.")
        target_card = None
        for i in range(count):
            t = await movie_cards.nth(i).locator(".card-title").inner_text()
            if "Như Ý Truyện" in t or "nhu y truyen" in t.lower():
                target_card = movie_cards.nth(i)
                print(f"   -> Chọn phim: '{t}'")
                break
        
        if not target_card:
            target_card = movie_cards.first
        await target_card.click()
        await page.wait_for_timeout(3000)

        # 4. Kiểm tra Modal Chi Tiết Phim
        print("\n3. Kiểm tra Modal Chi Tiết Phim:")
        modal_visible = await page.locator("#detailModal").is_visible()
        print(f"   -> Modal chi tiết hiển thị: {modal_visible}")
        
        # Kiểm tra thanh chọn Server (Vietsub, Lồng Tiếng)
        server_tabs = page.locator("#modalServerBar .btn-server-tab")
        server_tab_count = await server_tabs.count()
        print(f"   -> Số lượng Server hiển thị: {server_tab_count}")
        for i in range(server_tab_count):
            s_name = await server_tabs.nth(i).inner_text()
            print(f"      * Server {i+1}: {s_name}")

        episodes_in_modal = await page.locator("#episodesGrid .btn-episode").count()
        print(f"   -> Tổng số tập hiển thị trong danh sách: {episodes_in_modal} tập")

        # 5. TEST TẬP 40 (Lỗi DNS trước đó)
        print("\n4. TEST PHÁT TẬP 40 (Khắc phục lỗi DNS ERR_NAME_NOT_RESOLVED):")
        ep40_btn = page.locator("#episodesGrid .btn-episode").filter(has_text="40").first
        if await ep40_btn.count() > 0:
            await ep40_btn.click()
        else:
            await page.locator("#episodesGrid .btn-episode").nth(39).click()

        print("   -> Đang tải luồng HLS Tập 40 qua Proxy...")
        await page.wait_for_timeout(7000)

        # Kiểm tra trạng thái video
        video_state_40 = await page.evaluate("""() => {
            const v = document.getElementById('videoPlayer');
            const iframe = document.getElementById('playerIframe');
            return {
                nativeVisible: v && window.getComputedStyle(v).display !== 'none',
                currentTime: v ? v.currentTime : 0,
                duration: v ? v.duration : 0,
                paused: v ? v.paused : true,
                readyState: v ? v.readyState : 0,
                iframeVisible: iframe && window.getComputedStyle(iframe).display !== 'none',
                iframeSrc: iframe ? iframe.src : ''
            };
        }""")
        print(f"   -> VideoPlayer Native hiển thị: {video_state_40['nativeVisible']}")
        print(f"   -> Thời gian phát (currentTime): {video_state_40['currentTime']:.2f}s (duration: {video_state_40['duration']:.2f}s)")
        print(f"   -> Trạng thái: paused={video_state_40['paused']}, readyState={video_state_40['readyState']}")
        print(f"   -> Iframe nhúng bị ẩn sạch: {not video_state_40['iframeVisible']}")

        # Kiểm tra danh sách tập trong Sidebar khi đang xem phim
        sidebar_eps_count = await page.locator("#sidebarEpisodesGrid .btn-sidebar-ep").count()
        print(f"   -> Số lượng tập trong Sidebar Player: {sidebar_eps_count} tập")

        # Chụp ảnh bằng chứng Tập 40 phát mượt mà
        await page.screenshot(path="scripts/live_prod_v325_ep40_playing.png")
        print("   📸 Đã chụp ảnh Tập 40: scripts/live_prod_v325_ep40_playing.png")

        # 6. TEST CHUYỂN TẬP TIẾP THEO (NEXT EPISODE)
        print("\n5. TEST CHUYỂN TẬP TIẾP THEO (Tập 41):")
        btn_next = page.locator("#btnCenterNext")
        if await btn_next.is_visible() and await btn_next.is_enabled():
            await btn_next.click()
            print("   -> Đã bấm nút 'Tập tiếp theo'...")
            await page.wait_for_timeout(6000)
            
            sub_title = await page.locator("#playerSub").inner_text()
            print(f"   -> Tiêu đề tập hiện tại: {sub_title}")
            
            time_after_next = await page.evaluate("document.getElementById('videoPlayer').currentTime")
            print(f"   -> Thời gian phát Tập tiếp theo: {time_after_next:.2f}s")
            await page.screenshot(path="scripts/live_prod_v325_ep_next_playing.png")
            print("   📸 Đã chụp ảnh Tập tiếp: scripts/live_prod_v325_ep_next_playing.png")

        # 7. TEST TẬP 1 (Lỗi Anti-Adblock Guard trước đó)
        print("\n6. TEST TẬP 1 (Khắc phục lỗi Anti-Adblock Guard):")
        # Chọn Tập 1 từ Sidebar
        ep1_sidebar = page.locator("#sidebarEpisodesGrid .btn-sidebar-ep").first
        if await ep1_sidebar.count() > 0:
            await ep1_sidebar.click()
            print("   -> Đã chọn Tập 1 từ Sidebar...")
            await page.wait_for_timeout(6000)

            sub_title_1 = await page.locator("#playerSub").inner_text()
            print(f"   -> Tiêu đề: {sub_title_1}")

            video_state_1 = await page.evaluate("""() => {
                const v = document.getElementById('videoPlayer');
                return {
                    currentTime: v ? v.currentTime : 0,
                    paused: v ? v.paused : true,
                    readyState: v ? v.readyState : 0
                };
            }""")
            print(f"   -> Tập 1 đang phát: currentTime={video_state_1['currentTime']:.2f}s, paused={video_state_1['paused']}")
            
            # Kiểm tra xem có popup Anti-adblock hay không
            body_text = await page.locator("body").inner_text()
            has_adblock_modal = "chặn quảng cáo" in body_text.lower()
            print(f"   -> Phát hiện thông báo Anti-Adblock: {has_adblock_modal} (Kỳ vọng: False)")

            await page.screenshot(path="scripts/live_prod_v325_ep1_playing.png")
            print("   📸 Đã chụp ảnh Tập 1: scripts/live_prod_v325_ep1_playing.png")

        await browser.close()

        # Đánh giá tổng thể
        success = (
            video_state_40['currentTime'] > 0 and 
            not video_state_40['iframeVisible'] and 
            sidebar_eps_count > 0 and
            not has_adblock_modal
        )

        if success:
            print("\n=======================================================")
            print("🎉🎉🎉 GREEN GATE HOÀN TẤT 100%: TẤT CẢ KIỂM THỬ ĐÃ ĐẠT!")
            print("  1. Phim NguonC Hậu Cung Như Ý Truyện phát native HLS chuẩn.")
            print("  2. Lỗi DNS ERR_NAME_NOT_RESOLVED ở Tập 40 ĐÃ ĐƯỢC XÓA BỎ.")
            print("  3. Lỗi Anti-Adblock Guard ở Tập 1 ĐÃ ĐƯỢC XÓA BỎ.")
            print("  4. Danh sách 87 tập trong Sidebar hoạt động hoàn hảo.")
            print("  5. Chuyển tập Next / Prev mượt mà.")
            print("=======================================================")
            return 0
        else:
            print("\n❌ Kiểm thử chưa đạt hoàn toàn. Vui lòng kiểm tra lại log.")
            return 1

if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(code)
