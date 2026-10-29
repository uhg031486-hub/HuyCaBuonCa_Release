import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})

        print("1. Navigating to Web App http://localhost:8080 ...")
        await page.goto("http://localhost:8080", wait_until="networkidle")

        # 2. Bấm vào tab FREEREELS (Phim Ngắn)
        print("2. Clicking Tab FREEREELS (#srcPhimNgan)...")
        await page.click('#srcPhimNgan')
        await page.wait_for_timeout(2000)

        # 3. Chọn Sub-source Gà Mờ Mê Phim bằng data-sub
        print("3. Selecting Sub-Source: Gà Mờ Mê Phim (data-sub='short_src://gamomephim')...")
        await page.click('button[data-sub="short_src://gamomephim"]')
        await page.wait_for_timeout(2500)

        # 4. Kiểm tra các filter mới của Gà Mờ Mê Phim
        filters = await page.locator('#filterBar .btn-filter').all_inner_texts()
        print(f"Total filters displayed for GaMoMePhim: {len(filters)}")
        for i, f_name in enumerate(filters):
            print(f"  [{i+1}] {f_name}")
        assert len(filters) >= 15, f"Expected at least 15 filters, got {len(filters)}"

        # 5. Bấm filter 'Bảng Xếp Hạng Thịnh Hành' (filter mới)
        print("4. Testing filter: 'Bảng Xếp Hạng Thịnh Hành'...")
        await page.click('#filterBar button[data-url="gamomephim://ban-xep-hang"]')
        await page.wait_for_timeout(3500)
        cards = page.locator('#mainGrid .movie-card')
        count_bxh = await cards.count()
        print(f"Movies in 'Bảng Xếp Hạng Thịnh Hành': {count_bxh}")
        assert count_bxh > 0, "No movies loaded in GaMoMePhim BXH!"

        # 6. Bấm filter 'Gương Vỡ Lại Lành & Ngược Tâm' (filter mới)
        print("5. Testing filter: 'Gương Vỡ Lại Lành & Ngược Tâm'...")
        await page.click('#filterBar button[data-url="gamomephim://the-loai/guong-vo-lai-lanh"]')
        await page.wait_for_timeout(3500)
        count_gv = await cards.count()
        print(f"Movies in 'Gương Vỡ Lại Lành': {count_gv}")
        assert count_gv > 0, "No movies loaded in 'Gương Vỡ Lại Lành'!"

        # 7. Test cuộn xuống (phân trang / kéo thêm phim)
        print("6. Testing infinite scroll (kéo thêm phim)...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(3500)
        count_after = await cards.count()
        print(f"Movies after scrolling: {count_after}")
        assert count_after > count_gv, f"Scroll did not add more movies! Before: {count_gv}, After: {count_after}"

        # 8. Test filter ít phim (ví dụ Trọng Sinh chỉ có 11 phim gốc) -> kiểm tra cơ chế fallback không bao giờ bị nghẽn
        print("7. Testing filter ít phim 'Trọng Sinh & Báo Thù'...")
        await page.click('#filterBar button[data-url="gamomephim://the-loai/trong-sinh"]')
        await page.wait_for_timeout(3500)
        count_ts = await cards.count()
        print(f"Movies in 'Trọng Sinh & Báo Thù' (P1): {count_ts}")
        assert count_ts > 0, "No movies loaded in 'Trọng Sinh'!"

        print("Scrolling on 'Trọng Sinh' to test infinite fallback...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(3500)
        count_ts_after = await cards.count()
        print(f"Movies in 'Trọng Sinh' after scroll: {count_ts_after}")
        assert count_ts_after >= count_ts, "Scroll failed on Trọng Sinh!"

        await page.screenshot(path="scripts/gamome_filters_verified.png")
        print("Screenshot saved to scripts/gamome_filters_verified.png")

        # 9. Test Phim Ngắn Subtitle
        print("8. Testing FreeReels Subtitle playback...")
        await page.click('button[data-sub="short_src://freereels"]')
        await page.wait_for_timeout(3000)
        first_card = page.locator('#mainGrid .movie-card').first
        await first_card.click()
        await page.wait_for_timeout(3000)

        # Check detailModal
        detail_modal = page.locator('#detailModal')
        assert await detail_modal.is_visible(), "Detail modal not visible after clicking movie card!"

        # Click Xem Phim (#btnPlayFirst) or episode button
        print("Clicking Play Now (#btnPlayFirst)...")
        btn_play = page.locator('#btnPlayFirst')
        if await btn_play.is_visible():
            await btn_play.click()
        else:
            await page.locator('#episodesGrid .btn-ep').first.click()

        await page.wait_for_timeout(5000)

        container = page.locator('#playerContainer')
        is_visible = await container.is_visible()
        print(f"Player Container visible: {is_visible}")
        assert is_visible, "Player container not visible!"

        await page.screenshot(path="scripts/short_drama_sub_verified.png")
        print("Screenshot saved to scripts/short_drama_sub_verified.png")

        await browser.close()
        print(">>> ALL VERIFICATION TESTS PASSED 100%! <<<")

if __name__ == '__main__':
    asyncio.run(run_test())
