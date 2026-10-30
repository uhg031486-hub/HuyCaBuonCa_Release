import sys
import json
import urllib.request
import re

sys.stdout.reconfigure(encoding='utf-8')

# Tìm kiếm trên IPTV-org các kênh news tiếng Anh nổi tiếng
iptv_sources = [
    "https://iptv-org.github.io/iptv/languages/eng.m3u",
    "https://iptv-org.github.io/iptv/categories/news.m3u"
]

wanted = ['cnn', 'nbc', 'fox news', 'msnbc', 'reuters', 'sky news', 'al jazeera']

print("Đang quét các kênh tin tức chất lượng cao từ iptv-org...")

candidates = []
for src in iptv_sources:
    try:
        req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            lines = r.read().decode('utf-8', errors='ignore').splitlines()
            current_name = ""
            current_logo = ""
            for line in lines:
                if line.startswith('#EXTINF:'):
                    current_name = re.findall(r',([^,]+)$', line)
                    current_name = current_name[0] if current_name else ""
                    logo_match = re.findall(r'tvg-logo="([^"]+)"', line)
                    current_logo = logo_match[0] if logo_match else ""
                elif line.startswith('http') and current_name:
                    lower_nm = current_name.lower()
                    if any(w in lower_nm for w in wanted):
                        candidates.append({
                            'name': current_name,
                            'logo': current_logo,
                            'url': line
                        })
                    current_name = ""
    except Exception as e:
        print(f"Lỗi tải {src}: {e}")

print(f"Tìm thấy {len(candidates)} ứng viên tin tức. Đang test song song...")

working_news = []
import concurrent.futures
def test_candidate(item):
    try:
        req = urllib.request.Request(item['url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status in [200, 206]:
                return True, item
    except:
        pass
    return False, item

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(test_candidate, c) for c in candidates[:60]]
    for f in concurrent.futures.as_completed(futures):
        ok, item = f.result()
        if ok:
            print(f" -> SỐNG: {item['name']} -> {item['url']}")
            working_news.append(item)

print(f"Tổng số kênh tin tức sống xác minh: {len(working_news)}")
