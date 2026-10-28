import sys
import json
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

mapping_path = r'c:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\scripts\zh_vi_mapping.json'
src_html = r'C:\Users\yoga\Downloads\muse_local\muse2api-main\admin.html'
dst_html = r'c:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\scripts\admin_vi.html'

with open(mapping_path, 'r', encoding='utf-8') as f:
    mapping = json.load(f)

with open(src_html, 'r', encoding='utf-8') as f:
    html = f.read()

# Chỉnh lang và title
html = html.replace('<html lang="zh-CN">', '<html lang="vi">')

# Thay thế từ dài đến ngắn
sorted_keys = sorted(mapping.keys(), key=lambda x: len(x), reverse=True)

replaced_count = 0
for k in sorted_keys:
    v = mapping[k]
    if k in html:
        html = html.replace(k, v)
        replaced_count += 1

with open(dst_html, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Da thay the thanh cong {replaced_count} cum tu!")
print(f"File da ghi ra: {dst_html}")
