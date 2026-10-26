from PIL import Image
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

src_path = r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b\.user_uploaded\media_1792933902707_008531c4.jpg"
src = Image.open(src_path).convert("RGBA")

# Bố cục ảnh gốc 1024x1024 là ảnh vuông hoàn chỉnh, hiển thị đầy đủ màn hình TV 3D và khủng long bạo chúa.
# Để icon vừa vặn, chuẩn đẹp bình thường như trước (không bị zoom to bè viền), ta dùng toàn bộ ảnh gốc 1024x1024.
square_icon = src.copy()

# TV Banner (16:9 - 320x180): Tạo banner 16:9 với nền tối ăn khớp và đặt hình icon ở giữa cân đối
banner = Image.new("RGBA", (960, 540), (10, 10, 15, 255))
# Resize square_icon vừa chiều cao 540
icon_fit = square_icon.resize((540, 540), Image.Resampling.LANCZOS)
# Dán vào giữa banner 960x540: x = (960-540)//2 = 210
banner.paste(icon_fit, (210, 0), icon_fit)

# Cập nhật cho TV app
tv_mipmap = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192
}

print("1. Cập nhật icon cho HuyCaBuonCa_TV...")
for folder, size in tv_mipmap.items():
    dest_dir = os.path.join(r"HuyCaBuonCa_TV\app\src\main\res", folder)
    os.makedirs(dest_dir, exist_ok=True)
    resized = square_icon.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(os.path.join(dest_dir, "ic_launcher.png"))
    resized.save(os.path.join(dest_dir, "ic_launcher_round.png"))

tv_drawable = r"HuyCaBuonCa_TV\app\src\main\res\drawable"
banner_resized = banner.resize((320, 180), Image.Resampling.LANCZOS)
banner_resized.save(os.path.join(tv_drawable, "tv_banner.png"))

print("2. Cập nhật icon cho HuyCaBuonCa_Mobile...")
for folder, size in tv_mipmap.items():
    dest_dir = os.path.join(r"HuyCaBuonCa_Mobile\app\src\main\res", folder)
    os.makedirs(dest_dir, exist_ok=True)
    resized = square_icon.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(os.path.join(dest_dir, "ic_launcher.png"))
    resized.save(os.path.join(dest_dir, "ic_launcher_round.png"))

print("3. Cập nhật icon cho HuyCa_Windows...")
win_ico_path = r"HuyCa_Windows\app.ico"
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
square_icon.save(win_ico_path, format="ICO", sizes=ico_sizes)

print("4. Cập nhật icon cho HuyCaBuonCa_LG_webOS...")
square_icon.resize((80, 80), Image.Resampling.LANCZOS).save(r"HuyCaBuonCa_LG_webOS\icon.png")
square_icon.resize((130, 130), Image.Resampling.LANCZOS).save(r"HuyCaBuonCa_LG_webOS\largeIcon.png")

print("Hoàn tất cập nhật icon về kích thước bình thường đẹp mắt!")
