import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. TV build.gradle.kts
tv_b = 'HuyCaBuonCa_TV/app/build.gradle.kts'
with open(tv_b, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('versionCode = 26', 'versionCode = 27').replace('versionName = "3.3.2"', 'versionName = "3.3.3"')
with open(tv_b, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated TV build.gradle.kts to v3.3.3 (27)')

# 2. Mobile build.gradle.kts
m_b = 'HuyCaBuonCa_Mobile/app/build.gradle.kts'
with open(m_b, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('versionCode = 26', 'versionCode = 27').replace('versionName = "3.3.2"', 'versionName = "3.3.3"')
with open(m_b, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated Mobile build.gradle.kts to v3.3.3 (27)')

# 3. WebOS appinfo.json
webos_path = 'HuyCa_WebOS/appinfo.json'
try:
    with open(webos_path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('"version": "3.3.2"', '"version": "3.3.3"')
    with open(webos_path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Updated WebOS appinfo.json to v3.3.3')
except Exception as e:
    print('WebOS appinfo error:', e)

# 4. Web index.html
web_idx = 'HuyCa_Web/index.html'
try:
    with open(web_idx, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('v3.3.2', 'v3.3.3').replace('3.3.2', '3.3.3')
    with open(web_idx, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Updated HuyCa_Web/index.html to v3.3.3')
except Exception as e:
    print('Web index.html error:', e)
