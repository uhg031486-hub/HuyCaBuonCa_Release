import os
from PIL import Image

for fname in ['emulator_tv_v333_home.png', 'emulator_tv_v333_short_drama.png', 'emulator_tv_v333_gamomephim.png', 'emulator_mobile_v333_home.png']:
    p = os.path.join(r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b", fname)
    if os.path.exists(p):
        img = Image.open(p)
        colors = img.getcolors(maxcolors=256)
        print(f"File {fname}: size={img.size}, mode={img.mode}, distinct colors count={len(colors) if colors else '>256'}")
        if colors and len(colors) <= 5:
            print("  Almost entirely single color:", colors)
