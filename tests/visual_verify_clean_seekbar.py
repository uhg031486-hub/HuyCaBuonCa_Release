import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright
from PIL import Image

async def capture_clean_player():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        web_index_path = os.path.abspath("HuyCa_Web/index.html")
        await page.goto(f"file:///{web_index_path}")

        # Activate player and setup state matching the user's screenshot
        await page.evaluate("""() => {
            const playerCont = document.getElementById('playerContainer');
            playerCont.style.display = 'flex';
            playerCont.classList.remove('hide');

            const overlay = document.getElementById('playerOverlay');
            overlay.classList.remove('hide', 'controls-hidden');
            overlay.style.opacity = '1';
            overlay.style.display = 'flex';
            overlay.style.pointerEvents = 'auto';

            const playerTitle = document.getElementById('playerTitle');
            if (playerTitle) playerTitle.textContent = 'Ngọc Điệm Thu';

            const playerSub = document.getElementById('playerSub');
            if (playerSub) playerSub.textContent = 'Tập 01';

            const video = document.getElementById('videoPlayer');
            Object.defineProperty(video, 'duration', { value: 2654, configurable: true });
            Object.defineProperty(video, 'currentTime', { value: 348, configurable: true });

            const playedBar = document.getElementById('seekPlayedBar');
            if (playedBar) playedBar.style.width = '13.1%';

            const bufferBar = document.getElementById('seekBufferBar');
            if (bufferBar) bufferBar.style.width = '35%';

            const curTime = document.getElementById('currentTime');
            if (curTime) curTime.textContent = '05:48';

            const durTime = document.getElementById('durationTime');
            if (durTime) durTime.textContent = '44:14';

            const seekBar = document.getElementById('seekBar');
            if (seekBar) {
                seekBar.value = 13.1;
                seekBar.focus();
            }
        }""")

        # Hover directly over the progress bar with force=True
        await page.hover("#progressContainer", force=True)
        await page.wait_for_timeout(500)

        artifact_dir = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
        full_shot = os.path.join(artifact_dir, "verified_clean_player_youtube_grade.png")
        await page.screenshot(path=full_shot)
        print("Captured full screenshot:", full_shot)

        # Crop the seekbar region to match the user's second screenshot
        im = Image.open(full_shot)
        width, height = im.size
        crop_box = (0, int(height * 0.85), width, int(height * 0.94))
        cropped = im.crop(crop_box)
        crop_shot = os.path.join(artifact_dir, "verified_clean_seekbar_crop.png")
        cropped.save(crop_shot)
        print("Captured cropped seekbar screenshot:", crop_shot)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_clean_player())
