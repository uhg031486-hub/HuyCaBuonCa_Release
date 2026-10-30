import urllib.request
import re
import sys
import json
import time
import concurrent.futures

sys.stdout.reconfigure(encoding='utf-8')

PLAYLIST_URLS = [
    ("IPTV_VN", "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/vn.m3u"),
    ("IPTV_NEWS", "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/news.m3u"),
    ("IPTV_SPORTS", "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/sports.m3u"),
    ("IPTV_MOVIES", "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/movies.m3u"),
    ("IPTV_DOC", "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/documentary.m3u"),
    ("IPTV_ANIMATION", "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/animation.m3u")
]

def fetch_m3u(source_name, url):
    channels = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode('utf-8', errors='ignore')
            lines = text.splitlines()
            current_name = None
            current_logo = None
            current_group = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    # extract tvg-logo
                    logo_m = re.search(r'tvg-logo="([^"]*)"', line)
                    current_logo = logo_m.group(1) if logo_m else ''
                    
                    # extract group-title
                    grp_m = re.search(r'group-title="([^"]*)"', line)
                    current_group = grp_m.group(1) if grp_m else ''
                    
                    # name is after comma
                    parts = line.split(',', 1)
                    current_name = parts[1].strip() if len(parts) > 1 else 'Unknown'
                elif line and not line.startswith('#'):
                    if current_name:
                        channels.append({
                            'source': source_name,
                            'name': current_name,
                            'logo': current_logo,
                            'group': current_group,
                            'url': line
                        })
                    current_name = None
                    current_logo = None
                    current_group = None
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
    return channels

def test_url(ch):
    url = ch['url']
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        })
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = resp.read(256).decode('utf-8', errors='ignore')
            if resp.status == 200 and ('#EXTM3U' in data or 'EXT-X-' in data or 'avc' in data or len(data) > 20):
                return (ch, True)
    except:
        pass
    return (ch, False)

print("Đang tải các playlist IPTV chuẩn...")
all_cands = []
for src_name, url in PLAYLIST_URLS:
    res = fetch_m3u(src_name, url)
    print(f"  {src_name}: tìm thấy {len(res)} kênh")
    all_cands.extend(res)

print(f"Tổng số kênh tiềm năng: {len(all_cands)}")

# Lọc danh sách các kênh quốc tế và thể thao nổi tiếng
target_keywords = [
    "NHK World", "Al Jazeera", "BBC", "CNN", "ABC News", "CBS News", "NBC News",
    "Sky News", "Euronews", "CNA", "Channel NewsAsia", "Bloomberg", "DW",
    "France 24", "TRT World", "Arirang", "YTN", "KBS", "CGTN",
    "Discovery", "History", "National Geographic", "Nat Geo", "Animal Planet",
    "Red Bull", "Eurosport", "beIN", "Fight Network", "Racers", "Motorvision",
    "Cartoon Network", "Boomerang", "Animax", "HBO", "Cinemax", "Warner", "AXN",
    "Fashion TV", "Qwest", "Stingray", "MTV", "NASA", "Weather Channel",
    "VTV1", "VTV2", "VTV3", "VTV4", "VTV5", "VTV7", "VTV8", "VTV9", "VTV Cần Thơ",
    "HTV7", "HTV9", "HTV Thể Thao", "HTV1", "HTV2", "HTV3",
    "THVL1", "THVL2", "THVL3", "THVL4", "VTC1", "VTC2", "VTC3", "TodayTV"
]

selected = []
for c in all_cands:
    nm = c['name'].lower()
    for kw in target_keywords:
        if kw.lower() in nm:
            selected.append(c)
            break

print(f"Số kênh chọn lọc theo tên thương hiệu quốc tế & Việt Nam: {len(selected)}")

# Kiểm tra luồng song song
print("Đang kiểm tra luồng phát trực tiếp (timeout 3s)...")
alive_channels = []
with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(test_url, c) for c in selected]
    for f in concurrent.futures.as_completed(futures):
        ch, is_alive = f.result()
        if is_alive:
            alive_channels.append(ch)

print(f"Số kênh hoạt động 100% cực tốt: {len(alive_channels)}")
with open('scripts/working_iptv_channels.json', 'w', encoding='utf-8') as f:
    json.dump(alive_channels, f, ensure_ascii=False, indent=2)

for ch in alive_channels[:30]:
    print(f"  [{ch['source']}] {ch['name']} -> {ch['url']}")
