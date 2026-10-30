import os
import sys
import time
import subprocess
import shutil

if sys.platform == 'win33' or sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"

def run_adb(cmd, timeout=30):
    full_cmd = f"adb {cmd}"
    try:
        res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='ignore')
        return res.returncode, res.stdout.strip()
    except Exception as e:
        return -1, str(e)

print("=== BẮT ĐẦU CHỤP ẢNH MỤC XEM TIVI TRÊN CẢ 2 BẢN APK V3.3.6 ===")

# ----------------- 1. TEST MOBILE APP -----------------
print("\n--- 1. MOBILE APP: CHUYỂN ĐẾN TAB XEM TIVI ---")
run_adb("shell am force-stop com.huycabuonca.mobile")
time.sleep(1)
run_adb("shell am start -n com.huycabuonca.mobile/.ui.MainActivity")
time.sleep(4)

# Tap vào nút [📺 XEM TIVI] tại bounds [545,248][796,343] -> X=670, Y=295
print("Tap vào tab '📺 XEM TIVI' trên Mobile (670, 295)...")
run_adb("shell input tap 670 295")
time.sleep(4)

# Chụp ảnh Mobile tab Xem Tivi
run_adb("shell screencap -p /sdcard/emulator_mobile_v336_xemtivi.png")
run_adb("pull /sdcard/emulator_mobile_v336_xemtivi.png scripts/emulator_mobile_v336_xemtivi.png")
shutil.copy("scripts/emulator_mobile_v336_xemtivi.png", os.path.join(ARTIFACT_DIR, "emulator_mobile_v336_xemtivi.png"))
print(" -> Đã lưu: emulator_mobile_v336_xemtivi.png")

# Cuộn xuống để xem thêm các kênh tiếp theo
print("Cuộn xuống trên Mobile...")
run_adb("shell input swipe 540 1800 540 800 300")
time.sleep(2)
run_adb("shell screencap -p /sdcard/emulator_mobile_v336_xemtivi_scroll.png")
run_adb("pull /sdcard/emulator_mobile_v336_xemtivi_scroll.png scripts/emulator_mobile_v336_xemtivi_scroll.png")
shutil.copy("scripts/emulator_mobile_v336_xemtivi_scroll.png", os.path.join(ARTIFACT_DIR, "emulator_mobile_v336_xemtivi_scroll.png"))
print(" -> Đã lưu: emulator_mobile_v336_xemtivi_scroll.png")


# ----------------- 2. TEST TV APP -----------------
print("\n--- 2. TV APP: CHUYỂN ĐẾN TAB XEM TIVI ---")
run_adb("shell am force-stop com.huycabuonca.tv")
time.sleep(1)
run_adb("shell am start -n com.huycabuonca.tv/.ui.MainActivity")
time.sleep(5)

# Lấy layout dump của TV để biết chính xác các tab trên TV
run_adb("shell uiautomator dump /sdcard/tv_dump.xml")
run_adb("pull /sdcard/tv_dump.xml scripts/tv_dump.xml")

# Nhấn UP lên header tab bar
run_adb("shell input keyevent KEYCODE_DPAD_UP")
time.sleep(0.5)
run_adb("shell input keyevent KEYCODE_DPAD_UP")
time.sleep(0.5)

# Kiểm tra xem có tab Tivi không bằng việc gửi phím điều hướng
# Thông thường: Nguồn (1) -> Phim Ngắn (2) -> Thể Thao (3) -> Xem Tivi (4)
# Di chuyển sang phải 3 lần
for i in range(3):
    run_adb("shell input keyevent KEYCODE_DPAD_RIGHT")
    time.sleep(0.5)

# Nhấn CENTER hoặc DOWN để vào danh sách kênh
run_adb("shell input keyevent KEYCODE_DPAD_CENTER")
time.sleep(0.5)
run_adb("shell input keyevent KEYCODE_DPAD_DOWN")
time.sleep(3)

# Chụp ảnh TV tab Xem Tivi
run_adb("shell screencap -p /sdcard/emulator_tv_v336_xemtivi.png")
run_adb("pull /sdcard/emulator_tv_v336_xemtivi.png scripts/emulator_tv_v336_xemtivi.png")
shutil.copy("scripts/emulator_tv_v336_xemtivi.png", os.path.join(ARTIFACT_DIR, "emulator_tv_v336_xemtivi.png"))
print(" -> Đã lưu: emulator_tv_v336_xemtivi.png")

# Cuộn xuống trên TV
run_adb("shell input keyevent KEYCODE_DPAD_DOWN")
time.sleep(0.5)
run_adb("shell input keyevent KEYCODE_DPAD_DOWN")
time.sleep(2)
run_adb("shell screencap -p /sdcard/emulator_tv_v336_xemtivi_scroll.png")
run_adb("pull /sdcard/emulator_tv_v336_xemtivi_scroll.png scripts/emulator_tv_v336_xemtivi_scroll.png")
shutil.copy("scripts/emulator_tv_v336_xemtivi_scroll.png", os.path.join(ARTIFACT_DIR, "emulator_tv_v336_xemtivi_scroll.png"))
print(" -> Đã lưu: emulator_tv_v336_xemtivi_scroll.png")

print("\n=== HOÀN THÀNH TẤT CẢ CÁC BƯỚC CHỤP ẢNH XÁC THỰC! ===")
