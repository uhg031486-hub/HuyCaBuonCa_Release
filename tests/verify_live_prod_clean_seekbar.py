import asyncio
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright
from PIL import Image

async def verify_exact_live_production():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1024, "height": 768})
        page = await context.new_page()

        live_url = "https://huyca.pages.dev"
        print(f"Loading {live_url} ...")
        await page.goto(live_url, wait_until="networkidle")

        # Setup player state with subtitle "Đứng lại đó!" exactly as in user's screenshot
        await page.evaluate("""() => {
            const playerCont = document.getElementById('playerContainer');
            playerCont.style.display = 'flex';
            playerCont.classList.remove('hide');

            const overlay = document.getElementById('playerOverlay');
            overlay.classList.remove('hide', 'controls-hidden');
            overlay.style.opacity = '1';
            overlay.style.display = 'flex';
            overlay.style.pointerEvents = 'auto';

            const video = document.getElementById('videoPlayer');
            Object.defineProperty(video, 'duration', { value: 2400, configurable: true });
            Object.defineProperty(video, 'currentTime', { value: 300, configurable: true });

            const playedBar = document.getElementById('seekPlayedBar');
            if (playedBar) playedBar.style.width = '12.5%';

            const seekBar = document.getElementById('seekBar');
            if (seekBar) {
                seekBar.value = 12.5;
                seekBar.focus();
            }

            let sub = document.getElementById('playerSubtitleTrack') || document.querySelector('.player-subtitle');
            if (!sub) {
                sub = document.createElement('div');
                sub.id = 'testSubtitle';
                sub.style.position = 'absolute';
                sub.style.bottom = '80px';
                sub.style.left = '50%';
                sub.style.transform = 'translateX(-50%)';
                sub.style.color = '#ffffff';
                sub.style.fontSize = '24px';
                sub.style.fontWeight = 'bold';
                sub.style.textShadow = '0 2px 4px rgba(0,0,0,0.9)';
                sub.style.zIndex = '30';
                sub.textContent = 'Đứng lại đó!';
                playerCont.appendChild(sub);
            }
        }""")

        box = await page.locator("#progressContainer").bounding_box()
        print("progressContainer bounding box:", box)

        # Hover directly on progressContainer
        await page.hover("#progressContainer", force=True)
        await page.wait_for_timeout(500)

        artifact_dir = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
        shot_path = os.path.join(artifact_dir, "verified_live_production_1024.png")
        await page.screenshot(path=shot_path)
        print("Captured full screenshot at 1024px:", shot_path)

        # Crop exact seekbar region (box expanded by 10px on all sides)
        im = Image.open(shot_path).convert('RGB')
        bx = max(0, int(box['x'] - 10))
        by = max(0, int(box['y'] - 10))
        bw = min(im.width, int(box['x'] + box['width'] + 10))
        bh = min(im.height, int(box['y'] + box['height'] + 10))

        cropped = im.crop((bx, by, bw, bh))
        crop_path = os.path.join(artifact_dir, "exact_live_seekbar_crop.png")
        cropped.save(crop_path)
        print("Saved exact seekbar crop:", crop_path)

        # Pixel analysis on seekbar area
        cw, ch = cropped.size
        cpixels = cropped.load()
        cyan_pixels = []
        for y in range(ch):
            for x in range(cw):
                r, g, b = cpixels[x, y]
                # Cyan check: bright cyan glow like #00e5ff
                if g > 100 and b > 100 and (g + b) > 2 * r + 40 and b > r + 30:
                    cyan_pixels.append((x, y, r, g, b))

        print(f"Total cyan pixels in seekbar area: {len(cyan_pixels)}")
        await browser.close()

        assert len(cyan_pixels) == 0, f"Found {len(cyan_pixels)} cyan pixels in seekbar area!"
        print(">>> 100% CLEAN: ZERO CYAN PIXELS ON LIVE PRODUCTION! <<<")

if __name__ == "__main__":
    asyncio.run(verify_exact_live_production())
