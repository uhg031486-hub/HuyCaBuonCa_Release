import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def inspect_network():
    url = "https://embed14.streamc.xyz/embed.php?hash=c20e700926871acf9dabae7945ce09ec"
    print(f"Opening {url} with Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            extra_http_headers={"Referer": "https://phim.nguonc.com/"}
        )
        page = context.new_page()

        video_requests = []
        page.on("request", lambda r: video_requests.append(r.url) if ('.m3u8' in r.url or '.mp4' in r.url or 'stream' in r.url or 'cdn' in r.url) else None)

        try:
            page.goto(url, wait_until="networkidle", timeout=15000)
            print("Page loaded successfully.")
            import time
            time.sleep(3)
        except Exception as e:
            print("Goto err:", e)

        print("\n--- VIDEO REQUESTS CAPTURED ---")
        for u in video_requests:
            print(" ->", u)

        # Kiểm tra JWPlayer config
        jw_config = page.evaluate("""() => {
            if (window.jwplayer && typeof window.jwplayer === 'function') {
                try {
                    const pl = window.jwplayer();
                    return {
                        playlist: pl.getPlaylist ? pl.getPlaylist() : null,
                        item: pl.getPlaylistItem ? pl.getPlaylistItem() : null
                    };
                } catch(e) { return { err: e.toString() }; }
            }
            return { jw: false };
        }""")
        print("\nJWPlayer Config:", jw_config)

        browser.close()

if __name__ == '__main__':
    inspect_network()
