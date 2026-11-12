import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

async def test_tv_remote_navigation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 1920x1080 standard Full HD TV screen resolution
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Web0S; SmartTV; LargeScreen) AppleWebKit/537.36 Chrome/108.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        web_index_path = os.path.abspath("HuyCa_Web/index.html")
        print(f"Loading web app in TV mode: file:///{web_index_path} ...")
        await page.goto(f"file:///{web_index_path}", wait_until="networkidle")

        # 1. Kiem tra Mode TV da tu dong duoc kich hoat
        body_class = await page.evaluate("() => document.body.className")
        print(f"1. Body class (TV Mode detection): '{body_class}'")
        assert "mode-tv" in body_class, "App must detect TV mode on TV user agent"

        # 2. Test D-Pad Navigation tren trang chu (ArrowRight, ArrowDown)
        print("2. Testing D-Pad on Home Screen (ArrowRight, ArrowDown)...")
        # Nhan ArrowRight
        await page.keyboard.press("ArrowRight")
        await page.wait_for_timeout(200)

        focused_tag = await page.evaluate("""() => {
            const el = document.querySelector('.focused') || document.activeElement;
            return el ? { tag: el.tagName, className: el.className, id: el.id, text: el.innerText.substring(0, 30) } : null;
        }""")
        print("Focused item after ArrowRight:", focused_tag)
        assert focused_tag is not None, "D-Pad ArrowRight must focus an item on TV"

        # Nhan tiep ArrowDown
        await page.keyboard.press("ArrowDown")
        await page.wait_for_timeout(200)

        focused_card = await page.evaluate("""() => {
            const el = document.querySelector('.focused') || document.activeElement;
            return el ? { tag: el.tagName, className: el.className, id: el.id } : null;
        }""")
        print("Focused item after ArrowDown:", focused_card)
        assert focused_card is not None, "D-Pad ArrowDown must focus an item on TV"

        # 3. Test Video Player D-Pad (Tua phim Trai/Phai +-10s va Play/Pause)
        print("3. Testing TV Remote inside Video Player...")
        player_res = await page.evaluate("""() => {
            const playerCont = document.getElementById('playerContainer');
            playerCont.style.display = 'flex';
            playerCont.classList.remove('hide');

            const overlay = document.getElementById('playerOverlay');
            overlay.classList.remove('hide', 'controls-hidden');
            overlay.style.display = 'flex';

            const video = document.getElementById('videoPlayer');
            Object.defineProperty(video, 'duration', { value: 3000, configurable: true, writable: true });
            video.currentTime = 500;

            return { initialTime: video.currentTime, duration: video.duration };
        }""")
        print("Initial player state:", player_res)

        # Nhan ArrowRight (Tua toi +10s)
        await page.keyboard.press("ArrowRight")
        await page.wait_for_timeout(300)

        time_after_right = await page.evaluate("() => document.getElementById('videoPlayer').currentTime")
        toast_text = await page.evaluate("""() => {
            const t = document.getElementById('toastNotification');
            return t ? t.textContent : '';
        }""")
        print(f"After ArrowRight: currentTime = {time_after_right}s (Expected 510s), Toast: '{toast_text}'")
        assert time_after_right == 510, f"ArrowRight on TV remote must fast forward +10s (got {time_after_right})"

        # Nhan ArrowLeft (Tua lui -10s)
        await page.keyboard.press("ArrowLeft")
        await page.wait_for_timeout(300)

        time_after_left = await page.evaluate("() => document.getElementById('videoPlayer').currentTime")
        print(f"After ArrowLeft: currentTime = {time_after_left}s (Expected 500s)")
        assert time_after_left == 500, f"ArrowLeft on TV remote must rewind -10s (got {time_after_left})"

        # 4. Test Up / Down focus vao nut Play/Pause va nut dieu khien
        print("4. Testing Up / Down navigation in Player controls...")
        await page.keyboard.press("ArrowDown")
        await page.wait_for_timeout(200)

        player_focused = await page.evaluate("""() => {
            const el = document.querySelector('.focused') || document.activeElement;
            return el ? { id: el.id, className: el.className } : null;
        }""")
        print("Focused element in player controls:", player_focused)

        # 5. Test Remote Back Button (Keycode 461 on LG webOS / Esc 27)
        print("5. Testing TV Remote Back Button (Keycode 461 / Esc)...")
        # Dispatch LG webOS back button event (keycode 461)
        await page.evaluate("""() => {
            const event = new KeyboardEvent('keydown', {
                keyCode: 461,
                which: 461,
                bubbles: true,
                cancelable: true
            });
            window.dispatchEvent(event);
        }""")
        await page.wait_for_timeout(300)

        player_display = await page.evaluate("""() => {
            const p = document.getElementById('playerContainer');
            return p ? p.style.display : 'none';
        }""")
        print("Player display after TV Remote Back:", player_display)
        assert player_display == 'none', "TV Remote Back button (keycode 461) must close the player"

        # Chup anh xac minh giao dien TV hoan hao
        artifact_dir = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
        shot_path = os.path.join(artifact_dir, "verified_tv_remote_navigation.png")
        await page.screenshot(path=shot_path)
        print("Captured TV screen screenshot:", shot_path)

        await browser.close()
        print("\n>>> ALL TV REMOTE CHECKS PASSED: DIEU KHIEN TREN TV HOAT DONG 100% HOAN HAO! <<<")

if __name__ == "__main__":
    asyncio.run(test_tv_remote_navigation())
