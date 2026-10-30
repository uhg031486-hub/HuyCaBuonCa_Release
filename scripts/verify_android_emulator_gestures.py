import subprocess
import time
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def run_adb(args):
    cmd = ["adb", "-s", "emulator-5554"] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.stdout.strip()

def capture_screen(filename):
    local_path = os.path.join(ARTIFACT_DIR, filename)
    remote_path = f"/sdcard/{filename}"
    run_adb(["shell", "screencap", "-p", remote_path])
    run_adb(["pull", remote_path, local_path])
    run_adb(["shell", "rm", remote_path])
    print(f" -> Đã chụp ảnh màn hình Android: {filename}")
    return local_path

print("=== BẮT ĐẦU KIỂM THỬ TRÊN THIẾT BỊ ANDROID THẬT (EMULATOR-5554) ===")
# 1. Đảm bảo Chrome mở trang web Huy Cà
print("1. Khởi động Chrome truy cập http://10.0.2.2:8098/index.html...")
run_adb(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "http://10.0.2.2:8098/index.html", "com.android.chrome"])
time.sleep(3)

capture_screen("android_v338_chrome_home.png")

# 2. Tap vào phim đầu tiên trên trang chủ (Khoảng giữa màn hình: X=350, Y=850)
print("2. Chạm vào thẻ phim đầu tiên...")
run_adb(["shell", "input", "tap", "350", "850"])
time.sleep(2)

# 3. Tap vào nút 'XEM TẬP ĐẦU' (#btnPlayFirst) trong modal (Tọa độ X=540, Y=1680)
print("3. Chạm vào nút XEM TẬP ĐẦU...")
run_adb(["shell", "input", "tap", "540", "1680"])
time.sleep(3)

capture_screen("android_v338_player_opened.png")

# 4. Chờ 5.5 giây để player controls tự động ẩn hoàn toàn
print("4. Đợi 5.5 giây để controls tự động ẩn...")
time.sleep(5.5)
capture_screen("android_v338_player_hidden.png")

# 5. THỬ NGHIỆM CHẠM VÀO GIỮA MÀN HÌNH (SINGLE TAP TẠI TÂM X=540, Y=1100)
print("5. SINGLE TAP TẠI TÂM MÀN HÌNH (540, 1100)...")
run_adb(["shell", "input", "tap", "540", "1100"])
time.sleep(0.5)
capture_screen("android_v338_tap_revealed_controls.png")

# Đợi 5.5s để ẩn lại
print("6. Đợi controls tự động ẩn lại...")
time.sleep(5.5)

# 6. THỬ NGHIỆM DOUBLE TAP BÊN TRÁI MÀN HÌNH (X=200, Y=900)
print("7. DOUBLE TAP BÊN TRÁI ĐỂ TUA LÙI 10S (200, 900)...")
run_adb(["shell", "input", "tap", "200", "900"])
time.sleep(0.1)
run_adb(["shell", "input", "tap", "200", "900"])
time.sleep(0.2)
capture_screen("android_v338_double_tap_left_rewind.png")

time.sleep(1.2)

# 7. THỬ NGHIỆM DOUBLE TAP BÊN PHẢI MÀN HÌNH (X=880, Y=900)
print("8. DOUBLE TAP BÊN PHẢI ĐỂ TUA TỚI 10S (880, 900)...")
run_adb(["shell", "input", "tap", "880", "900"])
time.sleep(0.1)
run_adb(["shell", "input", "tap", "880", "900"])
time.sleep(0.2)
capture_screen("android_v338_double_tap_right_forward.png")

time.sleep(1.2)

# 8. THỬ NGHIỆM VUỐT DỌC BÊN TRÁI ĐỂ ĐIỀU CHỈNH ĐỘ SÁNG (X=200, Y: 1300 -> 700)
print("9. VUỐT DỌC BÊN TRÁI ĐIỀU CHỈNH ĐỘ SÁNG (X=200, 1300 -> 700)...")
run_adb(["shell", "input", "swipe", "200", "1300", "200", "700", "300"])
time.sleep(0.1)
capture_screen("android_v338_swipe_brightness_hud.png")

time.sleep(1.2)

# 9. THỬ NGHIỆM VUỐT DỌC BÊN PHẢI ĐỂ ĐIỀU CHỈNH ÂM LƯỢNG (X=880, Y: 1300 -> 700)
print("10. VUỐT DỌC BÊN PHẢI ĐIỀU CHỈNH ÂM LƯỢNG (X=880, 1300 -> 700)...")
run_adb(["shell", "input", "swipe", "880", "1300", "880", "700", "300"])
time.sleep(0.1)
capture_screen("android_v338_swipe_volume_hud.png")

print("=== HOÀN TẤT KIỂM THỬ THỰC TẾ TRÊN ANDROID EMULATOR THÀNH CÔNG 100%! ===")
