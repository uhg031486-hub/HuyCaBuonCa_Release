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
    print("=== MỞ CHI TIẾT PHIM ĐA SERVER 'THƯỢNG CÔNG CHÚA' TRÊN ANDROID TV ===")

    # Mở lại SearchActivity
    adb("shell am start -n com.huycabuonca.tv/.ui.SearchActivity")
    time.sleep(2)
    ui = dump_ui()
    
    # Tìm node chứa chữ Thượng Công Chúa
    tcp = next((el for el in ui if "Thượng Công Chúa" in el['text']), None)
    if not tcp:
        adb("shell input text thuong-cong-chua")
        time.sleep(1)
        adb("shell input keyevent 66")
        time.sleep(3)
        ui = dump_ui()
        tcp = next((el for el in ui if "Thượng Công Chúa" in el['text']), None)

    if tcp:
        print(f"Tìm thấy phim: '{tcp['text']}' tại bounds: {tcp['bounds']}")
        cx, cy = get_center_coords(tcp['bounds'])
        adb(f"shell input tap {cx} {cy}")
    else:
        print("Fallback click tọa độ [194, 2065]")
        adb("shell input tap 194 2065")

    print("Chờ 5 giây nạp dữ liệu chi tiết đa server...")
    time.sleep(5)

    adb_screencap("emulator_tv_v331_thuongcongchua_detail.png")
    detail_ui = dump_ui()

    title_el = next((el for el in detail_ui if el['id'].endswith('txtDetailTitle')), None)
    if title_el:
        print(f"🎬 Phim đang xem: {title_el['text']}")

    # Kiểm tra các Server Tab
    server_tabs = [el for el in detail_ui if "Phụ Đề" in el['text'] or "Thuyết Minh" in el['text'] or "Lồng Tiếng" in el['text'] or "Server" in el['text']]
    episodes = [el for el in detail_ui if el['id'].endswith('btnEpisode') or "Tập" in el['text']]

    print(f"\n🎉 KẾT QUẢ DANH SÁCH SERVER TABS ({len(server_tabs)} Tabs):")
    for idx, s in enumerate(server_tabs):
        print(f"   Tab [{idx+1}]: '{s['text']}' tại tọa độ {s['bounds']}")

    print(f"\n📺 Danh sách tập ban đầu (Server 1) ({len(episodes)} tập):")
    for ep in episodes[:8]:
        print(f"   - {ep['text']}")

    # Bấm chọn Server 2 (Thuyết Minh)
    tm_tab = next((s for s in server_tabs if "Thuyết Minh" in s['text']), None)
    if tm_tab:
        print(f"\n👉 Chuyển sang Tab Thuyết Minh: '{tm_tab['text']}'")
        cx_tm, cy_tm = get_center_coords(tm_tab['bounds'])
        adb(f"shell input tap {cx_tm} {cy_tm}")
        time.sleep(3)
        adb_screencap("emulator_tv_v331_thuyetminh_selected.png")
        print("Đã chụp screenshot Server Thuyết Minh.")

    # Bấm chọn Server 3 (Lồng Tiếng)
    lt_tab = next((s for s in server_tabs if "Lồng Tiếng" in s['text']), None)
    if lt_tab:
        print(f"\n👉 Chuyển sang Tab Lồng Tiếng: '{lt_tab['text']}'")
        cx_lt, cy_lt = get_center_coords(lt_tab['bounds'])
        adb(f"shell input tap {cx_lt} {cy_lt}")
        time.sleep(3)
        adb_screencap("emulator_tv_v331_longtieng_selected.png")
        print("Đã chụp screenshot Server Lồng Tiếng.")

    print("\n=== HOÀN TẤT KIỂM THỬ ĐA SERVER CHI TIẾT TRÊN TV ===")

if __name__ == '__main__':
    main()
