import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--autoplay-policy=no-user-gesture-required', '--no-sandbox']
    )
    page = browser.new_page(viewport={'width': 1280, 'height': 720})
    page.on('console', lambda msg: print(f'[CONSOLE] {msg.type}: {msg.text}'))

    print('Navigating to http://localhost:8099/player_test.html...')
    page.goto('http://localhost:8099/player_test.html')

    success = False
    for i in range(15):
        page.wait_for_timeout(1000)
        status_text = page.eval_on_selector('#status', 'el => el.innerText')
        video_info = page.evaluate("""() => {
            const v = document.getElementById('video');
            return {
                currentTime: v.currentTime,
                paused: v.paused,
                duration: v.duration,
                readyState: v.readyState
            };
        }""")
        print(f'Second {i+1}: status="{status_text}" video={video_info}')
        if video_info['currentTime'] > 0 and not video_info['paused']:
            print('🎉 VIDEO IS ACTIVELY PLAYING CLEANLY!')
            success = True
            break

    page.screenshot(path='scripts/clean_hls_playback_success.png')
    print('Screenshot saved: scripts/clean_hls_playback_success.png')
    browser.close()

    assert success, "LỖI: Video không phát thành công!"
