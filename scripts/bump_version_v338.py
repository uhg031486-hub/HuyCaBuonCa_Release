import os
import shutil
import json

root = r"c:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity"

# 1. Update HuyCaBuonCa_Mobile build.gradle.kts
mobile_gradle = os.path.join(root, "HuyCaBuonCa_Mobile", "app", "build.gradle.kts")
with open(mobile_gradle, "r", encoding="utf-8") as f:
    m_content = f.read()
m_content = m_content.replace('versionCode = 31', 'versionCode = 32').replace('versionName = "3.3.7"', 'versionName = "3.3.8"')
with open(mobile_gradle, "w", encoding="utf-8") as f:
    f.write(m_content)
print("Updated Mobile build.gradle.kts to v3.3.8 (code 32)")

# 2. Update HuyCaBuonCa_TV build.gradle.kts
tv_gradle = os.path.join(root, "HuyCaBuonCa_TV", "app", "build.gradle.kts")
with open(tv_gradle, "r", encoding="utf-8") as f:
    tv_content = f.read()
tv_content = tv_content.replace('versionCode = 31', 'versionCode = 32').replace('versionName = "3.3.7"', 'versionName = "3.3.8"')
with open(tv_gradle, "w", encoding="utf-8") as f:
    f.write(tv_content)
print("Updated TV build.gradle.kts to v3.3.8 (code 32)")

# 3. Update LG webOS appinfo.json
webos_appinfo = os.path.join(root, "HuyCaBuonCa_LG_webOS", "appinfo.json")
if os.path.exists(webos_appinfo):
    with open(webos_appinfo, "r", encoding="utf-8") as f:
        appinfo = json.load(f)
    appinfo["version"] = "3.3.8"
    with open(webos_appinfo, "w", encoding="utf-8") as f:
        json.dump(appinfo, f, indent=2, ensure_ascii=False)
    print("Updated LG webOS appinfo.json to 3.3.8")

# 4. Sync HuyCa_Web files to LG webOS & Windows
web_dir = os.path.join(root, "HuyCa_Web")
webos_dir = os.path.join(root, "HuyCaBuonCa_LG_webOS")
windows_www_dir = os.path.join(root, "HuyCa_Windows", "www")

# Update version text in index.html
web_index = os.path.join(web_dir, "index.html")
with open(web_index, "r", encoding="utf-8") as f:
    idx_content = f.read()
idx_content = idx_content.replace("HuyCa_Mobile_v3.3.7.apk", "HuyCa_Mobile_v3.3.8.apk")
idx_content = idx_content.replace("HuyCa_TV_v3.3.7.apk", "HuyCa_TV_v3.3.8.apk")
idx_content = idx_content.replace("v3.3.7", "v3.3.8")
with open(web_index, "w", encoding="utf-8") as f:
    f.write(idx_content)
print("Updated index.html to v3.3.8")

# Copy to webOS
for item in ["css", "js", "cinematic", "index.html"]:
    src = os.path.join(web_dir, item)
    dst = os.path.join(webos_dir, item)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    elif os.path.isfile(src):
        shutil.copy2(src, dst)
print("Synced assets to LG webOS")

# Copy to Windows www
if os.path.exists(windows_www_dir):
    for item in ["css", "js", "cinematic", "index.html"]:
        src = os.path.join(web_dir, item)
        dst = os.path.join(windows_www_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif os.path.isfile(src):
            shutil.copy2(src, dst)
    print("Synced assets to Windows www")

print("ALL VERSION & ASSET SYNC COMPLETED SUCCESSFULLY!")
