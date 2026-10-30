import os
import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

web_dir = 'HuyCa_Web'
output_wgt = 'HuyCa_Samsung_Tizen_v3.2.8.wgt'

# Files/folders to exclude
excludes = {'.git', 'clean_test.html', 'test_embed.html'}

with zipfile.ZipFile(output_wgt, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(web_dir):
        # Exclude hidden or excluded directories
        dirs[:] = [d for d in dirs if d not in excludes and not d.startswith('.')]
        for f in files:
            if f in excludes or f.endswith('.tmp'):
                continue
            abs_path = os.path.join(root, f)
            rel_path = os.path.relpath(abs_path, web_dir)
            z.write(abs_path, rel_path)

print(f"Đã đóng gói thành công gói cài đặt Tizen: {output_wgt} (Dung lượng: {os.path.getsize(output_wgt)} bytes)")
