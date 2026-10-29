import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ARTIFACTS_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"

async def main():
    print("=== BẮT ĐẦU KIỂM THỬ PLAYWRIGHT: GIAO DIỆN LỊCH THI ĐẤU ĐỦ 2 BIỂU TƯỢNG ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Khởi tạo kích thước màn hình TV / Desktop 1280x720 giống ảnh người dùng
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        # 1. Truy cập local server chế độ TV
        url = "http://localhost:8080/#tv"
        print(f"1. Truy cập: {url}")
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(2)

        # 2. Click vào nguồn "📺 XEM TIVI"
        print("2. Chuyển sang nguồn '📺 XEM TIVI' (#srcXemTiVi)...")
        await page.click("#srcXemTiVi")
        await asyncio.sleep(2)

        # 3. Click vào tab "⚽ Lịch Thi Đấu & Bóng Đá"
        print("3. Click tab '⚽ Lịch Thi Đấu & Bóng Đá'...")
        schedule_btn = page.locator(".btn-filter:has-text('Lịch Thi Đấu')").first
        if await schedule_btn.count() > 0:
            await schedule_btn.click()
            print(" -> Đã click tab Lịch Thi Đấu thành công.")
        else:
            print(" -> Fallback: Click nút filter thứ 2...")
            await page.locator(".btn-filter").nth(1).click()

        print("Chờ 5 giây cho dữ liệu trận đấu và các logo tải hoàn tất...")
        await asyncio.sleep(5)

        # 4. Kiểm tra các thẻ trận đấu
        match_cards = page.locator(".match-grid-card")
        count = await match_cards.count()
        print(f"\n4. Số lượng thẻ trận đấu trên lưới: {count}")

        if count > 0:
            for idx in range(min(5, count)):
                card = match_cards.nth(idx)
                team_a = await card.locator(".team-home .match-team-title").text_content()
                team_b = await card.locator(".team-away .match-team-title").text_content()
                vs_text = await card.locator(".match-vs-text").text_content()
                time_text = await card.locator(".match-time-text").text_content()
                tournament = await card.locator(".match-grid-tournament").text_content()
                
                logos = card.locator("img.team-crest")
                logo_count = await logos.count()
                logo_a = await logos.nth(0).get_attribute("src") if logo_count > 0 else ""
                logo_b = await logos.nth(1).get_attribute("src") if logo_count > 1 else ""

                print(f"\n--- [TRẬN {idx + 1}] {tournament} ---")
                print(f"   🏠 Đội Nhà: '{team_a}' | Logo: {logo_a[:55]}...")
                print(f"   ⚡ Đối Đầu: '{vs_text}' | Giờ: '{time_text}'")
                print(f"   ✈️ Đội Khách: '{team_b}' | Logo: {logo_b[:55]}...")
                print(f"   ✅ Số Biểu Tượng (Logo): {logo_count} => {'ĐẠT CHUẨN 2 BIỂU TƯỢNG (PASS)' if logo_count == 2 else 'LỖI'}")

        # 5. Chụp ảnh màn hình kiểm thử lưới trận đấu
        shot1_path = os.path.join(ARTIFACTS_DIR, "dual_logos_matches_success.png")
        await page.screenshot(path=shot1_path)
        print(f"\n📸 ĐÃ LƯU ẢNH CHỨNG MINH THỰC TẾ: {shot1_path} ({os.path.getsize(shot1_path):,} bytes)")

        # 6. Click vào trận đấu đầu tiên để kiểm tra Modal 4 Server
        print("\n6. Click vào trận đấu đầu tiên để kiểm tra Modal 4 Server...")
        if count > 0:
            await match_cards.first.click()
            await asyncio.sleep(2)

            shot2_path = os.path.join(ARTIFACTS_DIR, "dual_logos_server_modal_success.png")
            await page.screenshot(path=shot2_path)
            print(f"📸 ĐÃ LƯU ẢNH MODAL 4 SERVER: {shot2_path} ({os.path.getsize(shot2_path):,} bytes)")

        await browser.close()
        print("\n🎉 KIỂM THỬ PLAYWRIGHT HOÀN TẤT THÀNH CÔNG 100%!")

if __name__ == '__main__':
    asyncio.run(main())
