import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    print("=== THỬ NGHIỆM CHẶN SẠCH QUẢNG CÁO NGUỒN C BẰNG SANDBOX (KHÔNG CHO PHÉP POPUP) ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--autoplay-policy=no-user-gesture-required'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Đếm số lượng popup được mở ra
        popups = []
        context.on("page", lambda p: popups.append(p))

        # Tạo trang thử nghiệm nhúng iframe có sandbox chặn popup
        test_html = """
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>Test Sandboxed Player</title></head>
        <body style="margin:0; background:#000;">
          <iframe id="testIframe" 
                  src="https://embed17.streamc.xyz/embed.php?hash=6d8dbf7d53b9867fd9987659c2c9a09f"
                  style="width: 100vw; height: 100vh; border: none;"
                  allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
                  sandbox="allow-scripts allow-same-origin allow-forms allow-presentation"
                  referrerpolicy="no-referrer-when-downgrade">
          </iframe>
          <script>
            // Parent helper handshake
            window.addEventListener('message', (e) => {
              if (e.data && e.data.type === 'stream-guard-hello') {
                const fr = document.getElementById('testIframe');
                if (fr && fr.contentWindow) {
                  fr.contentWindow.postMessage({
                    type: 'stream-parent-state',
                    version: 'guard-5',
                    id: e.data.id,
                    helperVersion: 'guard-5',
                    parentAdblock: 'clear',
                    seq: Date.now(),
                    supported: true,
                    suspected: false
                  }, '*');
                }
              }
            });
          </script>
        </body>
        </html>
        """
        
        await page.set_content(test_html)
        print("Đã nạp trang test sandbox. Đợi iframe tải...")
        await page.wait_for_timeout(6000)

        # Chụp ảnh trước khi click
        await page.screenshot(path="scripts/sandbox_before_click.png")
        print("Đã lưu: scripts/sandbox_before_click.png")

        # Tìm frame
        target_frame = None
        for f in page.frames:
            if "streamc" in f.url:
                target_frame = f
                break

        if target_frame:
            print(f"Frame URL: {target_frame.url}")
            
            # Thử click 5 lần vào các vị trí khác nhau trên player để kích hoạt popup
            print("Thử click 5 lần vào khung player để kiểm tra có bị bật popup quảng cáo không...")
            for i in range(5):
                await page.mouse.click(640, 360)
                await page.wait_for_timeout(1000)

            print(f"Tổng số trang popup quảng cáo bị mở ra: {len(popups)}")
            
            # Kiểm tra trạng thái video trong iframe
            video_status = await target_frame.evaluate("""() => {
                const v = document.querySelector('video');
                const jw = (typeof window.jwplayer === 'function') ? window.jwplayer() : null;
                return {
                    hasVideo: !!v,
                    currentTime: v ? v.currentTime : 0,
                    paused: v ? v.paused : true,
                    duration: v ? v.duration : 0,
                    jwState: jw && jw.getState ? jw.getState() : 'no_jw',
                    jwPosition: jw && jw.getPosition ? jw.getPosition() : 0
                };
            }""")
            print(f"Trạng thái video trong sandbox: {video_status}")

            # Chụp ảnh sau khi click
            await page.screenshot(path="scripts/sandbox_after_click.png")
            print("Đã lưu: scripts/sandbox_after_click.png")
        else:
            print("❌ Không tìm thấy iframe!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
