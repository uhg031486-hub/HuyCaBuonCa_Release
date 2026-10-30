# scripts/bump_version_334.py
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. TV build.gradle.kts
tv_b = 'HuyCaBuonCa_TV/app/build.gradle.kts'
with open(tv_b, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('versionCode = 27', 'versionCode = 28').replace('versionName = "3.3.3"', 'versionName = "3.3.4"')
with open(tv_b, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated TV build.gradle.kts to v3.3.4 (28)')

# 2. Mobile build.gradle.kts
m_b = 'HuyCaBuonCa_Mobile/app/build.gradle.kts'
with open(m_b, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('versionCode = 27', 'versionCode = 28').replace('versionName = "3.3.3"', 'versionName = "3.3.4"')
with open(m_b, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated Mobile build.gradle.kts to v3.3.4 (28)')

# 3. WebOS appinfo.json
for webos_path in ['HuyCa_WebOS/appinfo.json', 'HuyCa_LG_webOS/appinfo.json']:
    try:
        with open(webos_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace('"version": "3.3.3"', '"version": "3.3.4"')
        with open(webos_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'Updated {webos_path} to v3.3.4')
    except Exception as e:
        pass

# 4. Web index.html
web_idx = 'HuyCa_Web/index.html'
try:
    with open(web_idx, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('v3.3.3', 'v3.3.4').replace('3.3.3', '3.3.4')
    with open(web_idx, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Updated HuyCa_Web/index.html to v3.3.4')
except Exception as e:
    print('Web index.html error:', e)

# 5. version.json
v_json = 'version.json'
try:
    with open(v_json, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('"version": "v3.3.3"', '"version": "v3.3.4"')
    c = c.replace('"version_name": "v3.3.3"', '"version_name": "v3.3.4"')
    c = c.replace('"version_code": 27', '"version_code": 28')
    c = c.replace('3.3.3', '3.3.4')
    with open(v_json, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Updated version.json to v3.3.4')
except Exception as e:
    print('version.json error:', e)
