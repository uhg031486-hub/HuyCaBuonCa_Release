import sys

sys.stdout.reconfigure(encoding='utf-8')

app_js_path = "HuyCa_Web/js/app.js"
with open(app_js_path, "r", encoding="utf-8") as f:
    content = f.read()

old_func = """  const DEFAULT_TV_LOGO = 'data/logos/tv_default_premium.svg';

  function getTvChannelLogo(movie) {
    const rawLogo = movie.posterUrl || movie.thumbUrl || '';
    if (rawLogo && rawLogo.startsWith('data/logos/') && !rawLogo.includes('default')) {
      return rawLogo;
    }
    const name = (movie.name || '').toLowerCase();
    if (name.includes('true premier football 1') || name.includes('true premier 1')) return 'data/logos/true_premier_1.svg';
    if (name.includes('true premier football 2') || name.includes('true premier 2')) return 'data/logos/true_premier_2.svg';
    if (name.includes('true premier')) return 'data/logos/true_premier_1.svg';
    if (name.includes('astro supersport 1')) return 'data/logos/astro_supersport_1.svg';
    if (name.includes('astro supersport 2')) return 'data/logos/astro_supersport_2.svg';
    if (name.includes('astro')) return 'data/logos/astro_supersport_1.svg';
    if (name.includes('sky sports')) return 'data/logos/sky_sports_pl.svg';
    if (name.includes('tnt sports')) return 'data/logos/tnt_sports_1.svg';
    if (name.includes('bein sports') || name.includes('bein')) return 'data/logos/bein_sports_1.svg';
    if (name.includes('bbc earth')) return 'data/logos/bbc_earth.svg';
    if (name.includes('on cine') || name.includes('on phim') || name.includes('on vie') || name.includes('on golf') || name.includes('on life') || name.includes('on movies') || name.includes('on music') || name.includes('vtvcab')) return 'data/logos/vtvcab_on.svg';
    if (name.includes('vtv10') || name.includes('cần thơ')) return 'data/logos/vtv_cantho.png';
    if (name.includes('vtv1')) return 'data/logos/vtv1.png';
    if (name.includes('vtv2')) return 'data/logos/vtv2.png';
    if (name.includes('vtv3')) return 'data/logos/vtv3.png';
    if (name.includes('vtv4')) return 'data/logos/vtv4.png';
    if (name.includes('vtv5')) return 'data/logos/vtv5.png';
    if (name.includes('vtv6')) return 'data/logos/vtv6.png';
    if (name.includes('vtv7')) return 'data/logos/vtv7.png';
    if (name.includes('vtv8')) return 'data/logos/vtv8.png';
    if (name.includes('vtv9')) return 'data/logos/vtv9.png';
    if (name.includes('htv') || name.includes('htvc')) return 'data/logos/htv_thethao.png';

    if (rawLogo && !rawLogo.includes('iptv-org') && !rawLogo.includes('file:///android_asset')) {
      return rawLogo;
    }
    return DEFAULT_TV_LOGO;
  }"""

new_func = """  const DEFAULT_TV_LOGO = 'data/logos/tv_default_premium.png';

  function getTvChannelLogo(movie) {
    const rawLogo = movie.posterUrl || movie.thumbUrl || '';
    if (rawLogo && rawLogo.startsWith('data/logos/') && !rawLogo.includes('default')) {
      return rawLogo.replace('.svg', '.png');
    }
    const name = (movie.name || '').toLowerCase();
    if (name.includes('true premier football 1') || name.includes('true premier 1')) return 'data/logos/true_premier_1.png';
    if (name.includes('true premier football 2') || name.includes('true premier 2')) return 'data/logos/true_premier_2.png';
    if (name.includes('true premier')) return 'data/logos/true_premier_1.png';
    if (name.includes('astro supersport 1')) return 'data/logos/astro_supersport_1.png';
    if (name.includes('astro supersport 2')) return 'data/logos/astro_supersport_2.png';
    if (name.includes('astro')) return 'data/logos/astro_supersport_1.png';
    if (name.includes('sky sports')) return 'data/logos/sky_sports_pl.png';
    if (name.includes('tnt sports')) return 'data/logos/tnt_sports_1.png';
    if (name.includes('bein sports') || name.includes('bein')) return 'data/logos/bein_sports_1.png';
    if (name.includes('bbc earth')) return 'data/logos/bbc_earth.png';
    if (name.includes('on cine')) return 'data/logos/on_cine.png';
    if (name.includes('on phim')) return 'data/logos/on_phimviet.png';
    if (name.includes('on vie drama')) return 'data/logos/on_viedramas.png';
    if (name.includes('on movies') || name.includes('you tv')) return 'data/logos/on_movies.png';
    if (name.includes('on music')) return 'data/logos/on_music.png';
    if (name.includes('on bibi')) return 'data/logos/on_bibi.png';
    if (name.includes('on e-') || name.includes('one channel')) return 'data/logos/on_echannel.png';
    if (name.includes('on style')) return 'data/logos/on_style.png';
    if (name.includes('vtvcab')) return 'data/logos/vtvcab_on.png';
    if (name.includes('htv thể thao') || name.includes('htvc thể thao')) return 'data/logos/htv_thethao.png';
    if (name.includes('htv1')) return 'data/logos/htv1.png';
    if (name.includes('htv2')) return 'data/logos/htv2.png';
    if (name.includes('htv3')) return 'data/logos/htv3.png';
    if (name.includes('htv7')) return 'data/logos/htv7.webp';
    if (name.includes('htv9')) return 'data/logos/htv9.webp';
    if (name.includes('thvl1')) return 'data/logos/thvl1.png';
    if (name.includes('thvl2')) return 'data/logos/thvl2.png';
    if (name.includes('thvl3')) return 'data/logos/thvl3.png';
    if (name.includes('thvl4')) return 'data/logos/thvl4.png';
    if (name.includes('vtv10') || name.includes('cần thơ')) return 'data/logos/vtv_cantho.png';
    if (name.includes('vtv1')) return 'data/logos/vtv1.png';
    if (name.includes('vtv2')) return 'data/logos/vtv2.png';
    if (name.includes('vtv3')) return 'data/logos/vtv3.png';
    if (name.includes('vtv4')) return 'data/logos/vtv4.png';
    if (name.includes('vtv5')) return 'data/logos/vtv5.png';
    if (name.includes('vtv6')) return 'data/logos/vtv6.png';
    if (name.includes('vtv7')) return 'data/logos/vtv7.png';
    if (name.includes('vtv8')) return 'data/logos/vtv8.png';
    if (name.includes('vtv9')) return 'data/logos/vtv9.png';
    if (name.includes('cnn')) return 'data/logos/cnn.png';
    if (name.includes('bloomberg')) return 'data/logos/bloomberg.png';
    if (name.includes('warnertv') || name.includes('warner tv')) return 'data/logos/warnertv.png';
    if (name.includes('nhk world')) return 'data/logos/nhkworld.png';
    if (name.includes('cbs news')) return 'data/logos/cbs_news.png';
    if (name.includes('france 24')) return 'data/logos/france24.png';
    if (name.includes('dw ') || name.includes('dw english')) return 'data/logos/dw.png';
    if (name.includes('al jazeera')) return 'data/logos/aljazeera.png';
    if (name.includes('cartoonito')) return 'data/logos/cartoonito.png';
    if (name.includes('arirang')) return 'data/logos/arirang.png';
    if (name.includes('mbc')) return 'data/logos/mbc.png';

    if (rawLogo && !rawLogo.includes('iptv-org') && !rawLogo.includes('file:///android_asset')) {
      return rawLogo;
    }
    return DEFAULT_TV_LOGO;
  }"""

content_norm = content.replace("\r\n", "\n")
old_norm = old_func.replace("\r\n", "\n")
new_norm = new_func.replace("\r\n", "\n")

if old_norm in content_norm:
    content_norm = content_norm.replace(old_norm, new_norm)
    with open(app_js_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content_norm)
    print("✔ Đã cập nhật getTvChannelLogo trong HuyCa_Web/js/app.js!")
else:
    print("❌ Không tìm thấy old_func trong app.js!")
