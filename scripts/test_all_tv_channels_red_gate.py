import sys
import json
import urllib.request
import concurrent.futures
import time

sys.stdout.reconfigure(encoding='utf-8')

def check_channel_stream(ch):
    url = ch.get('url', '')
    name = ch.get('name', 'Unknown')
    cat = ch.get('category', 'Khác')
    
    if not url:
        return {'channel': ch, 'alive': False, 'error': 'No URL', 'time': 0}
        
    start = time.time()
    try:
        # User agents: browser-like
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': '*/*'
        }
        if 'vtv' in url.lower():
            headers['Referer'] = 'https://vtvgo.vn/'
        elif 'thvl' in url.lower():
            headers['Referer'] = 'https://thvli.vn/'
            
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            content_sample = resp.read(512).decode('utf-8', errors='ignore')
            elapsed = time.time() - start
            is_valid = ('#EXTM3U' in content_sample or resp.status == 200)
            return {
                'channel': ch,
                'alive': is_valid,
                'status': resp.status,
                'error': None if is_valid else 'Invalid M3U8',
                'time': round(elapsed, 2)
            }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'channel': ch,
            'alive': False,
            'status': getattr(e, 'code', 0),
            'error': str(e),
            'time': round(elapsed, 2)
        }

def main():
    print("=== TEST RED GATE: KIỂM THỬ TOÀN BỘ KHO KÊNH TV HIỆN CÓ ===")
    with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
        channels = json.load(f)

    print(f"Tổng số kênh cần kiểm tra: {len(channels)}")

    # Nhóm theo category
    cat_counts = {}
    for c in channels:
        cat = c.get('category', 'Khác')
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    print("\nPhân bổ danh mục:")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  - {cat}: {cnt} kênh")

    print("\nĐang kiểm tra tình trạng luồng phát trực tiếp của tất cả các kênh...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(check_channel_stream, ch) for ch in channels]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    alive_channels = [r for r in results if r['alive']]
    dead_channels = [r for r in results if not r['alive']]

    print(f"\n=== KẾT QUẢ KIỂM THỬ TỔNG QUAN ===")
    print(f"✅ Hoạt động tốt: {len(alive_channels)} / {len(channels)} kênh ({len(alive_channels)*100//len(channels)}%)")
    print(f"❌ Kênh lỗi / Chết luồng: {len(dead_channels)} / {len(channels)} kênh")

    # Kiểm tra riêng các kênh Quốc Tế
    intl_results = [r for r in results if any(k in r['channel'].get('category', '').lower() for k in ['quốc tế', 'intl', 'nước ngoài', 'tin tức'])]
    intl_alive = [r for r in intl_results if r['alive']]
    intl_dead = [r for r in intl_results if not r['alive']]

    print(f"\n=== CHI TIẾT KÊNH QUỐC TẾ / TIN TỨC ===")
    print(f"Tổng số kênh quốc tế: {len(intl_results)}")
    print(f"✅ Hoạt động: {len(intl_alive)}")
    print(f"❌ Lỗi / Không xem được: {len(intl_dead)}")

    if intl_dead:
        print("\nDanh sách kênh quốc tế đang bị lỗi:")
        for r in intl_dead:
            ch = r['channel']
            print(f"  - [{ch.get('category')}] {ch.get('name')}: Lỗi '{r['error']}' (URL: {ch.get('url')[:60]}...)")

    print("\nTop các kênh lỗi khác trong kho:")
    for r in dead_channels[:15]:
        ch = r['channel']
        print(f"  - [{ch.get('category')}] {ch.get('name')}: {r['error']}")

    # Ghi lại file kết quả json
    summary_data = {
        'total': len(channels),
        'alive': len(alive_channels),
        'dead': len(dead_channels),
        'dead_list': [{'id': r['channel'].get('id'), 'name': r['channel'].get('name'), 'cat': r['channel'].get('category'), 'url': r['channel'].get('url'), 'error': r['error']} for r in dead_channels]
    }
    with open('scripts/red_gate_channels_result.json', 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    print("\nĐã lưu kết quả chi tiết vào: scripts/red_gate_channels_result.json")

    # Xác nhận thất bại Red Gate nếu có kênh lỗi
    if len(dead_channels) > 0:
        print(f"\n[RED GATE CONFIRMED] Có {len(dead_channels)} kênh bị lỗi, đặc biệt có {len(intl_dead)} kênh quốc tế không xem được!")

if __name__ == '__main__':
    main()
