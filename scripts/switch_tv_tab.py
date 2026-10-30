import os
import sys
import time
import subprocess
import shutil

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"

def run_adb(cmd):
    full_cmd = f"adb {cmd}"
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.returncode, res.stdout.strip()

print("Bấm vào tab '📺 XEM TIVI' trên TV (1174, 107)...")
run_adb("shell input tap 1174 107")
time.sleep(4)

# Dump lại UI của TV để xác nhận
run_adb("shell uiautomator dump /sdcard/tv_tivi_dump.xml")
run_adb("pull /sdcard/tv_tivi_dump.xml scripts/tv_tivi_dump.xml")

# Chụp ảnh TV tab Xem Tivi
run_adb("shell screencap -p /sdcard/emulator_tv_v336_xemtivi.png")
run_adb("pull /sdcard/emulator_tv_v336_xemtivi.png scripts/emulator_tv_v336_xemtivi.png")
shutil.copy("scripts/emulator_tv_v336_xemtivi.png", os.path.join(ARTIFACT_DIR, "emulator_tv_v336_xemtivi.png"))
print("Đã chụp TV tab Xem Tivi!")

# Nhấn DOWN để focus vào grid kênh
run_adb("shell input keyevent KEYCODE_DPAD_DOWN")
time.sleep(1)
run_adb("shell input keyevent KEYCODE_DPAD_DOWN")
time.sleep(1)
run_adb("shell screencap -p /sdcard/emulator_tv_v336_xemtivi_focus.png")
run_adb("pull /sdcard/emulator_tv_v336_xemtivi_focus.png scripts/emulator_tv_v336_xemtivi_focus.png")
shutil.copy("scripts/emulator_tv_v336_xemtivi_focus.png", os.path.join(ARTIFACT_DIR, "emulator_tv_v336_xemtivi_focus.png"))
print("Đã chụp TV tab Xem Tivi focus!")
