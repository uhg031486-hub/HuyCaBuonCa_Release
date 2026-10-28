import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import time
from playwright.sync_api import sync_playwright
import json

def test_each_intl_channel_on_live():
    print("=" * 70)
    print("🌐 KIỂM THỬ TỪNG KÊNH QUỐC TẾ TRÊN TRÌNH DUYỆT CHROME LIVE")
    print("=" * 70)

    with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
        channels = json.load(f)

    intl_channels = [c for c in channels if c.get('group') == 'Quốc Tế']

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Giả lập đúng trình duyệt của người dùng trên HTTPS
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            accept_downloads=True
        )
        page = context.new_page()

        # Bắt console error và request failed
        failed_requests = []
        page.on('requestfailed', lambda r: failed_requests.append({'url': r.url, 'err': r.failure}))
        
        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}") if msg.type in ['error', 'warning'] else None)

        print("1. Đang truy cập https://huyca.pages.dev ...")
        page.goto("https://huyca.pages.dev", wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # Chuyển sang Tab TV
        page.locator("#srcXemTiVi").click()
        time.sleep(1)

        print(f"\n2. Bắt đầu kiểm tra {len(intl_channels)} kênh Quốc Tế...\n")

        for idx, ch in enumerate(intl_channels):
            failed_requests.clear()
            console_logs.clear()
            name = ch.get('name')
            ch_id = ch.get('id')
            url = ch.get('url')

            # Mở phát kênh bằng JS
            play_res = page.evaluate("""(id) => {
                const all = window.TV_CHANNELS || window.INITIAL_TV_CHANNELS || [];
                const target = all.find(c => c.id === id);
                if (target && typeof window.playTvChannelDirectly === 'function') {
                    window.playTvChannelDirectly(target);
                    return true;
                }
                return false;
            }""", ch_id)

            # Đợi 3.5 giây để Hls.js tải manifest và play
            time.sleep(3.5)

            # Đo trạng thái player
            state = page.evaluate("""() => {
                const v = document.getElementById('videoPlayer');
                const t = document.getElementById('playerTitle')?.textContent || '';
                return {
                    title: t,
                    paused: v ? v.paused : true,
                    currentTime: v ? v.currentTime : 0,
                    readyState: v ? v.readyState : 0,
                    error: v && v.error ? v.error.code : null,
                    videoSrc: v ? v.src : ''
                };
            }""")

            # Đánh giá xem kênh có phát được không
            # readyState >= 2 (HAVE_CURRENT_DATA) hoặc currentTime > 0 nghĩa là phát được
            is_playing = (state['readyState'] >= 2) or (state['currentTime'] > 0)
            
            # Ghi nhận lỗi nếu có
            reasons = []
            if url.startswith('http://'):
                reasons.append("Bị Mixed Content (HTTP trên trang HTTPS)")
            if any('CORS' in l or 'cors' in l for l in console_logs):
                reasons.append("Lỗi CORS Policy")
            if any('ERR_BLOCKED_BY_CLIENT' in str(r) or 'ERR_SSL_PROTOCOL_ERROR' in str(r) or 'failed' in str(r) for r in failed_requests):
                reasons.append("Request bị trình duyệt chặn")
            if state['error']:
                reasons.append(f"MediaElement error code {state['error']}")

            res_item = {
                'name': name,
                'id': ch_id,
                'url': url,
                'is_playing': is_playing,
                'readyState': state['readyState'],
                'currentTime': state['currentTime'],
                'reasons': reasons
            }
            results.append(res_item)

            icon = "✅ ĐƯỢC" if is_playing else "❌ KHÔNG ĐƯỢC"
            detail_err = f" -> Nguyên nhân: {', '.join(reasons)}" if reasons and not is_playing else ""
            print(f"[{idx+1}/{len(intl_channels)}] {icon} | {name}: readyState={state['readyState']}, time={state['currentTime']}s {detail_err}")

        browser.close()

    print("\n" + "=" * 70)
    ok_count = sum(1 for r in results if r['is_playing'])
    fail_count = sum(1 for r in results if not r['is_playing'])
    print(f"KẾT QUẢ: {ok_count} kênh ĐƯỢC, {fail_count} kênh KHÔNG ĐƯỢC / tổng số {len(results)} kênh.")
    print("=" * 70)

if __name__ == '__main__':
    test_each_intl_channel_on_live()
