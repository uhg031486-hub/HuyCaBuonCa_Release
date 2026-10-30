import subprocess
import time
import os
import sys
import io
import re
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ARTIFACTS_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"

def adb(cmd):
    res = subprocess.run(f"adb -s emulator-5554 {cmd}", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.stdout.strip()

def adb_screencap(filename):
    local_path = os.path.join(ARTIFACTS_DIR, filename)
    subprocess.run(f"adb -s emulator-5554 exec-out screencap -p > \"{local_path}\"", shell=True)
    if os.path.exists(local_path):
        print(f"Captured: {filename} ({os.path.getsize(local_path):,} bytes)")
    return local_path

def dump_ui():
    adb("shell uiautomator dump /data/local/tmp/uidump.xml")
    xml_content = adb("shell cat /data/local/tmp/uidump.xml")
    try:
        root = ET.fromstring(xml_content)
        elements = []
        for node in root.iter():
            txt = node.attrib.get('text', '')
            desc = node.attrib.get('content-desc', '')
            rid = node.attrib.get('resource-id', '')
            bounds = node.attrib.get('bounds', '')
            clazz = node.attrib.get('class', '')
            clickable = node.attrib.get('clickable', '')
            focused = node.attrib.get('focused', '')
            if txt or desc or rid:
                elements.append({
                    'text': txt,
                    'desc': desc,
                    'id': rid,
                    'bounds': bounds,
                    'class': clazz,
                    'clickable': clickable,
                    'focused': focused
                })
        return elements
    except Exception as e:
        print("Error parsing UI dump:", e)
        return []

def get_center_coords(bounds_str):
    m = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
    if m:
        cx = (int(m[0][0]) + int(m[1][0])) // 2
        cy = (int(m[0][1]) + int(m[1][1])) // 2
        return cx, cy
    return None

def main():
    print("=== KIỂM THỬ CHI TIẾT TÍNH NĂNG CHỌN SERVER TRÊN ANDROID TV ===")
    
    # 1. Mở lại MainActivity của TV
    adb("shell am force-stop com.huycabuonca.tv")
    adb("shell am force-stop com.huycabuonca.mobile")
    time.sleep(1)
    adb("shell am start -n com.huycabuonca.tv/.ui.MainActivity")
    print("Chờ 6 giây tải dữ liệu KKPhim...")
    time.sleep(6)

    # 2. Bỏ qua Dialog update nếu có
    ui = dump_ui()
    cancel_btn = next((el for el in ui if el['text'] == 'ĐỂ SAU'), None)
    if cancel_btn:
        print("Bấm bỏ qua cập nhật 'ĐỂ SAU'...")
        cx, cy = get_center_coords(cancel_btn['bounds'])
        adb(f"shell input tap {cx} {cy}")
        time.sleep(2)

    ui = dump_ui()
    # Tìm các item phim txtTitle
    movie_titles = [el for el in ui if el['id'].endswith('txtTitle')]
    print(f"Tìm thấy {len(movie_titles)} phim trên trang chủ:")
    for m in movie_titles[:5]:
        print(f"  🎬 [{m['text']}] at bounds {m['bounds']}")

    if not movie_titles:
        print("Chưa tìm thấy txtTitle, thử dùng DPAD_DOWN...")
        adb("shell input keyevent 20") # DOWN
        adb("shell input keyevent 20") # DOWN
        time.sleep(2)
        ui = dump_ui()
        movie_titles = [el for el in ui if el['id'].endswith('txtTitle')]

    # Click vào phim đầu tiên
    target_movie = movie_titles[0] if movie_titles else None
    if target_movie:
        print(f"\n--> Click vào phim: '{target_movie['text']}'")
        cx, cy = get_center_coords(target_movie['bounds'])
        adb(f"shell input tap {cx} {cy}")
    else:
        # Fallback: Tap vào vị trí grid row 1 col 1 (ví dụ: x=200, y=500)
        print("Fallback: tap vào tọa độ 200, 500")
        adb("shell input tap 200 500")

    print("Chờ 5 giây cho DetailActivity tải chi tiết phim và các server...")
    time.sleep(5)

    adb_screencap("emulator_tv_v331_detail_loaded.png")
    detail_ui = dump_ui()

    title_el = next((el for el in detail_ui if el['id'].endswith('txtDetailTitle')), None)
    if title_el:
        print(f"\n✅ Đã mở thành công chi tiết phim: '{title_el['text']}'")

    # Kiểm tra thanh server
    server_elements = [el for el in detail_ui if "Phụ Đề" in el['text'] or "Thuyết Minh" in el['text'] or "Lồng Tiếng" in el['text'] or "HuyCa Server" in el['text'] or "Server" in el['text']]
    episodes = [el for el in detail_ui if el['id'].endswith('btnEpisode') or "Tập" in el['text'] or (el['text'].isdigit() and len(el['text']) <= 3)]

    print(f"\n🎯 KẾT QUẢ KIỂM THỬ THANH CHỌN SERVER TRÊN ANDROID TV:")
    print(f"-> Số lượng Server Tabs tìm thấy: {len(server_elements)}")
    for s in server_elements:
        print(f"   [TAB SERVER] '{s['text']}' | focused: {s['focused']} | bounds: {s['bounds']}")

    print(f"-> Số lượng Tập phim đang hiển thị: {len(episodes)}")
    for ep in episodes[:10]:
        print(f"   [TẬP] '{ep['text']}'")

    if len(server_elements) >= 2:
        print(f"\n--> Chuyển sang Server thứ 2: '{server_elements[1]['text']}'")
        cx2, cy2 = get_center_coords(server_elements[1]['bounds'])
        adb(f"shell input tap {cx2} {cy2}")
        time.sleep(3)
        adb_screencap("emulator_tv_v331_server_switched.png")
        print("✅ Đã chuyển server thành công và chụp màn hình!")
    elif len(server_elements) == 1:
        print(f"ℹ️ Phim này chỉ có 1 server duy nhất ({server_elements[0]['text']}). Thử kiểm tra phim khác có 2 server.")

    # 4. Kiểm tra trên Mobile
    print("\n--- KIỂM TRA DETAIL TRÊN MOBILE ---")
    adb("shell am force-stop com.huycabuonca.tv")
    adb("shell am start -n com.huycabuonca.mobile/.ui.MainActivity")
    time.sleep(5)
    # Bấm "ĐỂ SAU" trên dialog nếu có
    mob_ui = dump_ui()
    mob_cancel = next((el for el in mob_ui if el['text'] == 'ĐỂ SAU'), None)
    if mob_cancel:
        cx, cy = get_center_coords(mob_cancel['bounds'])
        adb(f"shell input tap {cx} {cy}")
        time.sleep(2)

    # Click phim đầu tiên trên Mobile
    mob_ui = dump_ui()
    mob_titles = [el for el in mob_ui if el['id'].endswith('txtTitle')]
    if mob_titles:
        print(f"Mobile: Click vào phim '{mob_titles[0]['text']}'")
        cx, cy = get_center_coords(mob_titles[0]['bounds'])
        adb(f"shell input tap {cx} {cy}")
        time.sleep(5)
        adb_screencap("emulator_mobile_v331_detail_server.png")
        mob_detail = dump_ui()
        mob_servers = [el for el in mob_detail if "Phụ Đề" in el['text'] or "Thuyết Minh" in el['text'] or "Lồng Tiếng" in el['text'] or "Server" in el['text']]
        print(f"Mobile: Tìm thấy {len(mob_servers)} Server Tabs:")
        for s in mob_servers:
            print(f"   [Mobile TAB] '{s['text']}'")

    print("\n=== HOÀN TẤT KIỂM THỬ CHI TIẾT ===")

if __name__ == '__main__':
    main()
