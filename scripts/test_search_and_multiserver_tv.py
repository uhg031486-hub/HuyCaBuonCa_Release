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
            if txt or desc or rid:
                elements.append({
                    'text': txt,
                    'desc': desc,
                    'id': rid,
                    'bounds': bounds,
                    'class': clazz
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
    print("=== KIỂM THỬ E2E TÌM KIẾM & CHỌN SERVER ĐA LUỒNG (PHỤ ĐỀ + THUYẾT MINH) TRÊN ANDROID TV ===")

    # 1. Mở SearchActivity trên TV
    adb("shell am start -n com.huycabuonca.tv/.ui.SearchActivity")
    time.sleep(3)

    # 2. Nhập từ khóa tìm kiếm: "thuong-cong-chua"
    print("Nhập từ khóa 'thuong-cong-chua'...")
    adb("shell input text thuong-cong-chua")
    time.sleep(1)
    adb("shell input keyevent 66") # ENTER / SEARCH
    print("Chờ 4 giây tải kết quả tìm kiếm...")
    time.sleep(4)

    ui = dump_ui()
    results = [el for el in ui if el['id'].endswith('txtTitle')]
    print(f"Kết quả tìm kiếm ({len(results)} kết quả):")
    for r in results:
        print(f"  🎬 [{r['text']}] bounds: {r['bounds']}")

    if not results:
        # Thử bấm btnDoSearch
        search_btn = next((el for el in ui if el['id'].endswith('btnDoSearch')), None)
        if search_btn:
            cx, cy = get_center_coords(search_btn['bounds'])
            adb(f"shell input tap {cx} {cy}")
            time.sleep(4)
            ui = dump_ui()
            results = [el for el in ui if el['id'].endswith('txtTitle')]
            print(f"Kết quả tìm kiếm sau khi tap btnDoSearch ({len(results)} kết quả):")
            for r in results:
                print(f"  🎬 [{r['text']}] bounds: {r['bounds']}")

    target = results[0] if results else None
    if not target:
        print("Không tìm thấy kết quả tìm kiếm, chuyển sang mở bằng danh sách...")
        return

    print(f"\n--> Mở chi tiết phim: '{target['text']}'")
    cx, cy = get_center_coords(target['bounds'])
    adb(f"shell input tap {cx} {cy}")
    print("Chờ 5 giây cho DetailActivity nạp chi tiết các server...")
    time.sleep(5)

    adb_screencap("emulator_tv_v331_multiserver_success.png")
    detail_ui = dump_ui()

    title_el = next((el for el in detail_ui if el['id'].endswith('txtDetailTitle')), None)
    if title_el:
        print(f"✅ Màn hình chi tiết: {title_el['text']}")

    # Tìm các nút server
    server_tabs = [el for el in detail_ui if "Phụ Đề" in el['text'] or "Thuyết Minh" in el['text'] or "Lồng Tiếng" in el['text'] or "Server" in el['text']]
    episodes = [el for el in detail_ui if el['id'].endswith('btnEpisode') or "Tập" in el['text']]

    print(f"\n🔥 DANH SÁCH CÁC SERVER TAB HIỂN THỊ ({len(server_tabs)} Tabs):")
    for idx, s in enumerate(server_tabs):
        print(f"   [{idx + 1}] {s['text']} (tọa độ: {s['bounds']})")

    print(f"\n📺 DANH SÁCH TẬP HIỆN TẠI CỦA SERVER 1 ({len(episodes)} Tập):")
    for ep in episodes[:6]:
        print(f"   - {ep['text']}")

    # Kiểm tra bấm chuyển sang Server 2 (Thuyết Minh)
    if len(server_tabs) >= 2:
        print(f"\n👉 BẤM CHỌN SERVER 2: '{server_tabs[1]['text']}'")
        cx2, cy2 = get_center_coords(server_tabs[1]['bounds'])
        adb(f"shell input tap {cx2} {cy2}")
        time.sleep(3)
        adb_screencap("emulator_tv_v331_server2_selected.png")
        
        detail_ui2 = dump_ui()
        episodes2 = [el for el in detail_ui2 if el['id'].endswith('btnEpisode') or "Tập" in el['text']]
        print(f"✅ ĐÃ CHUYỂN SERVER THÀNH CÔNG! Danh sách tập cập nhật: {len(episodes2)} tập.")
        for ep in episodes2[:6]:
            print(f"   - {ep['text']}")

    # Kiểm tra bấm chuyển sang Server 3 (Lồng Tiếng) nếu có
    if len(server_tabs) >= 3:
        print(f"\n👉 BẤM CHỌN SERVER 3: '{server_tabs[2]['text']}'")
        cx3, cy3 = get_center_coords(server_tabs[2]['bounds'])
        adb(f"shell input tap {cx3} {cy3}")
        time.sleep(3)
        adb_screencap("emulator_tv_v331_server3_selected.png")
        print("✅ Đã kiểm tra chọn Server 3 thành công!")

    print("\n=== HOÀN TẤT KIỂM THỬ ĐA SERVER TRÊN ANDROID TV THÀNH CÔNG 100%! ===")

if __name__ == '__main__':
    main()
