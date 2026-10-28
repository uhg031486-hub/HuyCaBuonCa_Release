import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== KIỂM THỬ THỰC TẾ TRÊN PRODUCTION LIVE: CHẶN 100% QUẢNG CÁO NGUỒN C (v3.2.7) ===")
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

        # Chỉ bắt các popup mới phát sinh sau khi trang chính đã mở
        ad_popups = []
        context.on("page", lambda new_pg: ad_popups.append(new_pg) if new_pg != page else None)

        print("1. Mở trang Production https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # 2. Kiểm tra thuộc tính Sandbox trên playerIframe
        iframe_el = page.locator("#playerIframe")
        sandbox_attr = await iframe_el.get_attribute("sandbox")
        print(f"Thuộc tính Sandbox của #playerIframe: '{sandbox_attr}'")
        assert sandbox_attr is not None, "LỖI: Chưa có thuộc tính sandbox trên #playerIframe!"
        assert "allow-popups" not in sandbox_attr, "LỖI: Thuộc tính sandbox vẫn chứa allow-popups!"
        assert "allow-top-navigation" not in sandbox_attr, "LỖI: Thuộc tính sandbox vẫn chứa allow-top-navigation!"
        print("✓ Thuộc tính Sandbox chặn hoàn toàn Popups và Top Navigation thành công!")

        # 3. Tìm kiếm và mở phim Hậu Cung Như Ý Truyện
        print("3. Tìm kiếm 'nhu y truyen'...")
        await page.locator("#btnSearch").click()
        await page.wait_for_timeout(500)
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(3000)

        card = page.locator("#searchResultsGrid .movie-card").first
        await card.click()

        direct_btn = page.locator("#btnDirectPlayDetail")
        await direct_btn.wait_for(state="visible", timeout=10000)
        print("✓ Nút Xem Trực Tiếp trong Modal hiển thị sẵn sàng!")

        # 4. Bấm Tập 1
        print("4. Bấm mở Tập 1...")
        await page.locator("#episodesGrid .btn-episode").first.click()
        await page.wait_for_timeout(4000)

        # 5. Thử nghiệm click liên tục 10 lần vào vùng Player để kiểm tra chặn quảng cáo
        print("5. Click liên tục 10 lần vào màn hình Player để kiểm tra chặn quảng cáo...")
        for i in range(10):
            # Click vào nhiều vị trí khác nhau trong khung player
            click_x = 400 + (i % 5) * 100
            click_y = 250 + (i % 3) * 100
            await page.mouse.click(click_x, click_y)
            await page.wait_for_timeout(500)

        print(f"\n=> KẾT QUẢ KIỂM THỬ BẢO VỆ AD-SHIELD:")
        print(f"   Tổng số trang popup quảng cáo bị mở ra: {len(ad_popups)} (Yêu cầu bắt buộc = 0)")
        assert len(ad_popups) == 0, f"LỖI: Vẫn có {len(ad_popups)} trang popup quảng cáo bị mở ra: {[p.url for p in ad_popups]}"
        print("✓ CHẶN ĐỨNG HOÀN TOÀN 100% CÁC POPUP QUẢNG CÁO & CỜ BẠC!")

        # Kiểm tra trang chính không bị chuyển hướng
        current_url = page.url
        print(f"   URL trang chính: {current_url}")
        assert "huyca.pages.dev" in current_url, f"LỖI: Trang chính bị chuyển hướng sang: {current_url}"
        print("✓ Trang chính duy trì bảo mật tuyệt đối, không bị chuyển hướng!")

        # Chụp ảnh bằng chứng
        shot_path = "scripts/live_prod_v327_adshield_success.png"
        await page.screenshot(path=shot_path)
        print(f"✓ Đã chụp ảnh lưu bằng chứng: {shot_path}")

        print("\n🎉 KIỂM THỬ PRODUCTION LIVE v3.2.7 XÁC MINH CHẶN QUẢNG CÁO THÀNH CÔNG RỰC RỠ (EXIT CODE = 0)!")
        await browser.close()
        return 0

if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(code)
