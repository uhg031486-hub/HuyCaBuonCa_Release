import os
import sys
import shutil
import fitz # PyMuPDF
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

print("=== BƯỚC 1: CHUYỂN ĐỔI SVG SANG PNG VÀ ĐỒNG BỘ LOGO KÊNH TV ===")

web_logos_dir = "HuyCa_Web/data/logos"
tv_assets_dir = "HuyCaBuonCa_TV/app/src/main/assets/logos"
mobile_assets_dir = "HuyCaBuonCa_Mobile/app/src/main/assets/logos"
webos_logos_dir = "HuyCaBuonCa_LG_webOS/data/logos"
win_logos_dir = "HuyCa_Windows/www/data/logos"

for d in [web_logos_dir, tv_assets_dir, mobile_assets_dir, webos_logos_dir, win_logos_dir]:
    os.makedirs(d, exist_ok=True)

# 1. Chuyển đổi mọi file SVG trong web_logos_dir thành PNG 300 DPI
for f in os.listdir(web_logos_dir):
    if f.endswith(".svg"):
        svg_path = os.path.join(web_logos_dir, f)
        png_name = f.replace(".svg", ".png")
        png_path = os.path.join(web_logos_dir, png_name)
        try:
            doc = fitz.open(svg_path)
            pix = doc[0].get_pixmap(dpi=300)
            pix.save(png_path)
            print(f" -> Đã chuyển đổi SVG sang PNG: {f} -> {png_name} ({pix.width}x{pix.height})")
        except Exception as e:
            print(f" -> Lỗi chuyển đổi {f}:", e)

# 2. Tạo hoặc tải các icon bổ sung chất lượng cao
extra_downloads = [
    # VTVcab ON
    ("vtvcab_on.png", "https://raw.githubusercontent.com/vuminhthanh12/Logo/main/ONPHIMVIET.png"),
    ("on_cine.png", "https://i.ytimg.com/vi/rwhsuTvSXxo/maxresdefault.jpg"),
    ("on_phimviet.png", "https://raw.githubusercontent.com/vuminhthanh12/Logo/main/ONPHIMVIET.png"),
    ("on_viedramas.png", "https://i.ytimg.com/vi/4SqDlPT8oEI/maxresdefault.jpg"),
    ("on_life.png", "https://upload.wikimedia.org/wikipedia/commons/b/bb/ONLIFE.jpg"),
    ("on_movies.png", "https://raw.githubusercontent.com/vuminhthanh12/Logo/main/onmovies.png"),
    ("on_music.png", "https://img-zlr1.tv360.vn/image1/2023/07/20/10/1689822524259/0f3a4d1ebfaf_640_360.png"),
    ("on_bibi.png", "https://raw.githubusercontent.com/vuminhthanh12/Logo/main/onbibi.png"),
    ("on_echannel.png", "https://raw.githubusercontent.com/vuminhthanh12/Logo/main/onechannel.png"),
    ("on_style.png", "https://raw.githubusercontent.com/vuminhthanh12/Logo/main/onstyle.png"),
    # HTV
    ("htv1.png", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/HTV1.png/960px-HTV1.png"),
    ("htv2.png", "https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/HTV5.jpg"),
    ("htv3.png", "https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/HTV3.jpg"),
    ("htv7.webp", "https://upload.wikimedia.org/wikipedia/commons/c/c0/HTV7_logo.webp"),
    ("htv9.webp", "https://upload.wikimedia.org/wikipedia/commons/b/bf/HTV9_logo.webp"),
    ("htv_thethao.png", "https://huyca.pages.dev/data/logos/htv_thethao.png"),
    # VTV Imgur Backup
    ("vtv1_hd.png", "https://i.imgur.com/vZYlGIW.png"),
    ("vtv2_hd.png", "https://i.imgur.com/qWWpYRR.png"),
    ("vtv3_hd.png", "https://i.imgur.com/4lJG1fu.png"),
    ("vtv4_hd.png", "https://i.imgur.com/WsLLmR2.png"),
    ("vtv5_hd.png", "https://i.imgur.com/Vnnna1C.png"),
    ("vtv7_hd.png", "https://i.imgur.com/ZwoP823.png"),
    ("vtv8_hd.png", "https://i.imgur.com/rf9adGJ.png"),
    ("vtv9_hd.png", "https://i.imgur.com/QiY55sy.png"),
    # THVL
    ("thvl1.png", "https://i.imgur.com/5YFsqPx.png"),
    ("thvl2.png", "https://i.imgur.com/iluoazf.png"),
    ("thvl3.png", "https://i.imgur.com/OQXEhqu.png"),
    ("thvl4.png", "https://i.imgur.com/ARhIkvR.png"),
    # Sports & News
    ("sky_sports_pl.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-kingdom/sky-sports-premier-league-uk.png"),
    ("sky_sports_main.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-kingdom/sky-sports-main-event-uk.png"),
    ("tnt_sports_1.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-kingdom/tnt-sports-1-uk.png"),
    ("espn.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/espn-us.png"),
    ("espn2.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/espn-2-us.png"),
    ("fubo_sports.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/fubo-sports-network-us.png"),
    ("nba_tv.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/nba-tv-us.png"),
    ("nfl_network.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/nfl-network-us.png"),
    ("fox_sports.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/fox-sports-1-us.png"),
    ("tennis_channel.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/tennis-channel-us.png"),
    ("cnn.png", "https://freem3u.xyz/static/images/global/cnn.png"),
    ("bloomberg.png", "https://freem3u.xyz/static/images/global/bloomberg.png"),
    ("warnertv.png", "https://freem3u.xyz/static/images/global/warnertv.png"),
    ("nhkworld.png", "https://raw.githubusercontent.com/vuminhthanh12/Logo/main/nhkworld.png"),
    ("cbs_news.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-states/cbs-news-24-7-us.png"),
    ("france24.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/france/france-24-fr.png"),
    ("dw.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/dw-de.png"),
    ("aljazeera.png", "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/united-kingdom/aljazeera-uk.png"),
    ("cartoonito.png", "https://freem3u.xyz/static/images/global/cartoonito.png"),
    ("cartoon_network.png", "https://freem3u.xyz/static/images/global/cartoon-network.png"),
    ("arirang.png", "https://i.imgur.com/Asu5pE9.png"),
    ("mbc.png", "https://img.imbc.com/commons/2018/image/comm2018noti/meta_mbc.png")
]

for filename, url in extra_downloads:
    dest_path = os.path.join(web_logos_dir, filename)
    if not os.path.exists(dest_path):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as res:
                with open(dest_path, "wb") as f:
                    f.write(res.read())
            print(f" -> Đã tải logo bổ sung: {filename}")
        except Exception as e:
            print(f" -> Không thể tải {filename} từ {url}: {e}")

# 3. Đồng bộ toàn bộ logo từ web_logos_dir sang các thư mục assets và dist
all_logos = [f for f in os.listdir(web_logos_dir) if f.endswith(('.png', '.webp', '.jpg', '.svg'))]
print(f"\n3. Đồng bộ {len(all_logos)} logo sang TV, Mobile, webOS, Windows...")

target_dirs = [tv_assets_dir, mobile_assets_dir, webos_logos_dir, win_logos_dir]

for logo in all_logos:
    src = os.path.join(web_logos_dir, logo)
    for td in target_dirs:
        dst = os.path.join(td, logo)
        shutil.copy2(src, dst)

print("✅ HOÀN TẤT ĐỒNG BỘ LOGO KÊNH TV VÀO TẤT CẢ DỰ ÁN!")
