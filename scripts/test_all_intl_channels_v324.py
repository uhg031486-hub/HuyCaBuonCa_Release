import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import time
from playwright.sync_api import sync_playwright
import json

def test_all_intl_channels_v324():
    print("=" * 70)
    print("🚀 KIỂM THỬ TẤT CẢ 12 KÊNH QUỐC TẾ CHUẨN VÀNG TRÊN V3.2.4")
    print("=" * 70)

    web_path = os.path.abspath('HuyCa_Web/index.html').replace(os.sep, '/')

    with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
        channels = json.load(f)

    intl_channels = [c for c in channels if c.get('group') == 'Quốc Tế']
    print(f"Tổng số kênh Quốc Tế: {len(intl_channels)}")
    assert len(intl_channels) == 12, f"Phải có đúng 12 kênh chuẩn vàng, hiện có: {len(intl_channels)}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            accept_downloads=True
        )
        page = context.new_page()

        page.goto(f'file:///{web_path}', wait_until='networkidle')
        time.sleep(1)

        # Tab TV
        page.locator('#srcXemTiVi').click()
        time.sleep(1)

        success_count = 0

        for idx, ch in enumerate(intl_channels):
            name = ch.get('name')
            ch_id = ch.get('id')

            # Mở phát kênh
            page.evaluate("""(id) => {
                const all = window.TV_CHANNELS || window.INITIAL_TV_CHANNELS || [];
                const target = all.find(c => c.id === id);
                if (target && typeof window.playTvChannelDirectly === 'function') {
                    window.playTvChannelDirectly(target);
                }
            }""", ch_id)

            time.sleep(2.5)

            state = page.evaluate("""() => {
                const v = document.getElementById('videoPlayer');
                return {
                    readyState: v ? v.readyState : 0,
                    currentTime: v ? v.currentTime : 0
                };
            }""")

            is_ok = (state['readyState'] >= 2) or (state['currentTime'] > 0)
            if not is_ok:
                time.sleep(1.5)
                state = page.evaluate("() => ({ readyState: document.getElementById('videoPlayer')?.readyState || 0, currentTime: document.getElementById('videoPlayer')?.currentTime || 0 })")
                is_ok = (state['readyState'] >= 2) or (state['currentTime'] > 0)

            print(f"[{idx+1}/12] {'✅ PASS' if is_ok else '❌ FAIL'} | {name}: readyState={state['readyState']}, time={state['currentTime']}s")
            assert is_ok == True, f"Kênh {name} bắt buộc phải phát thành công!"
            success_count += 1

        browser.close()

    print("\n" + "=" * 70)
    print(f"🎉 100% TẤT CẢ {success_count}/12 KÊNH QUỐC TẾ ĐỀU PASS THÀNH CÔNG (100% TỈ LỆ ĐẠT)!")
    print("=" * 70)

if __name__ == '__main__':
    test_all_intl_channels_v324()
