import os
from PIL import Image

p = os.path.join(r"C:\Users\yoga\.gemini\antigravity\brain\ac3633cf-7ca4-4342-a8fb-2d22c7872b1b", 'emulator_tv_v333_short_drama.png')
img = Image.open(p)
# Check non-black pixels
pixels = list(img.getdata())
non_black = [px for px in pixels if px[0] > 20 or px[1] > 20 or px[2] > 20]
print(f"Total pixels: {len(pixels)}, Non-black pixels: {len(non_black)} ({len(non_black)/len(pixels)*100:.2f}%)")

# Crop top part (tab bar and filters)
top_img = img.crop((0, 0, 1080, 600))
top_img.save("scripts/tv_short_drama_top.png")
print("Saved top crop to scripts/tv_short_drama_top.png")
