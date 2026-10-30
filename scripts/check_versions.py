import re

for path in ['HuyCaBuonCa_Mobile/app/build.gradle.kts', 'HuyCaBuonCa_TV/app/build.gradle.kts', 'version.json']:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        v = re.findall(r'(versionCode\s*=\s*\d+|versionName\s*=\s*"[^"]+"|version)', text)
        print(f'{path}: {v[:5]}')
    except Exception as e:
        print(f'{path}: {e}')
