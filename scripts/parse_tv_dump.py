import sys
import xml.etree.ElementTree as ET
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse('scripts/tv_dump.xml')
for node in tree.iter('node'):
    text = node.attrib.get('text', '')
    desc = node.attrib.get('content-desc', '')
    combined = (text + " " + desc).lower()
    if any(k in combined for k in ['tivi', 'vtv', 'htv', 'kênh', 'phim', 'thể thao']):
        print(f"Text: '{text}' | Desc: '{desc}' | Bounds: {node.attrib.get('bounds')}")
