import sys
import xml.etree.ElementTree as ET
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse('scripts/mobile_ui.xml')
for node in tree.iter('node'):
    rid = node.attrib.get('resource-id', '')
    text = node.attrib.get('text', '')
    if 'btnSource' in rid:
        print(f"{rid} -> text: '{text}' -> bounds: {node.attrib.get('bounds')}")
