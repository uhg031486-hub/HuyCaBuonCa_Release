import os
import sys
import time
import subprocess
import shutil

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"

def run_adb(cmd):
    full_cmd = f"adb wait-for-device {cmd}"
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.returncode, res.stdout.strip()

print("Chụp ảnh TV Tab Xem Tivi...")
run_adb("shell screencap -p /sdcard/tv_tab.png")
time.sleep(1)
run_adb("pull /sdcard/tv_tab.png scripts/emulator_tv_v336_xemtivi_tab.png")
if os.path.exists("scripts/emulator_tv_v336_xemtivi_tab.png"):
    shutil.copy("scripts/emulator_tv_v336_xemtivi_tab.png", os.path.join(ARTIFACT_DIR, "emulator_tv_v336_xemtivi_tab.png"))
    print(" -> Đã lưu emulator_tv_v336_xemtivi_tab.png")
else:
    print(" ⚠️ Không tìm thấy scripts/emulator_tv_v336_xemtivi_tab.png")

print("Cuộn xuống danh sách kênh TV...")
for i in range(5):
    run_adb("shell input keyevent KEYCODE_DPAD_DOWN")
    time.sleep(0.4)

time.sleep(2)
run_adb("shell screencap -p /sdcard/tv_grid.png")
time.sleep(1)
run_adb("pull /sdcard/tv_grid.png scripts/emulator_tv_v336_channels_grid.png")
if os.path.exists("scripts/emulator_tv_v336_channels_grid.png"):
    shutil.copy("scripts/emulator_tv_v336_channels_grid.png", os.path.join(ARTIFACT_DIR, "emulator_tv_v336_channels_grid.png"))
    print(" -> Đã lưu emulator_tv_v336_channels_grid.png")

# Cuộn thêm để xem kênh thể thao, tin tức
for i in range(4):
    run_adb("shell input keyevent KEYCODE_DPAD_DOWN")
    time.sleep(0.4)

time.sleep(2)
run_adb("shell screencap -p /sdcard/tv_grid2.png")
time.sleep(1)
run_adb("pull /sdcard/tv_grid2.png scripts/emulator_tv_v336_channels_grid2.png")
if os.path.exists("scripts/emulator_tv_v336_channels_grid2.png"):
    shutil.copy("scripts/emulator_tv_v336_channels_grid2.png", os.path.join(ARTIFACT_DIR, "emulator_tv_v336_channels_grid2.png"))
    print(" -> Đã lưu emulator_tv_v336_channels_grid2.png")

print("\n--- CHỤP TIẾP ỨNG DỤNG MOBILE KHI MỞ TAB XEM TIVI ---")
run_adb("shell am start -n com.huycabuonca.mobile/.ui.MainActivity")
time.sleep(4)
run_adb("shell input tap 670 295") # Nút 📺 XEM TIVI
time.sleep(4)
run_adb("shell screencap -p /sdcard/mobile_tv.png")
time.sleep(1)
run_adb("pull /sdcard/mobile_tv.png scripts/emulator_mobile_v336_xemtivi.png")
if os.path.exists("scripts/emulator_mobile_v336_xemtivi.png"):
    shutil.copy("scripts/emulator_mobile_v336_xemtivi.png", os.path.join(ARTIFACT_DIR, "emulator_mobile_v336_xemtivi.png"))
    print(" -> Đã lưu emulator_mobile_v336_xemtivi.png")

# Cuộn xuống trên Mobile
run_adb("shell input swipe 540 1800 540 800 300")
time.sleep(2)
run_adb("shell screencap -p /sdcard/mobile_tv_scroll.png")
time.sleep(1)
run_adb("pull /sdcard/mobile_tv_scroll.png scripts/emulator_mobile_v336_xemtivi_scroll.png")
if os.path.exists("scripts/emulator_mobile_v336_xemtivi_scroll.png"):
    shutil.copy("scripts/emulator_mobile_v336_xemtivi_scroll.png", os.path.join(ARTIFACT_DIR, "emulator_mobile_v336_xemtivi_scroll.png"))
    print(" -> Đã lưu emulator_mobile_v336_xemtivi_scroll.png")

print("=== HOÀN TẤT CHỤP ẢNH TẤT CẢ GIAO DIỆN KÊNH TV! ===")
