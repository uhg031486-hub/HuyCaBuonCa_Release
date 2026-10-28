import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== RED GATE VERIFICATION: KIỂM TRA LỖI NGUỒN C HIỆN TẠI TRÊN PRODUCTION ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})

        toast_errors = []
        page.on("console", lambda m: toast_errors.append(m.text) if "Không thể tải luồng" in m.text or "proxy fallback" in m.text else None)

        print("1. Tải https://huyca.pages.dev ...")
        await page.goto("https://huyca.pages.dev", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Mở phim Hậu Cung Như Ý Truyện
        await page.locator("#btnSearch").click()
        await page.locator("#searchInput").fill("nhu y truyen")
        await page.locator("#btnDoSearch").click()
        await page.wait_for_timeout(3000)

        await page.locator("#searchResultsGrid .movie-card").first.click()
        await page.wait_for_timeout(2000)

        # Bấm Tập 1
        await page.locator("#episodesGrid .btn-episode").first.click()
        await page.wait_for_timeout(4000)

        # Kiểm tra xem toast lỗi có xuất hiện không
        toast_el = page.locator("#toast")
        toast_text = await toast_el.inner_text() if await toast_el.count() > 0 else ""
        toast_visible = await toast_el.is_visible() if await toast_el.count() > 0 else False
        print(f"Toast hiển thị: {toast_visible}, Nội dung: '{toast_text}'")

        # Kiểm tra xem có log proxy fallback rác không
        print("Proxy fallback logs:", toast_errors)

        # Kiểm tra xem nút Xem Trực Tiếp / Pop-out có trên modal và player chưa
        has_direct_btn = await page.locator("#btnOpenEmbedNewTab").count() > 0
        has_popout_btn = await page.locator("#btnPopoutPlayer").count() > 0
        print(f"Có nút Direct Tab: {has_direct_btn}, Có nút Pop-out: {has_popout_btn}")

        has_issue = toast_visible or len(toast_errors) > 0 or not has_popout_btn
        print(f"\n=> KẾT QUẢ RED GATE: CÓ LỖI TỒN TẠI? {has_issue}")

        await page.screenshot(path="scripts/red_gate_nguonc_v326.png")
        await browser.close()
        return 1 if has_issue else 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    print(f"Red gate exit code: {exit_code}")
