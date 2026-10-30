import os
import sys
import time
import subprocess
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

def run_adb(cmd):
    full_cmd = f"adb {cmd}"
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.stdout.strip()

def dump_ui(filename="ui_dump.xml"):
    run_adb("shell uiautomator dump /data/local/tmp/uidump.xml")
    run_adb(f"pull /data/local/tmp/uidump.xml scripts/{filename}")
    time.sleep(0.5)

def find_nodes_by_text(xml_path, text_contains):
    if not os.path.exists(xml_path):
        return []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        results = []
        for elem in root.iter():
            txt = elem.attrib.get('text', '')
            desc = elem.attrib.get('content-desc', '')
            if text_contains.lower() in txt.lower() or text_contains.lower() in desc.lower():
                bounds = elem.attrib.get('bounds', '')
                results.append((elem, bounds, txt))
        return results
    except Exception as e:
        print("XML error:", e)
        return []

def get_center_bounds(bounds_str):
    # bounds="[x1,y1][x2,y2]"
    try:
        parts = bounds_str.replace("][", ",").replace("[", "").replace("]", "").split(",")
        x1, y1, x2, y2 = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        return (x1 + x2) // 2, (y1 + y2) // 2
    except:
        return None, None

def clear_logcat():
    run_adb("logcat -c")

def dump_recent_logs(tag_filter="com.huycabuonca"):
    res = run_adb(f"logcat -d | grep -E \"{tag_filter}|ExoPlayer|FATAL|Exception\" | tail -n 30")
    return res

print("=== BẮT ĐẦU KIỂM THỬ NGUỒN PHIM NGẮN TRÊN GIẢ LẬP ===")
clear_logcat()

# 1. Khởi động TV App
print("\n1. Khởi chạy HuyCaBuonCa_TV...")
run_adb("shell am force-stop com.huycabuonca.tv")
time.sleep(1)
run_adb("shell am start -n com.huycabuonca.tv/com.huycabuonca.tv.ui.MainActivity")
time.sleep(4)

dump_ui("tv_home.xml")
run_adb("shell screencap -p /data/local/tmp/tv_home.png")
run_adb("pull /data/local/tmp/tv_home.png scripts/tv_home_live.png")
print(" -> Chụp ảnh màn hình: scripts/tv_home_live.png")

# 2. Tìm và bấm vào tab "Phim Ngắn"
print("\n2. Tìm tab 'Phim Ngắn'...")
nodes = find_nodes_by_text("scripts/tv_home.xml", "Phim Ngắn")
if nodes:
    _, bounds, txt = nodes[0]
    cx, cy = get_center_bounds(bounds)
    print(f" -> Thấy tab '{txt}' tại {bounds}, click ({cx}, {cy})")
    run_adb(f"shell input tap {cx} {cy}")
    time.sleep(4)
else:
    print(" ⚠️ Không tìm thấy tab Phim Ngắn bằng XML, dùng D-Pad...")
    run_adb("shell input keyevent 19") # UP
    run_adb("shell input keyevent 22") # RIGHT
    run_adb("shell input keyevent 22")
    run_adb("shell input keyevent 22")
    run_adb("shell input keyevent 23") # ENTER
    time.sleep(4)

dump_ui("tv_short_drama.xml")
run_adb("shell screencap -p /data/local/tmp/tv_short_drama.png")
run_adb("pull /data/local/tmp/tv_short_drama.png scripts/tv_short_drama_live.png")
print(" -> Chụp ảnh màn hình: scripts/tv_short_drama_live.png")

# 3. Kiểm tra các Sub-sources hiển thị
sub_sources = ["ReelShort", "DramaBox", "ShortMax", "FreeReels", "Gà Mờ Mê Phim", "AI Cinema", "GoodShort"]
print("\n3. Kiểm tra các nút Sub-sources:")
for sub in sub_sources:
    found = find_nodes_by_text("scripts/tv_short_drama.xml", sub)
    if found:
        print(f" ✅ Có Sub-source: {sub} ({found[0][1]})")
    else:
        print(f" ❌ Không thấy Sub-source: {sub}")

# 4. Kiểm tra các phim hiển thị trong danh sách
print("\n4. Kiểm tra danh sách phim hiển thị:")
# Xem có các card phim nào
try:
    tree = ET.parse("scripts/tv_short_drama.xml")
    movie_cards = []
    for elem in tree.getroot().iter():
        txt = elem.attrib.get('text', '').strip()
        rid = elem.attrib.get('resource-id', '')
        if "txtMovieName" in rid or "txt_title" in rid or (len(txt) > 3 and not any(s in txt for s in sub_sources) and "Huy Cá" not in txt):
            movie_cards.append((txt, elem.attrib.get('bounds', '')))
    print(f" -> Tìm thấy {len(movie_cards)} tiêu đề phim:")
    for mc in movie_cards[:6]:
        print(f"   * {mc[0]} ({mc[1]})")
except Exception as e:
    print("Error parsing cards:", e)

# 5. Thử bấm vào phim đầu tiên
if movie_cards:
    first_movie, b = movie_cards[0]
    cx, cy = get_center_bounds(b)
    print(f"\n5. Bấm vào phim đầu tiên: '{first_movie}' tại ({cx}, {cy})...")
    run_adb(f"shell input tap {cx} {cy}")
    time.sleep(4)

    dump_ui("tv_detail.xml")
    run_adb("shell screencap -p /data/local/tmp/tv_detail.png")
    run_adb("pull /data/local/tmp/tv_detail.png scripts/tv_detail_live.png")
    print(" -> Chụp ảnh màn hình chi tiết: scripts/tv_detail_live.png")

    # Kiểm tra xem DetailActivity nạp được tập phim không
    eps = find_nodes_by_text("scripts/tv_detail.xml", "Tập")
    play_btn = find_nodes_by_text("scripts/tv_detail.xml", "XEM PHIM") or find_nodes_by_text("scripts/tv_detail.xml", "XEM TIẾP")
    print(f" -> Tìm thấy {len(eps)} tập phim.")
    if play_btn:
        print(f" -> Nút Xem Phim: {play_btn[0][2]} ({play_btn[0][1]})")
        cx_p, cy_p = get_center_bounds(play_btn[0][1])
        print(f"\n6. Bấm nút '{play_btn[0][2]}' tại ({cx_p}, {cy_p})...")
        run_adb(f"shell input tap {cx_p} {cy_p}")
        time.sleep(5)

        run_adb("shell screencap -p /data/local/tmp/tv_player.png")
        run_adb("pull /data/local/tmp/tv_player.png scripts/tv_player_live.png")
        print(" -> Chụp ảnh màn hình Player: scripts/tv_player_live.png")

print("\n7. Logcat gần nhất:")
print(dump_recent_logs())
