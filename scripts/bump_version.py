import re

def bump_file(path, old_vcode, new_vcode, old_vname, new_vname):
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    txt = txt.replace(f"versionCode = {old_vcode}", f"versionCode = {new_vcode}")
    txt = txt.replace(f'versionName = "{old_vname}"', f'versionName = "{new_vname}"')
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"Updated {path}")

# 1. TV Gradle
bump_file(r"HuyCaBuonCa_TV\app\build.gradle.kts", 17, 18, "2.6", "2.7")

# 2. Mobile Gradle
bump_file(r"HuyCaBuonCa_Mobile\app\build.gradle.kts", 17, 18, "2.6", "2.7")

# 3. webOS appinfo.json
with open(r"HuyCaBuonCa_LG_webOS\appinfo.json", "r", encoding="utf-8") as f:
    webos = f.read()
webos = webos.replace('"version": "2.6.0"', '"version": "2.7.0"')
with open(r"HuyCaBuonCa_LG_webOS\appinfo.json", "w", encoding="utf-8") as f:
    f.write(webos)
print("Updated webOS appinfo.json")

# 4. Windows csproj
with open(r"HuyCa_Windows\HuyCa_Windows.csproj", "r", encoding="utf-8") as f:
    wincsproj = f.read()
wincsproj = wincsproj.replace("<Version>2.6.0</Version>", "<Version>2.7.0</Version>")
wincsproj = wincsproj.replace("<FileVersion>2.6.0.0</FileVersion>", "<FileVersion>2.7.0.0</FileVersion>")
wincsproj = wincsproj.replace("<AssemblyVersion>2.6.0.0</AssemblyVersion>", "<AssemblyVersion>2.7.0.0</AssemblyVersion>")
with open(r"HuyCa_Windows\HuyCa_Windows.csproj", "w", encoding="utf-8") as f:
    f.write(wincsproj)
print("Updated Windows csproj")
