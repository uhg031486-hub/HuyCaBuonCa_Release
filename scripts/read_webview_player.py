import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('initWebViewPlayer')
if idx != -1:
    print(text[max(0, idx - 100):min(len(text), idx + 2500)])
else:
    print('initWebViewPlayer not found')
