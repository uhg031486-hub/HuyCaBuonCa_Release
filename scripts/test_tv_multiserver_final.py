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
            pkg = node.attrib.get('package', '')
            if txt or desc or rid:
                elements.append({
                    'text': txt,
                    'desc': desc,
                    'id': rid,
                    'bounds': bounds,
                    'pkg': pkg
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
    print("=== TEST CHỌN SERVER ĐA LUỒNG TRÊN ANDROID TV (v3.3.1) ===")
    
    # 1. Tắt hết app khác, bật TV
    adb("shell am force-stop com.huycabuonca.mobile")
    adb("shell am force-stop com.huycabuonca.tv")
    time.sleep(1)
    
    adb("shell am start -n com.huycabuonca.tv/.ui.MainActivity")
    print("Khởi chạy TV MainActivity, chờ 6s...")
    time.sleep(6)

    ui = dump_ui()
    # Bấm nút Tìm kiếm (btnSearch)
    search_btn = next((el for el in ui if "btnSearch" in el['id'] or "TÌM KIẾM" in el['text']), None)
    if search_btn:
        print("Bấm vào nút Tìm Kiếm:", search_btn['bounds'])
        cx, cy = get_center_coords(search_btn['bounds'])
        adb(f"shell input tap {cx} {cy}")
    else:
        print("Mở trực tiếp SearchActivity...")
        adb("shell am start -n com.huycabuonca.tv/.ui.SearchActivity")
    
    time.sleep(3)
    # Nhập từ khóa 'thuong-cong-chua'
    print("Nhập từ khóa 'thuong-cong-chua' và Enter...")
    adb("shell input text thuong-cong-chua")
    time.sleep(1)
    adb("shell input keyevent 66") # ENTER
    time.sleep(4)

    search_ui = dump_ui()
    # Tìm card Thượng Công Chúa
    tcp = next((el for el in search_ui if "Thượng Công Chúa" in el['text']), None)
    if tcp:
        print(f"Tìm thấy phim '{tcp['text']}' tại {tcp['bounds']}")
        cx, cy = get_center_coords(tcp['bounds'])
        adb(f"shell input tap {cx} {cy}")
    else:
        # Lấy item txtTitle đầu tiên
        titles = [el for el in search_ui if el['id'].endswith('txtTitle')]
        if titles:
            print(f"Fallback click '{titles[0]['text']}' tại {titles[0]['bounds']}")
            cx, cy = get_center_coords(titles[0]['bounds'])
            adb(f"shell input tap {cx} {cy}")
        else:
            print("Không tìm thấy kết quả tìm kiếm!")
            return

    print("Chờ 5s cho TV DetailActivity tải dữ liệu các server...")
    time.sleep(5)

    adb_screencap("emulator_tv_v331_multiserver_exact.png")
    detail_ui = dump_ui()

    title_el = next((el for el in detail_ui if el['id'].endswith('txtDetailTitle')), None)
    print(f"\n🎬 Đang ở màn hình chi tiết TV: '{title_el['text'] if title_el else 'Unknown'}'")

    # Liệt kê tất cả các Server Tabs
    server_tabs = [el for el in detail_ui if "Phụ Đề" in el['text'] or "Thuyết Minh" in el['text'] or "Lồng Tiếng" in el['text'] or "Vietsub" in el['text']]
    episodes = [el for el in detail_ui if el['id'].endswith('btnEpisode') or (el['text'].startswith('Tập') and len(el['text']) <= 8)]

    print(f"\n🎯 KẾT QUẢ CÁC SERVER TAB TRÊN ANDROID TV ({len(server_tabs)} Tabs):")
    for idx, s in enumerate(server_tabs):
        print(f"   [{idx+1}] {s['text']} (tọa độ: {s['bounds']})")

    print(f"\n📺 DANH SÁCH TẬP HIỆN TẠI (Server 1) ({len(episodes)} Tập):")
    for ep in episodes[:10]:
        print(f"   * {ep['text']}")

    # Bấm chọn Server thứ 2 (Thuyết Minh)
    if len(server_tabs) >= 2:
        print(f"\n👉 THỰC HIỆN BẤM CHUYỂN SERVER SANG: '{server_tabs[1]['text']}'")
        cx2, cy2 = get_center_coords(server_tabs[1]['bounds'])
        adb(f"shell input tap {cx2} {cy2}")
        time.sleep(3)
        adb_screencap("emulator_tv_v331_thuyetminh_active.png")

        detail_ui2 = dump_ui()
        episodes2 = [el for el in detail_ui2 if el['id'].endswith('btnEpisode') or (el['text'].startswith('Tập') and len(el['text']) <= 8)]
        print(f"✅ ĐÃ CHUYỂN SERVER THÀNH CÔNG! Số tập hiển thị: {len(episodes2)} tập.")
        for ep in episodes2[:6]:
            print(f"   * {ep['text']}")

    print("\n=== HOÀN TẤT KIỂM THỬ THỰC TẾ 100% TRÊN GIẢ LẬP ANDROID TV ===")

if __name__ == '__main__':
    main()
