import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Mobile build.gradle.kts
f_mobile = 'HuyCaBuonCa_Mobile/app/build.gradle.kts'
with open(f_mobile, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('versionCode = 21', 'versionCode = 22').replace('versionName = "3.2.7"', 'versionName = "3.2.8"')
with open(f_mobile, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated Mobile build.gradle.kts to v3.2.8 (code 22)')

# 2. TV build.gradle.kts
f_tv = 'HuyCaBuonCa_TV/app/build.gradle.kts'
with open(f_tv, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('versionCode = 21', 'versionCode = 22').replace('versionName = "3.2.7"', 'versionName = "3.2.8"')
with open(f_tv, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated TV build.gradle.kts to v3.2.8 (code 22)')

# 3. HuyCa_Web index.html
f_web = 'HuyCa_Web/index.html'
with open(f_web, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('v=3.2.7', 'v=3.2.8')
with open(f_web, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated HuyCa_Web index.html to v3.2.8')
