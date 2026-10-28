import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== RED GATE: KIỂM TRA BẢO VỆ CHỐNG QUẢNG CÁO & POPUP TRÊN TOÀN HỆ THỐNG ===")

errors = []

# 1. Kiểm tra Mobile DetailActivity.kt
mobile_detail = 'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt'
if os.path.exists(mobile_detail):
    with open(mobile_detail, 'r', encoding='utf-8') as f:
        m_code = f.read()
    if 'shouldOverrideUrlLoading' not in m_code:
        errors.append("Mobile DetailActivity.kt: Thiếu shouldOverrideUrlLoading để chặn chuyển hướng quảng cáo!")
    if 'onCreateWindow' not in m_code:
        errors.append("Mobile DetailActivity.kt: Thiếu onCreateWindow để chặn đứng popup quảng cáo window.open!")
    if 'shouldInterceptRequest' not in m_code:
        errors.append("Mobile DetailActivity.kt: Thiếu shouldInterceptRequest để chặn nạp script quảng cáo ads.js!")

# 2. Kiểm tra TV PlayerActivity.kt
tv_player = 'HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/ui/PlayerActivity.kt'
if os.path.exists(tv_player):
    with open(tv_player, 'r', encoding='utf-8') as f:
        tv_code = f.read()
    if 'shouldOverrideUrlLoading' not in tv_code:
        errors.append("TV PlayerActivity.kt: Thiếu shouldOverrideUrlLoading để chặn chuyển hướng quảng cáo!")
    if 'onCreateWindow' not in tv_code:
        errors.append("TV PlayerActivity.kt: Thiếu onCreateWindow để chặn đứng popup quảng cáo window.open!")
    if 'shouldInterceptRequest' not in tv_code:
        errors.append("TV PlayerActivity.kt: Thiếu shouldInterceptRequest để chặn nạp script quảng cáo ads.js!")

# 3. Kiểm tra HuyCa_Web/index.html
web_index = 'HuyCa_Web/index.html'
if os.path.exists(web_index):
    with open(web_index, 'r', encoding='utf-8') as f:
        w_code = f.read()
    if 'sandbox=' not in w_code:
        errors.append("HuyCa_Web/index.html: Iframe thiếu thuộc tính sandbox để chặn popup quảng cáo!")
    elif 'allow-popups' in w_code:
        errors.append("HuyCa_Web/index.html: Iframe chứa allow-popups khiến quảng cáo có thể mở tab mới!")

print(f"\nTổng số lỗi bảo vệ quảng cáo phát hiện: {len(errors)}")
for err in errors:
    print(f"❌ {err}")

if len(errors) > 0:
    print("\n=> RED GATE XÁC NHẬN THẤT BẠI: HỆ THỐNG ĐANG BỊ HỔNG BẢO VỆ CHỐNG QUẢNG CÁO NGUỒN C!")
    sys.exit(1)
else:
    print("\n=> GREEN GATE: HỆ THỐNG ĐÃ CÓ ĐẦY ĐỦ BẢO VỆ CHỐNG QUẢNG CÁO!")
    sys.exit(0)
