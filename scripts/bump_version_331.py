import re

def update_file(path, old, new):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}: replaced '{old}' with '{new}'")
    else:
        print(f"Warning: '{old}' not found in {path}")

# 1. Gradle files
update_file("HuyCaBuonCa_TV/app/build.gradle.kts", "versionCode = 24", "versionCode = 25")
update_file("HuyCaBuonCa_TV/app/build.gradle.kts", 'versionName = "3.3.0"', 'versionName = "3.3.1"')

update_file("HuyCaBuonCa_Mobile/app/build.gradle.kts", "versionCode = 24", "versionCode = 25")
update_file("HuyCaBuonCa_Mobile/app/build.gradle.kts", 'versionName = "3.3.0"', 'versionName = "3.3.1"')

# 2. webOS appinfo.json
update_file("HuyCaBuonCa_LG_webOS/appinfo.json", '"version": "3.3.0"', '"version": "3.3.1"')

# 3. HuyCa_Web files
update_file("HuyCa_Web/index.html", "v3.3.0", "v3.3.1")
update_file("HuyCa_Web/index.html", "v=3.3.0", "v=3.3.1")
update_file("HuyCa_Web/index.html", "HuyCa_Mobile_v3.3.0.apk", "HuyCa_Mobile_v3.3.1.apk")
update_file("HuyCa_Web/index.html", "HuyCa_TV_v3.3.0.apk", "HuyCa_TV_v3.3.1.apk")
update_file("HuyCa_Web/index.html", "HuyCa_Windows_v3.3.0.zip", "HuyCa_Windows_v3.3.1.zip")
update_file("HuyCa_Web/index.html", "HuyCa_LG_webOS_v3.3.0.ipk", "HuyCa_LG_webOS_v3.3.1.ipk")

update_file("HuyCa_Web/_worker.js", "v3.3.0", "v3.3.1")
update_file("HuyCa_Web/functions/api/download.js", "v3.3.0", "v3.3.1")

print("All version bumps completed!")
