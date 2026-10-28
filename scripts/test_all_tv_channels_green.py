import sys
import json
import urllib.request
import concurrent.futures
import time

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCa_Web/data/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

print(f"=== BẮT ĐẦU KIỂM THỬ GREEN FEEDBACK LOOP CHO {len(channels)} KÊNH ===")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': '*/*'
}

def verify_channel(ch):
    url = ch.get('url', '')
    name = ch.get('name', '')
    group = ch.get('group', '')
    
    try:
        req = urllib.request.Request(url, headers=headers)
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            data = resp.read(256)
            elapsed = time.time() - t0
            return True, ch, resp.status, elapsed, ""
    except Exception as e:
        return False, ch, 0, 0, str(e)

success_count = 0
fail_count = 0
group_stats = {}

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(verify_channel, ch) for ch in channels]
    for future in concurrent.futures.as_completed(futures):
        ok, ch, status_code, elapsed, err = future.result()
        grp = ch.get('group', 'Unknown')
        if grp not in group_stats:
            group_stats[grp] = {'ok': 0, 'fail': 0}
            
        if ok:
            success_count += 1
            group_stats[grp]['ok'] += 1
        else:
            fail_count += 1
            group_stats[grp]['fail'] += 1
            print(f"⚠️ [FAIL] [{grp}] {ch['name']} - Lỗi: {err}")

print("\n=== THỐNG KÊ CHI TIẾT THEO NHÓM ===")
for grp, stat in sorted(group_stats.items(), key=lambda x: -x[1]['ok']):
    total_grp = stat['ok'] + stat['fail']
    rate = (stat['ok'] / total_grp) * 100 if total_grp > 0 else 0
    print(f" - {grp:30s}: {stat['ok']:2d}/{total_grp:2d} sống ({rate:.1f}%)")

total = len(channels)
pass_rate = (success_count / total) * 100
print(f"\n==========================================")
print(f"TỔNG KẾT: {success_count}/{total} kênh sống ({pass_rate:.1f}%)")
print(f"==========================================")

# Kiểm tra riêng các kênh Quốc Tế trọng điểm
intl_channels = [c for c in channels if any(k in (c.get('group') or '') for k in ['Quốc Tế', 'Vệ Tinh'])]
print(f"Kiểm thử riêng nhóm Kênh Quốc Tế & Vệ Tinh: {len(intl_channels)} kênh")

if pass_rate >= 95.0:
    print("✅ GREEN GATE PASSED: Kho kênh hoạt động xuất sắc đạt chuẩn >95%!")
    sys.exit(0)
else:
    print(f"❌ GREEN GATE FAILED: Tỷ lệ sống {pass_rate:.1f}% chưa đạt chuẩn yêu cầu!")
    sys.exit(1)
