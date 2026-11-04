import asyncio
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        
        # Load local web player
        # Use python http.server or file:/// path
        import os
        web_index_path = os.path.abspath("HuyCa_Web/index.html")
        await page.goto(f"file:///{web_index_path}")

        print("\n=== STEP 1: KIEM TRA ATTRIBUTES CUA #seekBar ===")
        attr_result = await page.evaluate("""() => {
            const seekBar = document.getElementById('seekBar');
            if (!seekBar) return { error: 'seekBar not found' };
            return {
                hasClassFocusable: seekBar.classList.contains('focusable'),
                className: seekBar.className,
                tabIndex: seekBar.getAttribute('tabindex')
            };
        }""")
        print("Attribute result:", attr_result)

        print("\n=== STEP 2: KIEM TRA COMPUTED STYLES KHI FOCUS VA HOVER TRONG CA CHE DO THUONG VA MODE-TV ===")
        style_result = await page.evaluate("""() => {
            const playerCont = document.getElementById('playerContainer');
            if (playerCont) {
                playerCont.style.display = 'flex';
                playerCont.classList.remove('hide');
            }
            const overlay = document.getElementById('playerOverlay');
            if (overlay) {
                overlay.classList.remove('hide', 'controls-hidden');
                overlay.style.opacity = '1';
                overlay.style.display = 'flex';
            }

            const seekBar = document.getElementById('seekBar');
            if (!seekBar) return { error: 'seekBar not found' };

            // Focus vao seekBar
            seekBar.focus();

            const normalFocusStyle = window.getComputedStyle(seekBar);
            const normalOutline = normalFocusStyle.outline;
            const normalBoxShadow = normalFocusStyle.boxShadow;
            const normalBorderColor = normalFocusStyle.borderColor;

            // Kiem tra trong mode-tv
            document.body.classList.add('mode-tv');
            seekBar.classList.add('focused');
            
            const tvFocusStyle = window.getComputedStyle(seekBar);
            const tvOutline = tvFocusStyle.outline;
            const tvBoxShadow = tvFocusStyle.boxShadow;
            const tvBorderColor = tvFocusStyle.borderColor;

            return {
                normalOutline,
                normalBoxShadow,
                normalBorderColor,
                tvOutline,
                tvBoxShadow,
                tvBorderColor,
                hasCyanNormal: normalOutline.includes('0, 229, 255') || normalBoxShadow.includes('0, 229, 255') || normalBorderColor.includes('0, 229, 255'),
                hasCyanTV: tvOutline.includes('0, 229, 255') || tvBoxShadow.includes('0, 229, 255') || tvBorderColor.includes('0, 229, 255')
            };
        }""")
        print("Style result:", style_result)

        print("\n=== STEP 3: KIEM TRA getFocusableCandidates KHONG CHUA #seekBar ===")
        candidates_result = await page.evaluate("""() => {
            const playerCont = document.getElementById('playerContainer');
            if (typeof getFocusableCandidates === 'function') {
                const candidates = getFocusableCandidates(playerCont);
                const containsSeekBar = candidates.some(el => el.id === 'seekBar');
                return { containsSeekBar, candidateCount: candidates.length };
            }
            return { skip: 'getFocusableCandidates not globally exposed' };
        }""")
        print("Candidates result:", candidates_result)

        # Chup screenshot hien tai de doi chieu
        await page.screenshot(path="tests/red_gate_seekbar_state.png")
        print("Saved snapshot: tests/red_gate_seekbar_state.png")

        await browser.close()

        # Validation:
        # Neu seekBar co class focusable hoac bi cyan glow thi test coi nhu FAIL (Red Gate)
        assert not attr_result.get('hasClassFocusable'), f"RED GATE: seekBar van con class focusable: {attr_result}"
        assert attr_result.get('tabIndex') == '-1', f"RED GATE: seekBar chua co tabindex='-1': {attr_result}"
        assert not style_result.get('hasCyanNormal'), f"RED GATE: seekBar co vien cyan o che do normal: {style_result}"
        assert not style_result.get('hasCyanTV'), f"RED GATE: seekBar co vien cyan o che do TV: {style_result}"
        print("\n>>> ALL CHECKS PASSED: SEEKBAR HOAN TOAN SACH SE, KHONG CON VIEN CYAN! <<<")

if __name__ == "__main__":
    asyncio.run(run_test())
