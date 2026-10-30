import os
import sys
import time
import subprocess
import xml.etree.ElementTree as ET

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def run_adb(cmd):
    full_cmd = f"adb {cmd}"
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.returncode, res.stdout.strip()

print("Mở lại TV app...")
run_adb("shell am force-stop com.huycabuonca.tv")
time.sleep(1)
run_adb("shell am start -n com.huycabuonca.tv/.ui.MainActivity")
time.sleep(3)

# Click chính xác vào nút [📺 XEM TIVI]
print("Tap vào [📺 XEM TIVI] tại 1170, 107...")
run_adb("shell input tap 1170 107")
time.sleep(4)

# Dump UI
run_adb("shell uiautomator dump /sdcard/tv_click.xml")
run_adb("pull /sdcard/tv_click.xml scripts/tv_click.xml")

tree = ET.parse('scripts/tv_click.xml')
texts = []
for node in tree.iter('node'):
    t = node.attrib.get('text', '')
    if t:
        texts.append(t)

print("Các texts hiển thị trên màn hình TV:")
for t in texts[:25]:
    print(f" - {t}")
