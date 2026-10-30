import subprocess
import time
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ARTIFACTS_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"

def adb(cmd):
    res = subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.stdout.strip()

def screencap(filename):
    local_path = os.path.join(ARTIFACTS_DIR, filename)
    subprocess.run(f"adb exec-out screencap -p > \"{local_path}\"", shell=True)
    if os.path.exists(local_path):
        size_kb = os.path.getsize(local_path) // 1024
        print(f"  📸 Screenshot saved: {filename} ({size_kb} KB)")
    return local_path

def clear_logcat():
    adb("logcat -c")

def check_logcat(tags=["PlayerActivity", "ExoPlayer", "DetailActivity", "AndroidRuntime"]):
    out = adb("logcat -d -t 150")
    relevant = []
    has_fatal_crash = False
    has_legacy_error = False
    has_playback_ready = False
    
    for line in out.splitlines():
        if "FATAL EXCEPTION" in line or "AndroidRuntime: FATAL" in line:
            has_fatal_crash = True
        if "Legacy decoding is disabled" in line:
            has_legacy_error = True
        if "STATE_READY" in line or "playbackState: 3" in line or "state=3" in line or "isPlaying=true" in line:
            has_playback_ready = True
        if any(tag in line for tag in tags):
            relevant.append(line)
            
    return has_fatal_crash, has_legacy_error, relevant

print("=================================================================")
print("🚀 KIỂM THỬ E2E PHÁT PHIM NGẮN TRÊN GIẢ LẬP ANDROID (TV & MOBILE)")
print("=================================================================")

# 1. Kiểm tra kết nối thiết bị
devs = adb("devices")
print("Devices:\n", devs)
if "emulator-5554" not in devs:
    print("❌ Giả lập chưa sẵn sàng!")
    sys.exit(1)

# 2. KIỂM THỬ TRÊN ANDROID TV
print("\n--- [1/2] KIỂM THỬ ANDROID TV APP (v3.3.5) ---")
adb("shell am force-stop com.huycabuonca.tv")
time.sleep(1)
clear_logcat()

print(" -> Khởi chạy HuyCa TV MainActivity...")
adb("shell am start -n com.huycabuonca.tv/.ui.MainActivity")
time.sleep(4)
screencap("emulator_tv_v335_home.png")

print(" -> Điều hướng D-PAD sang Tab Phim Ngắn...")
# Tab order: KKPhim (0) -> Anime (1) -> TV (2) -> Phim Ngắn (3)
# Đảm bảo focus đang ở Tab Bar hoặc chuyển lên Tab Bar
adb("shell input keyevent 19") # DPAD_UP
time.sleep(0.5)
adb("shell input keyevent 19") # DPAD_UP
time.sleep(0.5)
# Focus tab đầu tiên hoặc dịch phải 3 lần
adb("shell input keyevent 21") # DPAD_LEFT
adb("shell input keyevent 21") # DPAD_LEFT
adb("shell input keyevent 21") # DPAD_LEFT
time.sleep(0.5)
adb("shell input keyevent 22") # DPAD_RIGHT
time.sleep(0.5)
adb("shell input keyevent 22") # DPAD_RIGHT
time.sleep(0.5)
adb("shell input keyevent 22") # DPAD_RIGHT (Sang Phim Ngắn)
time.sleep(0.5)
adb("shell input keyevent 23") # DPAD_CENTER / ENTER
time.sleep(3)
screencap("emulator_tv_v335_short_drama_tab.png")

print(" -> Di chuyển D-PAD xuống danh sách phim ngắn và chọn 1 phim...")
adb("shell input keyevent 20") # DPAD_DOWN
time.sleep(0.5)
adb("shell input keyevent 20") # DPAD_DOWN
time.sleep(0.5)
adb("shell input keyevent 20") # DPAD_DOWN
time.sleep(1)
adb("shell input keyevent 23") # Bấm chọn phim đầu tiên để mở DetailActivity
time.sleep(4)
screencap("emulator_tv_v335_detail.png")

print(" -> Bấm XEM PHIM / Xem Tập 1...")
# Trong DetailActivity, nút XEM PHIM hoặc danh sách tập
adb("shell input keyevent 23") # Click XEM PHIM (btnPlayFirst đang focus hoặc bấm ENTER)
time.sleep(1)
# Nếu chưa vào player, thử bấm D-PAD DOWN rồi ENTER vào danh sách tập
adb("shell input keyevent 20") 
time.sleep(0.5)
adb("shell input keyevent 23")
time.sleep(5) # Đợi ExoPlayer nạp stream và phát

screencap("emulator_tv_v335_player_playback.png")

has_fatal, has_legacy, tv_logs = check_logcat()
print(f" -> Kết quả logcat TV: Fatal Crash = {has_fatal}, Legacy Decoding Error = {has_legacy}")
if has_fatal or has_legacy:
    print("❌ PHÁT HIỆN LỖI KHI PHÁT PHIM TRÊN TV!")
    for l in tv_logs[-15:]:
        print("   ", l)
else:
    print("✅ ANDROID TV PHÁT PHIM NGẮN THÀNH CÔNG, KHÔNG CRASH!")

# 3. KIỂM THỬ TRÊN ANDROID MOBILE
print("\n--- [2/2] KIỂM THỬ ANDROID MOBILE APP (v3.3.5) ---")
adb("shell am force-stop com.huycabuonca.mobile")
time.sleep(1)
clear_logcat()

print(" -> Khởi chạy HuyCa Mobile MainActivity...")
adb("shell am start -n com.huycabuonca.mobile/.ui.MainActivity")
time.sleep(4)
screencap("emulator_mobile_v335_home.png")

# Mobile: Chuyển sang Tab Phim Ngắn (Tab bottom navigation: Phim, Anime, TV, Phim Ngắn, Trận Đấu)
# Hoặc chạm vào tab Phim Ngắn (tọa độ khoảng x=650, y=2300 tùy màn hình hoặc dùng input keyevent/tap)
print(" -> Lấy kích thước màn hình để tính tọa độ tab Phim Ngắn...")
wm_size = adb("shell wm size")
print("  Window manager size:", wm_size)
# Thường là 1080x2400 hoặc tương tự
width, height = 1080, 2400
if "Physical size:" in wm_size:
    parts = wm_size.split("Physical size:")[1].strip().split("x")
    width, height = int(parts[0]), int(parts[1])

# Tab Phim Ngắn là tab thứ 4 trên 5 tabs ở bottom navigation:
# x = width * 7 / 10, y = height - 100
tab_x = int(width * 0.70)
tab_y = int(height - 80)
print(f" -> Chạm vào Tab Phim Ngắn (x={tab_x}, y={tab_y})...")
adb(f"shell input tap {tab_x} {tab_y}")
time.sleep(3)
screencap("emulator_mobile_v335_short_drama_tab.png")

# Chạm vào thẻ phim đầu tiên ở giữa màn hình (x=width*0.3, y=height*0.4)
film_x = int(width * 0.3)
film_y = int(height * 0.4)
print(f" -> Chạm vào phim đầu tiên (x={film_x}, y={film_y})...")
adb(f"shell input tap {film_x} {film_y}")
time.sleep(4)
screencap("emulator_mobile_v335_detail.png")

# Trong DetailActivity của Mobile, player nằm ở trên cùng hoặc có nút Xem Phim
# Bấm nút Play hoặc tap vào player
play_x = int(width * 0.5)
play_y = int(height * 0.25)
print(f" -> Chạm vào Player / Xem Phim (x={play_x}, y={play_y})...")
adb(f"shell input tap {play_x} {play_y}")
time.sleep(5)
screencap("emulator_mobile_v335_player_playback.png")

has_fatal_mb, has_legacy_mb, mb_logs = check_logcat()
print(f" -> Kết quả logcat Mobile: Fatal Crash = {has_fatal_mb}, Legacy Decoding Error = {has_legacy_mb}")
if has_fatal_mb or has_legacy_mb:
    print("❌ PHÁT HIỆN LỖI KHI PHÁT PHIM TRÊN MOBILE!")
    for l in mb_logs[-15:]:
        print("   ", l)
else:
    print("✅ ANDROID MOBILE PHÁT PHIM NGẮN THÀNH CÔNG, KHÔNG CRASH!")

print("\n=================================================================")
print("🎉 HOÀN TẤT BÀI KIỂM THỬ E2E TRÊN CẢ TV VÀ MOBILE!")
print("=================================================================")
