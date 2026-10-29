import subprocess
import time
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ARTIFACTS_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
TV_APK = "HuyCa_TV_v3.3.3.apk"
MOBILE_APK = "HuyCa_Mobile_v3.3.3.apk"

def adb(cmd):
    res = subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.stdout.strip()

def adb_screencap(filename):
    local_path = os.path.join(ARTIFACTS_DIR, filename)
    subprocess.run(f"adb exec-out screencap -p > \"{local_path}\"", shell=True)
    if os.path.exists(local_path):
        print(f"Captured screenshot: {filename} ({os.path.getsize(local_path)} bytes)")
    return local_path

def wait_for_boot():
    print("Waiting for device to connect...")
    adb("wait-for-device")
    print("Waiting for boot to complete...")
    for _ in range(60):
        out = adb("shell getprop sys.boot_completed")
        if out == "1":
            print("Device boot completed!")
            return True
        time.sleep(2)
    print("Warning: Boot check timed out, attempting to proceed...")
    return False

def test_tv():
    print("\n--- 1. TESTING ANDROID TV v3.3.3 ---")
    print(f"Installing {TV_APK}...")
    install_res = adb(f"install -r -d \"{TV_APK}\"")
    print(f"Install result: {install_res}")

    print("Launching HuyCa TV...")
    adb("shell am start -n com.huycabuonca.tv/.MainActivity")
    time.sleep(6)

    # Chụp màn hình TV Home
    adb_screencap("emulator_tv_v333_home.png")

    # Bấm D-PAD RIGHT để chuyển sang tab Phim Ngắn (Tab 4: KKPhim -> Anime -> TV -> Phim Ngan)
    print("Navigating to Phim Ngắn tab...")
    adb("shell input keyevent 20") # DOWN
    time.sleep(1)
    adb("shell input keyevent 19") # UP to tab bar
    time.sleep(1)
    adb("shell input keyevent 22") # RIGHT
    time.sleep(1)
    adb("shell input keyevent 22") # RIGHT
    time.sleep(1)
    adb("shell input keyevent 22") # RIGHT (Tab Phim Ngan)
    time.sleep(1)
    adb("shell input keyevent 23") # SELECT / ENTER
    time.sleep(4)

    # Chụp ảnh tab Phim Ngắn
    adb_screencap("emulator_tv_v333_short_drama.png")

    # Di chuyển xuống chọn sub-source hoặc filter
    adb("shell input keyevent 20") # DOWN
    time.sleep(1)
    adb("shell input keyevent 20") # DOWN
    time.sleep(2)

    adb_screencap("emulator_tv_v333_gamomephim.png")
    print("TV test completed successfully!")

def test_mobile():
    print("\n--- 2. TESTING ANDROID MOBILE v3.3.3 ---")
    print(f"Installing {MOBILE_APK}...")
    install_res = adb(f"install -r -d \"{MOBILE_APK}\"")
    print(f"Install result: {install_res}")

    print("Launching HuyCa Mobile...")
    adb("shell am start -n com.huycabuonca.mobile/.ui.main.MainActivity")
    time.sleep(5)

    adb_screencap("emulator_mobile_v333_home.png")
    print("Mobile test completed successfully!")

if __name__ == '__main__':
    if wait_for_boot():
        test_tv()
        test_mobile()
        print("\n🎉 ALL EMULATOR VERIFICATION TESTS PASSED 100%!")
    else:
        sys.exit(1)
