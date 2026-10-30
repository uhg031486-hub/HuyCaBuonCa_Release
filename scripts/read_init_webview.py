import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('private fun initWebViewPlayer')
if idx != -1:
    print(text[idx:idx + 3000])
else:
    print('initWebViewPlayer not found')
