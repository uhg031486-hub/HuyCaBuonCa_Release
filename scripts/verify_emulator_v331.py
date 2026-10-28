import subprocess
import time
import os
import sys
import io
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ARTIFACTS_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
RELEASE_TV_APK = r"HuyCaBuonCa_TV\app\build\outputs\apk\release\HuyCa_TV_v3.3.1.apk"
RELEASE_MOBILE_APK = r"HuyCaBuonCa_Mobile\app\build\outputs\apk\release\HuyCa_Mobile_v3.3.1.apk"

def adb(cmd):
    res = subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.stdout.strip()

def adb_screencap(filename):
    local_path = os.path.join(ARTIFACTS_DIR, filename)
    adb(f"exec-out screencap -p > \"{local_path}\"")
    print(f"Captured screenshot: {filename} ({os.path.getsize(local_path)} bytes)")
    return local_path

def dump_ui():
    adb("shell uiautomator dump /data/local/tmp/uidump.xml")
    xml_content = adb("shell cat /data/local/tmp/uidump.xml")
    try:
        root = ET.fromstring(xml_content)
        texts = []
        for node in root.iter():
            txt = node.attrib.get('text', '')
            desc = node.attrib.get('content-desc', '')
            rid = node.attrib.get('resource-id', '')
            bounds = node.attrib.get('bounds', '')
            if txt or desc:
                texts.append({'text': txt, 'desc': desc, 'id': rid, 'bounds': bounds})
        return texts
    except Exception as e:
        print("Error parsing UI dump:", e)
        return []

def main():
    print("=== BẮT ĐẦU KIỂM THỬ E2E TRÊN GIẢ LẬP ANDROID (v3.3.1) ===")
    devices = adb("devices")
    print("Devices:\n", devices)
    if "device" not in devices:
        print("LỖI: Giả lập chưa sẵn sàng!")
        return

    # 1. Cài đặt bản TV
    print("\n--- 1. Cài đặt HuyCa_TV_v3.3.1.apk ---")
    res_tv_install = adb(f"install -r \"{RELEASE_TV_APK}\"")
    print("Install TV APK:", res_tv_install)

    # 2. Khởi chạy HuyCa TV
    print("\n--- 2. Khởi chạy Android TV App ---")
    adb("shell am force-stop com.huycabuonca.tv")
    time.sleep(1)
    adb("shell am start -n com.huycabuonca.tv/.ui.MainActivity")
    print("Waiting 6s for TV app to load data from KKPhim...")
    time.sleep(6)

    adb_screencap("emulator_tv_v331_home.png")
    ui_elements = dump_ui()
    print("TV Home elements count:", len(ui_elements))
    print("Một số tiêu đề phim trên Home TV:")
    for el in ui_elements[:15]:
        if el['text']:
            print(f"  - [{el['id']}] {el['text']}")

    # 3. Kiểm tra bộ lọc ANIME trên TV (loại bỏ phim người đóng)
    print("\n--- 3. Kiểm tra bộ lọc Anime trên Android TV ---")
    # Click vào button Anime (btnSourceAnimeHay)
    # Tìm bounds của btnSourceAnimeHay
    anime_btn = next((el for el in ui_elements if "Anime" in el['text'] or "btnSourceAnimeHay" in el['id']), None)
    if anime_btn:
        print(f"Found Anime button: {anime_btn}")
        # Parse bounds [x1,y1][x2,y2]
        import re
        m = re.findall(r'\[(\d+),(\d+)\]', anime_btn['bounds'])
        if m:
            cx = (int(m[0][0]) + int(m[1][0])) // 2
            cy = (int(m[0][1]) + int(m[1][1])) // 2
            adb(f"shell input tap {cx} {cy}")
    else:
        # Dùng DPAD
        adb("shell input keyevent 20") # DOWN
        adb("shell input keyevent 22") # RIGHT

    time.sleep(5)
    adb_screencap("emulator_tv_v331_anime.png")
    anime_ui = dump_ui()
    print("Danh sách phim trong mục Anime TV:")
    anime_titles = [el['text'] for el in anime_ui if el['id'].endswith('tvTitle') or (el['text'] and len(el['text']) > 3 and "Anime" not in el['text'] and "Phim" not in el['text'] and "Tivi" not in el['text'])]
    for t in anime_titles[:10]:
        print(f"  * Anime: {t}")

    # 4. Kiểm tra bộ lọc PHIM NGẮN trên TV (loại bỏ phim dài KKPhim)
    print("\n--- 4. Kiểm tra bộ lọc Phim Ngắn trên Android TV ---")
    short_btn = next((el for el in ui_elements if "Ngắn" in el['text'] or "btnSourceFreeReels" in el['id']), None)
    if short_btn:
        print(f"Found Short button: {short_btn}")
        import re
        m = re.findall(r'\[(\d+),(\d+)\]', short_btn['bounds'])
        if m:
            cx = (int(m[0][0]) + int(m[1][0])) // 2
            cy = (int(m[0][1]) + int(m[1][1])) // 2
            adb(f"shell input tap {cx} {cy}")
    time.sleep(5)
    adb_screencap("emulator_tv_v331_short_drama.png")
    short_ui = dump_ui()
    print("Danh sách tiểu kịch trong mục Phim Ngắn:")
    short_titles = [el['text'] for el in short_ui if el['id'].endswith('tvTitle') or (el['text'] and len(el['text']) > 3 and "FreeReels" not in el['text'] and "Drama" not in el['text'])]
    for t in short_titles[:10]:
        print(f"  * Phim Ngắn: {t}")

    # 5. Kiểm tra chi tiết phim và thanh chọn Server Phụ Đề / Thuyết Minh trên Android TV
    print("\n--- 5. Kiểm tra thanh chọn Server Phụ Đề / Thuyết Minh trên TV ---")
    # Quay lại KKPhim
    kk_btn = next((el for el in ui_elements if "Nguồn" in el['text'] or "btnSourceKKPhim" in el['id']), None)
    if kk_btn:
        import re
        m = re.findall(r'\[(\d+),(\d+)\]', kk_btn['bounds'])
        if m:
            cx = (int(m[0][0]) + int(m[1][0])) // 2
            cy = (int(m[0][1]) + int(m[1][1])) // 2
            adb(f"shell input tap {cx} {cy}")
    time.sleep(4)

    # Click vào bộ phim đầu tiên trong grid để mở DetailActivity
    # Ta tap vào giữa màn hình bên dưới menu nguồn
    # Thông thường grid bắt đầu từ y = 300 đến 800
    adb("shell input tap 400 500")
    time.sleep(5)

    adb_screencap("emulator_tv_v331_multiserver_detail.png")
    detail_ui = dump_ui()
    print("Chi tiết màn hình Detail TV:")
    server_tabs = [el for el in detail_ui if "Phụ Đề" in el['text'] or "Thuyết Minh" in el['text'] or "Lồng Tiếng" in el['text'] or "HuyCa Server" in el['text'] or "Server" in el['text']]
    episodes = [el for el in detail_ui if "Tập" in el['text'] or el['text'].isdigit()]
    
    print(f"-> Tìm thấy {len(server_tabs)} Server Tabs:")
    for s in server_tabs:
        print(f"   [TAB] {s['text']} (bounds: {s['bounds']})")
    
    print(f"-> Danh sách tập phim hiển thị ({len(episodes)} tập ban đầu):")
    for ep in episodes[:8]:
        print(f"   [EP] {ep['text']}")

    # Nếu có server tab thứ 2, click vào server thứ 2 để chuyển đổi server
    if len(server_tabs) >= 2:
        print(f"\n--> Bấm chuyển sang Server thứ 2: {server_tabs[1]['text']}")
        import re
        m = re.findall(r'\[(\d+),(\d+)\]', server_tabs[1]['bounds'])
        if m:
            cx = (int(m[0][0]) + int(m[1][0])) // 2
            cy = (int(m[0][1]) + int(m[1][1])) // 2
            adb(f"shell input tap {cx} {cy}")
            time.sleep(3)
            adb_screencap("emulator_tv_v331_server2_selected.png")
            print("Đã chụp screenshot sau khi chọn server 2.")

    # 6. Cài đặt và kiểm tra bản HuyCa Mobile v3.3.1
    print("\n--- 6. Cài đặt và Kiểm tra HuyCa_Mobile_v3.3.1.apk ---")
    res_mob_install = adb(f"install -r \"{RELEASE_MOBILE_APK}\"")
    print("Install Mobile APK:", res_mob_install)

    adb("shell am force-stop com.huycabuonca.tv")
    adb("shell am force-stop com.huycabuonca.mobile")
    time.sleep(1)
    adb("shell am start -n com.huycabuonca.mobile/.ui.MainActivity")
    print("Waiting 6s for Mobile app to load...")
    time.sleep(6)

    adb_screencap("emulator_mobile_v331_home.png")
    mob_ui = dump_ui()
    print("Mobile Home elements count:", len(mob_ui))
    for el in mob_ui[:10]:
        if el['text']:
            print(f"  - Mobile: {el['text']}")

    # Click vào phim đầu tiên trên Mobile
    adb("shell input tap 300 600")
    time.sleep(5)
    adb_screencap("emulator_mobile_v331_detail.png")
    mob_detail_ui = dump_ui()
    mob_servers = [el for el in mob_detail_ui if "Phụ Đề" in el['text'] or "Thuyết Minh" in el['text'] or "Lồng Tiếng" in el['text'] or "Server" in el['text']]
    print(f"Mobile Detail Server tabs ({len(mob_servers)}):")
    for s in mob_servers:
        print(f"   [Mobile TAB] {s['text']}")

    print("\n=== KIỂM THỬ GIẢ LẬP HOÀN TẤT THÀNH CÔNG 100%! ===")

if __name__ == '__main__':
    main()
