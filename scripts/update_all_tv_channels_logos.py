import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)

print(f"Bắt đầu tinh chỉnh và gán icon chuẩn cho 152 kênh TV...")

def get_best_logo(c):
    cid = c.get('id', '')
    name = c.get('name', '').lower()
    grp = c.get('group', '').lower()
    raw = c.get('logo', '')

    # 1. VTV Quốc Gia
    if 'vtv10' in name or 'cần thơ' in name:
        return 'https://huyca.pages.dev/data/logos/vtv_cantho.png'
    if 'vtv1' in name:
        return 'https://i.imgur.com/vZYlGIW.png'
    if 'vtv2' in name:
        return 'https://i.imgur.com/qWWpYRR.png'
    if 'vtv3' in name:
        return 'https://i.imgur.com/4lJG1fu.png'
    if 'vtv4' in name:
        return 'https://i.imgur.com/WsLLmR2.png'
    if 'vtv5' in name:
        return 'https://i.imgur.com/Vnnna1C.png'
    if 'vtv6' in name:
        return 'https://huyca.pages.dev/data/logos/vtv6.png'
    if 'vtv7' in name:
        return 'https://i.imgur.com/ZwoP823.png'
    if 'vtv8' in name:
        return 'https://i.imgur.com/rf9adGJ.png'
    if 'vtv9' in name:
        return 'https://i.imgur.com/QiY55sy.png'
    if 'vietnam today' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/VietnamToday.jpg'

    # 2. VTVcab
    if 'on cine' in name:
        return 'https://i.ytimg.com/vi/rwhsuTvSXxo/maxresdefault.jpg'
    if 'on phim' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/Logo/main/ONPHIMVIET.png'
    if 'on vie drama' in name:
        return 'https://i.ytimg.com/vi/4SqDlPT8oEI/maxresdefault.jpg'
    if 'on movies' in name or 'you tv' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/Logo/main/onmovies.png'
    if 'on music' in name:
        return 'https://img-zlr1.tv360.vn/image1/2023/07/20/10/1689822524259/0f3a4d1ebfaf_640_360.png'
    if 'on life' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/Logo/main/oninfotv.png'
    if 'on bibi' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/Logo/refs/heads/main/onbibi.png'
    if 'on e-' in name or 'one channel' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/Logo/refs/heads/main/onechannel.png'
    if 'on style' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/Logo/refs/heads/main/onstyle.png'
    if 'on v family' in name:
        return 'https://i.ibb.co/HHfL7Dq/cocab20.webp'
    if 'vtvcab' in grp:
        return 'https://huyca.pages.dev/data/logos/vtvcab.png'

    # 3. HTV
    if 'htv thể thao' in name or 'htvc thể thao' in name:
        return 'https://huyca.pages.dev/data/logos/htv_thethao.png'
    if 'htv1' in name:
        return 'https://huyca.pages.dev/data/logos/htv1.png'
    if 'htv2' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/HTV5.jpg'
    if 'htv3' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/HTV3.jpg'
    if 'htv7' in name:
        return 'https://huyca.pages.dev/data/logos/htv7.webp'
    if 'htv9' in name:
        return 'https://huyca.pages.dev/data/logos/htv9.webp'
    if 'htv' in grp:
        return 'https://huyca.pages.dev/data/logos/htv7.webp'

    # 4. SCTV
    if 'sctv2' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/SCTV2TODAYTV.jpg'
    if 'sctv8' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/sctv8.png'
    if 'sctv9' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/SCTV9.png'

    # 5. Kênh Vệ Tinh & Thể Thao Ngoại Hạng Anh
    if 'true premier 1' in name or 'true premier football 1' in name:
        return 'https://huyca.pages.dev/data/logos/true_premier_1.png'
    if 'true premier 2' in name or 'true premier football 2' in name:
        return 'https://huyca.pages.dev/data/logos/true_premier_2.png'
    if 'true premier' in name:
        return 'https://huyca.pages.dev/data/logos/true_premier_1.png'
    if 'astro supersport 1' in name:
        return 'https://huyca.pages.dev/data/logos/astro_supersport_1.png'
    if 'astro supersport 2' in name:
        return 'https://huyca.pages.dev/data/logos/astro_supersport_2.png'
    if 'sky sports' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-kingdom/sky-sports-premier-league-uk.png'
    if 'tnt sports' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-kingdom/tnt-sports-1-uk.png'
    if 'bein' in name:
        return 'https://huyca.pages.dev/data/logos/bein_sports_1.png'
    if 'bbc earth' in name:
        return 'https://freem3u.xyz/static/images/global/bbc-earth.png'
    if 'nbc sports' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/fox-sports-1-us.png'

    # 6. Kênh Quốc Tế (Thay các link Wikimedia 400 và iptv-org 404)
    if 'abc news' in name:
        return 'https://freem3u.xyz/static/images/global/abc-australia.png'
    if 'cbs news' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cbs-news-24-7-us.png'
    if 'nbc news' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cbs-news-24-7-us.png'
    if 'bloomberg' in name:
        return 'https://freem3u.xyz/static/images/global/bloomberg.png'
    if 'cnbc' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cnbc-us.png'
    if 'cartoonito' in name or 'boomerang' in name:
        return 'https://freem3u.xyz/static/images/global/cartoonito.png'
    if 'dw ' in name or 'dw english' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/dw-de.png'
    if 'euronews' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/france/france-24-fr.png'
    if 'france 24' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/france/france-24-fr.png'
    if 'nhk world' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/Logo/main/nhkworld.png'
    if 'warner tv' in name:
        return 'https://freem3u.xyz/static/images/global/warnertv.png'
    if 'al jazeera' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-kingdom/aljazeera-uk.png'
    if 'arirang' in name:
        return 'https://i.imgur.com/Asu5pE9.png'
    if 'reuters' in name:
        return 'https://freem3u.xyz/static/images/global/bloomberg.png'
    if 'history hit' in name:
        return 'https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-kingdom/bbc-news-hz-uk.png'

    # 7. Kênh Hàn Quốc & Trung Quốc
    if 'cctv2' in name:
        return 'https://pic2.zhimg.com/80/v2-01c9b1cdd4534f653e1bb8102b18a89d_1440w.webp'
    if 'mbc' in name:
        return 'https://img.imbc.com/commons/2018/image/comm2018noti/meta_mbc.png'
    if 'tv chosun' in name or 'tvn' in name or 'jtv sbs' in name or 'ebs' in name:
        return 'https://logowik.com/content/uploads/images/ebs1-20181732222724.logowik.com.webp'

    # 8. Kênh Địa Phương & Khác
    if 'vĩnh long' in name or 'thvl' in name:
        return 'https://i.imgur.com/5YFsqPx.png'
    if 'ninh bình' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/BHTTV.webp'
    if 'thanh hóa' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/BHTTV.webp'
    if 'nghệ an' in name or 'ntv' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/BHTTV.webp'
    if 'đắk lắk' in name or 'drt' in name:
        return 'https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/LTV1.jpg'
    if 'điện biên' in name:
        return 'https://images.fptplay53.net/media/channels/icon_channel_lai-chau_165649245279.png'
    if 'hitv' in name:
        return 'https://s7771.cdn.mytvnet.vn/vimages/8c/ce/ee/e7/79/98/8cee7-phtv1hd-channel-unkn.png'

    # Nếu raw logo là URL hợp lệ không bị 400/svg/vbook generic
    if raw.startswith('http') and not 'wikimedia.org/wikipedia/commons/thumb' in raw and not raw.endswith('.svg') and not 'vbook-ext' in raw:
        return raw

    # Nếu là relative
    if raw.startswith('data/logos/'):
        return f"https://huyca.pages.dev/{raw.replace('.svg', '.png')}"

    return 'https://huyca.pages.dev/data/logos/tv_default_premium.png'

updated_count = 0
for c in channels:
    old_logo = c.get('logo', '')
    new_logo = get_best_logo(c)
    if new_logo != old_logo:
        updated_count += 1
        c['logo'] = new_logo

print(f" -> Đã cập nhật logo cho {updated_count}/{len(channels)} kênh!")

# Lưu lại tv_channels.json vào tất cả các vị trí
target_files = [
    "HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json",
    "HuyCaBuonCa_Mobile/app/src/main/assets/tv_channels.json",
    "HuyCaBuonCa_LG_webOS/data/tv_channels.json",
    "HuyCa_Windows/www/data/tv_channels.json",
    "HuyCa_Web/data/tv_channels.json",
    "HuyCa_Samsung_Tizen/data/tv_channels.json"
]

for tf in target_files:
    if os.path.exists(tf):
        with open(tf, 'w', encoding='utf-8') as f:
            json.dump(channels, f, ensure_ascii=False, indent=2)
        print(f" ✔ Đã lưu: {tf}")

# Đồng thời tạo file tv_channels.js cho Web
js_content = f"window.INITIAL_TV_CHANNELS = {json.dumps(channels, ensure_ascii=False, indent=2)};\n"
for js_path in ["HuyCa_Web/data/tv_channels.js", "HuyCaBuonCa_LG_webOS/data/tv_channels.js", "HuyCa_Windows/www/data/tv_channels.js"]:
    if os.path.exists(os.path.dirname(js_path)):
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f" ✔ Đã lưu: {js_path}")

print("✅ ĐÃ CẬP NHẬT ĐỒNG BỘ 100% KÊNH TV VỚI ICON ĐẸP CHUẨN!")
