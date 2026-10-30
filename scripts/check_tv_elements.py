import sys
import xml.etree.ElementTree as ET
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse('scripts/tv_tivi_dump.xml')
found = 0
for node in tree.iter('node'):
    text = node.attrib.get('text', '')
    if any(k in text.lower() for k in ['vtv', 'htv', 'thvl', 'kênh', 'tất cả', 'sctv', 'ngoại hạng']):
        print(f"'{text}' -> {node.attrib.get('bounds')}")
        found += 1
print(f"Tổng số phần tử kênh/danh mục tìm thấy: {found}")
