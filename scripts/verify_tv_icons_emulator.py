import os
import sys
import time
import subprocess

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def run_adb(cmd, timeout=30):
    full_cmd = f"adb {cmd}"
    try:
        res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='ignore')
        return res.returncode, res.stdout.strip()
    except Exception as e:
        return -1, str(e)

print("=== ĐỢI GIẢ LẬP ANDROID KHỞI ĐỘNG ===")
for i in range(40):
    code, out = run_adb("shell getprop sys.boot_completed")
    if code == 0 and "1" in out:
        print("✅ Giả lập Android đã sẵn sàng!")
        break
    print(f"Đang chờ khởi động ({i+1}/40)...")
    time.sleep(3)

# Đợi thêm 3s cho UI ổn định
time.sleep(3)

# Cài đặt HuyCa_TV_v3.3.6.apk
print("\n--- Cài đặt HuyCa_TV_v3.3.6.apk ---")
code, out = run_adb("install -r HuyCa_TV_v3.3.6.apk", timeout=60)
print(f"TV Install: {out}")

# Cài đặt HuyCa_Mobile_v3.3.6.apk
print("\n--- Cài đặt HuyCa_Mobile_v3.3.6.apk ---")
code, out = run_adb("install -r HuyCa_Mobile_v3.3.6.apk", timeout=60)
print(f"Mobile Install: {out}")

# 1. TEST TV APP - TAB XEM TIVI
print("\n--- KIỂM THỬ HUY CÁ TV: TAB XEM TIVI & ICONS ---")
run_adb("shell am force-stop com.huycabuonca.tv")
time.sleep(1)
run_adb("shell am start -n com.huycabuonca.tv/.ui.MainActivity")
print("Đã mở com.huycabuonca.tv, đợi 5s tải dữ liệu...")
time.sleep(5)

# Bấm phím RIGHT 3 lần để sang tab "Xem Tivi" (Nguồn -> Phim Ngắn -> Thể Thao -> Xem Tivi)
# Hoặc kiểm tra UI hierarchy
for step in range(5):
    run_adb("shell input keyevent KEYCODE_DPAD_RIGHT")
    time.sleep(0.5)

time.sleep(3)
# Chụp ảnh TV Tab Xem Tivi
run_adb("shell screencap -p /sdcard/tv_xemtivi_icons.png")
run_adb("pull /sdcard/tv_xemtivi_icons.png scripts/emulator_tv_v336_xemtivi.png")
print("Đã chụp ảnh màn hình TV tab Xem Tivi: scripts/emulator_tv_v336_xemtivi.png")

# Scroll xuống một chút trên TV để xem thêm icon các kênh khác
run_adb("shell input keyevent KEYCODE_DPAD_DOWN")
time.sleep(0.5)
run_adb("shell input keyevent KEYCODE_DPAD_DOWN")
time.sleep(1)
run_adb("shell screencap -p /sdcard/tv_xemtivi_icons_down.png")
run_adb("pull /sdcard/tv_xemtivi_icons_down.png scripts/emulator_tv_v336_xemtivi_down.png")
print("Đã chụp ảnh màn hình TV tab Xem Tivi (cuộn xuống): scripts/emulator_tv_v336_xemtivi_down.png")

# 2. TEST MOBILE APP - TAB XEM TIVI
print("\n--- KIỂM THỬ HUY CÁ MOBILE: TAB XEM TIVI & ICONS ---")
run_adb("shell am force-stop com.huycabuonca.mobile")
time.sleep(1)
run_adb("shell am start -n com.huycabuonca.mobile/.ui.MainActivity")
print("Đã mở com.huycabuonca.mobile, đợi 5s tải dữ liệu...")
time.sleep(5)

# Tìm vị trí tab hoặc click vào Xem Tivi trên Mobile
# Lấy dump XML để click đúng tab Xem Tivi
run_adb("shell uiautomator dump /sdcard/mobile_ui.xml")
run_adb("pull /sdcard/mobile_ui.xml scripts/mobile_ui.xml")

# Click tọa độ tab Xem Tivi (thường là menu bar ở trên hoặc dưới)
# Hoặc gửi keyevent hoặc click trực tiếp
run_adb("shell screencap -p /sdcard/mobile_home.png")
run_adb("pull /sdcard/mobile_home.png scripts/emulator_mobile_v336_home.png")

# Dùng script tìm chữ "Tivi" hoặc "Xem Tivi" trong XML
try:
    with open("scripts/mobile_ui.xml", "r", encoding="utf-8") as f:
        xml_content = f.read()
    import re
    # tìm node có text="Xem Tivi" hoặc "Tivi"
    matches = re.findall(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"[^>]*?(?:Xem Tivi|Tivi)', xml_content)
    if not matches:
        matches = re.findall(r'(?:Xem Tivi|Tivi)[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml_content)
    if matches:
        x1, y1, x2, y2 = map(int, matches[0])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        print(f"Click vào tab Tivi tại: ({cx}, {cy})")
        run_adb(f"shell input tap {cx} {cy}")
        time.sleep(4)
        run_adb("shell screencap -p /sdcard/mobile_xemtivi.png")
        run_adb("pull /sdcard/mobile_xemtivi.png scripts/emulator_mobile_v336_xemtivi.png")
        print("Đã chụp ảnh màn hình Mobile tab Xem Tivi: scripts/emulator_mobile_v336_xemtivi.png")
    else:
        print("Không tìm thấy text Tivi trực tiếp trong XML, thử click tọa độ tab Tivi ước lượng")
except Exception as e:
    print(f"Lỗi parse XML: {e}")

print("\n=== HOÀN TẤT KIỂM THỬ GIẢ LẬP ===")
