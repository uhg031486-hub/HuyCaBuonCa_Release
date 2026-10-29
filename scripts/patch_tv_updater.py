import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/util/AppUpdateManager.kt', 'r', encoding='utf-8') as f:
    c = f.read()

target = 'val apkUrl = json.optString("tvApkUrl", "")'
rep = 'val apkUrl = json.optString("tvApkUrl").ifEmpty { json.optString("apkUrl", "") }'

if target in c:
    c = c.replace(target, rep)
    with open('HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/util/AppUpdateManager.kt', 'w', encoding='utf-8') as f:
        f.write(c)
    print('SUCCESS patched TV AppUpdateManager.kt')
else:
    print('Target not found in TV AppUpdateManager.kt')
