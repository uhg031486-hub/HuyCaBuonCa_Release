// Huy Cá - Phiên Bản v2.5 (Premier League & 4-Tier Match Streaming)
(function () {
  'use strict';

  function getAppProxyUrl(target) {
    if (!target) return '';
    if (target.includes('/api/proxy?url=')) return target;
    const isCloudflare = window.location.hostname && (window.location.hostname.endsWith('pages.dev') || window.location.hostname.includes('huyca.'));
    const base = isCloudflare ? '/api/proxy?url=' : 'https://huyca.pages.dev/api/proxy?url=';
    return base + encodeURIComponent(target);
  }


  // --- State ---
  let currentSource = 'KKPHIM'; // KKPHIM, ANIMEHAY, XEMTIVI, FREEREELS
  let currentFilter = '';
  let currentPage = 1;
  let isLoading = false;
  let currentMoviesList = [];
  let currentPlayingMovie = null;
  let currentPlayingDetail = null;
  let currentEpisodeIndex = 0;
  let currentServerIndex = 0;
  let hlsInstance = null;
  let dashInstance = null;
  let overlayTimeout = null;
  let numberZapBuffer = '';
  let numberZapTimeout = null;
  let lastBackTime = 0;
  let currentFocusedElement = null;
  const isNativeWebOS = /webOS|SmartTV/i.test(navigator.userAgent) || window.webOS !== undefined;
  let currentAspectIdx = 0;
  const aspectModes = [
    { mode: 'contain', label: 'Mặc định (Fit)', desc: 'Chuẩn gốc không cắt viền', badge: 'Fit' },
    { mode: 'cover', label: 'Lấp đầy (Fill)', desc: 'Tràn viền, cắt viền đen', badge: 'Fill' },
    { mode: 'fill', label: 'Căng phẳng (Stretch)', desc: 'Kéo giãn 100% toàn khung', badge: 'Căng' }
  ];

  // --- Constants ---
  const KKPHIM_IMG_BASE = 'https://phimimg.com/';
  const DEFAULT_TV_LOGO = 'data/logos/tv_default_premium.png';

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
  }

  // --- Match Schedules ---
  const LIVE_MATCHES = [
    {
      id: "match_c1_1",
      tournament: "🏆 UEFA Champions League",
      teamA: "Real Madrid",
      teamB: "Manchester City",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/86.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
      time: "Đang diễn ra • Trực Tiếp",
      channelSlug: "sports_vn_vtv6",
      channelName: "VTV6 Thể Thao HD (FPT)"
    },
    {
      id: "match_epl_1",
      tournament: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh",
      teamA: "Arsenal",
      teamB: "Chelsea",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/359.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/363.png",
      time: "Hôm Nay • 20:30",
      channelSlug: "sports_intl_cbs_golazo",
      channelName: "CBS Sports Golazo (Cúp C1 / Serie A)"
    },
    {
      id: "match_laliga_1",
      tournament: "🇪🇸 La Liga Tây Ban Nha",
      teamA: "Barcelona",
      teamB: "Atletico Madrid",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/83.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/1068.png",
      time: "Hôm Nay • 23:00",
      channelSlug: "sports_intl_bein_xtra",
      channelName: "beIN SPORTS XTRA HD"
    },
    {
      id: "match_aff_1",
      tournament: "🇻🇳 AFF Mitsubishi Electric Cup",
      teamA: "Việt Nam",
      teamB: "Thái Lan",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/2927.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/2926.png",
      time: "Ngày Mai • 19:30",
      channelSlug: "vtv5_tay_nam_bo",
      channelName: "VTV5 Tây Nam Bộ"
    },
    {
      id: "match_uel_1",
      tournament: "🏆 UEFA Europa League",
      teamA: "Manchester United",
      teamB: "AS Roma",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/104.png",
      time: "Hôm Nay • 03:00",
      channelSlug: "sports_intl_eurosport_live",
      channelName: "Eurosport Live HD"
    }
  ];

  // --- Filters per Source ---
  // --- Anime Sub-Sources Data ---

  // --- MD5 Implementation for FreeReels HMAC Signing ---
  function md5(str) {
    function safeAdd(x, y) {
      const lsw = (x & 0xffff) + (y & 0xffff);
      const msw = (x >> 16) + (y >> 16) + (lsw >> 16);
      return (msw << 16) | (lsw & 0xffff);
    }
    function bitRol(num, cnt) {
      return (num << cnt) | (num >>> (32 - cnt));
    }
    function md5cmn(q, a, b, x, s, t) {
      return safeAdd(bitRol(safeAdd(safeAdd(a, q), safeAdd(x, t)), s), b);
    }
    function md5ff(a, b, c, d, x, s, t) {
      return md5cmn((b & c) | (~b & d), a, b, x, s, t);
    }
    function md5gg(a, b, c, d, x, s, t) {
      return md5cmn((b & d) | (c & ~d), a, b, x, s, t);
    }
    function md5hh(a, b, c, d, x, s, t) {
      return md5cmn(b ^ c ^ d, a, b, x, s, t);
    }
    function md5ii(a, b, c, d, x, s, t) {
      return md5cmn(c ^ (b | ~d), a, b, x, s, t);
    }
    function binlMD5(x, len) {
      x[len >> 5] |= 0x80 << (len % 32);
      x[(((len + 64) >>> 9) << 4) + 14] = len;
      let a = 1732584193, b = -271733879, c = -1732584194, d = 271733878;
      for (let i = 0; i < x.length; i += 16) {
        const olda = a, oldb = b, oldc = c, oldd = d;
        a = md5ff(a, b, c, d, x[i], 7, -680876936);
        d = md5ff(d, a, b, c, x[i + 1], 12, -389564586);
        c = md5ff(c, d, a, b, x[i + 2], 17, 606105819);
        b = md5ff(b, c, d, a, x[i + 3], 22, -1044525330);
        a = md5ff(a, b, c, d, x[i + 4], 7, -176418897);
        d = md5ff(d, a, b, c, x[i + 5], 12, 1200080426);
        c = md5ff(c, d, a, b, x[i + 6], 17, -1473231341);
        b = md5ff(b, c, d, a, x[i + 7], 22, -45705983);
        a = md5ff(a, b, c, d, x[i + 8], 7, 1770035416);
        d = md5ff(d, a, b, c, x[i + 9], 12, -1958414417);
        c = md5ff(c, d, a, b, x[i + 10], 17, -42063);
        b = md5ff(b, c, d, a, x[i + 11], 22, -1990404162);
        a = md5ff(a, b, c, d, x[i + 12], 7, 1804603682);
        d = md5ff(d, a, b, c, x[i + 13], 12, -40341101);
        c = md5ff(c, d, a, b, x[i + 14], 17, -1502002290);
        b = md5ff(b, c, d, a, x[i + 15], 22, 1236535329);

        a = md5gg(a, b, c, d, x[i + 1], 5, -165796510);
        d = md5gg(d, a, b, c, x[i + 6], 9, -1069501632);
        c = md5gg(c, d, a, b, x[i + 11], 14, 643717713);
        b = md5gg(b, c, d, a, x[i], 20, -373897302);
        a = md5gg(a, b, c, d, x[i + 5], 5, -701558691);
        d = md5gg(d, a, b, c, x[i + 10], 9, 38016083);
        c = md5gg(c, d, a, b, x[i + 15], 14, -660478335);
        b = md5gg(b, c, d, a, x[i + 4], 20, -405537848);
        a = md5gg(a, b, c, d, x[i + 9], 5, 568446438);
        d = md5gg(d, a, b, c, x[i + 14], 9, -1019803690);
        c = md5gg(c, d, a, b, x[i + 3], 14, -187363961);
        b = md5gg(b, c, d, a, x[i + 8], 20, 1163531501);
        a = md5gg(a, b, c, d, x[i + 13], 5, -1444681467);
        d = md5gg(d, a, b, c, x[i + 2], 9, -51403784);
        c = md5gg(c, d, a, b, x[i + 7], 14, 1735328473);
        b = md5gg(b, c, d, a, x[i + 12], 20, -1926607734);

        a = md5hh(a, b, c, d, x[i + 5], 4, -378558);
        d = md5hh(d, a, b, c, x[i + 8], 11, -2022574463);
        c = md5hh(c, d, a, b, x[i + 11], 16, 1839030562);
        b = md5hh(b, c, d, a, x[i + 14], 23, -35309556);
        a = md5hh(a, b, c, d, x[i + 1], 4, -1530992060);
        d = md5hh(d, a, b, c, x[i + 4], 11, 1272893353);
        c = md5hh(c, d, a, b, x[i + 7], 16, -155497632);
        b = md5hh(b, c, d, a, x[i + 10], 23, -1094730640);
        a = md5hh(a, b, c, d, x[i + 13], 4, 681279174);
        d = md5hh(d, a, b, c, x[i], 11, -358537222);
        c = md5hh(c, d, a, b, x[i + 3], 16, -722521979);
        b = md5hh(b, c, d, a, x[i + 6], 23, 76029189);
        a = md5hh(a, b, c, d, x[i + 9], 4, -640364487);
        d = md5hh(d, a, b, c, x[i + 12], 11, -421815835);
        c = md5hh(c, d, a, b, x[i + 15], 16, 530742520);
        b = md5hh(b, c, d, a, x[i + 2], 23, -995338651);

        a = md5ii(a, b, c, d, x[i], 6, -198630844);
        d = md5ii(d, a, b, c, x[i + 7], 10, 1126891415);
        c = md5ii(c, d, a, b, x[i + 14], 15, -1416354905);
        b = md5ii(b, c, d, a, x[i + 5], 21, -57434055);
        a = md5ii(a, b, c, d, x[i + 12], 6, 1700485571);
        d = md5ii(d, a, b, c, x[i + 3], 10, -1894986606);
        c = md5ii(c, d, a, b, x[i + 10], 15, -1051523);
        b = md5ii(b, c, d, a, x[i + 1], 21, -2054922799);
        a = md5ii(a, b, c, d, x[i + 8], 6, 1873313359);
        d = md5ii(d, a, b, c, x[i + 15], 10, -30611744);
        c = md5ii(c, d, a, b, x[i + 6], 15, -1560198380);
        b = md5ii(b, c, d, a, x[i + 13], 21, 1309151649);
        a = md5ii(a, b, c, d, x[i + 4], 6, -145523070);
        d = md5ii(d, a, b, c, x[i + 11], 10, -1120210379);
        c = md5ii(c, d, a, b, x[i + 2], 15, 718787259);
        b = md5ii(b, c, d, a, x[i + 9], 21, -343485551);

        a = safeAdd(a, olda);
        b = safeAdd(b, oldb);
        c = safeAdd(c, oldc);
        d = safeAdd(d, oldd);
      }
      return [a, b, c, d];
    }
    function rstr2binl(input) {
      const output = Array(input.length >> 2).fill(0);
      for (let i = 0; i < input.length * 8; i += 8) {
        output[i >> 5] |= (input.charCodeAt(i / 8) & 0xff) << (i % 32);
      }
      return output;
    }
    function binl2rstr(input) {
      let output = '';
      for (let i = 0; i < input.length * 32; i += 8) {
        output += String.fromCharCode((input[i >> 5] >>> (i % 32)) & 0xff);
      }
      return output;
    }
    function rstr2hex(input) {
      const hexTab = '0123456789abcdef';
      let output = '';
      for (let i = 0; i < input.length; i++) {
        const x = input.charCodeAt(i);
        output += hexTab.charAt((x >>> 4) & 0x0f) + hexTab.charAt(x & 0x0f);
      }
      return output;
    }
    return rstr2hex(binl2rstr(binlMD5(rstr2binl(unescape(encodeURIComponent(str))), unescape(encodeURIComponent(str)).length * 8)));
  }

  // --- GaMoMePhim Native Client (v2.7) ---
  const GaMoMePhimClient = window.GaMoMePhimClient = {
    BASE_URL: 'https://gamomephim.com',
    getProxyUrl(target) {
      return getAppProxyUrl(target);
    },
    parseHtmlItems(html) {
      const list = [];
      const seen = new Set();
      const aRegex = /<a[^>]+href="\/phim\/([^"/]+)"[^>]*>(.*?)<\/a>/gs;
      let match;
      while ((match = aRegex.exec(html)) !== null) {
        const slug = match[1].trim();
        const body = match[2];
        if (!slug || seen.has(slug)) continue;

        let title = '';
        const titleMatch = match[0].match(/title="([^"]+)"/);
        if (titleMatch) {
          title = titleMatch[1].trim();
        }
        if (!title) {
          const hMatch = body.match(/<h[34][^>]*>(.*?)<\/h[34]>/s);
          if (hMatch) {
            title = hMatch[1].replace(/<[^>]+>/g, '').trim();
          }
        }
        if (!title) {
          const altMatch = body.match(/<img[^>]+alt="([^"]+)"/);
          if (altMatch) {
            title = altMatch[1].replace(/Poster phim |Poster /g, '').trim();
          }
        }

        let thumb = '';
        const imgMatch = body.match(/<img[^>]+src="([^"]+)"/);
        if (imgMatch) {
          thumb = imgMatch[1].trim();
        }

        if (slug && title) {
          seen.add(slug);
          list.push({
            id: `gamomephim:${slug}`,
            name: title,
            slug: `gamomephim:${slug}`,
            originName: 'Gà Mờ Mê Phim • Thuyết Minh',
            thumbUrl: thumb,
            posterUrl: thumb,
            year: '2026',
            quality: '🎙️ Thuyết Minh & Vietsub',
            episodeCurrent: 'Full Bộ HD',
            source: 'FREEREELS'
          });
        }
      }
      return list;
    },
    async getDramaList(filterUrl, page = 1) {
      try {
        const genrePath = filterUrl.replace('gamomephim://', '');
        const targetUrl = page <= 1 ? `${this.BASE_URL}/${genrePath}` : `${this.BASE_URL}/${genrePath}?page=${page}`;
        const resp = await fetch(this.getProxyUrl(targetUrl));
        if (!resp.ok) return [];
        const html = await resp.text();
        let list = this.parseHtmlItems(html);

        // Tự động fallback sang Phim Mới nếu thể loại này ít phim và hết ở trang tiếp theo (chống lỗi kéo thêm không ra phim)
        if (list.length === 0 && page > 1 && genrePath !== 'phim-moi') {
          try {
            const fbResp = await fetch(this.getProxyUrl(`${this.BASE_URL}/phim-moi?page=${page}`));
            if (fbResp.ok) {
              const fbHtml = await fbResp.text();
              const fbList = this.parseHtmlItems(fbHtml);
              if (fbList.length > 0) {
                fbList.forEach(item => {
                  item.originName = 'Gà Mờ Mê Phim • Mới Cập Nhật';
                  list.push(item);
                });
              }
            }
          } catch(err) {
            console.warn('GaMoMePhim fallback err:', err);
          }
        }

        return list;
      } catch (e) {
        console.warn('GaMoMePhim getDramaList err:', e);
        return [];
      }
    },
    async getDramaDetail(cleanSlug) {
      try {
        const clean = cleanSlug.replace(/^phim\//, '');
        // Trang xem video chính thức trên GaMoMePhim là /${clean}
        let resp = await fetch(this.getProxyUrl(`${this.BASE_URL}/${clean}`));
        if (!resp.ok) {
          resp = await fetch(this.getProxyUrl(`${this.BASE_URL}/phim/${clean}`));
        }
        if (!resp.ok) return null;
        let html = await resp.text();
        html = html.replace(/\\\//g, '/');

        let title = '';
        const titleMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/);
        if (titleMatch) title = titleMatch[1].trim();
        if (!title) title = clean.replace(/-/g, ' ');

        let desc = 'Phim ngắn tiểu kịch lồng tiếng/thuyết minh tiếng Việt trọn bộ cực hay.';
        const descMatch = html.match(/description\\":\\"([^\\"]+)\\"/) || html.match(/description":\s*"([^"]+)"/);
        if (descMatch) desc = descMatch[1].replace(/\\n/g, '\n');

        let thumb = '';
        const thumbMatch = html.match(/https:\/\/r2\.gamomephim\.com\/thumbnails\/[^"'\s<>]+/);
        if (thumbMatch) thumb = thumbMatch[0];

        const streamMatches = [...html.matchAll(/https:\/\/r2\.gamomephim\.com\/videos\/[^\s"'<>]+\.mp4/g)];
        const streamUrls = [...new Set(streamMatches.map(m => m[0]))].filter(s => !s.includes('-thumb'));

        const tmStream = streamUrls.find(s => /-tm(?:-\d+)?\.mp4/i.test(s));
        const subStream = streamUrls.find(s => /-sub(?:-\d+)?\.mp4/i.test(s));

        const servers = [];
        if (tmStream) {
          servers.push({
            server_name: '🎙️ Thuyết Minh (Gà Mờ Mê Phim)',
            server_data: [{
              name: 'Tập Full (Thuyết Minh)',
              slug: cleanSlug,
              link_m3u8: tmStream
            }]
          });
        }
        if (subStream) {
          servers.push({
            server_name: '🇻🇳 Vietsub (Gà Mờ Mê Phim)',
            server_data: [{
              name: 'Tập Full (Vietsub)',
              slug: cleanSlug,
              link_m3u8: subStream
            }]
          });
        }
        if (servers.length === 0 && streamUrls.length > 0) {
          servers.push({
            server_name: '▶️ Bản Chuẩn HD (Gà Mờ Mê Phim)',
            server_data: [{
              name: 'Tập Full',
              slug: cleanSlug,
              link_m3u8: streamUrls[0]
            }]
          });
        }

        return {
          id: `gamomephim:${cleanSlug}`,
          name: title,
          slug: `gamomephim:${cleanSlug}`,
          content: desc,
          thumbUrl: thumb,
          posterUrl: thumb,
          year: '2026',
          time: 'Trọn bộ',
          quality: 'Full HD',
          lang: tmStream ? 'Thuyết Minh' : 'Vietsub',
          source: 'FREEREELS',
          episodes: servers
        };
      } catch (e) {
        console.warn('GaMoMePhim getDramaDetail err:', e);
        return null;
      }
    },
    async search(keyword) {
      try {
        const targetUrl = `${this.BASE_URL}/tim-kiem?q=${encodeURIComponent(keyword)}`;
        const resp = await fetch(this.getProxyUrl(targetUrl));
        if (!resp.ok) return [];
        const html = await resp.text();
        const pattern = /<a[^>]+title="([^"]+)"[^>]+href="\/phim\/([^"]+)".*?<img[^>]+src="([^"]+)"/gs;
        const matches = [...html.matchAll(pattern)];
        const list = [];
        const seen = new Set();
        for (const m of matches) {
          const title = m[1].trim();
          const slug = m[2].trim();
          const thumb = m[3].trim();
          if (slug && !seen.has(slug)) {
            seen.add(slug);
            list.push({
              id: `gamomephim:${slug}`,
              name: title,
              slug: `gamomephim:${slug}`,
              originName: 'Gà Mờ Mê Phim • Thuyết Minh',
              thumbUrl: thumb,
              posterUrl: thumb,
              year: '2026',
              quality: '🎙️ Thuyết Minh & Vietsub',
              episodeCurrent: 'Full Bộ HD',
              source: 'FREEREELS'
            });
          }
        }
        return list;
      } catch (e) {
        return [];
      }
    }
  };

  // --- FreeReels Native API Client (v2.5) ---
  const FreeReelsClient = window.FreeReelsClient = {
    API_BASE: 'https://apiv2.free-reels.com/frv2-api',
    getProxyUrl(target) {
      return getAppProxyUrl(target);
    },
    APP_SECRET: '8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv',
    APP_NAME: 'com.freereels.app',
    APP_VERSION: '2.2.81',
    deviceId: '',
    sessionId: '',
    oauthToken: '',
    oauthSecret: '',

    async ensureLogin() {
      if (this.oauthToken && this.oauthSecret) return true;
      try {
        if (!this.deviceId) {
          try {
            this.deviceId = localStorage.getItem('huyca_fr_device_id') || '';
          } catch(e) {}
          if (!this.deviceId) {
            this.deviceId = 'fr_' + Math.random().toString(36).substring(2) + Date.now().toString(36);
            try { localStorage.setItem('huyca_fr_device_id', this.deviceId); } catch(e) {}
          }
        }
        if (!this.sessionId) {
          this.sessionId = 'sess_' + Math.random().toString(36).substring(2) + Date.now().toString(36);
        }

        const sign = md5(this.APP_SECRET + this.deviceId);
        const loginData = {
          device_id: this.deviceId,
          device_name: 'samsung SM-A536E',
          sign: sign
        };

        const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/anonymous/login`), {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'app-name': this.APP_NAME,
            'app-version': this.APP_VERSION,
            'device': 'android',
            'device-version': '33',
            'device-id': this.deviceId,
            'session-id': this.sessionId,
            'language': 'vi-VN',
            'country': 'VN'
          },
          body: JSON.stringify(loginData)
        });

        if (!resp.ok) return false;
        const resJson = await resp.json();
        if (resJson && resJson.data) {
          this.oauthToken = resJson.data.auth_key || '';
          this.oauthSecret = resJson.data.auth_secret || '';
          return !!(this.oauthToken && this.oauthSecret);
        }
        return false;
      } catch (e) {
        console.warn('FreeReels login error:', e);
        return false;
      }
    },

    async getAuthorizedHeaders() {
      const ok = await this.ensureLogin();
      if (!ok) return null;
      const ts = String(Date.now());
      const sig = md5(`${this.APP_SECRET}&${this.oauthSecret}`);
      return {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
        'app-name': this.APP_NAME,
        'app-version': this.APP_VERSION,
        'device': 'android',
        'device-version': '33',
        'device-id': this.deviceId,
        'session-id': this.sessionId,
        'language': 'vi-VN',
        'country': 'VN',
        'Authorization': `oauth_signature=${sig},oauth_token=${this.oauthToken},ts=${ts}`
      };
    },

    cursorMap: {},
    tabFeedCache: {},
    searchResultCache: {},
    searchRateLimitedUntil: 0,

    parseDramaItems(itemsArr) {
      const list = [];
      if (!Array.isArray(itemsArr)) return list;
      itemsArr.forEach(el => {
        if (!el || typeof el !== 'object') return;
        const series = (el.series && typeof el.series === 'object') ? el.series : (el.info || el);
        const id = series.id || series.key || series.series_id || '';
        const title = (series.title || series.name || '').trim();
        const cover = series.cover || series.poster || '';
        const epCount = Number(series.episode_count || series.episodes_count || 1);
        const isForeignDub = /\((synchron|doblado|dublado|doublé|doppiato)\)/i.test(title);
        if (id && title && title.toUpperCase() !== 'TOP' && !isForeignDub) {
          const isDubbed = title.toLowerCase().includes('lồng tiếng') || title.toLowerCase().includes('thuyết minh');
          list.push({
            id: `freereels:${id}`,
            name: title,
            slug: `freereels:${id}`,
            originName: isDubbed ? `${epCount} tập • Lồng Tiếng Việt` : `${epCount} tập • Phụ Đề Tiếng Việt`,
            thumbUrl: cover,
            posterUrl: cover,
            year: '2026',
            quality: isDubbed ? '🎙️ Lồng Tiếng' : '🎬 Phụ Đề HD',
            episodeCurrent: `${epCount} tập`,
            source: 'FREEREELS'
          });
        }
      });
      return list;
    },

    async fetchTabFeedOffset(tabKey = '503', offset = 0) {
      const cKey = `${tabKey}_${offset}`;
      if (this.tabFeedCache[cKey] && this.tabFeedCache[cKey].length > 0) {
        return this.tabFeedCache[cKey];
      }
      const headers = await this.getAuthorizedHeaders();
      if (!headers) return [];

      try {
        if (tabKey === 'foryou') {
          const nextParam = offset > 0 ? `offset=${offset}` : '';
          const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/foryou/feed?next=${encodeURIComponent(nextParam)}`), { headers });
          if (!resp.ok) return [];
          const res = await resp.json();
          const data = res.data || {};
          const parsed = this.parseDramaItems(data.items || data.list || []);
          if (parsed.length > 0) this.tabFeedCache[cKey] = parsed;
          return parsed;
        }

        const TAB_META = {
          '503': { moduleKey: '1036', pos: 10000, simpleNext: true },
          '505': { moduleKey: '1040', pos: 10001, simpleNext: false },
          '504': { moduleKey: '1039', pos: 10003, simpleNext: false },
          '506': { moduleKey: '1041', pos: 10004, simpleNext: false },
          '547': { moduleKey: '2204', pos: 10005, simpleNext: true }
        };
        const meta = TAB_META[tabKey] || TAB_META['503'];
        const nextStr = meta.simpleNext
          ? `offset=${offset}&position_index=${meta.pos}`
          : `last_quality=0&offset=${offset}&position_index=${meta.pos}&timestamp=`;

        const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/homepage/v2/tab/feed`), {
          method: 'POST',
          headers,
          body: JSON.stringify({
            tab_key: String(tabKey),
            module_key: meta.moduleKey,
            next: nextStr
          })
        });
        if (!resp.ok) return [];
        const res = await resp.json();
        const data = res.data || {};
        const parsed = this.parseDramaItems(data.items || data.list || []);
        if (parsed.length > 0) this.tabFeedCache[cKey] = parsed;
        return parsed;
      } catch (e) {
        console.warn('FreeReels fetchTabFeedOffset err:', e);
        return [];
      }
    },

    async getDramaList(filterUrl, page = 1) {
      const baseOffset = (page - 1) * 20;
      if (filterUrl === 'freereels://foryou' || filterUrl.startsWith('freereels://foryou')) {
        const [a, b] = await Promise.all([
          this.fetchTabFeedOffset('503', baseOffset + 10),
          this.fetchTabFeedOffset('504', baseOffset + 20)
        ]);
        return [...a, ...b];
      }
      if (filterUrl === 'freereels://dubbed_vi') {
        const [a, b, c] = await Promise.all([
          this.fetchTabFeedOffset('503', baseOffset),
          this.fetchTabFeedOffset('504', baseOffset),
          this.fetchTabFeedOffset('506', baseOffset)
        ]);
        const combined = [...a, ...b, ...c];
        const dubbed = combined.filter(m => m.name.toLowerCase().includes('lồng tiếng') || m.name.toLowerCase().includes('thuyết minh'));
        return dubbed.length > 0 ? dubbed : combined;
      }
      if (filterUrl.startsWith('freereels://tab_')) {
        const tabKey = filterUrl.replace('freereels://tab_', '');
        const [a, b] = await Promise.all([
          this.fetchTabFeedOffset(tabKey, baseOffset),
          this.fetchTabFeedOffset(tabKey, baseOffset + 10)
        ]);
        return [...a, ...b];
      }
      const [a, b] = await Promise.all([
        this.fetchTabFeedOffset('503', baseOffset),
        this.fetchTabFeedOffset('foryou', baseOffset)
      ]);
      return [...a, ...b];
    },

    searchCursorMap: {},
    async search(keyword, page = 1) {
      const cacheKey = `search_${keyword}_p${page}`;
      if (this.searchResultCache[cacheKey] && this.searchResultCache[cacheKey].length > 0) {
        return this.searchResultCache[cacheKey];
      }

      const headers = await this.getAuthorizedHeaders();
      if (!headers) return [];

      // Thử gọi /search/drama nếu không đang trong thời gian cooldown rate-limit
      if (!this.searchRateLimitedUntil || Date.now() > this.searchRateLimitedUntil) {
        const cursorKey = `cursor_${keyword}`;
        if (page <= 1) {
          this.searchCursorMap[cursorKey] = '';
        }
        const cursor = this.searchCursorMap[cursorKey] || '';
        try {
          const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/search/drama`), {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ keyword: keyword, next: cursor })
          });
          if (resp.ok) {
            const res = await resp.json();
            const data = res.data || {};
            if (data.next) {
              this.searchCursorMap[cursorKey] = data.next;
            }
            const list = this.parseDramaItems(data.items || data.list || []);
            if (list.length > 0) {
              this.searchResultCache[cacheKey] = list;
              return list;
            } else {
              // /search/drama trả rỗng do bị giới hạn tần suất -> kích hoạt fallback sang Tab Feed không giới hạn trong 90s
              this.searchRateLimitedUntil = Date.now() + 90000;
            }
          }
        } catch (e) {
          console.warn('FreeReels search error:', e);
        }
      }

      // Fallback thông minh sang hệ thống Tab Feed & ForYou Feed (Mỗi nguồn & bộ lọc có danh sách phim riêng biệt, không trùng lặp!)
      const kwLower = (keyword || '').toLowerCase().trim();
      const FALLBACK_FEED_MAP = {
        'người sói': ['505', 0, 'foryou', 10],
        'vua sói': ['505', 20, 'foryou', 0],
        'ma cà rồng': ['505', 20, 'foryou', 30],
        'tỷ phú': ['505', 10, 'foryou', 20],
        'mafia': ['505', 30, 'foryou', 40],
        'hợp đồng': ['505', 40, 'foryou', 50],
        'tổng tài': ['504', 0, '503', 10],
        'báo thù': ['503', 20, '504', 20],
        'trọng sinh': ['503', 30, '504', 30],
        'chiến thần': ['503', 10, '506', 30],
        'cổ trang': ['504', 10, '506', 20],
        'hào môn': ['504', 40, '503', 20],
        'nghịch tập': ['506', 10, '503', 40],
        'cao thủ': ['506', 30, '503', 10],
        'thần y': ['506', 20, '506', 30],
        'mạt thế': ['506', 40, '547', 20],
        'thế thân': ['504', 20, '505', 20],
        'người máy': ['547', 10, '547', 0],
        'trí tuệ nhân tạo': ['547', 20, '506', 20],
        'khoa học': ['547', 20, '547', 30],
        'đếm ngược': ['547', 30, '506', 10],
        'hệ thống': ['547', 0, '503', 20],
        'cưng chiều': ['foryou', 0, '504', 20],
        'tình yêu': ['foryou', 10, '504', 30],
        'định mệnh': ['foryou', 20, '505', 10],
        'cô dâu': ['foryou', 10, '504', 10],
        'ngọt sủng': ['foryou', 30, '504', 0],
        'bảo bối': ['504', 30, 'foryou', 40],
        'lồng tiếng': ['503', 0, '506', 0]
      };

      const cfg = FALLBACK_FEED_MAP[kwLower] || ['503', (kwLower.length % 5) * 10, 'foryou', ((kwLower.length + 2) % 5) * 10];
      const pOffset = cfg[1] + (page - 1) * 20;
      const sOffset = cfg[3] + (page - 1) * 20;
      const [batch1, batch2] = await Promise.all([
        this.fetchTabFeedOffset(cfg[0], pOffset),
        this.fetchTabFeedOffset(cfg[2], sOffset)
      ]);
      const fallbackList = [...batch1, ...batch2];
      if (fallbackList.length > 0) {
        this.searchResultCache[cacheKey] = fallbackList;
      }
      return fallbackList;
    },

    async getDramaDetail(seriesId) {
      const headers = await this.getAuthorizedHeaders();
      if (!headers) return null;

      const url = `${this.API_BASE}/drama/info_v2?series_id=${encodeURIComponent(seriesId)}&scene=search`;
      try {
        const resp = await fetch(this.getProxyUrl(url), { headers });
        if (!resp.ok) return null;
        const res = await resp.json();
        const data = res.data || {};
        const info = (data.info && typeof data.info === 'object') ? data.info : data;

        const title = info.name || info.title || '';
        const cover = info.cover || info.poster || '';
        const desc = info.desc || 'Phim ngắn màn hình dọc FreeReels chất lượng cao (9:16) kèm phụ đề/thuyết minh Tiếng Việt.';
        const epCount = info.episode_count || 'Nhiều';
        const epArray = info.episode_list || [];

        const epList = [];
        epArray.forEach((el, idx) => {
          const epId = el.id || el.key || '';
          let rawName = (el.name || '').trim();
          let epName = `Tập ${idx + 1}`;
          if (rawName && !rawName.toLowerCase().includes(title.toLowerCase()) && rawName.length <= 20) {
            epName = /^\d+$/.test(rawName) ? `Tập ${rawName}` : rawName;
          }

          let viSubUrl = null;
          if (Array.isArray(el.subtitle_list)) {
            el.subtitle_list.forEach(s => {
              const lang = (s.language || '').toLowerCase();
              const disp = (s.display_name || '').toLowerCase();
              if (lang.includes('vi') || disp.includes('việt') || disp.includes('viet')) {
                viSubUrl = s.subtitle || s.vtt || null;
              }
            });
            if (!viSubUrl && el.subtitle_list.length > 0) {
              const enSub = el.subtitle_list.find(s => (s.language || '').toLowerCase().includes('en'));
              viSubUrl = enSub ? (enSub.subtitle || enSub.vtt) : (el.subtitle_list[0].subtitle || el.subtitle_list[0].vtt);
            }
          }
          if (viSubUrl && viSubUrl.startsWith('http')) {
            viSubUrl = this.getProxyUrl(viSubUrl);
          }

          let rawStream = el.external_audio_h264_m3u8 || el.m3u8_url || el.video_url || el.external_audio_h265_m3u8 || '';
          let finalLink = `freereels_unlock:${seriesId}:${epId}`;
          if (rawStream && rawStream.startsWith('http')) {
            finalLink = this.getProxyUrl(rawStream);
          }

          epList.push({
            name: epName,
            slug: epId,
            filename: epName,
            link_m3u8: finalLink,
            subtitleUrl: viSubUrl
          });
        });

        // Mở khóa trước tập 1 nếu chưa có link trực tiếp
        if (epList.length > 0 && epList[0].link_m3u8.startsWith('freereels_unlock:')) {
          const unlockRes = await this.unlockEpisode(seriesId, epList[0].slug);
          if (unlockRes && unlockRes.streamUrl) {
            epList[0].link_m3u8 = unlockRes.streamUrl;
            if (unlockRes.subtitleUrl) epList[0].subtitleUrl = unlockRes.subtitleUrl;
          }
        }

        return {
          movie: {
            id: `freereels:${seriesId}`,
            name: title,
            slug: `freereels:${seriesId}`,
            content: desc,
            thumb_url: cover,
            poster_url: cover,
            year: '2026',
            time: `${epCount} tập`,
            quality: '9:16 Dọc HD',
            lang: 'Vietsub / Thuyết Minh Tiếng Việt'
          },
          episodes: [
            {
              server_name: 'FreeReels VIP (Phụ Đề / Lồng Tiếng Việt)',
              server_data: epList
            }
          ]
        };
      } catch (e) {
        console.warn('FreeReels getDramaDetail err:', e);
        return null;
      }
    },

    async unlockEpisode(seriesId, episodeId) {
      const headers = await this.getAuthorizedHeaders();
      if (!headers) return null;

      const url = `${this.API_BASE}/drama/unlock_episode`;
      const body = JSON.stringify({ series_id: seriesId, episode_id: episodeId, lang: 'vi' });
      try {
        const resp = await fetch(this.getProxyUrl(url), { method: 'POST', headers, body });
        if (!resp.ok) return null;
        const res = await resp.json();
        const data = res.data || {};
        let stream = data.external_audio_h264_m3u8 || data.m3u8_url || data.video_url || null;
        if (stream && stream.startsWith('http')) {
          stream = this.getProxyUrl(stream);
        }
        let viSubUrl = null;
        if (Array.isArray(data.subtitle_list)) {
          data.subtitle_list.forEach(s => {
            const lang = (s.language || '').toLowerCase();
            const disp = (s.display_name || '').toLowerCase();
            if (lang.includes('vi') || disp.includes('việt') || disp.includes('viet')) {
              viSubUrl = s.subtitle || s.vtt || null;
            }
          });
          if (!viSubUrl && data.subtitle_list.length > 0) {
            const enSub = data.subtitle_list.find(s => (s.language || '').toLowerCase().includes('en'));
            viSubUrl = enSub ? (enSub.subtitle || enSub.vtt) : (data.subtitle_list[0].subtitle || data.subtitle_list[0].vtt);
          }
        }
        if (viSubUrl && viSubUrl.startsWith('http')) {
          viSubUrl = this.getProxyUrl(viSubUrl);
        }
        return { streamUrl: stream, subtitleUrl: viSubUrl };
      } catch (e) {
        console.warn('FreeReels unlockEpisode err:', e);
        return null;
      }
    },


  };

  let currentSubSource = 'movie_sub://kkphim';
  const SUB_SOURCES = {
    KKPHIM: [
      { name: "⚡ KKPhim VIP (HLS 1080p)", key: "movie_sub://kkphim" },
      { name: "🔥 NguonC Cinema (Phim Rạp & Mới)", key: "movie_sub://nguonc" },
      { name: "🎙️ Thuyết Minh & Lồng Tiếng", key: "movie_sub://dubbed" },
      { name: "🍿 Phim Chiếu Rạp Bom Tấn", key: "movie_sub://cinema" }
    ],
    ANIMEHAY: [
      { name: "⛩️ Anime Vietsub", key: "anime_sub://vietsub" },
      { name: "🐉 Hoạt Hình 3D Trung Quốc", key: "anime_sub://hh3d" },
      { name: "🏰 Hoạt Hình Chiếu Rạp", key: "anime_sub://movies" },
      { name: "🎙️ Anime Thuyết Minh (Tổng Hợp)", key: "anime_sub://dubbed" }
    ],
    FREEREELS: [
      { name: "🐺 Nguồn ReelShort (Âu Mỹ)", key: "short_src://reelshort" },
      { name: "📱 Nguồn DramaBox (Top Thế Giới)", key: "short_src://dramabox" },
      { name: "⚡ Nguồn ShortMax (Thịnh Hành)", key: "short_src://shortmax" },
      { name: "💎 Nguồn FreeReels Gốc (9:16)", key: "short_src://freereels" },
      { name: "🎙️ Nguồn Gà Mờ Mê Phim (Thuyết Minh)", key: "short_src://gamomephim" },
      { name: "🤖 Nguồn AI Cinema (Phim AI & Sora)", key: "short_src://aicinema" },
      { name: "🎭 Nguồn GoodShort & Sereal+", key: "short_src://goodshort" }
    ],
    'movie_sub://nguonc': [
      { name: "🔥 Mới Cập Nhật", url: "https://phim.nguonc.com/api/films/phim-moi-cap-nhat" },
      { name: "🎬 Phim Bộ Mới", url: "https://phim.nguonc.com/api/films/danh-sach/phim-bo" },
      { name: "🍿 Phim Lẻ / Chiếu Rạp", url: "https://phim.nguonc.com/api/films/danh-sach/phim-le" },
      { name: "📺 TV Shows", url: "https://phim.nguonc.com/api/films/danh-sach/tv-shows" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Phim Yêu Thích", url: "app://favorites" }
    ],
    'movie_sub://dubbed': [
      { name: "🎙️ Thuyết Minh Chuẩn", url: "https://phimapi.com/v1/api/danh-sach/phim-thuyet-minh" },
      { name: "🗣️ Lồng Tiếng", url: "https://phimapi.com/v1/api/danh-sach/phim-long-tieng" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Phim Yêu Thích", url: "app://favorites" }
    ],
    'movie_sub://cinema': [
      { name: "🍿 Chiếu Rạp Mới Nhất", url: "https://phimapi.com/v1/api/danh-sach/phim-le" },
      { name: "🇺🇸 Bom Tấn Âu Mỹ", url: "https://phimapi.com/v1/api/quoc-gia/au-my" },
      { name: "🇰🇷 Chiếu Rạp Hàn Quốc", url: "https://phimapi.com/v1/api/quoc-gia/han-quoc" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Phim Yêu Thích", url: "app://favorites" }
    ],
    'anime_sub://vietsub': [
      { name: "Anime Mới Cập Nhật", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Anime Yêu Thích", url: "app://favorites" },
      { name: "Hành Động", url: "https://phimapi.com/v1/api/the-loai/hanh-dong" },
      { name: "Thần Thoại", url: "https://phimapi.com/v1/api/the-loai/than-thoai" },
      { name: "Học Đường", url: "https://phimapi.com/v1/api/the-loai/hoc-duong" },
      { name: "Viễn Tưởng", url: "https://phimapi.com/v1/api/the-loai/vien-tuong" }
    ],
    'anime_sub://hh3d': [
      { name: "3D Mới Cập Nhật", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Hoạt Hình Yêu Thích", url: "app://favorites" },
      { name: "Tu Tiên & Huyền Huyễn", url: "https://phimapi.com/v1/api/the-loai/than-thoai" },
      { name: "Kiếm Hiệp & Võ Thuật", url: "https://phimapi.com/v1/api/the-loai/kiem-hiep" },
      { name: "Hành Động 3D", url: "https://phimapi.com/v1/api/the-loai/hanh-dong" },
      { name: "Cổ Trang 3D", url: "https://phimapi.com/v1/api/the-loai/co-trang" }
    ],
    'anime_sub://movies': [
      { name: "Hoạt Hình Chiếu Rạp", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" },
      { name: "Ghibli & Cổ Điển", url: "https://phimapi.com/v1/api/the-loai/gia-dinh" },
      { name: "Phiêu Lưu", url: "https://phimapi.com/v1/api/the-loai/phieu-luu" },
      { name: "Hài Hước", url: "https://phimapi.com/v1/api/the-loai/hai-huoc" }
    ],
    'anime_sub://dubbed': [
      { name: "🎙️ Tất Cả Anime Thuyết Minh", url: "anime_dubbed://all" },
      { name: "⛩️ Anime Nhật Lồng Tiếng", url: "anime_dubbed://japan" },
      { name: "🐉 Hoạt Hình 3D Trung Quốc", url: "anime_dubbed://china" },
      { name: "🏰 Hoạt Hình Chiếu Rạp", url: "anime_dubbed://cinema" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'short_src://reelshort': [
      { name: "🔥 Thịnh Hành ReelShort", url: "short_kw://reelshort_hot" },
      { name: "🐺 Người Sói & Alpha (Werewolf)", url: "short_kw://werewolf" },
      { name: "🧛 Ma Cà Rồng (Vampire)", url: "short_kw://vampire" },
      { name: "💎 Tỷ Phú Âu Mỹ (Billionaire)", url: "short_kw://billionaire" },
      { name: "🔫 Mafia & Boss Ngầm", url: "short_kw://mafia" },
      { name: "💔 Hôn Nhân Hợp Đồng & Ngược Tâm", url: "short_kw://rejected" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'short_src://dramabox': [
      { name: "🔥 Top Thịnh Hành DramaBox", url: "short_kw://dramabox_hot" },
      { name: "👑 Tổng Tài Bá Đạo", url: "short_kw://tong_tai" },
      { name: "🐉 Trọng Sinh & Báo Thù", url: "short_kw://trong_sinh" },
      { name: "⚔️ Chiến Thần & Long Vương", url: "short_kw://chien_than" },
      { name: "🏰 Cổ Trang & Cung Đấu", url: "short_kw://co_trang" },
      { name: "💖 Hào Môn Thế Gia", url: "short_kw://hao_mon" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'short_src://shortmax': [
      { name: "⚡ Thịnh Hành ShortMax", url: "short_kw://shortmax_hot" },
      { name: "🚀 Nghịch Tập Đổi Đời", url: "short_kw://nghich_tap" },
      { name: "🩺 Thần Y & Cao Thủ", url: "short_kw://than_y" },
      { name: "🧟 Sinh Tồn & Mạt Thế", url: "short_kw://mat_the" },
      { name: "💍 Cô Dâu Thế Thân & Ngược Tâm", url: "short_kw://nguoc_tam" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'short_src://freereels': [
      { name: "🔥 Đề Xuất Thịnh Hành", url: "freereels://foryou" },
      { name: "🎙️ Phim Lồng Tiếng Việt", url: "freereels://dubbed_vi" },
      { name: "⚡ Mới Lên Sóng", url: "freereels://tab_505" },
      { name: "🎀 Tuyển Tập Phim Nữ", url: "freereels://tab_504" },
      { name: "👑 Tuyển Tập Phim Nam", url: "freereels://tab_506" },
      { name: "🎭 Hoạt Hình Ngắn 3D", url: "freereels://tab_547" },
      { name: "👑 Trọn Bộ Hoàn Tất", url: "short_kw://tron_bo" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'short_src://gamomephim': [
      { name: "🔥 Phim Mới Cập Nhật", url: "gamomephim://phim-moi" },
      { name: "🏆 Bảng Xếp Hạng Thịnh Hành", url: "gamomephim://ban-xep-hang" },
      { name: "👑 Cưới Trước Yêu Sau & Tổng Tài", url: "gamomephim://the-loai/cuoi-truoc-yeu-sau" },
      { name: "🪞 Gương Vỡ Lại Lành & Ngược Tâm", url: "gamomephim://the-loai/guong-vo-lai-lanh" },
      { name: "💘 Yêu Thầm & Ngọt Sủng", url: "gamomephim://the-loai/yeu-tham" },
      { name: "🌆 Tiểu Kịch Hiện Đại", url: "gamomephim://the-loai/hien-dai" },
      { name: "🐉 Trọng Sinh & Báo Thù", url: "gamomephim://the-loai/trong-sinh" },
      { name: "⏳ Xuyên Không Trùng Sinh", url: "gamomephim://the-loai/xuyen-khong" },
      { name: "🏰 Cổ Trang & Cung Đấu", url: "gamomephim://the-loai/co-trang" },
      { name: "🤣 Hài Hước & Hóm Hỉnh", url: "gamomephim://the-loai/hai-huoc" },
      { name: "🍵 Trà Xanh Nam & Ngược Tâm", url: "gamomephim://the-loai/tra-xanh-nam" },
      { name: "✨ Chữa Lành & Thanh Xuân", url: "gamomephim://the-loai/chua-lanh" },
      { name: "🎒 Thanh Xuân Vườn Trường", url: "gamomephim://the-loai/thanh-xuan" },
      { name: "🕰️ Dân Quốc & Niên Đại", url: "gamomephim://the-loai/dan-quoc" },
      { name: "🌾 Niên Đại Thập Niên", url: "gamomephim://the-loai/nien-dai" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'short_src://aicinema': [
      { name: "🤖 Tất Cả Phim AI & Sora", url: "short_kw://ai_all" },
      { name: "🦾 Thế Giới Robot & Cyborg", url: "short_kw://ai_robot" },
      { name: "🌌 Khoa Học Viễn Tưởng (Sci-Fi)", url: "short_kw://ai_scifi" },
      { name: "⏳ Du Hành Tương Lai", url: "short_kw://ai_future" },
      { name: "🧬 Thực Tế Ảo & Huyền Huyễn AI", url: "short_kw://ai_fantasy" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'short_src://goodshort': [
      { name: "🌟 Tuyển Chọn GoodShort", url: "short_kw://goodshort_hot" },
      { name: "🎬 Sereal+ Quốc Tế", url: "short_kw://sereal" },
      { name: "🍿 MoboReels & Mini Drama", url: "short_kw://moboreels" },
      { name: "💕 Ngôn Tình Ngọt Sủng", url: "short_kw://ngot_sung" },
      { name: "👶 Bảo Bối Thiên Tài", url: "short_kw://bao_boi" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ]
  };

  const SUB_FILTERS = SUB_SOURCES;

  const FILTERS = {
    KKPHIM: [
      { name: "Mới Cập Nhật", url: "https://phimapi.com/danh-sach/phim-moi-cap-nhat" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Phim Yêu Thích", url: "app://favorites" },
      { name: "Phim Bộ", url: "https://phimapi.com/v1/api/danh-sach/phim-bo" },
      { name: "Phim Lẻ", url: "https://phimapi.com/v1/api/danh-sach/phim-le" },
      { name: "Hoạt Hình", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" },
      { name: "TV Shows", url: "https://phimapi.com/v1/api/danh-sach/tv-shows" },
      { name: "Thuyết Minh", url: "https://phimapi.com/v1/api/danh-sach/phim-thuyet-minh" },
      { name: "Lồng Tiếng", url: "https://phimapi.com/v1/api/danh-sach/phim-long-tieng" },
      { name: "Hành Động", url: "https://phimapi.com/v1/api/the-loai/hanh-dong" },
      { name: "Cổ Trang", url: "https://phimapi.com/v1/api/the-loai/co-trang" },
      { name: "Tình Cảm", url: "https://phimapi.com/v1/api/the-loai/tinh-cam" },
      { name: "Kinh Dị", url: "https://phimapi.com/v1/api/the-loai/kinh-di" },
      { name: "Hàn Quốc", url: "https://phimapi.com/v1/api/quoc-gia/han-quoc" },
      { name: "Trung Quốc", url: "https://phimapi.com/v1/api/quoc-gia/trung-quoc" },
      { name: "Âu Mỹ", url: "https://phimapi.com/v1/api/quoc-gia/au-my" }
    ],
    ANIMEHAY: [
      { name: "Anime Mới Cập Nhật", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Anime Yêu Thích", url: "app://favorites" },
      { name: "Anime Hành Động", url: "https://phimapi.com/v1/api/the-loai/hanh-dong" },
      { name: "Anime Thần Thoại", url: "https://phimapi.com/v1/api/the-loai/than-thoai" },
      { name: "Anime Học Đường", url: "https://phimapi.com/v1/api/the-loai/hoc-duong" },
      { name: "Anime Viễn Tưởng", url: "https://phimapi.com/v1/api/the-loai/vien-tuong" }
    ],
    XEMTIVI: [
      { name: "Tất Cả Kênh", url: "tv://all" },
      { name: "⚽ Lịch Thi Đấu & Bóng Đá", url: "tv://schedule" },
      { name: "🕒 Kênh Vừa Xem", url: "app://history" },
      { name: "⭐ Kênh Yêu Thích", url: "tv://favorites" },
      { name: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh (EPL)", url: "tv://epl" },
      { name: "📡 Kênh Vệ Tinh Quốc Tế", url: "tv://satellite" },
      { name: "⚽ Bóng Đá & Thể Thao VN", url: "tv://football" },
      { name: "🏆 Cúp C1 & Thể Thao ESPN", url: "tv://sports_intl" },
      { name: "🏎️ Đua Xe & Võ Thuật", url: "tv://racing_combat" },
      { name: "VTV Quốc Gia", url: "tv://vtv" },
      { name: "VTVcab", url: "tv://vtvcab" },
      { name: "SCTV", url: "tv://sctv" },
      { name: "Rạp Phim", url: "tv://movies" },
      { name: "Sự Kiện TV360", url: "tv://live" },
      { name: "Kênh Quốc Tế", url: "tv://intl" },
      { name: "Đài Địa Phương", url: "tv://local" },
      { name: "Radio Trực Tuyến", url: "tv://radio" },
      { name: "➕ Thêm Kênh IPTV", url: "tv://custom" }
    ],
    FREEREELS: [
      { name: "🔥 Thịnh Hành", url: "https://phimapi.com/danh-sach/phim-moi-cap-nhat" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Phim Ngắn Yêu Thích", url: "app://favorites" },
      { name: "✨ Phim Ngắn Mới", url: "https://phimapi.com/v1/api/danh-sach/phim-bo" }
    ]
  };

  // --- Local Storage Storage Helpers ---
  function getFavorites() {
    try {
      return JSON.parse(localStorage.getItem('huycabuonca_favs') || '[]');
    } catch (e) {
      return [];
    }
  }

  function isFavorite(id) {
    const favs = getFavorites();
    return favs.some(item => item.id === id);
  }

  function toggleFavorite(movie) {
    let favs = getFavorites();
    const idx = favs.findIndex(item => item.id === movie.id);
    let added = false;
    if (idx >= 0) {
      favs.splice(idx, 1);
      added = false;
    } else {
      favs.unshift(movie);
      added = true;
    }
    localStorage.setItem('huycabuonca_favs', JSON.stringify(favs));
    showToast(added ? `⭐ Đã thêm "${movie.name}" vào Yêu Thích` : `Đã bỏ Yêu Thích "${movie.name}"`);
    renderHistoryAndFavs();
    return added;
  }

  function getHistory() {
    try {
      return JSON.parse(localStorage.getItem('huycabuonca_history') || '[]');
    } catch (e) {
      return [];
    }
  }

  function saveHistory(movie, currentSec, durationSec, episodeName, episodeIndex) {
    if (!movie || !movie.id) return;
    let hist = getHistory().filter(item => item.id !== movie.id);
    const percent = durationSec > 0 ? Math.min(100, Math.round((currentSec / durationSec) * 100)) : 0;
    const epIdx = (typeof episodeIndex === 'number') ? episodeIndex : (typeof currentEpisodeIndex === 'number' ? currentEpisodeIndex : 0);
    hist.unshift({
      id: movie.id,
      name: movie.name,
      slug: movie.slug,
      posterUrl: movie.posterUrl || movie.thumbUrl,
      source: movie.source || currentSource,
      episodeName: episodeName || movie.episodeCurrent || 'Tập 1',
      episodeIndex: epIdx,
      currentSec: Math.round(currentSec),
      durationSec: Math.round(durationSec),
      percent: percent,
      timestamp: Date.now()
    });
    if (hist.length > 30) hist = hist.slice(0, 30);
    localStorage.setItem('huycabuonca_history', JSON.stringify(hist));
    renderHistoryAndFavs();
  }

  function getCustomChannels() {
    try {
      return JSON.parse(localStorage.getItem('huycabuonca_custom_iptv') || '[]');
    } catch (e) {
      return [];
    }
  }

  function getAllChannels() {
    const base = window.INITIAL_TV_CHANNELS || window.CHANNELS_DATA || [];
    const custom = getCustomChannels();
    return [...custom, ...base];
  }

  // --- Clock ---
  function updateClock() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const el = document.getElementById('clockDisplay');
    if (el) el.textContent = `${h}:${m}`;
  }
  setInterval(updateClock, 1000);
  updateClock();

  // --- Toast ---
  function showToast(msg) {
    const toast = document.getElementById('toastBox');
    if (!toast) return;
    toast.textContent = msg;
    toast.style.display = 'block';
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => {
      toast.style.display = 'none';
    }, 2800);
  }

  // --- Source Selection ---
  function initSources() {
    const buttons = document.querySelectorAll('.btn-source');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentSource = btn.dataset.source;
        renderFilterBar();
      });
    });
  }

  // --- Render Filter Bar ---
  function renderFilterBar() {
    const bar = document.getElementById('filterBar');
    const animeSubBar = document.getElementById('animeSubSourcesBar');
    bar.innerHTML = '';
    bar.scrollLeft = 0;

    const currentSubList = SUB_SOURCES[currentSource];
    let filters = [];

    if (currentSubList && currentSubList.length > 0) {
      if (animeSubBar) {
        animeSubBar.classList.remove('hidden-bar');
        animeSubBar.style.display = 'flex';
        animeSubBar.innerHTML = '';
        if (!currentSubList.some(s => s.key === currentSubSource)) {
          currentSubSource = currentSubList[0].key;
        }
        currentSubList.forEach(s => {
          const btn = document.createElement('button');
          btn.className = `btn-sub-source focusable ${s.key === currentSubSource ? 'active' : ''}`;
          btn.dataset.sub = s.key;
          btn.textContent = s.name;
          btn.onclick = () => {
            currentSubSource = s.key;
            renderFilterBar();
          };
          animeSubBar.appendChild(btn);
        });
      }
      filters = (SUB_FILTERS && SUB_FILTERS[currentSubSource]) || FILTERS[currentSource] || [];
    } else {
      if (animeSubBar) {
        animeSubBar.innerHTML = '';
        animeSubBar.style.display = 'none';
        animeSubBar.classList.add('hidden-bar');
      }
      filters = FILTERS[currentSource] || [];
    }
    if (filters.length === 0) return;

    filters.forEach((f, idx) => {
      const btn = document.createElement('button');
      btn.className = `btn-filter focusable ${idx === 0 ? 'active' : ''}`;
      btn.textContent = f.name;
      btn.dataset.url = f.url;
      btn.addEventListener('click', () => {
        bar.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        btn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        handleFilterClick(f);
      });
      bar.appendChild(btn);
    });

    // Cập nhật trạng thái hiển thị của nút Prev/Next
    setTimeout(updateFilterNavState, 100);

    // Tự động load filter đầu tiên
    handleFilterClick(filters[0]);
  }

  function updateFilterNavState() {
    const filterBar = document.getElementById('filterBar');
    const btnPrev = document.getElementById('btnFilterPrev');
    const btnNext = document.getElementById('btnFilterNext');
    if (!filterBar || !btnPrev || !btnNext) return;
    const maxScroll = filterBar.scrollWidth - filterBar.clientWidth;
    btnPrev.style.opacity = filterBar.scrollLeft <= 5 ? '0.35' : '1';
    btnNext.style.opacity = filterBar.scrollLeft >= maxScroll - 5 ? '0.35' : '1';
  }

  // --- Điều Hướng Thanh Filter Cho Windows (Nút Bấm, Con Lăn Chuột & Kéo Chuột) ---
  function initFilterBarNavigation() {
    const filterBar = document.getElementById('filterBar');
    const btnPrev = document.getElementById('btnFilterPrev');
    const btnNext = document.getElementById('btnFilterNext');
    if (!filterBar) return;

    if (btnPrev) {
      btnPrev.addEventListener('click', () => {
        filterBar.scrollBy({ left: -280, behavior: 'smooth' });
        setTimeout(updateFilterNavState, 350);
      });
    }

    if (btnNext) {
      btnNext.addEventListener('click', () => {
        filterBar.scrollBy({ left: 280, behavior: 'smooth' });
        setTimeout(updateFilterNavState, 350);
      });
    }

    // 1. Cuộn ngang bằng con lăn chuột (Mouse Wheel) khi rê trên thanh filter
    filterBar.addEventListener('wheel', (e) => {
      if (e.deltaY !== 0) {
        e.preventDefault();
        filterBar.scrollLeft += e.deltaY * 1.2;
        updateFilterNavState();
      }
    }, { passive: false });

    // 2. Kéo thả chuột ngang (Drag to scroll)
    let isMouseDown = false;
    let startX = 0;
    let scrollStart = 0;

    filterBar.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return; // Chỉ chuột trái
      isMouseDown = true;
      startX = e.pageX - filterBar.offsetLeft;
      scrollStart = filterBar.scrollLeft;
    });

    window.addEventListener('mouseup', () => {
      isMouseDown = false;
    });

    filterBar.addEventListener('mousemove', (e) => {
      if (!isMouseDown) return;
      e.preventDefault();
      const x = e.pageX - filterBar.offsetLeft;
      const walk = (x - startX) * 1.5;
      filterBar.scrollLeft = scrollStart - walk;
      updateFilterNavState();
    });

    filterBar.addEventListener('scroll', updateFilterNavState);
    window.addEventListener('resize', updateFilterNavState);
    setTimeout(updateFilterNavState, 200);
  }

  function handleFilterClick(filterItem) {
    if (filterItem.url === 'tv://custom') {
      showIptvModal();
      return;
    }
    currentFilter = filterItem.url;
    currentPage = 1;
    loadMovies(true);
  }

  // --- Load Movies & TV Channels ---
  let activeRequestId = 0;
  async function loadMovies(reset) {
    if (reset) {
      isLoading = false; // Khi chuyển tab: Reset cờ loading ngay lập tức!
    } else if (isLoading) {
      return;
    }
    isLoading = true;
    const reqId = ++activeRequestId;

    const grid = document.getElementById('mainGrid');
    const paginationContainer = document.getElementById('paginationContainer');
    const paginationInfo = document.getElementById('paginationInfo');
    const btnLoadMore = document.getElementById('btnLoadMore');
    const spinner = document.getElementById('loadingMoreSpinner');

    if (reset) {
      grid.innerHTML = '<div style="color: #94a3b8; font-size: 18px; padding: 40px; text-align: center; width: 100%; grid-column: 1 / -1;">⏳ Đang tải danh sách...</div>';
      currentMoviesList = [];
      currentPage = 1;
      if (paginationContainer) paginationContainer.style.display = 'none';
    } else {
      if (btnLoadMore) btnLoadMore.style.display = 'none';
      if (spinner) spinner.style.display = 'block';
    }

    try {
      if (currentFilter === 'app://favorites') {
        const favs = getFavorites().filter(f => f.source === currentSource || (currentSource === 'KKPHIM' && !f.source));
        renderCards(favs, reset);
        if (paginationContainer) paginationContainer.style.display = 'none';
        isLoading = false;
        return;
      }

      if (currentFilter === 'app://history') {
        const hist = getHistory().filter(h => h.source === currentSource || (currentSource === 'KKPHIM' && !h.source));
        renderCards(hist, reset);
        if (paginationContainer) paginationContainer.style.display = 'none';
        isLoading = false;
        return;
      }

      if (currentSource === 'XEMTIVI') {
        const allChannels = getAllChannels();
        let filtered = allChannels;

                if (currentFilter === 'tv://schedule') {
          const eplMatches = await fetchRealtimePremierLeagueMatches();
          const sourceList = (eplMatches && eplMatches.length > 0) ? eplMatches : LIVE_MATCHES;
          const matchCards = sourceList.map(m => ({
            id: m.id,
            name: `${m.teamA} vs ${m.teamB}`,
            slug: m.id,
            originName: m.tournament,
            thumbUrl: m.teamALogo || DEFAULT_TV_LOGO,
            posterUrl: m.teamALogo || DEFAULT_TV_LOGO,
            teamA: m.teamA,
            teamB: m.teamB,
            teamALogo: m.teamALogo || DEFAULT_TV_LOGO,
            teamBLogo: m.teamBLogo || DEFAULT_TV_LOGO,
            quality: m.isLive ? 'LIVE' : 'EPL',
            episodeCurrent: m.time,
            source: 'XEMTIVI',
            isEplMatch: true,
            rawMatch: m,
            hasReminder: isMatchReminderSet(m.id)
          }));
          const sportsChannels = allChannels.filter(c => {
            const grp = (c.group || '').toLowerCase();
            const nm = (c.name || '').toLowerCase();
            return grp.includes('bóng đá') || grp.includes('thể thao') || nm.includes('k+') || nm.includes('sport');
          }).map(c => ({
            id: c.id,
            name: c.name,
            slug: c.id,
            originName: `[${c.group || 'Thể Thao'}]`,
            thumbUrl: c.logo || DEFAULT_TV_LOGO,
            posterUrl: c.logo || DEFAULT_TV_LOGO,
            quality: '1080p',
            episodeCurrent: 'Trực Tiếp',
            source: 'XEMTIVI',
            streamUrl: c.url,
            group: c.group
          }));
          renderCards([...matchCards, ...sportsChannels], reset);
          if (paginationContainer) paginationContainer.style.display = 'none';
          isLoading = false;
          return;
        } else if (currentFilter === 'tv://epl') {
          // 1. Tải danh sách trận đấu Ngoại Hạng Anh FPL thời gian thực
          const eplMatches = await fetchRealtimePremierLeagueMatches();
          const sourceList = (eplMatches && eplMatches.length > 0) ? eplMatches : LIVE_MATCHES;
          
          // Tạo các thẻ trận đấu Ngoại Hạng Anh với icon chuông thông báo độc lập
          const matchCards = sourceList.map(m => {
            const hasReminder = isMatchReminderSet(m.id);
            return {
              id: m.id,
              name: `${m.teamA} vs ${m.teamB}`,
              slug: m.id,
              originName: m.tournament,
              thumbUrl: m.teamALogo || DEFAULT_TV_LOGO,
              posterUrl: m.teamALogo || DEFAULT_TV_LOGO,
              teamA: m.teamA,
              teamB: m.teamB,
              teamALogo: m.teamALogo || DEFAULT_TV_LOGO,
              teamBLogo: m.teamBLogo || DEFAULT_TV_LOGO,
              quality: m.isLive ? 'LIVE' : 'EPL',
              episodeCurrent: m.time,
              source: 'XEMTIVI',
              isEplMatch: true,
              rawMatch: m,
              hasReminder: hasReminder
            };
          });

          // 2. Tải thêm các kênh Vệ Tinh Quốc Tế phát sóng Ngoại Hạng Anh
          const satChannels = allChannels.filter(c => (c.group || '').includes('Vệ Tinh') || (c.name || '').includes('True Premier') || (c.name || '').includes('Astro') || (c.name || '').includes('Sky Sports') || (c.name || '').includes('TNT Sports'));
          const satItems = satChannels.map(c => ({
            id: c.id,
            name: c.name,
            slug: c.id,
            originName: `[${c.group || 'Vệ Tinh'}]`,
            thumbUrl: c.logo || DEFAULT_TV_LOGO,
            posterUrl: c.logo || DEFAULT_TV_LOGO,
            quality: '1080p',
            episodeCurrent: '24/7',
            source: 'XEMTIVI',
            streamUrl: c.url,
            group: c.group
          }));

          renderCards([...matchCards, ...satItems], reset);
          if (paginationContainer) paginationContainer.style.display = 'none';
          isLoading = false;
          return;
        } else if (currentFilter === 'tv://satellite') {
          filtered = allChannels.filter(c => (c.group || '').includes('Vệ Tinh') || (c.name || '').includes('True Premier') || (c.name || '').includes('Astro') || (c.name || '').includes('Sky Sports') || (c.name || '').includes('TNT Sports') || (c.name || '').includes('beIN'));
        } else if (currentFilter === 'tv://favorites') {
          const favs = getFavorites();
          filtered = allChannels.filter(c => favs.some(f => f.id === c.id));
        } else if (currentFilter === 'tv://football') {
          // Lọc toàn bộ kênh bóng đá đỉnh cao Việt Nam & Quốc Tế
          filtered = allChannels.filter(c => {
            const grp = (c.group || '').toLowerCase();
            const nm = (c.name || '').toLowerCase();
            return grp.includes('bóng đá') || 
                   grp.includes('thể thao') || 
                   grp.includes('c1') ||
                   nm.includes('k+') || 
                   nm.includes('sport') || 
                   nm.includes('football') ||
                   nm.includes('vtv5') || 
                   nm.includes('vtv6') ||
                   nm.includes('htv thể thao') ||
                   nm.includes('bein') ||
                   nm.includes('cbs') ||
                   nm.includes('eurosport') ||
                   nm.includes('fifa') ||
                   nm.includes('espn');
          });
        } else if (currentFilter === 'tv://vtv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtv') || (c.name || '').toLowerCase().startsWith('vtv'));
        } else if (currentFilter === 'tv://vtvcab') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtvcab'));
        } else if (currentFilter === 'tv://sctv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('sctv'));
        } else if (currentFilter === 'tv://sports_intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('ESPN') || (c.group || '').includes('Bóng Rổ') || (c.group || '').includes('FOX') || (c.group || '').includes('Bóng Đá Quốc Tế') || (c.name || '').toLowerCase().includes('sport') || (c.name || '').toLowerCase().includes('bein') || (c.name || '').toLowerCase().includes('eurosport') || (c.name || '').toLowerCase().includes('fifa') || (c.name || '').toLowerCase().includes('red bull'));
        } else if (currentFilter === 'tv://racing_combat') {
          filtered = allChannels.filter(c => (c.group || '').includes('Đua Xe') || (c.group || '').includes('Võ Thuật') || (c.group || '').includes('Mạo Hiểm') || (c.group || '').includes('Đối Kháng') || (c.name || '').toLowerCase().includes('red bull'));
        } else if (currentFilter === 'tv://movies') {
          filtered = allChannels.filter(c => (c.group || '').includes('Rạp Phim') || (c.group || '').toLowerCase().includes('phim') || (c.name || '').toLowerCase().includes('hbo') || (c.name || '').toLowerCase().includes('warner') || (c.name || '').toLowerCase().includes('cinemax'));
        } else if (currentFilter === 'tv://live') {
          filtered = allChannels.filter(c => (c.group || '').includes('Sự Kiện') || (c.group || '').includes('LIVE'));
        } else if (currentFilter === 'tv://intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('Quốc Tế') || (c.group || '').includes('Hàn Quốc') || (c.group || '').includes('Trung Quốc') || (c.group || '').includes('Israel') || (c.group || '').includes('In The Box') || (c.group || '').includes('TVB') || (c.group || '').includes('Vệ Tinh') || (c.name || '').includes('NHK') || (c.name || '').includes('Al Jazeera') || (c.name || '').includes('DW ') || (c.name || '').includes('France 24') || (c.name || '').includes('ABC News') || (c.name || '').includes('CBS News') || (c.name || '').includes('NBC News') || (c.name || '').includes('Bloomberg') || (c.name || '').includes('CNA') || (c.name || '').includes('Euronews') || (c.name || '').includes('Arirang') || (c.name || '').includes('Red Bull'));
        } else if (currentFilter === 'tv://local') {
          filtered = allChannels.filter(c => (c.group || '').includes('Địa phương') || (c.group || '').includes('HTV') || (c.name || '').toLowerCase().startsWith('htv') || (c.name || '').toLowerCase().startsWith('thvl'));
        } else if (currentFilter === 'tv://radio') {
          filtered = allChannels.filter(c => (c.group || '').includes('Radio'));
        }

        const items = filtered.map(c => ({
          id: c.id,
          name: c.name,
          slug: c.id,
          originName: `[${c.group || 'Kênh TV'}]`,
          thumbUrl: c.logo || DEFAULT_TV_LOGO,
          posterUrl: c.logo || DEFAULT_TV_LOGO,
          quality: 'LIVE',
          episodeCurrent: 'Trực Tiếp',
          source: 'XEMTIVI',
          streamUrl: c.url,
          group: c.group
        }));

        renderCards(items, reset);
        if (paginationContainer) paginationContainer.style.display = 'none';
        isLoading = false;
        return;
      }

      // Xử lý Anime Thuyết Minh (100% Hoạt Hình, Lọc Sạch Phim Người Đóng)
      if (currentFilter.startsWith('anime_dubbed://')) {
        const filterType = currentFilter.replace('anime_dubbed://', '');
        const p1 = (currentPage - 1) * 2 + 1;
        const p2 = currentPage * 2;
        const collectedItems = [];
        
        for (const p of [p1, p2]) {
          const endpoints = [
            `https://phimapi.com/v1/api/danh-sach/phim-thuyet-minh?page=${p}`,
            `https://phimapi.com/v1/api/danh-sach/phim-long-tieng?page=${p}`,
            `https://phimapi.com/v1/api/the-loai/hoat-hinh?page=${p}`
          ];
          for (const ep of endpoints) {
            try {
              const r = await fetch(ep);
              if (!r.ok) continue;
              const j = await r.json();
              const arr = (j.items || (j.data && j.data.items)) || [];
              arr.forEach(o => {
                const type = o.type || '';
                const lang = (o.lang || '').toLowerCase();
                const cats = o.category || [];
                const isCatAnim = cats.some(c => (c.slug || '').includes('hoat-hinh'));
                const isAnim = (type === 'hoathinh' || isCatAnim);
                const isDub = (lang.includes('thuyết minh') || lang.includes('lồng tiếng') || lang.includes('tm') || lang.includes('lt'));

                if (isAnim && isDub) {
                  const countries = (o.country || []).map(c => c.slug || '');
                  let matched = true;
                  if (filterType === 'japan' && !countries.includes('nhat-ban')) matched = false;
                  if (filterType === 'china' && !countries.includes('trung-quoc')) matched = false;
                  if (filterType === 'cinema' && !countries.some(c => ['au-my', 'my', 'phap', 'anh', 'canada', 'uc', 'duc'].includes(c))) matched = false;

                  if (matched) {
                    let thumb = o.thumb_url || '';
                    let poster = o.poster_url || thumb;
                    if (thumb && !thumb.startsWith('http')) thumb = KKPHIM_IMG_BASE + thumb.replace(/^\//, '');
                    if (poster && !poster.startsWith('http')) poster = KKPHIM_IMG_BASE + poster.replace(/^\//, '');
                    collectedItems.push({
                      id: o._id || o.slug,
                      name: o.name,
                      slug: o.slug,
                      originName: o.origin_name || '',
                      thumbUrl: thumb,
                      posterUrl: poster || thumb,
                      portraitUrl: poster || thumb,
                      landscapeUrl: thumb || poster,
                      year: o.year || '',
                      quality: o.quality || 'FHD',
                      episodeCurrent: o.episode_current || '',
                      source: 'KKPHIM'
                    });
                  }
                }
              });
            } catch(e) {}
          }
        }
        // Loại bỏ trùng lặp
        const seen = new Set();
        const distinct = collectedItems.filter(item => {
          const k = item.name.trim().toLowerCase();
          if (seen.has(k)) return false;
          seen.add(k);
          return true;
        });
        renderCards(distinct, reset);
        if (paginationContainer) paginationContainer.style.display = 'flex';
        isLoading = false;
        return;
      }

      // =========================================================================
      // XỬ LÝ PHÂN LOẠI PHIM NGẮN CHUẨN XÁC 100% TIỂU KỊCH (KHÔNG LẪN PHIM LẺ KKPHIM)
      // =========================================================================
      if (currentFilter.startsWith('short_kw://') || currentFilter.startsWith('platform_short://')) {
        const kwType = currentFilter.replace('short_kw://', '').replace('platform_short://', '');
        const SHORT_KW_MAP = {
          // Nguồn ReelShort (Âu Mỹ)
          'reelshort': ['người sói', 'ma cà rồng', 'tỷ phú', 'mafia', 'hợp đồng'],
          'reelshort_hot': ['người sói', 'tỷ phú', 'ma cà rồng', 'mafia', 'hợp đồng'],
          'werewolf': ['người sói', 'vua sói', 'nữ hoàng alpha', 'werewolf', 'bạn đời'],
          'vampire': ['ma cà rồng', 'chúa tể bóng đêm', 'khát máu', 'vampire', 'thợ săn'],
          'billionaire': ['tỷ phú', 'thừa kế', 'ông trùm', 'đại gia', 'chồng tỷ phú'],
          'mafia': ['mafia', 'ông trùm', 'băng đảng', 'sát thủ', 'vệ sĩ'],
          'rejected': ['hợp đồng', 'ly hôn', 'vợ cũ', 'bị từ chối', 'thế thân'],
          // Nguồn DramaBox
          'dramabox': ['tổng tài', 'báo thù', 'chiếc lồng son', 'trọng sinh', 'hào môn'],
          'dramabox_hot': ['tổng tài', 'báo thù', 'trọng sinh', 'chiếc lồng son', 'hào môn'],
          'tong_tai': ['tổng tài', 'chủ tịch', 'bá đạo', 'phu nhân', 'thư ký'],
          'trong_sinh': ['trọng sinh', 'trùng sinh', 'báo thù', 'kiếp trước', 'phản bội'],
          'chien_than': ['chiến thần', 'long vương', 'tu tiên', 'võ thần', 'đại tướng'],
          'co_trang': ['cổ trang', 'hoàng hậu', 'cung đấu', 'vương gia', 'xuyên không'],
          'hao_mon': ['hào môn', 'thế gia', 'thiên kim', 'thiếu gia', 'thừa kế'],
          // Nguồn ShortMax
          'shortmax': ['cao thủ', 'thần y', 'nghịch tập', 'mạt thế', 'vua cờ bạc'],
          'shortmax_hot': ['cao thủ', 'thần y', 'vua cờ bạc', 'nghịch tập', 'chiến thần'],
          'nghich_tap': ['nghịch tập', 'đổi đời', 'ở rể', 'ẩn danh', 'phế vật'],
          'than_y': ['thần y', 'cao thủ', 'y thuật', 'xuống núi', 'kỳ tài'],
          'mat_the': ['mạt thế', 'sinh tồn', 'không gian', 'tận thế', 'zombie'],
          'nguoc_tam': ['thế thân', 'ngược tâm', 'ly hôn', 'hối hận', 'bỏ rơi'],
          // Nguồn AI Cinema
          'ai-cinema': ['người máy', 'hệ thống', 'khoa học', 'thực tế ảo', 'công nghệ'],
          'ai_all': ['người máy', 'hệ thống', 'khoa học', 'thực tế ảo', 'công nghệ'],
          'ai_robot': ['người máy', 'trí tuệ nhân tạo', 'công nghệ', 'kỳ tài', 'hệ thống'],
          'ai_scifi': ['khoa học', 'vũ trụ', 'siêu năng lực', 'không gian', 'công nghệ'],
          'ai_future': ['đếm ngược', 'thời gian', 'tương lai', 'tái sinh', 'vũ trụ'],
          'ai_fantasy': ['hệ thống', 'thực tế ảo', 'siêu năng lực', 'dị năng', 'phép thuật'],
          // Nguồn GoodShort & Sereal+
          'goodshort': ['ngọt sủng', 'bảo bối', 'cưng chiều', 'mẹ đơn thân', 'định mệnh'],
          'goodshort_hot': ['cưng chiều', 'tình yêu', 'ngọt sủng', 'hôn nhân', 'lãng mạn'],
          'sereal': ['định mệnh', 'bí mật', 'tình yêu', 'người yêu', 'hôn ước'],
          'moboreels': ['cô dâu', 'trọn bộ', 'hiện đại', 'đô thị', 'hôn nhân'],
          'ngot_sung': ['ngọt sủng', 'cưng chiều', 'yêu thầm', 'thanh xuân', 'học đường'],
          'bao_boi': ['bảo bối', 'thiên tài', 'mẹ đơn thân', 'sinh đôi', 'nhóc tỳ'],
          'tron_bo': ['lồng tiếng', 'tổng tài', 'trọng sinh', 'cưng chiều', 'hào môn']
        };

        const kwList = SHORT_KW_MAP[kwType] || ['tiểu kịch', 'tổng tài', 'trọng sinh'];
        const targetKw = kwList[(currentPage - 1) % kwList.length];
        let newItems = await FreeReelsClient.search(targetKw, currentPage);
        if (newItems.length < 6) {
          try {
            const fbItems = await GaMoMePhimClient.getDramaList('gamomephim://the-loai/hien-dai', 1);
            if (fbItems && fbItems.length > 0) {
              newItems = newItems.concat(fbItems);
            }
          } catch(e) {}
        }

        if (reqId !== activeRequestId) return;

        // Lọc trùng theo tên và ID
        const seenNames = new Set(reset ? [] : currentMoviesList.map(m => m.name.toLowerCase().trim()));
        const uniqueItems = [];
        for (const it of newItems) {
          const k = it.name.toLowerCase().trim();
          if (!seenNames.has(k)) {
            seenNames.add(k);
            uniqueItems.push(it);
          }
        }

        if (reset) {
          currentMoviesList = uniqueItems;
          renderCards(currentMoviesList, true);
        } else {
          currentMoviesList.push(...uniqueItems);
          renderCards(uniqueItems, false);
        }

        if (paginationContainer) paginationContainer.style.display = 'flex';
        if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim nền tảng (Trang ${currentPage})`;
        if (btnLoadMore) {
          btnLoadMore.style.display = 'inline-flex';
          const nextPageEl = document.getElementById('nextPageNum');
          if (nextPageEl) nextPageEl.textContent = currentPage + 1;
        }
        if (spinner) spinner.style.display = 'none';

        if (reset && currentPage === 1 && uniqueItems.length >= 10) {
          setTimeout(() => { if (!isLoading) loadMoreMovies(); }, 250);
        }

        isLoading = false;
        return;
      }

      // Xử lý Phim Ngắn GaMoMePhim Thuyết Minh (Hỗ trợ phân trang vô cực)
      if (currentFilter.startsWith('gamomephim://')) {
        let gmMovies = await GaMoMePhimClient.getDramaList(currentFilter, currentPage);
        if (reqId !== activeRequestId) return;

        if (reset) {
          currentMoviesList = gmMovies;
          renderCards(currentMoviesList, true);
        } else {
          const seen = new Set(currentMoviesList.map(m => m.slug));
          const unique = gmMovies.filter(m => !seen.has(m.slug));
          currentMoviesList.push(...unique);
          renderCards(unique, false);
        }

        if (paginationContainer) paginationContainer.style.display = 'flex';
        if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim ngắn thuyết minh (Trang ${currentPage})`;
        if (btnLoadMore) {
          btnLoadMore.style.display = gmMovies.length > 0 ? 'inline-flex' : 'none';
          const nextPageEl = document.getElementById('nextPageNum');
          if (nextPageEl) nextPageEl.textContent = currentPage + 1;
        }
        if (spinner) spinner.style.display = 'none';

        if (reset && currentPage === 1 && gmMovies.length >= 10) {
          setTimeout(() => { if (!isLoading) loadMoreMovies(); }, 250);
        }

        isLoading = false;
        return;
      }

      // Xử lý Phim Ngắn FreeReels Bản Quyền Dọc (Hỗ trợ phân trang vô cực)
      if (currentFilter.startsWith('freereels://')) {
        let frItems = await FreeReelsClient.getDramaList(currentFilter, currentPage);
        if (reqId !== activeRequestId) return;

        const seenNames = new Set(reset ? [] : currentMoviesList.map(m => m.name.toLowerCase().trim()));
        const uniqueItems = [];
        for (const it of frItems) {
          const k = it.name.toLowerCase().trim();
          if (!seenNames.has(k)) {
            seenNames.add(k);
            uniqueItems.push(it);
          }
        }

        if (reset) {
          currentMoviesList = uniqueItems;
          renderCards(currentMoviesList, true);
        } else {
          currentMoviesList.push(...uniqueItems);
          renderCards(uniqueItems, false);
        }

        if (paginationContainer) {
          paginationContainer.style.display = 'flex';
          if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim ngắn FreeReels (Trang ${currentPage})`;
          if (btnLoadMore) {
            btnLoadMore.style.display = 'inline-flex';
            const nextPageEl = document.getElementById('nextPageNum');
            if (nextPageEl) nextPageEl.textContent = currentPage + 1;
          }
          if (spinner) spinner.style.display = 'none';
          if (reset && currentPage === 1 && frItems.length >= 8) {
            setTimeout(() => { if (!isLoading) loadMoreMovies(); }, 250);
          }
        }
        isLoading = false;
        return;
      }

      // Xử lý Tiểu Kịch Vietsub & DramaBox (Gọi trực tiếp FreeReels chuẩn dọc 9:16, không trộn phim dài tập KKPhim)
      if (currentFilter.startsWith('short_filter://') || currentFilter.startsWith('short_dramabox://') || currentFilter.startsWith('multi_short://')) {
        let kw = 'tổng tài';
        if (currentFilter.includes('trong-sinh')) kw = 'trọng sinh';
        if (currentFilter.includes('ngon-tinh') || currentFilter.includes('hao-mon')) kw = 'hào môn';
        if (currentFilter.includes('hai-huoc')) kw = 'hài hước';
        if (currentFilter.includes('chienthan') || currentFilter.includes('chien-than')) kw = 'chiến thần';
        if (currentFilter.includes('thieugia') || currentFilter.includes('thieu-gia')) kw = 'thiếu gia';
        if (currentFilter.includes('cotrang') || currentFilter.includes('co-trang')) kw = 'cổ trang';
        
        let frItems = await FreeReelsClient.search(kw, currentPage);
        renderCards(frItems, reset);
        if (paginationContainer) {
          paginationContainer.style.display = 'flex';
          if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim ngắn (Trang ${currentPage})`;
          if (btnLoadMore) {
            btnLoadMore.style.display = 'inline-flex';
            const nextPageEl = document.getElementById('nextPageNum');
            if (nextPageEl) nextPageEl.textContent = currentPage + 1;
          }
        }
        if (spinner) spinner.style.display = 'none';
        isLoading = false;
        return;
      }

      const sep = currentFilter.includes('?') ? '&' : '?';
      const fetchUrl = `${currentFilter}${sep}page=${currentPage}`;

      const resp = await fetch(fetchUrl);
      if (!resp.ok) throw new Error('Network error');
      const data = await resp.json();

      let items = [];
      if (data.items && Array.isArray(data.items)) {
        items = data.items;
      } else if (data.data && data.data.items && Array.isArray(data.data.items)) {
        items = data.data.items;
      }

      // Chặn triệt để phim thường (live-action) ngồi nhầm lớp sang danh mục Anime
      if (currentSource === 'ANIMEHAY') {
        items = items.filter(o => {
          const type = o.type || '';
          const hasAnimCat = Array.isArray(o.category) && o.category.some(c => (c.slug || '').includes('hoat-hinh'));
          const nameLower = (o.name || '').toLowerCase();
          return type === 'hoathinh' || hasAnimCat || nameLower.includes('anime') || nameLower.includes('hoạt hình');
        });
      }

      const isNguonC = fetchUrl.includes('phim.nguonc.com');
      const mapped = items.map(o => {
        let thumb = o.thumb_url || '';
        let poster = o.poster_url || thumb;
        if (thumb && !thumb.startsWith('http')) thumb = KKPHIM_IMG_BASE + thumb.replace(/^\//, '');
        if (poster && !poster.startsWith('http')) poster = KKPHIM_IMG_BASE + poster.replace(/^\//, '');

        const slugId = isNguonC ? `nguonc:${o.slug}` : (o.slug || o._id);
        // KKPhim: thumb_url la anh ngang 16:9 (780x439), poster_url la anh doc 2:3 (500x760)
        // NguonC: poster_url la anh ngang 16:9 (1280x720), thumb_url la anh doc 2:3 (336x504)
        const landscapeImg = isNguonC ? (poster || thumb) : (thumb || poster);
        const portraitImg = isNguonC ? (thumb || poster) : (poster || thumb);

        return {
          id: o._id || slugId,
          name: o.name,
          slug: slugId,
          originName: o.original_name || o.origin_name || '',
          thumbUrl: thumb,
          posterUrl: portraitImg,
          portraitUrl: portraitImg,
          landscapeUrl: landscapeImg,
          year: o.year || '2026',
          quality: (o.quality || 'HD') + (o.language ? ` ${o.language}` : ''),
          episodeCurrent: o.current_episode || o.episode_current || '',
          source: currentSource
        };
      });

      renderCards(mapped, reset);

      // Cập nhật giao diện phân trang
      if (paginationContainer) {
        if (mapped.length > 0) {
          paginationContainer.style.display = 'flex';
          if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim (Trang ${currentPage})`;
          if (btnLoadMore) {
            btnLoadMore.style.display = 'inline-flex';
            const nextPageEl = document.getElementById('nextPageNum');
            if (nextPageEl) nextPageEl.textContent = currentPage + 1;
          }
          if (spinner) spinner.style.display = 'none';

          // Đồng bộ với Windows 4x4 (16 phim) & Android TV: Tải ngay trang 2 để lấp đầy đủ 4 hàng x 4 phim
          if (reset && currentPage === 1 && mapped.length > 0 && currentMoviesList.length < 20 && currentSource !== 'XEMTIVI' && !currentFilter.startsWith('app://')) {
            setTimeout(() => {
              if (!isLoading) loadMoreMovies();
            }, 60);
          }
        } else {
          if (paginationInfo) paginationInfo.textContent = `Đã tải toàn bộ ${currentMoviesList.length} phim trong danh mục này.`;
          if (btnLoadMore) btnLoadMore.style.display = 'none';
          if (spinner) spinner.style.display = 'none';
        }
      }
    } catch (err) {
      if (reset) {
        grid.innerHTML = '<div style="color: #f87171; font-size: 16px; padding: 30px; text-align: center; width: 100%; grid-column: 1 / -1;">Không thể tải dữ liệu. Vui lòng kiểm tra kết nối mạng! <button onclick="location.reload()" style="margin-left: 10px; padding: 6px 14px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">🔄 Thử Lại</button></div>';
      } else {
        showToast('Không thể tải thêm phim trang tiếp theo.');
        if (btnLoadMore) btnLoadMore.style.display = 'inline-flex';
        if (spinner) spinner.style.display = 'none';
      }
    } finally {
      isLoading = false;
    }
  }

  function loadMoreMovies() {
    if (isLoading) return;
    if (currentSource === 'XEMTIVI' || currentFilter === 'app://favorites' || currentFilter === 'app://history') return;
    currentPage++;
    loadMovies(false);
  }


  // --- PREMIER LEAGUE REAL-TIME FPL SERVICE & 4-TIER STREAMING (v2.5) ---
  const PREMIER_LEAGUE_TEAMS = {
    1: { name: "Arsenal", short: "ARS", logo: "https://resources.premierleague.com/premierleague/badges/70/t3.png" },
    2: { name: "Aston Villa", short: "AVL", logo: "https://resources.premierleague.com/premierleague/badges/70/t7.png" },
    3: { name: "Bournemouth", short: "BOU", logo: "https://resources.premierleague.com/premierleague/badges/70/t91.png" },
    4: { name: "Brentford", short: "BRE", logo: "https://resources.premierleague.com/premierleague/badges/70/t94.png" },
    5: { name: "Brighton", short: "BHA", logo: "https://resources.premierleague.com/premierleague/badges/70/t36.png" },
    6: { name: "Chelsea", short: "CHE", logo: "https://resources.premierleague.com/premierleague/badges/70/t8.png" },
    7: { name: "Crystal Palace", short: "CRY", logo: "https://resources.premierleague.com/premierleague/badges/70/t31.png" },
    8: { name: "Everton", short: "EVE", logo: "https://resources.premierleague.com/premierleague/badges/70/t11.png" },
    9: { name: "Fulham", short: "FUL", logo: "https://resources.premierleague.com/premierleague/badges/70/t54.png" },
    10: { name: "Ipswich Town", short: "IPS", logo: "https://resources.premierleague.com/premierleague/badges/70/t40.png" },
    11: { name: "Leicester City", short: "LEI", logo: "https://resources.premierleague.com/premierleague/badges/70/t13.png" },
    12: { name: "Liverpool", short: "LIV", logo: "https://resources.premierleague.com/premierleague/badges/70/t14.png" },
    13: { name: "Manchester City", short: "MCI", logo: "https://resources.premierleague.com/premierleague/badges/70/t43.png" },
    14: { name: "Manchester United", short: "MUN", logo: "https://resources.premierleague.com/premierleague/badges/70/t1.png" },
    15: { name: "Newcastle", short: "NEW", logo: "https://resources.premierleague.com/premierleague/badges/70/t4.png" },
    16: { name: "Nottingham Forest", short: "NFO", logo: "https://resources.premierleague.com/premierleague/badges/70/t17.png" },
    17: { name: "Southampton", short: "SOU", logo: "https://resources.premierleague.com/premierleague/badges/70/t20.png" },
    18: { name: "Tottenham Hotspur", short: "TOT", logo: "https://resources.premierleague.com/premierleague/badges/70/t6.png" },
    19: { name: "West Ham United", short: "WHU", logo: "https://resources.premierleague.com/premierleague/badges/70/t21.png" },
    20: { name: "Wolves", short: "WOL", logo: "https://resources.premierleague.com/premierleague/badges/70/t39.png" }
  };

  let activeMatchForServer = null;

  // Lấy danh sách trận đấu đã đặt chuông (chỉ báo đúng trận được người dùng chọn)
  function getMatchReminders() {
    try {
      return JSON.parse(localStorage.getItem('huyca_match_reminders') || '[]');
    } catch (e) {
      return [];
    }
  }

  function isMatchReminderSet(matchId) {
    const list = getMatchReminders();
    return list.some(item => String(item.id) === String(matchId));
  }

  function toggleMatchReminder(match) {
    let list = getMatchReminders();
    const idx = list.findIndex(item => String(item.id) === String(match.id));
    let added = false;
    if (idx >= 0) {
      list.splice(idx, 1);
      added = false;
      showToast(`🔕 Đã hủy thông báo: ${match.teamA} vs ${match.teamB}`);
    } else {
      list.push({
        id: match.id,
        teamA: match.teamA,
        teamB: match.teamB,
        kickoffTime: match.kickoffTime,
        timeStr: match.timeStr,
        notified: false
      });
      added = true;
      showToast(`🔔 Đã đặt chuông! App sẽ cảnh báo trước 15 phút khi trận "${match.teamA} vs ${match.teamB}" bắt đầu!`);
    }
    localStorage.setItem('huyca_match_reminders', JSON.stringify(list));
    return added;
  }

  // Bộ đếm kiểm tra thông báo định kỳ (Chỉ cảnh báo đúng trận được đặt)
  function startReminderChecker() {
    setInterval(() => {
      const list = getMatchReminders();
      if (!list || list.length === 0) return;

      const now = Date.now();
      let updated = false;

      list.forEach(m => {
        if (!m.notified && m.kickoffTime) {
          const diffMinutes = (m.kickoffTime - now) / (1000 * 60);
          if (diffMinutes <= 15 && diffMinutes >= -105) {
            m.notified = true;
            updated = true;
            showMatchAlertPopup(m);
          }
        }
      });

      if (updated) {
        localStorage.setItem('huyca_match_reminders', JSON.stringify(list));
      }
    }, 30000);
  }

  function showMatchAlertPopup(m) {
    showToast(`🔔⚽ SẮP BẮT ĐẦU: "${m.teamA} vs ${m.teamB}" trong 15 phút nữa! Bấm để chọn Server xem ngay!`);
    openMatchServerModal({
      id: m.id,
      tournament: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh",
      teamA: m.teamA,
      teamB: m.teamB,
      time: m.timeStr || "Sắp diễn ra"
    });
  }

  // Tải danh sách trận đấu Ngoại Hạng Anh thời gian thực từ FPL Premier League API
  async function fetchRealtimePremierLeagueMatches() {
    try {
      const leagues = [
        { code: 'eng.1', name: '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh', chName: 'True Premier Football 1 HD', chSlug: 'sports_sat_true_premier_1' },
        { code: 'uefa.champions', name: '🏆 Cúp C1 Châu Âu', chName: 'True Premier Football 2 HD', chSlug: 'sports_sat_true_premier_2' },
        { code: 'esp.1', name: '🇪🇸 La Liga', chName: 'Astro SuperSport 1 HD', chSlug: 'sports_sat_astro_supersport_1' },
        { code: 'ita.1', name: '🇮🇹 Serie A', chName: 'Astro SuperSport 2 HD', chSlug: 'sports_sat_astro_supersport_2' }
      ];

      const fetchLeague = async (lg) => {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 3500);
          const espnTarget = `https://site.api.espn.com/apis/site/v2/sports/soccer/${lg.code}/scoreboard`;
          const espnUrl = window.location.protocol.startsWith('http')
            ? `/api/proxy?url=${encodeURIComponent(espnTarget)}`
            : espnTarget;
          const resp = await fetch(espnUrl, {
            signal: controller.signal
          });
          clearTimeout(timeoutId);
          if (!resp.ok) return [];
          const data = await resp.json();
          const events = data.events || [];
          const res = [];
          for (const ev of events) {
            const mId = ev.id || '';
            const dateIso = ev.date || '';
            let timeFormatted = 'Hôm nay';
            if (dateIso) {
              const d = new Date(dateIso);
              const vnHour = String(d.getHours()).padStart(2, '0');
              const vnMin = String(d.getMinutes()).padStart(2, '0');
              const vnDay = String(d.getDate()).padStart(2, '0');
              const vnMonth = String(d.getMonth() + 1).padStart(2, '0');
              timeFormatted = `${vnHour}:${vnMin} • ${vnDay}/${vnMonth}`;
            }

            const state = ev.status?.type?.state || 'pre';
            const comps = ev.competitions?.[0]?.competitors || [];
            let teamHome = '', teamAway = '', logoHome = DEFAULT_TV_LOGO, logoAway = DEFAULT_TV_LOGO;
            let scoreHome = '', scoreAway = '';
            for (const item of comps) {
              const tName = item.team?.displayName || '';
              const tLogo = item.team?.logo || DEFAULT_TV_LOGO;
              const sc = item.score || '';
              if (item.homeAway === 'home') {
                teamHome = tName; logoHome = tLogo; scoreHome = sc;
              } else {
                teamAway = tName; logoAway = tLogo; scoreAway = sc;
              }
            }

            const isLive = (state === 'in');
            const isFinished = (state === 'post');
            let scoreStr = timeFormatted;
            if (isLive) {
              scoreStr = `🔴 LIVE • ${scoreHome} - ${scoreAway}`;
            } else if (isFinished) {
              scoreStr = `🏁 FT • ${scoreHome} - ${scoreAway}`;
            }

            res.push({
              id: `espn_${mId}`,
              tournament: lg.name,
              teamA: teamHome || 'Đội Nhà',
              teamB: teamAway || 'Đội Khách',
              teamALogo: logoHome,
              teamBLogo: logoAway,
              time: scoreStr,
              timeStr: timeFormatted,
              isLive: isLive,
              isFinished: isFinished,
              channelName: lg.chName,
              channelSlug: lg.chSlug
            });
          }
          return res;
        } catch (e) {
          return [];
        }
      };

      const results = await Promise.allSettled(leagues.map(fetchLeague));
      const matches = [];
      for (const r of results) {
        if (r.status === 'fulfilled' && Array.isArray(r.value)) {
          matches.push(...r.value);
        }
      }

      if (matches.length > 0) {
        matches.sort((a, b) => {
          if (a.isLive && !b.isLive) return -1;
          if (!a.isLive && b.isLive) return 1;
          if (!a.isFinished && b.isFinished) return -1;
          if (a.isFinished && !b.isFinished) return 1;
          return 0;
        });
        return matches;
      }
      return LIVE_MATCHES;
    } catch (err) {
      console.warn('ESPN fetch error:', err);
      return LIVE_MATCHES;
    }
  }

  // --- Modal Chọn 1 Trong 4 Server Xem Trực Tiếp ---
  let selectedMatchForServer = null;
  function openMatchServerModal(match) {
    if (!match) return;
    activeMatchForServer = match;
    selectedMatchForServer = match;
    const modal = document.getElementById('matchServerModal');
    if (!modal) return;

    const leagueEl = document.getElementById('serverModalLeague');
    const teamsEl = document.getElementById('serverModalTeams');
    const timeEl = document.getElementById('serverModalTime');

    if (leagueEl) leagueEl.textContent = match.tournament || '🏴󠁧󠁢󠁥󠁮󠁧󠁿 NGOẠI HẠNG ANH';
    if (teamsEl) {
      const logoA = match.teamALogo || DEFAULT_TV_LOGO;
      const logoB = match.teamBLogo || DEFAULT_TV_LOGO;
      teamsEl.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; gap: 14px; margin: 8px 0; flex-wrap: wrap;">
          <img src="${logoA}" style="width: 44px; height: 44px; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));" onerror="this.style.display='none'">
          <span style="font-size: 20px; font-weight: 900; color: #ffffff;">${match.teamA}</span>
          <span style="font-size: 15px; font-weight: 900; color: #facc15; padding: 2px 8px; background: rgba(250,204,21,0.15); border-radius: 6px;">VS</span>
          <span style="font-size: 20px; font-weight: 900; color: #ffffff;">${match.teamB}</span>
          <img src="${logoB}" style="width: 44px; height: 44px; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));" onerror="this.style.display='none'">
        </div>
      `;
    }
    if (timeEl) timeEl.textContent = match.time || 'Trực Tiếp';

    modal.style.display = 'flex';
  }
  const showMatchServerModal = openMatchServerModal;
  window.openMatchServerModal = openMatchServerModal;
  window.showMatchServerModal = openMatchServerModal;

  function initMatchServerModalEvents() {
    const modal = document.getElementById('matchServerModal');
    const btnClose = document.getElementById('btnCloseServerModal');
    if (btnClose) {
      btnClose.addEventListener('click', () => {
        if (modal) modal.style.display = 'none';
      });
    }

    // Server 1: Thập Cẩm HD
    document.getElementById('btnServer1')?.addEventListener('click', () => {
      if (modal) modal.style.display = 'none';
      playMatchViaServer(1, activeMatchForServer);
    });

    // Server 2: Xôi Lạc HD
    document.getElementById('btnServer2')?.addEventListener('click', () => {
      if (modal) modal.style.display = 'none';
      playMatchViaServer(2, activeMatchForServer);
    });

    // Server 3: Về Bờ HD
    document.getElementById('btnServer3')?.addEventListener('click', () => {
      if (modal) modal.style.display = 'none';
      playMatchViaServer(3, activeMatchForServer);
    });

    // Server 4: Vệ Tinh Quốc Tế (True Premier / Astro 1080p 50fps)
    document.getElementById('btnServer4')?.addEventListener('click', () => {
      if (modal) modal.style.display = 'none';
      playMatchViaServer(4, activeMatchForServer);
    });

    // Thoát Web Player Trận Đấu
    document.getElementById('btnCloseMatchWebPlayer')?.addEventListener('click', () => {
      closeMatchWebPlayer();
    });

    // Đổi Server Nhanh
    document.getElementById('btnSwitchServerQuick')?.addEventListener('click', () => {
      closeMatchWebPlayer();
      if (activeMatchForServer) openMatchServerModal(activeMatchForServer);
    });

    // Toàn màn hình match web player
    document.getElementById('btnFullscreenMatch')?.addEventListener('click', () => {
      const container = document.getElementById('matchWebPlayerContainer');
      if (!document.fullscreenElement) {
        container.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });
  }

  function playMatchViaServer(serverNum, match) {
    if (!match) return;

    if (serverNum === 4) {
      // Server 4: Mở kênh Vệ Tinh Quốc Tế True Premier Football hoặc Astro SuperSport phát trực tiếp
      const allChannels = getAllChannels();
      const satChannel = allChannels.find(c => c.id === 'sports_sat_true_premier_1') ||
                         allChannels.find(c => (c.name || '').includes('True Premier')) ||
                         allChannels.find(c => (c.name || '').includes('Astro SuperSport')) ||
                         allChannels.find(c => (c.group || '').includes('Vệ Tinh'));
      if (satChannel) {
        showToast(`🟡 Đang mở Server 4: ${satChannel.name}...`);
        playTvChannelDirectly({
          id: satChannel.id,
          name: `[Server 4 Vệ Tinh] ${match.teamA} vs ${match.teamB}`,
          streamUrl: satChannel.url,
          posterUrl: satChannel.logo
        });
      } else {
        showToast('Kênh vệ tinh đang được tải...');
      }
      return;
    }

    // Server 1, 2, 3: Mở Web Player không quảng cáo với domain đang hoạt động
    const container = document.getElementById('matchWebPlayerContainer');
    const iframe = document.getElementById('matchIframe');
    const titleEl = document.getElementById('matchWebPlayerTitle');
    const subEl = document.getElementById('matchWebPlayerSub');

    if (!container || !iframe) return;

    titleEl.textContent = `⚽ ${match.teamA} vs ${match.teamB}`;
    
    let streamEmbedUrl = '';
    if (serverNum === 1) {
      subEl.textContent = 'Server 1: Thập Cẩm HD (Bình Luận Tiếng Việt • Ad-Free)';
      streamEmbedUrl = 'https://thapcamtv.to/';
    } else if (serverNum === 2) {
      subEl.textContent = 'Server 2: Xôi Lạc HD (Bình Luận Tiếng Việt • Ad-Free)';
      streamEmbedUrl = 'https://xoilac-tv.college/';
    } else {
      subEl.textContent = 'Server 3: Về Bờ HD (Bình Luận Tiếng Việt • Ad-Free)';
      streamEmbedUrl = 'https://vebotv.live/';
    }

    showToast(`Đang kết nối Server ${serverNum} (Không quảng cáo)...`);
    iframe.src = streamEmbedUrl;
    const btnExt = document.getElementById('btnExternalMatch');
    if (btnExt) btnExt.href = streamEmbedUrl;
    container.style.display = 'block';

    // Tiêm mã CSS/JS để xóa sạch 100% banner quảng cáo cá cược
    iframe.onload = () => {
      try {
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        if (doc) {
          const style = doc.createElement('style');
          style.innerHTML = `
            .banner, .banner-ads, .popup-ads, .ad-box, #chat-box, .advertisement, [class*="bet"], [class*="banner"] { display: none !important; }
            header, footer, nav, .sidebar { display: none !important; }
            body, html { background: #000 !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important; }
            video, iframe, #player { width: 100vw !important; height: 100vh !important; max-height: 100vh !important; }
          `;
          doc.head.appendChild(style);
        }
      } catch (e) {
        // Cross-origin injection handled securely via sandbox/browser
      }
    };
  }

  function closeMatchWebPlayer() {
    const container = document.getElementById('matchWebPlayerContainer');
    const iframe = document.getElementById('matchIframe');
    if (iframe) iframe.src = 'about:blank';
    if (container) container.style.display = 'none';
  }

  // --- Render Movie Cards (7 Columns) ---
  const renderMovieGrid = (items, reset) => renderCards(items, reset);
  function renderCards(items, reset) {
    const grid = document.getElementById('mainGrid');
    if (reset) grid.innerHTML = '';

    if (items.length === 0 && reset) {
      grid.innerHTML = '<div style="color: #94a3b8; font-size: 16px; padding: 20px;">Không có nội dung hiển thị trong mục này.</div>';
      return;
    }

    currentMoviesList = reset ? items : [...currentMoviesList, ...items];

    items.forEach(movie => {
      const card = document.createElement('div');
      const isTv = movie.source === 'XEMTIVI';
      const isMatch = !!(movie.isEplMatch || movie.rawMatch);

      if (isMatch) {
        // --- GIAO DIỆN TRẬN ĐẤU BÓNG ĐÁ SONG ĐẤU ĐỦ 2 BIỂU TƯỢNG (HOME & AWAY) ---
        const raw = movie.rawMatch || {};
        const teamA = movie.teamA || raw.teamA || 'Đội Nhà';
        const teamB = movie.teamB || raw.teamB || 'Đội Khách';
        const logoA = movie.teamALogo || raw.teamALogo || DEFAULT_TV_LOGO;
        const logoB = movie.teamBLogo || raw.teamBLogo || DEFAULT_TV_LOGO;
        const tournament = raw.tournament || movie.originName || 'BÓNG ĐÁ';
        const isLive = !!(raw.isLive || movie.quality === 'LIVE');
        const badgeText = isLive ? 'LIVE' : (movie.quality || 'EPL');
        const matchTime = movie.episodeCurrent || raw.time || '';
        const vsOrScore = isLive ? (raw.score || '🔴 LIVE') : (raw.isFinished ? (raw.score || '🏁 FT') : 'VS');

        card.className = 'movie-card focusable match-grid-card tv-card';
        card.tabIndex = 0;
        card.dataset.id = movie.id;

        card.innerHTML = `
          <div class="match-grid-card-inner">
            <div class="match-grid-header">
              <span class="match-grid-tournament" title="${tournament}">${tournament}</span>
              <span class="match-grid-badge ${isLive ? 'live' : ''}">${badgeText}</span>
            </div>

            <div class="match-grid-versus">
              <!-- Cột Đội Nhà -->
              <div class="match-team-item team-home">
                <div class="match-team-logo-wrap">
                  <img class="team-crest" src="${logoA}" alt="${teamA}" onerror="this.onerror=null; this.src='https://assets.coingecko.com/coins/images/2518/small/ball.png';" loading="lazy">
                </div>
                <div class="match-team-title" title="${teamA}">${teamA}</div>
              </div>

              <!-- Cột Trung Tâm: VS / Tỷ Số + Giờ Đá -->
              <div class="match-center-pillar">
                <div class="match-vs-text ${isLive ? 'is-live' : ''}">${vsOrScore}</div>
                <div class="match-time-text">${matchTime}</div>
              </div>

              <!-- Cột Đội Khách -->
              <div class="match-team-item team-away">
                <div class="match-team-logo-wrap">
                  <img class="team-crest" src="${logoB}" alt="${teamB}" onerror="this.onerror=null; this.src='https://assets.coingecko.com/coins/images/2518/small/ball.png';" loading="lazy">
                </div>
                <div class="match-team-title" title="${teamB}">${teamB}</div>
              </div>
            </div>

            <div class="match-grid-footer">
              <span class="match-servers-text">⚡ 4 Server Trực Tiếp</span>
              <button class="btn-bell-reminder ${movie.hasReminder ? 'active' : ''}" data-match-id="${movie.id}" title="Thông báo khi đến giờ đá">
                ${movie.hasReminder ? '🔔 Đã Đặt' : '🔔 Nhắc Tôi'}
              </button>
            </div>
          </div>
        `;
      } else {
        // --- GIAO DIỆN PHIM / KÊNH TV THÔNG THƯỜNG ---
        card.className = `movie-card focusable ${isTv ? 'tv-card' : ''}`;
        card.tabIndex = 0;
        card.dataset.id = movie.id;

        const favBadge = isFavorite(movie.id) ? '<div class="badge-fav">⭐</div>' : '';
        const qualityBadge = `<div class="badge-quality">${movie.quality || 'HD'}</div>`;
        const epBadge = movie.episodeCurrent ? `<div class="badge-episode">${movie.episodeCurrent}</div>` : '';
        const isDesktopLayout = window.innerWidth > 800 && !(/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent || ''));
        const displayImgUrl = isTv
          ? getTvChannelLogo(movie)
          : (isDesktopLayout
              ? (movie.landscapeUrl || movie.thumbUrl || movie.posterUrl || DEFAULT_TV_LOGO)
              : (movie.portraitUrl || movie.posterUrl || movie.thumbUrl || DEFAULT_TV_LOGO));

        card.innerHTML = `
          <div class="poster-wrapper" style="--poster-bg: url('${displayImgUrl}')">
            <img class="card-poster" src="${displayImgUrl}" alt="${movie.name}" onload="if(window.innerWidth>800 && this.naturalHeight>this.naturalWidth*1.12){this.parentElement.classList.add('is-vertical-img');}" onerror="this.onerror=null; this.src='${isTv ? getTvChannelLogo(movie) : (movie.posterUrl || movie.thumbUrl || DEFAULT_TV_LOGO)}';" loading="lazy">
            ${qualityBadge}
            ${favBadge}
            ${epBadge}
          </div>
          <div class="card-info">
            <div class="card-title">${movie.name}</div>
            <div class="card-subtitle">${movie.originName || movie.year || ''}</div>
          </div>
        `;
      }

      // Click card
      card.addEventListener('click', (e) => {
        if (movie.isEplMatch || movie.rawMatch) {
          // Bấm vào trận đấu Ngoại Hạng Anh: Mở bảng chọn 1 trong 4 Server
          openMatchServerModal(movie.rawMatch || movie);
          return;
        }
        if (movie.source === 'XEMTIVI') {
          // BẤM VÀO KÊNH TV: VÀO XEM TRỰC TIẾP NGAY LẬP TỨC (Quy tắc v2.1)
          playTvChannelDirectly(movie);
        } else {
          openMovieDetail(movie);
        }
      });

      // Gán sự kiện cho nút chuông nhắc nhở độc lập
      const bellBtn = card.querySelector('.btn-bell-reminder');
      if (bellBtn && movie.rawMatch) {
        bellBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          const isSet = toggleMatchReminder(movie.rawMatch);
          bellBtn.classList.toggle('active', isSet);
          bellBtn.innerHTML = isSet ? '🔔 Đã Đặt' : '🔔 Nhắc Tôi';
        });
      }

      // Long press / Context menu / Yellow key: Toggle Favorite
      card.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        toggleFavorite(movie);
        loadMovies(true);
      });

      grid.appendChild(card);
    });

    // Tự động focus phần tử đầu tiên nếu chưa có focus
    if (!currentFocusedElement || !document.body.contains(currentFocusedElement)) {
      const firstCard = grid.querySelector('.movie-card');
      if (firstCard) setFocus(firstCard);
    }
  }

  // --- History & Favorites Section ---
  function renderHistoryAndFavs() {
    const historySec = document.getElementById('historySection');
    const historyScroll = document.getElementById('historyScroll');
    const isMobile = window.innerWidth <= 800 || document.body.classList.contains('mode-mobile') || /Android|iPhone|iPad|Mobile/i.test(navigator.userAgent);
    if (isMobile) {
      if (historySec) historySec.style.display = 'none';
      return;
    }

    const hist = getHistory();
    if (!hist || hist.length === 0) {
      if (historySec) historySec.style.display = 'none';
      return;
    }

    historySec.style.display = 'block';
    historyScroll.innerHTML = '';

    hist.forEach(item => {
      const card = document.createElement('div');
      card.className = 'history-item focusable';
      card.tabIndex = 0;
      card.innerHTML = `
        <img class="history-thumb" src="${item.posterUrl || DEFAULT_TV_LOGO}" onerror="this.src='${DEFAULT_TV_LOGO}'">
        <div class="history-progress-bg">
          <div class="history-progress-bar" style="width: ${item.percent || 0}%"></div>
        </div>
        <div class="history-info">
          <div class="history-name">${item.name}</div>
          <div class="history-sub">${item.episodeName || 'Đang xem'} • ${item.percent || 0}%</div>
        </div>
      `;
      card.addEventListener('click', () => {
        if (item.source === 'XEMTIVI') {
          playTvChannelDirectly({
            id: item.id,
            name: item.name,
            streamUrl: item.streamUrl || (getAllChannels().find(c => c.id === item.id) || {}).url,
            posterUrl: item.posterUrl
          });
        } else {
          openMovieDetail({
            id: item.id,
            name: item.name,
            slug: item.slug || item.id,
            source: item.source
          });
        }
      });
      historyScroll.appendChild(card);
    });
  }

  document.getElementById('btnClearHistory').addEventListener('click', () => {
    localStorage.removeItem('huycabuonca_history');
    renderHistoryAndFavs();
    showToast('Đã xóa toàn bộ lịch sử xem!');
  });

  // --- Detail Modal ---
  async function openMovieDetail(movie) {
    if (!movie) return;
    // BẢO VỆ CHỐNG NHẦM: Nếu là trận đấu bóng đá hoặc kênh TV, không bao giờ mở trang chi tiết phim!
    if (movie.isEplMatch || movie.rawMatch) {
      openMatchServerModal(movie.rawMatch || movie);
      return;
    }
    if (movie.source === 'XEMTIVI' || movie.isTv || movie.isLiveTv) {
      playTvChannelDirectly(movie);
      return;
    }
    const modal = document.getElementById('detailModal');
    modal.style.display = 'flex';
    pushNavigationState('detail');

    document.getElementById('detailTitle').textContent = movie.name;
    document.getElementById('detailSub').textContent = `${movie.originName || ''} • ${movie.year || '2026'}`;
    document.getElementById('detailPoster').src = movie.posterUrl || movie.thumbUrl || DEFAULT_TV_LOGO;
    document.getElementById('detailDesc').textContent = 'Đang tải thông tin chi tiết phim...';
    document.getElementById('episodesGrid').innerHTML = '<div style="color: #94a3b8;">Đang tải danh sách tập...</div>';

    const srvBarInit = document.getElementById('modalServerBar');
    if (srvBarInit) srvBarInit.style.display = 'none';
    const directBtnInit = document.getElementById('btnDirectPlayDetail');
    if (directBtnInit) directBtnInit.style.display = 'none';
    updateDetailFavButton(movie);

    // CRITICAL BUG FIX: Reset nút phát ngay lập tức để không chạy nhầm phim đã xem trước đó
    const playFirstBtn = document.getElementById('btnPlayFirst');
    if (playFirstBtn) {
      playFirstBtn.onclick = () => {
        showToast('⏳ Đang tải thông tin tập phim, vui lòng đợi...');
      };
    }

    try {
      if (movie.slug && movie.slug.startsWith('gamomephim:')) {
        const realSlug = movie.slug.replace('gamomephim:', '');
        const data = await GaMoMePhimClient.getDramaDetail(realSlug);
        if (!data) throw new Error('GaMoMePhim detail error');
        currentPlayingDetail = data;
        const m = data;

        document.getElementById('detailTitle').textContent = m.name;
        document.getElementById('detailSub').textContent = `${m.year || '2026'} • ${m.lang || 'Thuyết Minh'} • ${m.time || 'Trọn bộ'}`;
        document.getElementById('detailDesc').textContent = m.content || 'Phim ngắn tiểu kịch thuyết minh & vietsub Full HD.';
        document.getElementById('detailPoster').src = m.posterUrl || m.thumbUrl || DEFAULT_TV_LOGO;

        const tags = document.getElementById('detailTags');
        if (tags) {
          tags.innerHTML = `
            <span class="tag-badge">Chất lượng: ${m.quality || 'Full HD'}</span>
            <span class="tag-badge">Ngôn ngữ: ${m.lang || 'Thuyết Minh'}</span>
            <span class="tag-badge">Thể loại: Phim Ngắn Tiểu Kịch</span>
            <span class="tag-badge">Nguồn: Gà Mờ Mê Phim</span>
          `;
        }

        const epGrid = document.getElementById('episodesGrid');
        epGrid.innerHTML = '';

        if (data.episodes && data.episodes.length > 0) {
          const allEps = [];
          data.episodes.forEach((srv, srvIdx) => {
            (srv.server_data || []).forEach((ep, epIdx) => {
              allEps.push({ ...ep, serverIndex: srvIdx, epIndex: epIdx, srvName: srv.server_name });
            });
          });

          allEps.forEach((ep, idx) => {
            const btn = document.createElement('button');
            btn.className = `btn-episode focusable ${idx === 0 ? 'active' : ''}`;
            const srvLabel = ep.srvName && ep.srvName.includes('Thuyết Minh') ? 'Thuyết Minh' : 'Vietsub';
            btn.textContent = `${ep.name} [${srvLabel}]`;
            btn.addEventListener('click', () => {
              modal.style.display = 'none';
              playVideo(ep.link_m3u8, movie.name, ep.name, movie, data, ep.epIndex, ep.serverIndex);
            });
            epGrid.appendChild(btn);
          });

          // Nút Xem Tập Đầu
          document.getElementById('btnPlayFirst').onclick = () => {
            modal.style.display = 'none';
            const first = allEps[0];
            if (first) {
              playVideo(first.link_m3u8, movie.name, first.name, movie, data, first.epIndex, first.serverIndex, false, null, true);
            }
          };
        } else {
          epGrid.innerHTML = '<div style="color: #94a3b8;">Không tìm thấy luồng phát của phim này.</div>';
          document.getElementById('btnPlayFirst').onclick = () => {
            showToast('Chưa có link phát cho phim này!');
          };
        }

        setTimeout(() => {
          const playFirst = document.getElementById('btnPlayFirst');
          if (playFirst) setFocus(playFirst);
        }, 50);
        return;
      }

      if (movie.slug && movie.slug.startsWith('freereels:')) {
        const realId = movie.slug.replace('freereels:', '');
        const data = await FreeReelsClient.getDramaDetail(realId);
        if (!data) throw new Error('FreeReels detail error');
        const m = data.movie;
        currentPlayingDetail = data;

        document.getElementById('detailDesc').textContent = m.content || 'Phim ngắn dọc FreeReels HD kèm phụ đề tiếng Việt.';
        const tags = document.getElementById('detailTags');
        tags.innerHTML = `
          <span class="tag-badge">Chất lượng: ${m.quality || '9:16 HD'}</span>
          <span class="tag-badge">Thời lượng: ${m.time || 'Nhiều tập'}</span>
          <span class="tag-badge">Ngôn ngữ: ${m.lang || 'Vietsub'}</span>
          <span class="tag-badge">Thể loại: Phim Ngắn Dọc</span>
        `;

        const epGrid = document.getElementById('episodesGrid');
        epGrid.innerHTML = '';

        const server = data.episodes[0];
        const items = server.server_data || [];
        items.forEach((ep, idx) => {
          const btn = document.createElement('button');
          btn.className = 'btn-episode focusable';
          btn.textContent = ep.name;
          btn.addEventListener('click', async () => {
            modal.style.display = 'none';
            let stream = ep.link_m3u8;
            let sub = ep.subtitleUrl;
            if (stream && stream.startsWith('freereels_unlock:')) {
              showToast('🔓 Đang mở khóa tập...');
              const unl = await FreeReelsClient.unlockEpisode(realId, ep.slug);
              if (unl && unl.streamUrl) {
                stream = unl.streamUrl;
                if (unl.subtitleUrl) sub = unl.subtitleUrl;
              }
            }
            playVideo(stream, movie.name, ep.name, movie, data, idx, 0, sub);
          });
          epGrid.appendChild(btn);
        });

        document.getElementById('btnPlayFirst').onclick = async () => {
          modal.style.display = 'none';
          const firstEp = items[0];
          if (firstEp) {
            let stream = firstEp.link_m3u8;
            let sub = firstEp.subtitleUrl;
            if (stream && stream.startsWith('freereels_unlock:')) {
              showToast('🔓 Đang mở khóa tập 1...');
              const unl = await FreeReelsClient.unlockEpisode(realId, firstEp.slug);
              if (unl && unl.streamUrl) {
                stream = unl.streamUrl;
                if (unl.subtitleUrl) sub = unl.subtitleUrl;
              }
            }
            playVideo(stream, movie.name, firstEp.name, movie, data, 0, 0, sub, true);
          }
        };
      } else if (movie.slug && movie.slug.startsWith('nguonc:')) {
        const realSlug = movie.slug.replace('nguonc:', '');
        const resp = await fetch(`https://phim.nguonc.com/api/film/${realSlug}`);
        if (!resp.ok) throw new Error('NguonC detail error');
        const data = await resp.json();
        const m = data.movie;

        // Chuẩn hóa data.episodes sang format thống nhất chuẩn (server_name, server_data) để sidebar và player dùng chung
        if (m.episodes && m.episodes.length > 0) {
          data.episodes = m.episodes.map((s, sIdx) => ({
            server_name: s.server_name || `Server ${sIdx + 1}`,
            server_data: (s.items || []).map((it, itIdx) => {
              const epTitle = (it.name && /^\d+$/.test(it.name)) ? `Tập ${it.name}` : (it.name || `Tập ${itIdx + 1}`);
              return {
                name: epTitle,
                slug: it.slug,
                link_m3u8: it.embed || it.m3u8,
                embed: it.embed
              };
            })
          }));
        }
        currentPlayingDetail = data;

        document.getElementById('detailDesc').textContent = (m.description || '').replace(/<[^>]*>?/gm, '') || 'Không có mô tả chi tiết.';

        const tags = document.getElementById('detailTags');
        tags.innerHTML = `
          <span class="tag-badge">Chất lượng: ${m.quality || 'HD'}</span>
          <span class="tag-badge">Thời lượng: ${m.time || 'Trọn bộ'}</span>
          <span class="tag-badge">Ngôn ngữ: ${m.language || 'Vietsub'}</span>
          <span class="tag-badge">Tập: ${m.current_episode || 'Đang cập nhật'}</span>
        `;

        const epGrid = document.getElementById('episodesGrid');
        epGrid.innerHTML = '';

        if (data.episodes && data.episodes.length > 0) {
          let activeSrvIdx = 0;
          const renderModalEpisodes = (sIdx) => {
            epGrid.innerHTML = '';
            const s = data.episodes[sIdx] || data.episodes[0];
            const items = s.server_data || [];
            items.forEach((ep, idx) => {
              const btn = document.createElement('button');
              btn.className = 'btn-episode focusable';
              btn.textContent = ep.name;
              btn.addEventListener('click', () => {
                modal.style.display = 'none';
                playVideo(ep.link_m3u8 || ep.embed, movie.name, `${ep.name} (${s.server_name})`, movie, data, idx, sIdx);
              });
              epGrid.appendChild(btn);
            });
          };

          // Nếu có nhiều Server (Ví dụ: Vietsub #1, Lồng Tiếng #1), hiển thị thanh chuyển Server
          const oldServerBar = document.getElementById('modalServerBar');
          if (data.episodes.length > 1) {
            let srvBar = oldServerBar;
            if (!srvBar) {
              srvBar = document.createElement('div');
              srvBar.id = 'modalServerBar';
              srvBar.style.cssText = 'display: flex; gap: 8px; margin-bottom: 12px; overflow-x: auto; padding: 4px 0;';
              epGrid.parentNode.insertBefore(srvBar, epGrid);
            }
            srvBar.innerHTML = '';
            srvBar.style.display = 'flex';
            data.episodes.forEach((srv, sIdx) => {
              const sBtn = document.createElement('button');
              sBtn.className = `btn-server-tab focusable ${sIdx === 0 ? 'active' : ''}`;
              sBtn.style.cssText = `padding: 6px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; border: 1px solid rgba(255,255,255,0.15); background: ${sIdx === 0 ? 'var(--accent-red, #e50914)' : 'rgba(255,255,255,0.08)'}; color: #fff; transition: all 0.2s;`;
              sBtn.textContent = srv.server_name;
              sBtn.onclick = () => {
                activeSrvIdx = sIdx;
                srvBar.querySelectorAll('.btn-server-tab').forEach((b, i) => {
                  b.style.background = (i === sIdx) ? 'var(--accent-red, #e50914)' : 'rgba(255,255,255,0.08)';
                });
                renderModalEpisodes(sIdx);
              };
              srvBar.appendChild(sBtn);
            });
          } else if (oldServerBar) {
            oldServerBar.style.display = 'none';
          }

          renderModalEpisodes(0);

          // Nút Xem Trực Tiếp / Pop-out cho Nguồn C: Ẩn hoàn toàn để bảo vệ người dùng không bị văng ra tab quảng cáo ngoài
          const directBtn = document.getElementById('btnDirectPlayDetail');
          if (directBtn) {
            directBtn.style.display = 'none';
          }

          document.getElementById('btnPlayFirst').onclick = () => {
            modal.style.display = 'none';
            const curSrv = data.episodes[activeSrvIdx] || data.episodes[0];
            const firstEp = curSrv?.server_data?.[0];
            if (firstEp) {
              playVideo(firstEp.link_m3u8 || firstEp.embed, movie.name, `${firstEp.name} (${curSrv.server_name})`, movie, data, 0, activeSrvIdx, false, null, true);
            }
          };
        }
      } else {
        let data = null;
        try {
          const resp = await fetch(`https://phimapi.com/phim/${movie.slug}`);
          if (resp.ok) data = await resp.json();
        } catch(e) {}
        if (!data || !data.movie) {
          try {
            const resp = await fetch(`/api/proxy?url=${encodeURIComponent('https://phimapi.com/phim/' + movie.slug)}`);
            if (resp.ok) data = await resp.json();
          } catch(e) {}
        }
        if (!data || !data.movie) {
          try {
            const resp = await fetch(`https://ophim1.com/phim/${movie.slug}`);
            if (resp.ok) data = await resp.json();
          } catch(e) {}
        }
        if (!data || !data.movie) throw new Error('Detail error');
        const m = data.movie;
        currentPlayingDetail = data;

        document.getElementById('detailDesc').textContent = (m.content || '').replace(/<[^>]*>?/gm, '') || 'Không có mô tả chi tiết.';

        const tags = document.getElementById('detailTags');
        tags.innerHTML = `
          <span class="tag-badge">Chất lượng: ${m.quality || 'HD'}</span>
          <span class="tag-badge">Thời lượng: ${m.time || 'Trọn bộ'}</span>
          <span class="tag-badge">Ngôn ngữ: ${m.lang || 'Vietsub'}</span>
          <span class="tag-badge">Tập: ${m.episode_current || 'Đang cập nhật'}</span>
        `;

        // Danh sách tập
        const epGrid = document.getElementById('episodesGrid');
        epGrid.innerHTML = '';

        if (data.episodes && data.episodes.length > 0) {
          const s = data.episodes[0];
          (s.server_data || []).forEach((ep, idx) => {
            const btn = document.createElement('button');
            btn.className = 'btn-episode focusable';
            btn.textContent = ep.name || `Tập ${idx + 1}`;
            btn.addEventListener('click', () => {
              modal.style.display = 'none';
              playVideo(ep.link_m3u8, movie.name, ep.name, movie, data, idx, 0);
            });
            epGrid.appendChild(btn);
          });

          // Nút Xem Tập Đầu
          document.getElementById('btnPlayFirst').onclick = () => {
            modal.style.display = 'none';
            const firstEp = s.server_data[0];
            if (firstEp) {
              playVideo(firstEp.link_m3u8, movie.name, firstEp.name, movie, data, 0, 0, false, null, true);
            }
          };
        }
      }
    } catch (e) {
      console.error('Movie detail load error:', e);
      document.getElementById('detailDesc').textContent = 'Không thể tải thông tin phim. Vui lòng thử lại sau!';
      document.getElementById('episodesGrid').innerHTML = '<div style="color: #ef4444; padding: 12px; font-size: 13px;">⚠️ Không thể tải danh sách tập phim. Vui lòng chọn phim khác hoặc thử lại sau!</div>';
      if (playFirstBtn) {
        playFirstBtn.onclick = () => {
          showToast('⚠️ Phim này hiện không thể tải dữ liệu tập!');
        };
      }
    }

    setTimeout(() => {
      const playFirst = document.getElementById('btnPlayFirst');
      if (playFirst) setFocus(playFirst);
    }, 50);

    document.getElementById('btnCloseDetail').onclick = () => {
      modal.style.display = 'none';
      if (history.state && history.state.screen === 'detail') {
        try { history.back(); } catch(e) {}
      }
      focusCurrentOrFirstMovie();
    };

    document.getElementById('btnToggleFavDetail').onclick = () => {
      toggleFavorite(movie);
      updateDetailFavButton(movie);
    };
  }

  function updateDetailFavButton(movie) {
    const btn = document.getElementById('btnToggleFavDetail');
    if (isFavorite(movie.id)) {
      btn.textContent = '❤️ ĐÃ YÊU THÍCH';
      btn.style.color = '#ef4444';
    } else {
      btn.textContent = '⭐ THÊM YÊU THÍCH';
      btn.style.color = '#ffffff';
    }
  }

  // --- Play TV Channel Directly ---
  function playTvChannelDirectly(movie) {
    let url = movie.streamUrl;
    if (!url) {
      const found = getAllChannels().find(c => c.id === movie.id || c.name === movie.name);
      if (found) url = found.url;
    }
    if (!url) {
      showToast('Kênh này hiện chưa có luồng phát trực tiếp!');
      return;
    }

    playVideo(url, movie.name, 'Trực Tiếp', movie, null, 0, 0, true);
    setupQuickZapping(movie);
  }

  // 🛡️ BỘ LỌC QUẢNG CÁO HLS M3U8 TỰ ĐỘNG (Xóa sạch 100% video quảng cáo cờ bạc, cá độ, 18+ chèn ngang)
  function stripAdsFromM3U8(manifestText) {
    if (!manifestText || typeof manifestText !== 'string') return manifestText;
    if (!manifestText.includes('#EXT-X-DISCONTINUITY') && !manifestText.includes('convertv8') && !manifestText.includes('/v8/')) {
      return manifestText;
    }

    const isAdUri = (uri) => {
      if (!uri) return false;
      const s = uri.toLowerCase();
      return s.includes('convertv8') ||
             s.includes('/v8/') ||
             /segment_\d+\.ts/.test(s) ||
             s.includes('/ads/') ||
             s.includes('/ad/') ||
             s.includes('/advert') ||
             s.includes('/quangcao') ||
             s.includes('/promo/') ||
             s.includes('1xbet') ||
             s.includes('kubet') ||
             s.includes('shbet') ||
             s.includes('hi88') ||
             s.includes('789bet') ||
             s.includes('okvip') ||
             s.includes('jun88') ||
             s.includes('new88') ||
             s.includes('f8bet') ||
             s.includes('fb88') ||
             s.includes('sv388') ||
             s.includes('gamebai') ||
             s.includes('taixiu') ||
             s.includes('nohu');
    };

    const lines = manifestText.split(/\r?\n/);
    const out = [];
    let pendingTags = [];
    let adBlockActive = false;

    for (let i = 0; i < lines.length; i++) {
      const raw = lines[i];
      const line = raw.trim();
      if (!line) continue;

      if (line.startsWith('#')) {
        pendingTags.push(line);
      } else {
        if (isAdUri(line)) {
          // Bỏ qua segment quảng cáo và các tag đi kèm
          pendingTags = [];
          adBlockActive = true;
        } else {
          if (adBlockActive) {
            // Vừa thoát khỏi khối quảng cáo: loại bỏ tag ranh giới DISCONTINUITY và KEY:METHOD=NONE
            pendingTags = pendingTags.filter(t => t !== '#EXT-X-DISCONTINUITY' && !t.startsWith('#EXT-X-KEY:METHOD=NONE'));
            adBlockActive = false;
          }
          for (const t of pendingTags) {
            out.push(t);
          }
          pendingTags = [];
          out.push(line);
        }
      }
    }

    for (const t of pendingTags) {
      if (t !== '#EXT-X-DISCONTINUITY' && !t.startsWith('#EXT-X-KEY:METHOD=NONE')) {
        out.push(t);
      }
    }

    return out.join('\n');
  }

  function getHlsPlaylistLoader() {
    if (!window.Hls || !Hls.DefaultConfig || !Hls.DefaultConfig.loader) return undefined;
    return class extends Hls.DefaultConfig.loader {
      load(context, config, callbacks) {
        const origSuccess = callbacks.onSuccess;
        callbacks.onSuccess = function(response, stats, ctx, networkDetails) {
          if (response && typeof response.data === 'string') {
            response.data = stripAdsFromM3U8(response.data);
          }
          origSuccess.call(this, response, stats, ctx, networkDetails);
        };
        super.load(context, config, callbacks);
      }
    };
  }

  // --- Video Player (Native WebOS Hardware Decoding & HLS Fallback) ---
  
  // Video Error Handler with Automatic Proxy Fallback
  let currentActiveStream = '';
  const videoElem = document.getElementById('videoPlayer');
  if (videoElem) {
    videoElem.addEventListener('error', (e) => {
      // TUYỆT ĐỐI KHÔNG CAN THIỆP nếu đang phát dạng nhúng (Embed iframe) hoặc videoPlayer đang bị ẩn / src trống:
      if (isEmbedStreamUrl(currentActiveStream) || 
          (videoElem.style.display === 'none') || 
          !videoElem.src || 
          videoElem.src === window.location.href ||
          videoElem.src.endsWith('/')) {
        return;
      }

      console.warn('Video playback error detected:', videoElem.error);
      if (currentActiveStream && !videoElem.src.includes('/api/proxy') && currentActiveStream.startsWith('http')) {
        console.log('Retrying video via proxy fallback:', currentActiveStream);
        videoElem.src = `/api/proxy?url=${encodeURIComponent(currentActiveStream)}`;
        videoElem.load();
        videoElem.play().catch(() => {});
      } else {
        showToast('Không thể tải luồng phát video. Vui lòng thử tập khác!');
      }
    });
  }

  // --- Stream Guard Parent Helper (Giao thức Handshake Chuẩn với Iframe NguonC streamc.xyz) ---
  window.addEventListener('message', (event) => {
    try {
      const data = event.data;
      if (data && data.type === 'stream-guard-hello') {
        const iframe = document.getElementById('playerIframe');
        if (iframe && iframe.contentWindow) {
          iframe.contentWindow.postMessage({
            type: 'stream-parent-state',
            version: 'guard-5',
            id: data.id,
            helperVersion: 'guard-5',
            parentAdblock: 'clear',
            seq: Date.now(),
            supported: true,
            suspected: false
          }, '*');
        }
      }
    } catch(err) {}
  });

  // --- Kiểm tra URL nhúng Iframe tuyệt đối chính xác (Chặn đứng lỗi tự động tải file manifest.mpd / .ts) ---
  function isEmbedStreamUrl(url) {
    if (!url || typeof url !== 'string') return false;
    const u = url.toLowerCase().trim();

    // TUYỆT ĐỐI KHÔNG BAO GIỜ COI LÀ EMBED NẾU LÀ CÁC ĐỊNH DẠNG MEDIA HOẶC LINK STREAM TRỰC TIẾP:
    if (u.includes('.m3u8') || u.includes('.mp4') || u.includes('.mpd') || 
        u.includes('.webm') || u.includes('.ts') || u.includes('.m4s') || 
        u.includes('.mkv') || u.includes('.flv') || u.includes('.avi') ||
        u.includes('/hls/') || u.includes('/live/') || u.includes('manifest') ||
        u.includes('chunklist') || u.includes('playlist') || u.includes('/api/proxy') || u.includes('/api/nguonc_stream')) {
      return false;
    }

    // CHỈ COI LÀ EMBED NẾU LÀ WEB PLAYER HOẶC TRANG WEB NHÚNG:
    const embedKeywords = [
      '/embed/', '/videoembed/', 'player.html', 'embed.html', 'youtube.com', 'youtu.be',
      'ok.ru', 'dailymotion.com/embed', 'vidsrc', '2embed', 'autoembed', 'streamtape.com/e/'
    ];
    if (embedKeywords.some(kw => u.includes(kw))) return true;

    // Nếu kết thúc bằng đuôi web (.html, .htm, .php)
    const cleanPath = u.split('?')[0];
    if (cleanPath.endsWith('.html') || cleanPath.endsWith('.htm') || cleanPath.endsWith('.php')) {
      return true;
    }

    return false;
  }

  window.playVideo = (s, t, sub, m, d, ep, srv, tv, csub, forceStart) => playVideo(s, t, sub, m, d, ep, srv, tv, csub, forceStart);
  window.playTvChannelDirectly = (c) => playTvChannelDirectly(c);
  
  function parseSubtitleText(text) {
    if (!text || typeof text !== 'string') return [];
    const cues = [];
    const normalized = text.replace(/\r\n|\r/g, '\n');
    const blocks = normalized.split(/\n\s*\n/);
    const timeRegex = /(?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{3})/;

    for (const block of blocks) {
      const lines = block.trim().split('\n');
      let timeLineIdx = -1;
      for (let i = 0; i < lines.length; i++) {
        if (timeRegex.test(lines[i])) {
          timeLineIdx = i;
          break;
        }
      }
      if (timeLineIdx === -1) continue;

      const match = lines[timeLineIdx].match(timeRegex);
      if (!match) continue;

      const parseSeconds = (h, m, s, ms) => {
        const hours = parseInt(h || '0', 10);
        const minutes = parseInt(m, 10);
        const seconds = parseInt(s, 10);
        const millis = parseInt(ms, 10);
        return hours * 3600 + minutes * 60 + seconds + millis / 1000;
      };

      const startTime = parseSeconds(match[1], match[2], match[3], match[4]);
      const endTime = parseSeconds(match[5], match[6], match[7], match[8]);
      const cueLines = lines.slice(timeLineIdx + 1)
        .map(l => l.replace(/<\/?[^>]+(>|$)/g, '').replace(/\{\\[^}]*\}/g, '').trim())
        .filter(l => l.length > 0);

      if (cueLines.length > 0 && endTime > startTime) {
        cues.push({ start: startTime, end: endTime, text: cueLines.join('\n') });
      }
    }
    return cues;
  }

  function convertSrtToVtt(srtText) {
    if (!srtText || typeof srtText !== 'string') return 'WEBVTT\n\n';
    if (srtText.trim().startsWith('WEBVTT')) return srtText;
    return 'WEBVTT\n\n' + srtText
      .replace(/\r\n|\r/g, '\n')
      .replace(/(\d{2}:\d{2}:\d{2}),(\d{3})/g, '.');
  }

function playVideo(streamUrl, title, subtitle, movie, detail, epIndex, serverIndex, isTv = false, customSubtitleUrl = null, forceStartFromBeginning = false) {
    if (typeof isTv === 'string') {
      customSubtitleUrl = isTv;
      isTv = false;
    }
    if (!streamUrl) {
      showToast('Không tìm thấy link luồng phát video!');
      return;
    }

    if (streamUrl.startsWith('freereels_unlock:')) {
      showToast('🔄 Đang mở khóa tập phim...');
      const parts = streamUrl.split(':');
      const sId = parts[1] || (movie && movie.id ? movie.id.replace('freereels:', '') : '');
      const eId = parts[2] || '';
      FreeReelsClient.unlockEpisode(sId, eId).then(unl => {
        if (unl && unl.streamUrl) {
          playVideo(unl.streamUrl, title, subtitle, movie, detail, epIndex, serverIndex, isTv, unl.subtitleUrl || customSubtitleUrl);
        } else {
          showToast('Không thể mở khóa tập phim này!');
        }
      });
      return;
    }

    // GIẢI MÃ VÀ PHÁT LUỒNG NGUỒN C SẠCH 100% (ZERO ADS, NATIVE HLS)
    if (streamUrl && (streamUrl.includes('streamc.xyz') || streamUrl.includes('embed.php?hash='))) {
      streamUrl = `/api/nguonc_stream?url=${encodeURIComponent(streamUrl)}`;
    }

    // Đảm bảo luồng R2 mp4 (Gà Mờ Mê Phim) luôn qua proxy có hỗ trợ Range HTTP 206 & CORS
    if (streamUrl && (streamUrl.includes('r2.gamomephim.com') || streamUrl.includes('gamomephim')) && !streamUrl.includes('/api/proxy')) {
      streamUrl = `/api/proxy?url=${encodeURIComponent(streamUrl)}`;
    }

    // Tự động bảo vệ chống lỗi Mixed Content khi duyệt web trên HTTPS
    if (window.location.protocol === 'https:' && streamUrl.startsWith('http://') && !streamUrl.includes('/api/proxy')) {
      streamUrl = `/api/proxy?url=${encodeURIComponent(streamUrl)}`;
    }

    currentPlayingMovie = movie;
    window.currentPlayingMovie = movie;
    currentActiveStream = streamUrl;
    currentPlayingDetail = detail;
    currentEpisodeIndex = epIndex;
    currentServerIndex = serverIndex;
    updateSidebarAndControls(movie, detail, epIndex, serverIndex);
    updatePlayerFavIcon(isFavorite(movie.id));

    const container = document.getElementById('playerContainer');
    const miniBar = document.getElementById('miniPlayerBar');
    const video = document.getElementById('videoPlayer');
    if (container) {
      container.classList.remove('player-floating-mini');
      container.style.display = 'flex';
    }
    if (miniBar) miniBar.style.display = 'none';
    const curAsp = (aspectModes && aspectModes[currentAspectIdx]) ? aspectModes[currentAspectIdx].mode : 'contain';
    if (video) video.style.setProperty('object-fit', curAsp, 'important');
    pushNavigationState('player');

    const isDevicePortrait = (window.innerHeight > window.innerWidth);
    const isMobileDevice = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || (window.innerWidth <= 800);

    document.getElementById('playerTitle').textContent = title;
    document.getElementById('playerSub').textContent = subtitle;

    const zapBtn = document.getElementById('btnQuickZap');
    const nextBtn = document.getElementById('btnCenterNext') || document.getElementById('btnNextEpisode');
    const prevBtn = document.getElementById('btnCenterPrev') || document.getElementById('btnPrevEpisode');
    const progress = document.getElementById('progressContainer');
    const iframe = document.getElementById('playerIframe');
    const isEmbed = isEmbedStreamUrl(streamUrl);

    const isVerticalShortDrama = detail?.isShortDrama || movie?.isShortDrama || 
      (movie?.source === 'FREEREELS' && !isTv) || 
      (movie?.source === 'GAMOMEPHIM' && !isTv) ||
      (movie?.source === 'DRAMABOX') ||
      (movie?.source === 'REELSHORT') ||
      (movie?.source === 'SHORTMAX') ||
      (currentSource === 'FREEREELS' && !isTv);

    // TỰ ĐỘNG CHUYỂN HƯỚNG THEO PHIM: PHIM DỌC (9:16) VÀ PHIM NGANG (16:9)
    const rotateBtnText = document.getElementById('rotateBtnText');
    if (isVerticalShortDrama) {
      // Phim ngắn màn dọc (9:16): Tự động áp dụng chế độ dọc chuẩn TikTok/Reels!
      container.classList.remove('player-forced-landscape');
      container.classList.add('player-vertical-mode');
      if (rotateBtnText) rotateBtnText.textContent = 'Phim Dọc (9:16)';
      if (isMobileDevice) {
        try {
          if (screen.orientation && screen.orientation.lock) {
            screen.orientation.lock('portrait').catch(() => {});
          }
        } catch(e) {}
      }
    } else {
      // Phim ngang 16:9 (Phim lẻ, Phim bộ, Anime, Tivi)
      container.classList.remove('player-vertical-mode');
      if (isMobileDevice && isDevicePortrait) {
        container.classList.add('player-forced-landscape');
        if (rotateBtnText) rotateBtnText.textContent = 'Xoay Dọc';
        showToast(isTv ? '📺 Tự động chuyển màn hình ngang chuẩn Tivi' : '🎬 Tự động chuyển màn hình ngang chuẩn điện ảnh');
      } else {
        container.classList.remove('player-forced-landscape');
        if (rotateBtnText) rotateBtnText.textContent = 'Xoay Ngang';
      }
      if (isMobileDevice) {
        try {
          if (screen.orientation && screen.orientation.lock) {
            screen.orientation.lock('landscape').catch(() => {});
          } else if (screen.lockOrientation) {
            screen.lockOrientation('landscape');
          }
        } catch(e) {}
      }
    }

    if (isTv) {
      if (zapBtn) zapBtn.style.display = 'block';
      if (nextBtn) nextBtn.style.display = 'none';
      if (prevBtn) prevBtn.style.display = 'none';
      if (progress) progress.style.display = 'none';
    } else {
      if (zapBtn) zapBtn.style.display = 'none';
      if (progress) progress.style.display = 'flex';

      let totalEps = 0;
      if (detail && detail.episodes && detail.episodes[serverIndex || 0] && detail.episodes[serverIndex || 0].server_data) {
        totalEps = detail.episodes[serverIndex || 0].server_data.length;
      } else if (detail && detail.items) {
        totalEps = detail.items.length;
      }

      if (totalEps > 1) {
        if (prevBtn) {
          prevBtn.style.display = 'inline-flex';
          prevBtn.disabled = (epIndex <= 0);
          prevBtn.style.opacity = (epIndex <= 0) ? '0.35' : '1';
          prevBtn.style.pointerEvents = (epIndex <= 0) ? 'none' : 'auto';
        }
        if (nextBtn) {
          nextBtn.style.display = 'inline-flex';
          nextBtn.disabled = (epIndex >= totalEps - 1);
          nextBtn.style.opacity = (epIndex >= totalEps - 1) ? '0.35' : '1';
          nextBtn.style.pointerEvents = (epIndex >= totalEps - 1) ? 'none' : 'auto';
        }
      } else {
        if (prevBtn) prevBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
      }
    }

    // Lưu lại lịch sử xem của tập trước đó (nếu đang chuyển từ tập cũ sang tập mới)
    if (currentPlayingMovie && video && video.duration && typeof currentEpisodeIndex === 'number' && currentEpisodeIndex !== epIndex) {
      const oldSub = document.getElementById('playerSub')?.textContent;
      saveHistory(currentPlayingMovie, video.currentTime, video.duration, oldSub, currentEpisodeIndex);
    }

    // Reset video & HLS & DASH & Subtitles sạch sẽ
    if (hlsInstance) {
      try { hlsInstance.stopLoad(); hlsInstance.detachMedia(); hlsInstance.destroy(); } catch(e) {}
      hlsInstance = null;
    }
    if (dashInstance) {
      try { dashInstance.reset(); } catch(e) {}
      dashInstance = null;
    }
    video.pause();
    video.removeAttribute('src');
    video.src = '';
    video.querySelectorAll('track').forEach(t => t.remove());
    try { video.currentTime = 0; } catch(e) {}
    try { video.load(); } catch(e) {}

    // Cơ chế tự động thử link luồng dự phòng (Backup URLs) cho kênh TV nếu luồng chính lỗi:
    let currentBackupIdx = (movie && typeof movie._lastBackupIdx === 'number') ? movie._lastBackupIdx : 0;
    const tryNextTvBackup = () => {
      if (isTv && movie && Array.isArray(movie.backupUrls) && currentBackupIdx < movie.backupUrls.length) {
        const nextUrl = movie.backupUrls[currentBackupIdx];
        currentBackupIdx++;
        movie._lastBackupIdx = currentBackupIdx;
        showToast(`🔄 Đang chuyển sang luồng dự phòng ${currentBackupIdx}/${movie.backupUrls.length}...`);
        setTimeout(() => {
          playVideo(nextUrl, title, subtitle, movie, detail, epIndex, serverIndex, true, customSubtitleUrl, forceStartFromBeginning);
        }, 300);
        return true;
      }
      return false;
    };

    // Xác định chính xác vị trí bắt đầu phát:
    // NẾU LÀ TẬP MỚI (chuyển tập Next/Prev/chọn tập khác hoặc forceStartFromBeginning = true) -> targetStartTime BẮT BUỘC LÀ 0!
    // CHỈ khôi phục vị trí cũ NẾU ĐÚNG LÀ CÙNG 1 TẬP đang xem dở trước đó!
    let targetStartTime = 0;
    if (!isTv && !forceStartFromBeginning) {
      const hist = getHistory().find(h => h.id === movie.id);
      const isSameEpisode = hist && (
        (typeof hist.episodeIndex === 'number' && hist.episodeIndex === epIndex) ||
        (hist.episodeName && subtitle && hist.episodeName.trim().toLowerCase() === subtitle.trim().toLowerCase())
      );
      if (isSameEpisode && hist.currentSec > 10 && hist.durationSec && hist.currentSec < hist.durationSec - 30) {
        targetStartTime = hist.currentSec;
      }
    }

    if (isEmbed) {
      video.style.display = 'none';

      // NGUỒN C EMBED & ĐA TÊN MIỀN DỰ PHÒNG (CHỐNG LỖI DNS ERR_NAME_NOT_RESOLVED)
      const isNguonCEmbed = streamUrl.includes('streamc.xyz') || streamUrl.includes('embed.php?hash=');
      let currentEmbedUrl = streamUrl;
      const embedMirrors = [
        'embed17.streamc.xyz',
        'embed1.streamc.xyz',
        'embed2.streamc.xyz',
        'embed5.streamc.xyz',
        'embed18.streamc.xyz',
        'embed13.streamc.xyz',
        'embed14.streamc.xyz'
      ];
      let currentMirrorIdx = 0;

      if (isNguonCEmbed) {
        const hashMatch = streamUrl.match(/hash=([a-f0-9]+)/i);
        const hash = hashMatch ? hashMatch[1] : '';
        // Tự động chuyển đổi nếu là embed14 (thường bị nhà mạng VN lỗi DNS) sang embed17 hoặc embed1
        if (streamUrl.includes('embed14.streamc.xyz') && hash) {
          currentEmbedUrl = `https://embed17.streamc.xyz/embed.php?hash=${hash}`;
        }

        // Tạo hoặc cập nhật Embed Helper Toolbar trên Player (Bổ sung đầy đủ nút Thoát & Chọn Tập Phim)
        let helperBar = document.getElementById('embedHelperBar');
        if (!helperBar) {
          helperBar = document.createElement('div');
          helperBar.id = 'embedHelperBar';
          helperBar.className = 'embed-helper-bar';
          const mainArea = document.getElementById('playerMainArea') || container;
          if (mainArea) mainArea.appendChild(helperBar);
        }
        helperBar.style.display = 'flex';
        helperBar.innerHTML = `
          <button id="btnBackEmbed" class="btn-embed-action btn-embed-back focusable" title="Quay lại danh sách phim (Esc)">
            <span>↩️</span> Thoát
          </button>
          <button id="btnEpisodeSheetEmbed" class="btn-embed-action focusable" title="Mở danh sách tập phim & Server">
            <span>📑</span> Chọn Tập
          </button>
          <button id="btnSwitchEmbedMirror" class="btn-embed-action focusable" title="Chuyển sang Server Embed dự phòng khi bị lỗi DNS hoặc tải chậm">
            <span>🔄</span> Đổi Server
          </button>
          <button id="btnPopoutPlayer" class="btn-embed-action btn-popout-action focusable" title="Mở cửa sổ trình phát độc lập 16:9 sắc nét, sạch bóng quảng cáo">
            <span>🗔</span> Cửa Sổ Riêng
          </button>
          <button id="btnReloadEmbed" class="btn-embed-action focusable" title="Tải lại trình phát">
            <span>🔁</span> Tải Lại
          </button>
        `;

        const btnBackEmb = document.getElementById('btnBackEmbed');
        if (btnBackEmb) {
          btnBackEmb.onclick = (e) => {
            e.stopPropagation();
            closePlayer();
          };
        }

        const btnEpEmb = document.getElementById('btnEpisodeSheetEmbed');
        if (btnEpEmb) {
          btnEpEmb.onclick = (e) => {
            e.stopPropagation();
            const sheetBtn = document.getElementById('btnEpisodeSheetPlayer');
            if (sheetBtn) sheetBtn.click();
          };
        }

        const btnPop = document.getElementById('btnPopoutPlayer');
        if (btnPop) {
          btnPop.onclick = (e) => {
            e.stopPropagation();
            const w = Math.min(1280, window.screen.availWidth || 1200);
            const h = Math.min(720, window.screen.availHeight || 680);
            const left = Math.max(0, Math.floor((window.screen.availWidth - w) / 2));
            const top = Math.max(0, Math.floor((window.screen.availHeight - h) / 2));
            const popUrl = `/popout.html?stream=${encodeURIComponent(currentEmbedUrl)}&title=${encodeURIComponent(currentPlayingMovie ? currentPlayingMovie.name : 'Huy Cá')}`;
            const popWin = window.open(
              popUrl,
              'HuyCaCleanPlayer',
              `width=${w},height=${h},top=${top},left=${left},menubar=no,toolbar=no,location=no,status=no,resizable=yes,scrollbars=no`
            );
            if (popWin) {
              popWin.focus();
              showToast('🗔 Đã mở trình phát độc lập không quảng cáo!');
            }
          };
        }

        const btnSwitch = document.getElementById('btnSwitchEmbedMirror');
        if (btnSwitch) {
          btnSwitch.onclick = (e) => {
            e.stopPropagation();
            if (hash) {
              currentMirrorIdx = (currentMirrorIdx + 1) % embedMirrors.length;
              const nextDomain = embedMirrors[currentMirrorIdx];
              currentEmbedUrl = `https://${nextDomain}/embed.php?hash=${hash}`;
              if (iframe) iframe.src = currentEmbedUrl;
              // btnOpenEmbedNewTab đã được loại bỏ hoàn toàn để bảo vệ người dùng
              showToast(`🔄 Đang chuyển sang Server Embed dự phòng: ${nextDomain}...`);
            } else {
              showToast('⚠️ Không tìm thấy hash tập phim.');
            }
          };
        }

        const btnReload = document.getElementById('btnReloadEmbed');
        if (btnReload) {
          btnReload.onclick = (e) => {
            e.stopPropagation();
            if (iframe) iframe.src = currentEmbedUrl;
            showToast('🔁 Đang tải lại khung phát...');
          };
        }
      } else {
        const helperBar = document.getElementById('embedHelperBar');
        if (helperBar) helperBar.style.display = 'none';
      }

      if (iframe) {
        iframe.style.display = 'block';
        iframe.src = currentEmbedUrl;
      }
      if (progress) progress.style.display = 'none';
      return;
    } else {
      const helperBar = document.getElementById('embedHelperBar');
      if (helperBar) helperBar.style.display = 'none';
      if (iframe) {
        iframe.src = '';
        iframe.style.display = 'none';
      }
      video.style.display = 'block';
    }

    // Kiểm tra và đính kèm phụ đề qua #playerSubtitleOverlay (Chặn hoàn toàn lỗi chữ phụ đề to đè giữa màn hình)
    try {
      let subOverlay = document.getElementById('playerSubtitleOverlay');
      if (!subOverlay) {
        subOverlay = document.createElement('div');
        subOverlay.id = 'playerSubtitleOverlay';
        const mainArea = document.getElementById('playerMainArea') || document.getElementById('playerContainer');
        if (mainArea) mainArea.appendChild(subOverlay);
      }
      subOverlay.textContent = '';
      subOverlay.style.display = 'none';

      if (window._subTimeUpdateHandler) {
        video.removeEventListener('timeupdate', window._subTimeUpdateHandler);
        window._subTimeUpdateHandler = null;
      }
      video.querySelectorAll('track').forEach(t => t.remove());

      let currentEp = null;
      if (detail) {
        const sIdx = serverIndex || 0;
        if (detail.episodes && detail.episodes[sIdx] && detail.episodes[sIdx].server_data) {
          currentEp = detail.episodes[sIdx].server_data[epIndex];
        } else if (detail.items && detail.items[epIndex]) {
          currentEp = detail.items[epIndex];
        }
      }
      const subUrl = customSubtitleUrl || (currentEp && currentEp.subtitleUrl);
      if (subUrl) {
        video.crossOrigin = 'anonymous';
        let fetchUrl = subUrl;
        if (fetchUrl.startsWith('http') && !fetchUrl.includes('/api/proxy') && window.location.protocol.startsWith('http')) {
          fetchUrl = '/api/proxy?url=' + encodeURIComponent(fetchUrl);
        }

        fetch(fetchUrl)
          .then(r => r.text())
          .then(rawText => {
            if (!rawText || rawText.trim().length === 0) return;
            const parsedCues = parseSubtitleText(rawText);
            const vttContent = convertSrtToVtt(rawText);
            const blobUrl = URL.createObjectURL(new Blob([vttContent], { type: 'text/vtt' }));

            const track = document.createElement('track');
            track.kind = 'subtitles';
            track.srclang = 'vi';
            track.label = 'Tiếng Việt';
            track.src = blobUrl;
            track.default = true;
            video.appendChild(track);

            const bindHiddenTrack = () => {
              if (track.track) track.track.mode = 'hidden';
            };
            bindHiddenTrack();
            track.addEventListener('load', bindHiddenTrack);

            window._subTimeUpdateHandler = () => {
              if (!parsedCues || parsedCues.length === 0) return;
              const cur = video.currentTime;
              const matched = parsedCues.find(c => cur >= c.start && cur <= c.end);
              if (matched) {
                subOverlay.textContent = matched.text;
                subOverlay.style.display = 'block';
              } else {
                subOverlay.style.display = 'none';
              }
            };
            video.addEventListener('timeupdate', window._subTimeUpdateHandler);
          })
          .catch(e => {
            console.warn('Subtitle fetch/parse failed:', e);
          });
      } else {
        video.removeAttribute('crossorigin');
      }
    } catch (e) {
      console.warn('Subtitle attach warning:', e);
    }

    // Đảm bảo video luôn bắt đầu từ targetStartTime (0s cho tập mới, vị trí cũ cho tập xem dở)
    let hasEnforcedStartTime = false;
    const enforceStart = () => {
      if (hasEnforcedStartTime) return;
      hasEnforcedStartTime = true;
      try {
        if (targetStartTime === 0) {
          video.currentTime = 0;
        } else if (targetStartTime > 0 && video.duration && targetStartTime < video.duration - 15) {
          video.currentTime = targetStartTime;
          showToast(`⏱️ Tiếp tục xem từ ${formatTime(targetStartTime)} (${subtitle || 'tập trước'})`);
        }
      } catch(e) {}
    };

    video.addEventListener('loadedmetadata', enforceStart, { once: true });
    
    // TỰ ĐỘNG DÒ TỈ LỆ VIDEO THỰC TẾ TỪ LUỒNG STREAM ĐỂ ĐIỀU CHỈNH DỌC / NGANG CHÍNH XÁC 100%
    const detectOrientationFromVideo = () => {
      const vW = video.videoWidth || 0;
      const vH = video.videoHeight || 0;
      if (vW > 0 && vH > 0) {
        const isVideoVertical = (vH > vW);
        const playerCont = document.getElementById('playerContainer');
        const rotateText = document.getElementById('rotateBtnText');
        if (isVideoVertical) {
          if (playerCont) {
            playerCont.classList.remove('player-forced-landscape');
            playerCont.classList.add('player-vertical-mode');
          }
          if (rotateText) rotateText.textContent = 'Phim Dọc (9:16)';
          showToast('📱 Tự động nhận diện phim màn dọc (9:16) chuẩn Reels');
          if (isMobileDevice) {
            try { if (screen.orientation && screen.orientation.lock) screen.orientation.lock('portrait').catch(() => {}); } catch(e) {}
          }
        } else {
          if (playerCont) {
            playerCont.classList.remove('player-vertical-mode');
          }
          if (rotateText) {
            const isForced = playerCont && playerCont.classList.contains('player-forced-landscape');
            rotateText.textContent = isForced ? 'Xoay Dọc' : 'Xoay Ngang';
          }
        }
      }
    };
    video.addEventListener('loadedmetadata', detectOrientationFromVideo, { once: true });
    video.addEventListener('canplay', () => {
      if (targetStartTime === 0 && video.currentTime > 1) {
        try { video.currentTime = 0; } catch(e) {}
      }
    }, { once: true });

    if (window.Hls && Hls.isSupported() && (streamUrl.includes('.m3u8') || streamUrl.includes('type=nguonc') || streamUrl.includes('/api/nguonc_stream'))) {
      // 🚀 HLS.JS: Tương thích 100% với Windows PC, Edge Chromium & WebView2
      const pLoaderClass = getHlsPlaylistLoader();
      hlsInstance = new Hls({
        startPosition: targetStartTime, // 🚀 BẮT BUỘC: Hls.js luôn bắt đầu chính xác từ 0s nếu là tập mới!
        maxBufferLength: 30,
        maxMaxBufferLength: 60,
        maxBufferSize: 60 * 1024 * 1024,
        manifestLoadingTimeOut: 7000,
        manifestLoadingMaxRetry: 2,
        levelLoadingTimeOut: 7000,
        fragLoadingTimeOut: 10000,
        lowLatencyMode: false,
        enableWorker: true,
        ...(pLoaderClass ? { pLoader: pLoaderClass } : {})
      });
      hlsInstance.loadSource(streamUrl);
      hlsInstance.attachMedia(video);
      hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
        try {
          video.currentTime = targetStartTime;
        } catch(e) {}
        video.play().catch(e => {
          console.log('Play attempt error:', e);
        });
      });
      hlsInstance.on(Hls.Events.ERROR, (event, data) => {
        console.error('HLS ERROR:', data.type, data.details, data.fatal);
        if (data.fatal) {
          if (tryNextTvBackup()) {
            return;
          }
          if (data.type === Hls.ErrorTypes.NETWORK_ERROR && !streamUrl.includes('/api/proxy') && window.location.protocol.startsWith('http')) {
            showToast('🔄 Đang kết nối lại qua đường truyền tăng tốc...');
            setTimeout(() => {
              playVideo(`/api/proxy?url=${encodeURIComponent(streamUrl)}`, title, subtitle, movie, detail, epIndex, serverIndex, isTv, customSubtitleUrl, forceStartFromBeginning);
            }, 300);
            return;
          }
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              hlsInstance.startLoad();
              break;
            case Hls.ErrorTypes.MEDIA_ERROR:
              hlsInstance.recoverMediaError();
              break;
            default:
              hlsInstance.destroy();
              break;
          }
        }
      });
    } else if (streamUrl.includes('.mpd')) {
      // 🚀 MPEG-DASH (.mpd) Player qua Dash.js (Chặn đứng 100% popup download file)
      if (window.dashjs) {
        try {
          dashInstance = dashjs.MediaPlayer().create();
          dashInstance.initialize(video, streamUrl, true);
          dashInstance.on(dashjs.MediaPlayer.events.ERROR, (err) => {
            console.warn('DASH ERROR:', err);
            if (tryNextTvBackup()) return;
            showToast('⚠️ Luồng DASH yêu cầu bản quyền DRM hoặc không khả dụng.');
          });
        } catch (err) {
          if (!tryNextTvBackup()) {
            showToast('⚠️ Lỗi khởi tạo trình phát DASH.');
          }
        }
      } else {
        if (!tryNextTvBackup()) {
          showToast('⚠️ Định dạng MPD cần thư viện Dash.js hoặc chuyển sang kênh khác.');
        }
      }
    } else if (isNativeWebOS && streamUrl.includes('.m3u8')) {
      // 🚀 Dành riêng cho TV LG webOS Native
      video.src = streamUrl;
      video.load();
      enforceStart();
      video.play().catch(e => console.log('Native auto play blocked:', e));
    } else {
      video.onerror = () => {
        if (tryNextTvBackup()) return;
        if (isTv) showToast('⚠️ Không thể tải kênh truyền hình này. Vui lòng chọn kênh khác!');
      };
      video.src = streamUrl;
      video.load();
      enforceStart();
      video.play().catch(e => console.log('Auto play blocked:', e));
    }

    resetOverlayTimer();
    showToast(`Đang phát: ${title}`);
    const isIosDevice = /iPhone|iPad|iPod/i.test(navigator.userAgent);
    const isShortMovie = (currentPlayingMovie && (currentPlayingMovie.isShortDrama || currentPlayingMovie.source === 'FREEREELS' || currentPlayingMovie.source === 'gamomephim'));
    if (isIosDevice && window.innerHeight > window.innerWidth && !isShortMovie) {
      setTimeout(() => {
        showToast('💡 Mẹo iPhone: Bấm nút "🔄 Xoay Ngang" hoặc tắt Khóa Hướng Dọc rồi xoay ngang máy!');
      }, 2000);
    }

    // Tự động focus nút Play/Pause trong player
    setTimeout(() => {
      const playBtn = document.getElementById('btnPlayPause');
      if (playBtn) setFocus(playBtn);
    }, 100);
  }

  // --- Player Controls ---
  const video = document.getElementById('videoPlayer');
  const seekBar = document.getElementById('seekBar');
  const currentTimeLabel = document.getElementById('currentTime');
  const durationTimeLabel = document.getElementById('durationTime');
  const btnPlayPause = document.getElementById('btnPlayPause') || document.getElementById('btnCenterPlayPause');

  video.addEventListener('timeupdate', () => {
    if (video.duration) {
      const cur = video.currentTime;
      const dur = video.duration;
      seekBar.value = (cur / dur) * 100;
      currentTimeLabel.textContent = formatTime(cur);

      // Tự động hiện nút Bỏ qua Intro (+85s) chỉ cho phim dài (> 5 phút), ẩn trên Phim Ngắn
      const btnSkip = document.getElementById('btnSkipIntro');
      if (btnSkip) {
        const isShortEp = (dur < 300) || (currentPlayingMovie && (currentPlayingMovie.isShortDrama || currentPlayingMovie.source === 'FREEREELS'));
        if (!isShortEp && cur >= 1 && cur <= 95) {
          btnSkip.style.display = 'block';
        } else {
          btnSkip.style.display = 'none';
        }
      }

      durationTimeLabel.textContent = formatTime(dur);

      // Auto save history every 10 seconds (chỉ lưu khi đã xem qua 5 giây đầu để tránh ghi đè nhầm thời gian cũ khi vừa chuyển tập)
      if (cur >= 5 && Math.round(cur) % 10 === 0 && currentPlayingMovie) {
        saveHistory(currentPlayingMovie, cur, dur, document.getElementById('playerSub').textContent, currentEpisodeIndex);
      }
    }
  });

  video.addEventListener('ended', () => {
    showToast('Tự động phát tập tiếp theo trong 3s...');
    setTimeout(() => {
      playNextEpisode();
    }, 3000);
  });

  seekBar.addEventListener('input', () => {
    if (video.duration) {
      video.currentTime = (seekBar.value / 100) * video.duration;
    }
  });

  // --- Centralized Video Play/Pause Controller ---
  function togglePlayPause() {
    const v = document.getElementById('videoPlayer');
    if (!v) return;
    if (v.paused) {
      v.play().catch(err => {
        console.warn('Play was prevented:', err);
      });
      updatePlayPauseIcons(true);
    } else {
      v.pause();
      updatePlayPauseIcons(false);
    }
    resetOverlayTimer();
  }
  window.togglePlayPause = togglePlayPause;

  // --- Centralized Episode Navigation ---
  async function playPrevEpisode() {
    if (!currentPlayingDetail) {
      showToast('Đây là tập đầu tiên!');
      return;
    }
    let eps = [];
    if (currentPlayingDetail.episodes && currentPlayingDetail.episodes.length > 0) {
      const srv = currentPlayingDetail.episodes[currentServerIndex || 0] || currentPlayingDetail.episodes[0];
      eps = (srv && srv.server_data) || [];
    } else if (currentPlayingDetail.items && currentPlayingDetail.items.length > 0) {
      eps = currentPlayingDetail.items;
    }

    if (currentEpisodeIndex > 0 && eps.length > 0) {
      const prevEp = eps[currentEpisodeIndex - 1];
      if (!prevEp) return;
      let stream = prevEp.link_m3u8 || prevEp.m3u8 || prevEp.embed || prevEp.url;
      let sub = prevEp.subtitleUrl;
      if (stream && stream.startsWith('freereels_unlock:')) {
        showToast('🔓 Đang mở khóa tập trước...');
        const seriesId = (currentPlayingMovie.id || '').replace('freereels:', '');
        const unl = await FreeReelsClient.unlockEpisode(seriesId, prevEp.slug);
        if (unl && unl.streamUrl) {
          stream = unl.streamUrl;
          if (unl.subtitleUrl) sub = unl.subtitleUrl;
        }
      }
      showToast(`⏮️ Đang chuyển về ${prevEp.name || `Tập ${currentEpisodeIndex}`}`);
      playVideo(stream, currentPlayingMovie.name, prevEp.name, currentPlayingMovie, currentPlayingDetail, currentEpisodeIndex - 1, currentServerIndex || 0, false, sub, true);
    } else {
      showToast('Đây là tập đầu tiên!');
    }
  }
  window.playPrevEpisode = playPrevEpisode;

  async function playNextEpisode() {
    if (!currentPlayingDetail) {
      showToast('Đây là tập cuối cùng!');
      return;
    }
    let eps = [];
    if (currentPlayingDetail.episodes && currentPlayingDetail.episodes.length > 0) {
      const srv = currentPlayingDetail.episodes[currentServerIndex || 0] || currentPlayingDetail.episodes[0];
      eps = (srv && srv.server_data) || [];
    } else if (currentPlayingDetail.items && currentPlayingDetail.items.length > 0) {
      eps = currentPlayingDetail.items;
    }

    if (currentEpisodeIndex + 1 < eps.length) {
      const nextEp = eps[currentEpisodeIndex + 1];
      if (!nextEp) return;
      let stream = nextEp.link_m3u8 || nextEp.m3u8 || nextEp.embed || nextEp.url;
      let sub = nextEp.subtitleUrl;
      if (stream && stream.startsWith('freereels_unlock:')) {
        showToast('🔓 Đang mở khóa tập tiếp theo...');
        const seriesId = (currentPlayingMovie.id || '').replace('freereels:', '');
        const unl = await FreeReelsClient.unlockEpisode(seriesId, nextEp.slug);
        if (unl && unl.streamUrl) {
          stream = unl.streamUrl;
          if (unl.subtitleUrl) sub = unl.subtitleUrl;
        }
      }
      showToast(`⏭️ Đang chuyển sang ${nextEp.name || `Tập ${currentEpisodeIndex + 2}`}`);
      playVideo(stream, currentPlayingMovie.name, nextEp.name, currentPlayingMovie, currentPlayingDetail, currentEpisodeIndex + 1, currentServerIndex || 0, false, sub, true);
    } else {
      showToast('Đây là tập cuối cùng!');
    }
  }
  window.playNextEpisode = playNextEpisode;
  window.getCurrentEpisodeIndex = () => currentEpisodeIndex;

  // Nút Quay Lại trong Player (Thoát hoàn toàn player và khôi phục giao diện trước)
  const btnBackPlayer = document.getElementById('btnBackPlayer');
  if (btnBackPlayer) {
    btnBackPlayer.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      closePlayer(true, true);
    });
  }

  function updatePlayerFavIcon(isFav) {
    const star = document.getElementById('svgStarFav');
    const btn = document.getElementById('btnToggleFavPlayer');
    if (star) {
      star.style.color = isFav ? '#eab308' : '#94a3b8';
      star.style.fill = isFav ? '#eab308' : 'currentColor';
    }
    if (btn) {
      btn.classList.toggle('active', Boolean(isFav));
      btn.setAttribute('title', isFav ? 'Bỏ Yêu thích' : 'Thêm vào Yêu thích');
    }
  }

  const btnFavPlayer = document.getElementById('btnToggleFavPlayer');
  if (btnFavPlayer) {
    btnFavPlayer.addEventListener('click', (e) => {
      e.stopPropagation();
      if (currentPlayingMovie) {
        const added = toggleFavorite(currentPlayingMovie);
        updatePlayerFavIcon(added);
      }
    });
  }

  const btnFullscreen = document.getElementById('btnFullscreen');
  if (btnFullscreen) {
    btnFullscreen.addEventListener('click', () => {
      const container = document.getElementById('playerContainer');
      const video = document.getElementById('videoPlayer');

      // Tối ưu cho iPhone / iOS Safari: Dùng webkitEnterFullscreen của thẻ video
      if (video && video.webkitEnterFullscreen) {
        try {
          video.webkitEnterFullscreen();
          return;
        } catch(e) {}
      }

      if (!document.fullscreenElement && !document.webkitFullscreenElement) {
        const req = container.requestFullscreen || container.webkitRequestFullscreen || container.mozRequestFullScreen || container.msRequestFullscreen;
        if (req) {
          req.call(container).catch(() => {});
        }
      } else {
        const exit = document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen || document.msExitFullscreen;
        if (exit) {
          exit.call(document).catch(() => {});
        }
      }
    });
  }

  // Đồng bộ biểu tượng toàn màn hình khi trạng thái thay đổi
  document.addEventListener('fullscreenchange', () => {
    const isFs = !!(document.fullscreenElement || document.webkitFullscreenElement);
    const enterSvg = document.getElementById('svgFullscreenEnter');
    const exitSvg = document.getElementById('svgFullscreenExit');
    if (enterSvg) enterSvg.style.display = isFs ? 'none' : 'block';
    if (exitSvg) exitSvg.style.display = isFs ? 'block' : 'none';
  });

  // --- Bấm chuột vào vùng trống ngoài màn hình tương đương nút quay lại, back ---
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        if (modal.id === 'detailModal') {
          if (history.state && history.state.screen === 'detail') {
            history.back();
          } else {
            const btn = document.getElementById('btnCloseDetail');
            if (btn) btn.click();
            else modal.style.display = 'none';
          }
        } else if (modal.id === 'searchModal') {
          const btn = document.getElementById('btnCloseSearch');
          if (btn) btn.click();
          else modal.style.display = 'none';
        } else if (modal.id === 'scheduleModal') {
          const btn = document.getElementById('btnCloseSchedule');
          if (btn) btn.click();
          else modal.style.display = 'none';
        } else if (modal.id === 'iptvModal') {
          const btn = document.getElementById('btnCloseIptv');
          if (btn) btn.click();
          else modal.style.display = 'none';
        } else if (modal.id === 'matchServerModal') {
          modal.style.display = 'none';
        } else {
          modal.style.display = 'none';
        }
      }
    });
  });

  // --- Chế độ Hình Trong Hình / Floating Mini Player (v2.9.2) ---
  function enableMiniFloatingPlayer() {
    const container = document.getElementById('playerContainer');
    const miniBar = document.getElementById('miniPlayerBar');
    const miniTitle = document.getElementById('miniPlayerTitle');
    const playerTitle = document.getElementById('playerTitle');
    if (!container) return;

    container.classList.remove('player-forced-landscape');
    container.classList.add('player-floating-mini');
    container.style.display = 'flex';

    if (miniBar) miniBar.style.display = 'flex';
    if (miniTitle && playerTitle) miniTitle.textContent = playerTitle.textContent;

    // Đóng detailModal để người dùng thoải mái duyệt kho phim & nội dung khác
    const detail = document.getElementById('detailModal');
    if (detail) detail.style.display = 'none';

    showToast('📺 Đang phát ở chế độ Hình Trong Hình (Mini Player)');
  }

  function disableMiniFloatingPlayer(stopPlayback = true) {
    const container = document.getElementById('playerContainer');
    const miniBar = document.getElementById('miniPlayerBar');
    if (container) {
      container.classList.remove('player-floating-mini');
    }
    if (miniBar) miniBar.style.display = 'none';
    if (stopPlayback) {
      closePlayerDirect(false);
    }
  }

  function closePlayer(shouldReturnToDetail = true, forceStop = true) {
    const video = document.getElementById('videoPlayer');
    // Chỉ chuyển sang Mini Floating Player nếu người dùng KHÔNG yêu cầu dừng hẳn (forceStop === false)
    if (!forceStop && video && !video.paused && !video.ended && (video.currentTime > 0)) {
      if (document.pictureInPictureElement === video) {
        // Đang ở Native PiP: Chỉ ẩn container chính, giữ nguyên luồng video chạy
        const container = document.getElementById('playerContainer');
        if (container) {
          container.style.display = 'none';
          container.classList.remove('player-forced-landscape');
        }
        return;
      }
      enableMiniFloatingPlayer();
      return;
    }
    closePlayerDirect(shouldReturnToDetail);
  }

  function closePlayerDirect(shouldReturnToDetail = true) {
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    }
    if (screen.orientation && screen.orientation.unlock) {
      screen.orientation.unlock();
    }
    const subOv = document.getElementById('playerSubtitleOverlay');
    if (subOv) {
      subOv.textContent = '';
      subOv.style.display = 'none';
    }
    if (video) {
      if (currentPlayingMovie && video.duration) {
        saveHistory(currentPlayingMovie, video.currentTime, video.duration, document.getElementById('playerSub').textContent, currentEpisodeIndex);
      }
      video.pause();
      video.removeAttribute('src');
      video.querySelectorAll('track').forEach(t => t.remove());
      video.load();
    }
    if (hlsInstance) {
      hlsInstance.destroy();
      hlsInstance = null;
    }
    if (dashInstance) {
      try { dashInstance.reset(); } catch(e) {}
      dashInstance = null;
    }
    const iframe = document.getElementById('playerIframe');
    if (iframe) {
      iframe.src = '';
      iframe.style.display = 'none';
    }
    const helperBar = document.getElementById('embedHelperBar');
    if (helperBar) helperBar.style.display = 'none';
    const playerCont = document.getElementById('playerContainer');
    if (playerCont) {
      playerCont.style.display = 'none';
      playerCont.classList.remove('player-forced-landscape');
      playerCont.classList.remove('player-vertical-mode');
      playerCont.classList.remove('player-floating-mini');
    }
    const miniBar = document.getElementById('miniPlayerBar');
    if (miniBar) miniBar.style.display = 'none';
    const rotateBtnText = document.getElementById('rotateBtnText');
    if (rotateBtnText) rotateBtnText.textContent = 'Xoay Ngang';
    document.getElementById('zappingPanel').classList.remove('open');

    // Nếu vừa xem phim từ màn hình chi tiết, mở lại Detail Modal
    if (shouldReturnToDetail && currentPlayingDetail && currentPlayingMovie && currentPlayingMovie.source !== 'XEMTIVI') {
      const modal = document.getElementById('detailModal');
      modal.style.display = 'flex';
      setTimeout(() => {
        const epBtns = modal.querySelectorAll('.btn-episode');
        if (epBtns && epBtns[currentEpisodeIndex]) {
          setFocus(epBtns[currentEpisodeIndex]);
        } else {
          const firstBtn = modal.querySelector('.btn-primary-yellow') || document.getElementById('btnCloseDetail');
          if (firstBtn) setFocus(firstBtn);
        }
      }, 50);
    } else {
      // Với TV hoặc không có detail, quay về Grid và focus lại kênh
      setTimeout(() => {
        focusCurrentOrFirstMovie();
      }, 50);
    }
  }

  // --- Quick Zapping ---
  function setupQuickZapping(currentChannel) {
    const panel = document.getElementById('zappingList');
    panel.innerHTML = '';
    const all = getAllChannels();
    const groupChannels = all.filter(c => (c.group || '') === (currentChannel.group || ''));
    const list = groupChannels.length > 0 ? groupChannels : all;

    list.forEach(ch => {
      const item = document.createElement('div');
      item.className = `zapping-item focusable ${ch.id === currentChannel.id ? 'active' : ''}`;
      item.innerHTML = `
        <img class="zapping-logo" src="${ch.logo || DEFAULT_TV_LOGO}" onerror="this.src='${DEFAULT_TV_LOGO}'">
        <span class="zapping-name">${ch.name}</span>
      `;
      item.addEventListener('click', () => {
        document.getElementById('zappingPanel').classList.remove('open');
        playTvChannelDirectly({
          id: ch.id,
          name: ch.name,
          streamUrl: ch.url,
          group: ch.group,
          posterUrl: ch.logo
        });
      });
      panel.appendChild(item);
    });
  }

  const btnQuickZapEl = document.getElementById('btnQuickZap');
  if (btnQuickZapEl) {
    btnQuickZapEl.addEventListener('click', () => {
      const zp = document.getElementById('zappingPanel');
      if (zp) zp.classList.toggle('open');
    });
  }
  document.getElementById('btnCloseZap').addEventListener('click', () => {
    document.getElementById('zappingPanel').classList.remove('open');
  });

  // --- Remote Number Quick Zapping (0-9) ---
  function handleNumberZap(numStr) {
    numberZapBuffer += numStr;
    clearTimeout(numberZapTimeout);
    showToast(`Nhảy tới kênh số: ${numberZapBuffer}...`);

    numberZapTimeout = setTimeout(() => {
      const channelIndex = parseInt(numberZapBuffer, 10) - 1;
      numberZapBuffer = '';
      const all = getAllChannels();
      if (channelIndex >= 0 && channelIndex < all.length) {
        const target = all[channelIndex];
        playTvChannelDirectly({
          id: target.id,
          name: target.name,
          streamUrl: target.url,
          group: target.group,
          posterUrl: target.logo
        });
      } else {
        showToast('Số kênh không hợp lệ!');
      }
    }, 1200);
  }

  function renderScheduleCards(container, matches, modal) {
    if (!container) return;
    container.innerHTML = '';
    matches.forEach(m => {
      const card = document.createElement('div');
      card.className = 'match-card focusable';
      card.tabIndex = 0;
      card.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px;">
          ${m.teamALogo ? `<img src="${m.teamALogo}" style="width:24px; height:24px; object-fit:contain;" onerror="this.style.display='none'" />` : ''}
          <div>
            <div class="match-league">${m.tournament || 'Trực Tiếp Bóng Đá'}</div>
            <div class="match-teams">${m.teamA} vs ${m.teamB}</div>
            <div class="match-channel">📺 Kênh: ${m.channelName || 'Vệ Tinh Trực Tiếp'} • Bấm để xem</div>
          </div>
          ${m.teamBLogo ? `<img src="${m.teamBLogo}" style="width:24px; height:24px; object-fit:contain; margin-left:auto;" onerror="this.style.display='none'" />` : ''}
        </div>
        <div class="match-time-badge" style="${m.isLive ? 'background:#d32f2f;' : (m.isFinished ? 'background:#37474f;' : '')}">${m.time || 'Trực Tiếp'}</div>
      `;
      card.addEventListener('click', () => {
        modal.style.display = 'none';
        openMatchServerModal(m);
      });
      container.appendChild(card);
    });
  }

  // --- Football Matches Modal ---
  async function showScheduleModal() {
    const modal = document.getElementById('scheduleModal');
    const list = document.getElementById('matchesList');
    if (!modal || !list) return;

    // Render ngay lập tức dữ liệu LIVE_MATCHES để không bao giờ bị chờ đợi hay treo trắng
    renderScheduleCards(list, LIVE_MATCHES, modal);
    modal.style.display = 'flex';

    // Cập nhật ngầm từ API thời gian thực
    const matches = await fetchRealtimePremierLeagueMatches();
    if (matches && matches.length > 0) {
      renderScheduleCards(list, matches, modal);
    }
  }

  document.getElementById('btnScheduleHeader').addEventListener('click', showScheduleModal);
  document.getElementById('btnCloseSchedule').addEventListener('click', () => {
    document.getElementById('scheduleModal').style.display = 'none';
  });

  // --- Custom IPTV Modal ---
  function showIptvModal() {
    document.getElementById('iptvModal').style.display = 'flex';
  }
  document.getElementById('btnCloseIptv').addEventListener('click', () => {
    document.getElementById('iptvModal').style.display = 'none';
  });
  document.getElementById('btnAddIptvConfirm').addEventListener('click', () => {
    const name = document.getElementById('iptvName').value.trim();
    const url = document.getElementById('iptvUrl').value.trim();
    if (!name || !url) {
      showToast('Vui lòng nhập đầy đủ tên kênh và link m3u8!');
      return;
    }
    const customs = getCustomChannels();
    customs.unshift({
      id: `custom_${Date.now()}`,
      name: name,
      url: url,
      group: 'Kênh Tự Thêm',
      logo: DEFAULT_TV_LOGO
    });
    localStorage.setItem('huycabuonca_custom_iptv', JSON.stringify(customs));
    document.getElementById('iptvModal').style.display = 'none';
    showToast(`Đã thêm kênh "${name}" thành công!`);
    loadMovies(true);
  });

  // --- Search Modal ---
  document.getElementById('btnSearch').addEventListener('click', () => {
    document.getElementById('searchModal').style.display = 'flex';
    document.getElementById('searchInput').focus();
  });
  document.getElementById('btnCloseSearch').addEventListener('click', () => {
    document.getElementById('searchModal').style.display = 'none';
  });
  document.getElementById('btnDoSearch').addEventListener('click', doSearch);
  document.getElementById('searchInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') doSearch();
  });

  async function doSearch() {
    const kw = document.getElementById('searchInput').value.trim();
    if (!kw) return;
    const resGrid = document.getElementById('searchResultsGrid');
    resGrid.innerHTML = '<div style="color: #94a3b8; padding: 20px;">Đang tìm kiếm...</div>';

    let results = [];
    // 1. Search in TV
    const tvMatches = getAllChannels().filter(c => (c.name || '').toLowerCase().includes(kw.toLowerCase()) || (c.group || '').toLowerCase().includes(kw.toLowerCase()));
    tvMatches.forEach(c => {
      results.push({
        id: c.id,
        name: c.name,
        slug: c.id,
        originName: `[${c.group || 'Kênh TV'}]`,
        thumbUrl: c.logo || DEFAULT_TV_LOGO,
        posterUrl: c.logo || DEFAULT_TV_LOGO,
        quality: 'LIVE',
        source: 'XEMTIVI',
        streamUrl: c.url
      });
    });

    // Chạy song song tìm kiếm trên tất cả các nguồn trực tuyến (KKPhim, NguonC, FreeReels, GaMoMePhim)
    await Promise.allSettled([
      // 1.5. GaMoMePhim
      (async () => {
        try {
          const gmResults = await GaMoMePhimClient.search(kw);
          if (gmResults && gmResults.length > 0) results.push(...gmResults);
        } catch (e) {}
      })(),
      // 2. FreeReels
      (async () => {
        try {
          const frResults = await FreeReelsClient.search(kw);
          if (frResults && frResults.length > 0) results.push(...frResults);
        } catch (e) {}
      })(),
      // 3. NguonC
      (async () => {
        try {
          const respNc = await fetch(`https://phim.nguonc.com/api/films/search?keyword=${encodeURIComponent(kw)}`);
          if (respNc.ok) {
            const dNc = await respNc.json();
            const itemsNc = dNc.items || [];
            itemsNc.forEach(o => {
              let thumb = o.thumb_url || '';
              let poster = o.poster_url || thumb;
              results.push({
                id: `nguonc:${o.slug}`,
                name: o.name,
                slug: `nguonc:${o.slug}`,
                originName: o.original_name || o.origin_name || '',
                thumbUrl: thumb,
                posterUrl: poster || thumb,
                year: o.year || '2026',
                quality: (o.quality || 'HD') + (o.language ? ` ${o.language}` : ''),
                source: 'KKPHIM'
              });
            });
          }
        } catch (e) {}
      })(),
      // 4. KKPhim
      (async () => {
        try {
          const resp = await fetch(`https://phimapi.com/v1/api/tim-kiem?keyword=${encodeURIComponent(kw)}`);
          if (resp.ok) {
            const d = await resp.json();
            const items = (d.data && d.data.items) || [];
            items.forEach(o => {
              let thumb = o.thumb_url || '';
              if (thumb && !thumb.startsWith('http')) thumb = KKPHIM_IMG_BASE + thumb.replace(/^\//, '');
              results.push({
                id: o._id || o.slug,
                name: o.name,
                slug: o.slug,
                originName: o.origin_name || '',
                thumbUrl: thumb,
                posterUrl: thumb,
                year: o.year || '2026',
                quality: o.quality || 'HD',
                source: 'KKPHIM'
              });
            });
          }
        } catch (e) {}
      })()
    ]);

    resGrid.innerHTML = '';
    if (results.length === 0) {
      resGrid.innerHTML = '<div style="color: #94a3b8; padding: 20px;">Không tìm thấy nội dung phù hợp.</div>';
      return;
    }

    results.forEach(m => {
      const card = document.createElement('div');
      card.className = 'movie-card focusable';
      card.tabIndex = 0;
      card.innerHTML = `
        <div class="poster-wrapper" style="height: 180px;">
          <img class="card-poster" src="${m.posterUrl || DEFAULT_TV_LOGO}" onerror="this.src='${DEFAULT_TV_LOGO}'">
          <div class="badge-quality">${m.quality || 'HD'}</div>
        </div>
        <div class="card-info">
          <div class="card-title">${m.name}</div>
          <div class="card-subtitle">${m.originName || ''}</div>
        </div>
      `;
      card.addEventListener('click', () => {
        document.getElementById('searchModal').style.display = 'none';
        if (m.source === 'XEMTIVI') {
          playTvChannelDirectly(m);
        } else {
          openMovieDetail(m);
        }
      });
      resGrid.appendChild(card);
    });
  }

  // --- Favorite & History Header Buttons ---
  document.getElementById('btnFavHeader').addEventListener('click', () => {
    currentFilter = 'app://favorites';
    loadMovies(true);
  });
  const btnHistoryHeaderEl = document.getElementById('btnHistoryHeader');
  if (btnHistoryHeaderEl) {
    btnHistoryHeaderEl.addEventListener('click', () => {
      const isMobile = window.innerWidth <= 800 || document.body.classList.contains('mode-mobile');
      if (isMobile) {
        if (currentFilter === 'app://history') {
          currentFilter = '';
          showToast('Đang trở về danh sách phim...');
        } else {
          currentFilter = 'app://history';
          showToast('🕒 Đang hiển thị Lịch Sử Xem...');
        }
        currentPage = 1;
        loadMovies(true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        const sec = document.getElementById('historySection');
        if (sec) {
          if (sec.style.display === 'none') {
            sec.style.display = 'block';
            sec.scrollIntoView({ behavior: 'smooth' });
          } else {
            sec.style.display = 'none';
          }
        }
      }
    });
  }
  const btnUpdateHeader = document.getElementById('btnUpdateHeader');
  if (btnUpdateHeader) {
    btnUpdateHeader.addEventListener('click', () => {
      showToast('Đang kiểm tra bản cập nhật mới...');
      if (window.chrome && window.chrome.webview) {
        window.chrome.webview.postMessage('check_update');
      } else {
        showToast('Tính năng cập nhật khả dụng trên ứng dụng Huy Cá Windows!');
      }
    });
  }

  // --- Spatial Navigation 2D Engine for LG Remote & Smart TV ---
  function setFocus(el) {
    if (!el) return;
    if (currentFocusedElement && currentFocusedElement !== el) {
      currentFocusedElement.classList.remove('focused');
    }
    currentFocusedElement = el;
    el.classList.add('focused');
    try {
      el.focus();
    } catch (e) {}
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
  }

  function getActiveScope() {
    const zap = document.getElementById('zappingPanel');
    if (zap && zap.classList.contains('open')) return zap;

    const player = document.getElementById('playerContainer');
    if (player && player.style.display === 'flex') return player;

    const search = document.getElementById('searchModal');
    if (search && search.style.display === 'flex') return search;

    const detail = document.getElementById('detailModal');
    if (detail && detail.style.display === 'flex') return detail;

    const sched = document.getElementById('scheduleModal');
    if (sched && sched.style.display === 'flex') return sched;

    const iptv = document.getElementById('iptvModal');
    if (iptv && iptv.style.display === 'flex') return iptv;

    const inst = document.getElementById('installPlatformModal');
    if (inst && inst.style.display === 'flex') return inst;

    return document.body;
  }

  function getFocusableCandidates(scope) {
    const candidates = Array.from(scope.querySelectorAll('.focusable, button:not([disabled]), input:not([disabled]), [tabindex="0"]'));
    return candidates.filter(el => {
      if (el.disabled || el.getAttribute('aria-hidden') === 'true') return false;
      const rect = el.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) return false;
      const style = window.getComputedStyle(el);
      return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
    });
  }

  function focusCurrentOrFirstMovie() {
    const scope = getActiveScope();
    const candidates = getFocusableCandidates(scope);
    if (candidates.length === 0) return;

    if (currentPlayingMovie) {
      const match = candidates.find(c => c.dataset && c.dataset.id === currentPlayingMovie.id);
      if (match) {
        setFocus(match);
        return;
      }
    }
    const firstCard = scope.querySelector('.movie-card') || candidates[0];
    if (firstCard) setFocus(firstCard);
  }

  function navigate2D(direction) {
    const scope = getActiveScope();
    const isPlayerActive = scope.id === 'playerContainer';

    // Xử lý riêng khi đang ở màn hình Video Player
    if (isPlayerActive) {
      const overlay = document.getElementById('playerOverlay');
      const isOverlayHidden = overlay.classList.contains('hide');

      if (direction === 'left') {
        video.currentTime = Math.max(0, video.currentTime - 10);
        resetOverlayTimer();
        showToast('⏪ -10 giây');
        return;
      }
      if (direction === 'right') {
        video.currentTime = Math.min(video.duration || 0, video.currentTime + 10);
        resetOverlayTimer();
        showToast('⏩ +10 giây');
        return;
      }
      if (isOverlayHidden) {
        resetOverlayTimer();
        const playBtn = document.getElementById('btnPlayPause');
        if (playBtn) setFocus(playBtn);
        return;
      }
    }

    const candidates = getFocusableCandidates(scope);
    if (candidates.length === 0) return;

    let current = document.activeElement;
    if (!current || !scope.contains(current) || current === document.body) {
      current = currentFocusedElement && scope.contains(currentFocusedElement) ? currentFocusedElement : candidates[0];
      setFocus(current);
      return;
    }

    const rect1 = current.getBoundingClientRect();
    const c1 = {
      x: rect1.left + rect1.width / 2,
      y: rect1.top + rect1.height / 2
    };

    let bestCandidate = null;
    let minScore = Infinity;

    for (let i = 0; i < candidates.length; i++) {
      const cand = candidates[i];
      if (cand === current) continue;

      const rect2 = cand.getBoundingClientRect();
      const c2 = {
        x: rect2.left + rect2.width / 2,
        y: rect2.top + rect2.height / 2
      };

      const dx = c2.x - c1.x;
      const dy = c2.y - c1.y;

      let isValidDirection = false;
      let primaryDist = 0;
      let secondaryDist = 0;

      if (direction === 'up') {
        if (rect2.bottom <= rect1.top + 8 || dy < -8) {
          isValidDirection = true;
          primaryDist = -dy;
          secondaryDist = Math.abs(dx);
        }
      } else if (direction === 'down') {
        if (rect2.top >= rect1.bottom - 8 || dy > 8) {
          isValidDirection = true;
          primaryDist = dy;
          secondaryDist = Math.abs(dx);
        }
      } else if (direction === 'left') {
        if (rect2.right <= rect1.left + 8 || dx < -8) {
          isValidDirection = true;
          primaryDist = -dx;
          secondaryDist = Math.abs(dy);
        }
      } else if (direction === 'right') {
        if (rect2.left >= rect1.right - 8 || dx > 8) {
          isValidDirection = true;
          primaryDist = dx;
          secondaryDist = Math.abs(dy);
        }
      }

      if (isValidDirection) {
        // Trọng số phạt cho khoảng cách trục phụ để ưu tiên phần tử thẳng hàng
        const score = primaryDist + (secondaryDist * 2.2);
        if (score < minScore) {
          minScore = score;
          bestCandidate = cand;
        }
      }
    }

    if (bestCandidate) {
      setFocus(bestCandidate);
    }
  }

  // --- Multi-tiered Back Button Handler ---
  function handleBackAction(e) {
    if (e && typeof e.preventDefault === 'function') {
      e.preventDefault();
      e.stopPropagation();
    }

    const zap = document.getElementById('zappingPanel');
    const player = document.getElementById('playerContainer');
    const detail = document.getElementById('detailModal');
    const sched = document.getElementById('scheduleModal');
    const iptv = document.getElementById('iptvModal');
    const search = document.getElementById('searchModal');

    // Đóng Match Web Player nếu đang mở
    const matchWebPlayer = document.getElementById('matchWebPlayerContainer');
    if (matchWebPlayer && matchWebPlayer.style.display === 'block') {
      closeMatchWebPlayer();
      return;
    }

    // Đóng Match Server Modal nếu đang mở
    const matchServerModal = document.getElementById('matchServerModal');
    if (matchServerModal && matchServerModal.style.display === 'flex') {
      matchServerModal.style.display = 'none';
      return;
    }
    // 1. Nếu Quick Zapping Drawer đang mở -> đóng drawer
    if (zap && zap.classList.contains('open')) {
      zap.classList.remove('open');
      const zapBtn = document.getElementById('btnQuickZap');
      if (zapBtn) setFocus(zapBtn);
      return;
    }

    // 2. Nếu Video Player đang mở -> Đóng player dứt khoát
    if (player && player.style.display === 'flex') {
      closePlayer(true, true);
      return;
    }

    // 3. Nếu Detail Modal đang mở -> Đóng modal, quay về grid
    if (detail && detail.style.display === 'flex') {
      detail.style.display = 'none';
      focusCurrentOrFirstMovie();
      return;
    }

    // 4. Nếu Schedule Modal đang mở -> Đóng
    if (sched && sched.style.display === 'flex') {
      sched.style.display = 'none';
      const btn = document.getElementById('btnScheduleHeader');
      if (btn) setFocus(btn);
      return;
    }

    // 5. Nếu IPTV Modal đang mở -> Đóng
    if (iptv && iptv.style.display === 'flex') {
      iptv.style.display = 'none';
      focusCurrentOrFirstMovie();
      return;
    }

    // 6. Nếu Search Modal đang mở -> Đóng
    if (search && search.style.display === 'flex') {
      search.style.display = 'none';
      const btn = document.getElementById('btnSearch');
      if (btn) setFocus(btn);
      return;
    }

    // 6.5. Nếu Install Platform Modal đang mở -> Đóng
    const installModalEl = document.getElementById('installPlatformModal');
    if (installModalEl && installModalEl.style.display === 'flex') {
      installModalEl.style.display = 'none';
      const btn = document.getElementById('btnInstallApp');
      if (btn) setFocus(btn);
      return;
    }

    // 7. Nếu đang ở filter khác filter đầu tiên, quay lại filter đầu tiên
    const currentFilters = FILTERS[currentSource] || [];
    if (currentFilters.length > 0 && currentFilter !== currentFilters[0].url) {
      const firstFilterBtn = document.querySelector('.btn-filter');
      if (firstFilterBtn) {
        firstFilterBtn.click();
        return;
      }
    }

    // 8. Ở màn hình chính -> Bấm 2 lần trong 2.5s để thoát ứng dụng
    const now = Date.now();
    if (now - lastBackTime < 2500) {
      showToast('Đang thoát ứng dụng...');
      try {
        if (window.webOS && typeof window.webOS.platformBack === 'function') {
          window.webOS.platformBack();
        } else {
          window.close();
        }
      } catch (err) {
        window.close();
      }
    } else {
      lastBackTime = now;
      showToast('Nhấn Quay Lại một lần nữa để thoát ứng dụng');
    }
  }

  // --- Remote Key Listeners (LG webOS & Spatial Navigation) ---
  window.addEventListener('keydown', (e) => {
    const code = e.keyCode || e.which;

    // Phím Back: LG webOS Back Button (461), Escape (27), Backspace (8)
    if (code === 461 || code === 27 || (code === 8 && document.activeElement.tagName !== 'INPUT')) {
      e.preventDefault();
      handleBackAction(e);
      return;
    }

    // Space (32) trên PC: Tạm dừng / Tiếp tục xem phim
    if (code === 32 && document.activeElement.tagName !== 'INPUT') {
      const player = document.getElementById('playerContainer');
      if (player && player.style.display === 'flex') {
        e.preventDefault();
        togglePlayPause();
        return;
      }
    }

    // Phím [ (219) và ] (221) trên PC: Tập trước / Tập tiếp theo
    if (code === 219 && document.activeElement.tagName !== 'INPUT') {
      const player = document.getElementById('playerContainer');
      if (player && player.style.display === 'flex') {
        e.preventDefault();
        playPrevEpisode();
        return;
      }
    }
    if (code === 221 && document.activeElement.tagName !== 'INPUT') {
      const player = document.getElementById('playerContainer');
      if (player && player.style.display === 'flex') {
        e.preventDefault();
        playNextEpisode();
        return;
      }
    }

    // F (70) trên PC: Bật / Tắt toàn màn hình
    if (code === 70 && document.activeElement.tagName !== 'INPUT') {
      const player = document.getElementById('playerContainer');
      if (player && player.style.display === 'flex') {
        const fsBtn = document.getElementById('btnFullscreen');
        if (fsBtn) {
          e.preventDefault();
          fsBtn.click();
          return;
        }
      }
    }

    // M (77) trên PC: Bật / Tắt âm thanh (Mute)
    if (code === 77 && document.activeElement.tagName !== 'INPUT') {
      if (video) {
        e.preventDefault();
        video.muted = !video.muted;
        showToast(video.muted ? '🔇 Đã tắt tiếng' : '🔊 Đã bật tiếng');
        return;
      }
    }

    // D-Pad Navigation: ArrowUp (38), ArrowDown (40), ArrowLeft (37), ArrowRight (39)
    if (code === 38) { // Up
      e.preventDefault();
      navigate2D('up');
      return;
    }
    if (code === 40) { // Down
      e.preventDefault();
      navigate2D('down');
      return;
    }
    if (code === 37) { // Left
      if (document.activeElement.tagName !== 'INPUT') {
        e.preventDefault();
        navigate2D('left');
        return;
      }
    }
    if (code === 39) { // Right
      if (document.activeElement.tagName !== 'INPUT') {
        e.preventDefault();
        navigate2D('right');
        return;
      }
    }

    // OK / Enter (13)
    if (code === 13) {
      const player = document.getElementById('playerContainer');
      if (player && player.style.display === 'flex') {
        const overlay = document.getElementById('playerOverlay');
        if (overlay && (overlay.classList.contains('hide') || overlay.classList.contains('controls-hidden'))) {
          e.preventDefault();
          resetOverlayTimer();
          togglePlayPause();
          return;
        }
      }
      if (document.activeElement && typeof document.activeElement.click === 'function') {
        if (document.activeElement.tagName !== 'BUTTON' && document.activeElement.tagName !== 'INPUT') {
          e.preventDefault();
          document.activeElement.click();
        }
      }
      return;
    }

    // Number keys 0-9 for Quick Zapping
    if (code >= 48 && code <= 57) {
      const numStr = String.fromCharCode(code);
      handleNumberZap(numStr);
      return;
    }

    // Media keys từ Remote LG: Play (415), Pause (19), Stop (413), FastForward (417), Rewind (412)
    if (code === 415) { // Play
      if (video && video.paused) {
        video.play().catch(() => {});
        updatePlayPauseIcons(true);
      }
    } else if (code === 19 || code === 413) { // Pause / Stop
      if (video && !video.paused) {
        video.pause();
        updatePlayPauseIcons(false);
      }
    } else if (code === 412) { // Rewind
      if (video) {
        video.currentTime = Math.max(0, video.currentTime - 10);
        showToast('⏪ -10 giây');
      }
    } else if (code === 417) { // FastForward
      if (video) {
        video.currentTime = Math.min(video.duration || 0, video.currentTime + 10);
        showToast('⏩ +10 giây');
      }
    }
  });

  // --- Hệ Thống Điều Hướng Đa Tầng Cho Android & PWA (Swipe-Back Không Thoát App) ---
  function pushNavigationState(screen) {
    try {
      history.pushState({ screen: screen }, '');
    } catch(e) {}
  }

  // Lắng nghe sự kiện webOSBack và popstate từ Trình duyệt / Android Gesture Swipe-Back
  document.addEventListener('webOSBack', handleBackAction);
  window.addEventListener('popstate', (e) => {
    handleBackAction(e);
  });

  // --- Xử Lý Nút Back Trên Chuột (XButton1 / Mouse Button 3 trong DOM) ---
  window.addEventListener('mouseup', (e) => {
    // e.button: 0=Left, 1=Middle, 2=Right, 3=XButton1 (Back), 4=XButton2 (Forward)
    if (e.button === 3) {
      e.preventDefault();
      e.stopPropagation();
      handleBackAction(e);
    }
  }, true);

  window.addEventListener('pointerup', (e) => {
    if (e.button === 3) {
      e.preventDefault();
      e.stopPropagation();
      handleBackAction(e);
    }
  }, true);

  window.addEventListener('mousedown', (e) => {
    if (e.button === 3) {
      e.preventDefault();
      e.stopPropagation();
    }
  }, true);

  // Expose ra window để WPF C# có thể kích hoạt trực tiếp
  window.handleBackAction = handleBackAction;

  // Format seconds to mm:ss or hh:mm:ss
  function formatTime(sec) {
    if (isNaN(sec)) return '00:00';
    const s = Math.floor(sec % 60);
    const m = Math.floor((sec / 60) % 60);
    const h = Math.floor(sec / 3600);
    if (h > 0) {
      return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  // --- Phân Trang & Cuộn Chuột Tự Động Tải Thêm Phim (Windows PC) ---
  const btnLoadMore = document.getElementById('btnLoadMore');
  if (btnLoadMore) {
    btnLoadMore.addEventListener('click', () => {
      loadMoreMovies();
    });
  }

  const btnScrollTop = document.getElementById('btnScrollTop');
  if (btnScrollTop) {
    btnScrollTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // --- PWA Native App & Multi-Platform Install Modal Handler ---
  let deferredInstallPrompt = null;
  const btnInstallApp = document.getElementById('btnInstallApp');
  const btnInstallFooter = document.getElementById('btnInstallFooter');
  const bannerInstall = document.getElementById('btnBannerInstall');
  const bannerClose = document.getElementById('btnBannerClose');
  const pwaBanner = document.getElementById('pwaInstallBanner');
  const installPlatformModal = document.getElementById('installPlatformModal');
  const btnCloseInstallModal = document.getElementById('btnCloseInstallModal');
  const btnCloseInstallModalTop = document.getElementById('btnCloseInstallModalTop');
  const btnTriggerPwaInstall = document.getElementById('btnTriggerPwaInstall');

  // Kiểm tra nếu ứng dụng đang chạy ở chế độ App đã cài đặt (Windows PWA, Edge/Chrome App, Windows WebView2, Android/LG App)
  function checkIsInstalledEnvironment() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.matchMedia('(display-mode: window-controls-overlay)').matches ||
           window.matchMedia('(display-mode: minimal-ui)').matches ||
           window.matchMedia('(display-mode: fullscreen)').matches || (window.menubar && window.menubar.visible === false) || (window.toolbar && window.toolbar.visible === false) ||
           window.navigator.standalone === true ||
           document.referrer.includes('android-app://') ||
           !!(window.chrome && window.chrome.webview) ||
           !!window.webOS ||
           window.location.hostname === 'huyca.local' ||
           window.location.hostname.includes('appassets') ||
           window.location.protocol === 'file:';
  }

  const isInstalledApp = checkIsInstalledEnvironment();

  function hideInstallUIForInstalledApp() {
    if (pwaBanner) pwaBanner.style.setProperty('display', 'none', 'important');
    if (btnInstallApp) {
      btnInstallApp.classList.add('installed-hidden');
      btnInstallApp.style.setProperty('display', 'none', 'important');
    }
    if (btnInstallFooter) {
      btnInstallFooter.style.setProperty('display', 'none', 'important');
    }
    if (installPlatformModal) {
      installPlatformModal.style.setProperty('display', 'none', 'important');
    }
  }

  if (isInstalledApp) {
    hideInstallUIForInstalledApp();
  } else {
    if (btnInstallApp) btnInstallApp.style.display = 'inline-flex';
  }

  try {
    window.matchMedia('(display-mode: standalone)').addEventListener('change', (e) => {
      if (e.matches) hideInstallUIForInstalledApp();
    });
  } catch (e) {}

  window.addEventListener('appinstalled', () => {
    localStorage.setItem('app_installed', 'true');
    hideInstallUIForInstalledApp();
    showToast('✅ Đã cài đặt ứng dụng Huy Cá thành công!');
  });

  if (bannerClose && pwaBanner) {
    bannerClose.addEventListener('click', () => {
      pwaBanner.style.display = 'none';
      sessionStorage.setItem('hide_pwa_banner', '1');
    });
    if (sessionStorage.getItem('hide_pwa_banner') === '1') {
      pwaBanner.style.display = 'none';
    }
  }

  function triggerDirectPwaInstall() {
    if (deferredInstallPrompt) {
      deferredInstallPrompt.prompt();
      deferredInstallPrompt.userChoice.then((choice) => {
        if (choice.outcome === 'accepted') {
          showToast('Đang cài đặt Huy Cá vào máy của bạn...');
          if (pwaBanner) pwaBanner.style.display = 'none';
          if (installPlatformModal) installPlatformModal.style.display = 'none';
        }
        deferredInstallPrompt = null;
      });
    } else {
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
      if (isIOS) {
        showToast('📲 Trên iPhone/iPad: Bấm nút Chia Sẻ [⬆] ở thanh dưới Safari ➔ Chọn "Thêm vào MH chính" (Add to Home Screen)!', 6500);
      } else {
        showToast('📲 Trên trình duyệt: Bấm biểu tượng Cài đặt [⊕] trên thanh địa chỉ hoặc menu [⋮] ➔ Chọn "Cài đặt ứng dụng"!', 6500);
      }
    }
  }

  function openInstallPlatformModal() {
    if (installPlatformModal) {
      installPlatformModal.style.display = 'flex';
      pushNavigationState('install');
      setTimeout(() => {
        if (btnTriggerPwaInstall) setFocus(btnTriggerPwaInstall);
      }, 60);
    } else {
      triggerDirectPwaInstall();
    }
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredInstallPrompt = e;
    if (checkIsInstalledEnvironment()) {
      hideInstallUIForInstalledApp();
      return;
    }
    if (btnInstallApp) {
      btnInstallApp.style.display = 'inline-flex';
    }
  });

  if (bannerInstall) bannerInstall.addEventListener('click', openInstallPlatformModal);
  if (btnInstallApp) btnInstallApp.addEventListener('click', openInstallPlatformModal);
  if (btnInstallFooter) btnInstallFooter.addEventListener('click', openInstallPlatformModal);
  if (btnTriggerPwaInstall) btnTriggerPwaInstall.addEventListener('click', triggerDirectPwaInstall);
  if (btnCloseInstallModal) {
    btnCloseInstallModal.addEventListener('click', () => {
      if (installPlatformModal) installPlatformModal.style.display = 'none';
    });
  }
  if (btnCloseInstallModalTop) {
    btnCloseInstallModalTop.addEventListener('click', () => {
      if (installPlatformModal) installPlatformModal.style.display = 'none';
    });
  }

  // --- Tự Động Tải Thêm Phim (Infinite Scroll) Chuẩn Mobile & Desktop ---
  function triggerAutoLoadMore() {
    if (currentSource === 'XEMTIVI' || currentFilter === 'app://favorites' || currentFilter === 'app://history') return;
    if (isLoading) return;

    const scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    const windowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight || 0;
    const scrollHeight = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, 1);

    if (btnScrollTop) {
      btnScrollTop.style.display = scrollTop > 400 ? 'flex' : 'none';
    }

    // Khi cuộn còn cách đáy 800px -> Tự động nạp tiếp trang mới ngay lập tức
    if (scrollTop + windowHeight >= scrollHeight - 800) {
      loadMoreMovies();
    }
  }

  let scrollThrottle = null;
  function handleScrollThrottled() {
    if (scrollThrottle) return;
    scrollThrottle = setTimeout(() => {
      scrollThrottle = null;
      triggerAutoLoadMore();
    }, 80);
  }

  window.addEventListener('scroll', handleScrollThrottled, { passive: true });
  document.addEventListener('scroll', handleScrollThrottled, { passive: true });
  window.addEventListener('touchmove', handleScrollThrottled, { passive: true });

  // Dùng thêm IntersectionObserver để bắt dính 100% khi phần đáy xuất hiện trên màn hình
  const paginEl = document.getElementById('paginationContainer');
  if (paginEl && 'IntersectionObserver' in window) {
    const bottomObserver = new IntersectionObserver((entries) => {
      if (entries[0] && entries[0].isIntersecting) {
        triggerAutoLoadMore();
      }
    }, { rootMargin: '600px 0px' });
    bottomObserver.observe(paginEl);
  }

  // --- Remote Security & Maintenance Check ---
  function checkRemoteSecurityLock() {
    (function() {
      var urls = [
        'https://raw.githubusercontent.com/uhg031486-hub/HuyCaBuonCa_Release/main/version.json?t=' + Date.now(),
        'https://cdn.jsdelivr.net/gh/uhg031486-hub/HuyCaBuonCa_Release@main/version.json?t=' + Date.now()
      ];
      return fetch(urls[0]).catch(function() { return fetch(urls[1]); });
    })()
      .then(function(r) { return r.json(); })
      .then(function(cfg) {
        if (cfg && cfg.isMaintenanceLocked) {
          document.body.innerHTML = 
            '<div style="position:fixed;inset:0;background:#0b0e14;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px;text-align:center;z-index:999999;font-family:sans-serif;">' +
              '<div style="font-size:64px;margin-bottom:16px;">🔒</div>' +
              '<h1 style="color:#ffd700;font-size:26px;margin-bottom:12px;font-weight:bold;">THÔNG BÁO BẢO TRÌ NỘI BỘ</h1>' +
              '<p style="font-size:16px;color:#8a99ad;max-width:540px;line-height:1.6;margin:0 auto 20px;">' + (cfg.maintenanceMessage || 'Hệ thống đang bảo trì nội bộ. Vui lòng quay lại sau!') + '</p>' +
            '</div>';
        }
      })
      .catch(function() {});
  }

  // --- Initialize App ---
  checkRemoteSecurityLock();
  initSources();
  initFilterBarNavigation();
  initMatchServerModalEvents();
  startReminderChecker();
  renderFilterBar();
  renderHistoryAndFavs();


  // ==========================================================================
  // HUY CÁ ADAPTIVE DEVICE MANAGER (Mobile & TV Mode)
  // ==========================================================================
  function getDeviceMode() {
    const ua = navigator.userAgent || '';
    const isTv = /Web0S|SmartTV|Tizen|Android TV|GoogleTV|AppleTV|HbbTV|POV_TV|LargeScreen|Viera|BRAVIA|Hisense/i.test(ua);
    const isMobile = /Android|iPhone|iPad|iPod|Mobile/i.test(ua) || (window.innerWidth <= 800);
    
    // Trên điện thoại di động: LUÔN LUÔN là mobile mode
    if (isMobile && !isTv) {
      try { localStorage.setItem('huyca_view_mode', 'mobile'); } catch(e) {}
      return 'mobile';
    }

    // Trên Windows / Desktop / TV (màn hình rộng > 800px): LUÔN LUÔN dùng chế độ màn hình lớn ('tv')
    try { localStorage.setItem('huyca_view_mode', 'tv'); } catch(e) {}
    return 'tv';
  }

  function setDeviceMode(mode) {
    document.body.classList.remove('mode-mobile', 'mode-tv');
    document.body.classList.add(`mode-${mode}`);
    localStorage.setItem('huyca_view_mode', mode);

    const editionName = document.getElementById('footerEditionName');
    const btnSwitch = document.getElementById('btnSwitchMode');
    if (editionName) {
      editionName.textContent = mode === 'mobile' ? 'Mobile Edition' : 'TV Edition';
    }
    if (btnSwitch) {
      btnSwitch.textContent = mode === 'mobile' ? '📺 Chuyển sang Giao diện Tivi' : '📱 Chuyển sang Giao diện Di Động';
    }
  }

  // Khởi tạo chế độ khi tải trang
  const initialMode = getDeviceMode();
  setDeviceMode(initialMode);

  const btnSwitchMode = document.getElementById('btnSwitchMode');
  if (btnSwitchMode) {
    btnSwitchMode.addEventListener('click', () => {
      const current = document.body.classList.contains('mode-mobile') ? 'mobile' : 'tv';
      const next = current === 'mobile' ? 'tv' : 'mobile';
      setDeviceMode(next);
      showToast(next === 'mobile' ? '📱 Đã chuyển sang Giao diện Di Động' : '📺 Đã chuyển sang Giao diện Tivi');
    });
  }


  // --- Nút Xoay Ngang Màn Hình (Tối ưu cho iPhone & Mobile) ---
  const btnRotatePlayer = document.getElementById('btnRotatePlayer');
  if (btnRotatePlayer) {
    btnRotatePlayer.addEventListener('click', () => {
      const container = document.getElementById('playerContainer');
      const isVertMode = container.classList.contains('player-vertical-mode');
      const rotateBtnText = document.getElementById('rotateBtnText');
      
      container.classList.toggle('player-forced-landscape');
      const isForced = container.classList.contains('player-forced-landscape');
      
      if (rotateBtnText) {
        if (isVertMode) {
          rotateBtnText.textContent = isForced ? 'Xoay Dọc' : 'Phim Dọc (9:16)';
        } else {
          rotateBtnText.textContent = isForced ? 'Xoay Dọc' : 'Xoay Ngang';
        }
      }
      showToast(isForced ? '🔄 Đã xoay ngang màn hình (Cầm ngang để xem)' : '📱 Đã trở về màn hình dọc');
    });
  }

  // Tự động điều chỉnh khi người dùng xoay thiết bị thực tế (Device Orientation Change)
  function handleDeviceOrientationChange() {
    const container = document.getElementById('playerContainer');
    if (!container || container.style.display === 'none') return;
    const isLandscape = (window.innerWidth >= window.innerHeight);
    const rotateBtnText = document.getElementById('rotateBtnText');
    if (isLandscape) {
      // Khi xoay ngang điện thoại thật: gỡ bỏ player-forced-landscape để video hiển thị tự nhiên
      if (container.classList.contains('player-forced-landscape')) {
        container.classList.remove('player-forced-landscape');
        if (rotateBtnText) rotateBtnText.textContent = 'Màn Ngang';
      }
    }
  }
  window.addEventListener('resize', handleDeviceOrientationChange);
  window.addEventListener('orientationchange', handleDeviceOrientationChange);


  // ==========================================================================
  // ADVANCED PLAYER CONTROLS: TOUCH MOBILE (Ảnh 2) & WINDOWS DESKTOP (Ảnh 3)
  // ==========================================================================
  let isTouchLocked = false;
  let currentSpeedIdx = 0;
  const speedList = [1.0, 1.25, 1.5, 2.0, 0.75];

  // --- HỆ THỐNG ĐIỀU KHIỂN CẢM ỨNG ĐA NỀN TẢNG (TOUCH & CLICK ERGONOMICS v3.3.7) ---
  const playerOverlayEl = document.getElementById('playerOverlay');
  const playerMainAreaEl = document.getElementById('playerMainArea');
  const btnUnlockTouchEl = document.getElementById('btnUnlockTouch');
  const centerPlayIconEl = document.getElementById('centerPlayIcon');
  let overlayHideTimeout = null;
  let lastTouchActionTimestamp = 0;
  let touchStartCoords = { x: 0, y: 0 };

  function showPlayerControls() {
    if (!playerOverlayEl || isTouchLocked) return;
    playerOverlayEl.classList.remove('controls-hidden');
    playerOverlayEl.classList.remove('hide');
    resetOverlayTimer();
  }
  window.showPlayerControls = showPlayerControls;

  function hidePlayerControls() {
    if (!playerOverlayEl || isTouchLocked) return;
    const v = document.getElementById('videoPlayer');
    playerOverlayEl.classList.add('controls-hidden');
    if (overlayHideTimeout) clearTimeout(overlayHideTimeout);
  }
  window.hidePlayerControls = hidePlayerControls;

  function resetOverlayTimer(customDelay = 5000) {
    if (!playerOverlayEl || isTouchLocked) return;
    playerOverlayEl.classList.remove('controls-hidden');
    playerOverlayEl.classList.remove('hide');
    if (overlayHideTimeout) clearTimeout(overlayHideTimeout);
    overlayHideTimeout = setTimeout(() => {
      const v = document.getElementById('videoPlayer');
      const isSidebarOpen = document.getElementById('playerSidebar')?.classList.contains('mobile-open');
      const isZappingOpen = document.getElementById('zappingPanel')?.classList.contains('active');
      // Không tự ẩn nếu sidebar tập đang mở hoặc zapping đang mở
      if (isSidebarOpen || isZappingOpen) return;
      if ((v && !v.paused) || (isEmbedStreamUrl(currentActiveStream))) {
        playerOverlayEl.classList.add('controls-hidden');
      }
    }, customDelay);
  }
  window.resetOverlayTimer = resetOverlayTimer;

  function togglePlayerControls() {
    if (!playerOverlayEl || isTouchLocked) return;
    const isHidden = playerOverlayEl.classList.contains('controls-hidden') || playerOverlayEl.classList.contains('hide');
    if (isHidden) {
      showPlayerControls();
    } else {
      hidePlayerControls();
    }
  }
  window.togglePlayerControls = togglePlayerControls;

  if (playerMainAreaEl) {
    // 1. Lắng nghe touchstart trên màn hình di động: Ghi nhận tọa độ chạm ban đầu
    playerMainAreaEl.addEventListener('touchstart', (e) => {
      if (e.touches && e.touches.length > 0) {
        touchStartCoords = { x: e.touches[0].clientX, y: e.touches[0].clientY };
        lastTouchActionTimestamp = Date.now();
      }
    }, { passive: true });

    // 2. Lắng nghe touchend: Xử lý thao tác chạm TAP dứt khoát trên điện thoại (Không xung đột với vuốt)
    playerMainAreaEl.addEventListener('touchend', (e) => {
      if (!e.changedTouches || e.changedTouches.length === 0) return;
      const dx = Math.abs(e.changedTouches[0].clientX - touchStartCoords.x);
      const dy = Math.abs(e.changedTouches[0].clientY - touchStartCoords.y);
      // Nếu ngón tay di chuyển > 14px -> Coi là cử chỉ vuốt, không phải tap
      if (dx > 14 || dy > 14) return;

      lastTouchActionTimestamp = Date.now();

      // Nếu chạm vào các nút điều khiển, input, thanh scrubber tiến trình, sidebar
      if (e.target.closest('button, input, select, a, .player-top, .player-bottom-bar, .player-sidebar, .zapping-panel, .embed-helper-bar, .btn-unlock-touch')) {
        resetOverlayTimer();
        return;
      }

      if (isTouchLocked) {
        if (btnUnlockTouchEl) {
          btnUnlockTouchEl.style.display = 'block';
          setTimeout(() => { if (isTouchLocked && btnUnlockTouchEl) btnUnlockTouchEl.style.display = 'none'; }, 3000);
        }
        return;
      }

      // THỰC HIỆN BẬT / TẮT THANH ĐIỀU HƯỚNG PHIM
      e.preventDefault();
      togglePlayerControls();
    }, { passive: false });

    // 3. Lắng nghe click (dành cho chuột máy tính Desktop và dự phòng)
    playerMainAreaEl.addEventListener('click', (e) => {
      // Nếu vừa xử lý qua sự kiện touchend trong vòng 650ms, BỎ QUA synthetic click để tránh toggle kép!
      if (Date.now() - lastTouchActionTimestamp < 650) {
        return;
      }

      const container = document.getElementById('playerContainer');
      // Nếu đang ở chế độ Mini Floating Player
      if (container && container.classList.contains('player-floating-mini')) {
        if (!e.target.closest('#btnCloseMini')) {
          const expandBtn = document.getElementById('btnExpandMini');
          if (expandBtn) expandBtn.click();
          return;
        }
      }

      if (e.target.closest('button, input, select, a, .player-top, .player-bottom-bar, .player-center-controls, .player-sidebar, .zapping-panel, .embed-helper-bar, .btn-unlock-touch')) {
        resetOverlayTimer();
        return;
      }

      if (isTouchLocked) {
        if (btnUnlockTouchEl) {
          btnUnlockTouchEl.style.display = 'block';
          setTimeout(() => { if (isTouchLocked && btnUnlockTouchEl) btnUnlockTouchEl.style.display = 'none'; }, 3000);
        }
        return;
      }

      togglePlayerControls();
    });

    // 4. Double-click vào màn hình video -> Bật / Tắt toàn màn hình
    playerMainAreaEl.addEventListener('dblclick', (e) => {
      if (e.target.closest('button, input, select, .player-top, .player-bottom-bar, .player-sidebar, .zapping-panel, .embed-helper-bar')) {
        return;
      }
      const fsBtn = document.getElementById('btnFullscreen');
      if (fsBtn) fsBtn.click();
    });

    // 5. Sự kiện di chuột: Bỏ qua hoàn toàn nếu là synthetic mousemove phát sinh từ touch
    playerMainAreaEl.addEventListener('mousemove', () => {
      if (Date.now() - lastTouchActionTimestamp < 1200) return;
      if (!isTouchLocked) resetOverlayTimer();
    });
  }

  // --- Cinema Pro Player Event Handlers ---
  function updatePlayPauseIcons(isPlaying) {
    const svgPlay = document.getElementById('svgPlay');
    const svgPause = document.getElementById('svgPause');
    if (svgPlay) svgPlay.style.display = isPlaying ? 'none' : 'block';
    if (svgPause) svgPause.style.display = isPlaying ? 'block' : 'none';

    // Flash Center Ripple Animation (Netflix / YouTube Style)
    const ripple = document.getElementById('centerPlayRipple');
    const rPlay = document.getElementById('centerRipplePlaySvg');
    const rPause = document.getElementById('centerRipplePauseSvg');
    if (ripple && rPlay && rPause) {
      rPlay.style.display = isPlaying ? 'block' : 'none';
      rPause.style.display = isPlaying ? 'none' : 'block';
      ripple.style.display = 'flex';
      ripple.classList.remove('animate-pulse-scale');
      void ripple.offsetWidth; // force reflow
      ripple.classList.add('animate-pulse-scale');
      setTimeout(() => {
        if (ripple) ripple.style.display = 'none';
      }, 550);
    }
  }

  // Volume slider binding
  const volumeSliderEl = document.getElementById('volumeSlider');
  const btnVolumeToggleEl = document.getElementById('btnVolumeToggle');
  const svgVolumeHighEl = document.getElementById('svgVolumeHigh');
  const svgVolumeMutedEl = document.getElementById('svgVolumeMuted');
  let lastNonZeroVolume = 1;

  if (volumeSliderEl) {
    volumeSliderEl.addEventListener('input', (e) => {
      e.stopPropagation();
      const v = document.getElementById('videoPlayer');
      const val = parseFloat(e.target.value);
      if (v) {
        v.volume = val;
        v.muted = (val === 0);
      }
      if (val > 0) lastNonZeroVolume = val;
      if (svgVolumeHighEl) svgVolumeHighEl.style.display = (val === 0) ? 'none' : 'block';
      if (svgVolumeMutedEl) svgVolumeMutedEl.style.display = (val === 0) ? 'block' : 'none';
    });
    volumeSliderEl.addEventListener('click', (e) => e.stopPropagation());
  }

  if (btnVolumeToggleEl) {
    btnVolumeToggleEl.addEventListener('click', (e) => {
      e.stopPropagation();
      const v = document.getElementById('videoPlayer');
      if (!v) return;
      if (v.muted || v.volume === 0) {
        v.muted = false;
        v.volume = lastNonZeroVolume || 1;
        if (volumeSliderEl) volumeSliderEl.value = v.volume;
        if (svgVolumeHighEl) svgVolumeHighEl.style.display = 'block';
        if (svgVolumeMutedEl) svgVolumeMutedEl.style.display = 'none';
      } else {
        lastNonZeroVolume = v.volume;
        v.muted = true;
        v.volume = 0;
        if (volumeSliderEl) volumeSliderEl.value = 0;
        if (svgVolumeHighEl) svgVolumeHighEl.style.display = 'none';
        if (svgVolumeMutedEl) svgVolumeMutedEl.style.display = 'block';
      }
      resetOverlayTimer();
    });
  }

  // Nút Play / Pause chính dưới Dock (Cinema Pro)
  const btnPlayPauseMain = document.getElementById('btnPlayPause');
  if (btnPlayPauseMain) {
    btnPlayPauseMain.addEventListener('click', (e) => {
      e.stopPropagation();
      togglePlayPause();
    });
  }
  const vMain = document.getElementById('videoPlayer');
  if (vMain) {
    vMain.addEventListener('play', () => updatePlayPauseIcons(true));
    vMain.addEventListener('pause', () => updatePlayPauseIcons(false));
  }

  const btnCenterRewind = document.getElementById('btnCenterRewind');
  if (btnCenterRewind) {
    btnCenterRewind.addEventListener('click', (e) => {
      e.stopPropagation();
      const v = document.getElementById('videoPlayer');
      if (v) v.currentTime = Math.max(0, v.currentTime - 10);
      showToast('⏪ -10 giây');
      resetOverlayTimer();
    });
  }

  const btnCenterForward = document.getElementById('btnCenterForward');
  if (btnCenterForward) {
    btnCenterForward.addEventListener('click', (e) => {
      e.stopPropagation();
      const v = document.getElementById('videoPlayer');
      if (v) v.currentTime = Math.min(v.duration || 0, v.currentTime + 10);
      showToast('⏩ +10 giây');
      resetOverlayTimer();
    });
  }

  const btnCenterPrev = document.getElementById('btnCenterPrev');
  if (btnCenterPrev) {
    btnCenterPrev.addEventListener('click', (e) => {
      e.stopPropagation();
      playPrevEpisode();
      resetOverlayTimer();
    });
  }

  const btnCenterNext = document.getElementById('btnCenterNext');
  const btnQuickNextFloating = document.getElementById('btnQuickNextFloating');
  if (btnCenterNext) {
    btnCenterNext.addEventListener('click', (e) => {
      e.stopPropagation();
      playNextEpisode();
      resetOverlayTimer();
    });
  }
  if (btnQuickNextFloating) {
    btnQuickNextFloating.addEventListener('click', (e) => {
      e.stopPropagation();
      playNextEpisode();
      resetOverlayTimer();
    });
  }

  // Nút Bỏ qua Intro +85s (Ảnh 2)
  const btnSkipIntroEl = document.getElementById('btnSkipIntro');
  if (btnSkipIntroEl) {
    btnSkipIntroEl.addEventListener('click', (e) => {
      e.stopPropagation();
      const v = document.getElementById('videoPlayer');
      if (v && v.duration) {
        v.currentTime = Math.min(v.duration, v.currentTime + 85);
        showToast('⏩ Đã bỏ qua đoạn intro (+85s)');
        btnSkipIntroEl.style.display = 'none';
      }
      resetOverlayTimer();
    });
  }

  // Nút Tốc độ phát (Ảnh 2)
  const btnSpeedPlayer = document.getElementById('btnSpeedPlayer');
  if (btnSpeedPlayer) {
    btnSpeedPlayer.addEventListener('click', (e) => {
      e.stopPropagation();
      const v = document.getElementById('videoPlayer');
      if (!v) return;
      currentSpeedIdx = (currentSpeedIdx + 1) % speedList.length;
      const spd = speedList[currentSpeedIdx];
      v.playbackRate = spd;
      btnSpeedPlayer.textContent = spd + 'x';
      showToast(`Tốc độ phát: ${spd}x`);
      resetOverlayTimer();
    });
  }

  // Nút Picture in Picture (PiP) / Thu nhỏ Hình trong hình
  const btnPipPlayer = document.getElementById('btnPipPlayer');
  if (btnPipPlayer) {
    btnPipPlayer.addEventListener('click', (e) => {
      e.stopPropagation();
      const cont = document.getElementById('playerContainer');
      if (!cont) return;

      if (cont.classList.contains('player-floating-mini')) {
        const expandBtn = document.getElementById('btnExpandMini');
        if (expandBtn) expandBtn.click();
      } else {
        enableMiniFloatingPlayer();
      }
      resetOverlayTimer();
    });
  }

  // Sự kiện nút Phóng to và Đóng trên Mini Player
  const btnExpandMini = document.getElementById('btnExpandMini');
  if (btnExpandMini) {
    btnExpandMini.addEventListener('click', (e) => {
      e.stopPropagation();
      const container = document.getElementById('playerContainer');
      const miniBar = document.getElementById('miniPlayerBar');
      if (container) {
        container.classList.remove('player-floating-mini');
        container.style.display = 'flex';
        const isMobileDevice = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || (window.innerWidth <= 800);
        const isVert = container.classList.contains('player-vertical-mode');
        const isPortrait = (window.innerHeight > window.innerWidth);
        if (isMobileDevice && !isVert && isPortrait) {
          container.classList.add('player-forced-landscape');
          const rotateBtnText = document.getElementById('rotateBtnText');
          if (rotateBtnText) rotateBtnText.textContent = 'Xoay Dọc';
        }
      }
      if (miniBar) miniBar.style.display = 'none';
      resetOverlayTimer();
      showToast('🗖 Đã phóng to toàn màn hình');
    });
  }

  const btnCloseMini = document.getElementById('btnCloseMini');
  if (btnCloseMini) {
    btnCloseMini.addEventListener('click', (e) => {
      e.stopPropagation();
      disableMiniFloatingPlayer(true);
    });
  }

  // Nút Tỉ lệ khung hình (Aspect Ratio: Fit / Fill / Stretch)
  const btnAspectPlayer = document.getElementById('btnAspectPlayer');
  const aspectBadgeText = document.getElementById('aspectBadgeText');
  if (btnAspectPlayer) {
    btnAspectPlayer.addEventListener('click', (e) => {
      e.stopPropagation();
      const v = document.getElementById('videoPlayer');
      const iframe = document.getElementById('playerIframe');
      if (!v) return;
      currentAspectIdx = (currentAspectIdx + 1) % aspectModes.length;
      const cur = aspectModes[currentAspectIdx];
      v.style.setProperty('object-fit', cur.mode, 'important');
      if (iframe) iframe.style.setProperty('object-fit', cur.mode, 'important');
      if (aspectBadgeText) aspectBadgeText.textContent = cur.badge;
      btnAspectPlayer.setAttribute('title', `Tỉ lệ: ${cur.label} - ${cur.desc}`);
      showToast(`📐 Tỉ lệ màn hình: ${cur.label} (${cur.desc})`);
      resetOverlayTimer();
    });
  }

  // Nút Khóa cảm ứng (Ảnh 2)
  const btnLockPlayer = document.getElementById('btnLockPlayer');
  if (btnLockPlayer) {
    btnLockPlayer.addEventListener('click', (e) => {
      e.stopPropagation();
      isTouchLocked = true;
      window.isTouchLocked = true;
      if (playerOverlayEl) playerOverlayEl.classList.add('controls-hidden');
      if (btnUnlockTouchEl) btnUnlockTouchEl.style.display = 'block';
      showToast('🔒 Đã khóa cảm ứng (Bấm nút mở khóa để điều khiển lại)');
    });
  }

  if (btnUnlockTouchEl) {
    btnUnlockTouchEl.addEventListener('click', (e) => {
      e.stopPropagation();
      isTouchLocked = false;
      window.isTouchLocked = false;
      btnUnlockTouchEl.style.display = 'none';
      if (playerOverlayEl) playerOverlayEl.classList.remove('controls-hidden');
      showToast('🔓 Đã mở khóa cảm ứng');
      resetOverlayTimer();
    });
  }

  // Sidebar Danh Sách Tập & Server (Ảnh 3)
  const playerSidebarEl = document.getElementById('playerSidebar');
  const btnCloseSidebarEl = document.getElementById('btnCloseSidebar');
  const btnEpisodeSheetPlayerEl = document.getElementById('btnEpisodeSheetPlayer');

  if (btnCloseSidebarEl && playerSidebarEl) {
    btnCloseSidebarEl.addEventListener('click', (e) => {
      e.stopPropagation();
      playerSidebarEl.classList.remove('mobile-open');
      playerSidebarEl.classList.add('collapsed');
      showToast('Đã đóng danh sách tập');
    });
  }

  if (btnEpisodeSheetPlayerEl && playerSidebarEl) {
    btnEpisodeSheetPlayerEl.addEventListener('click', (e) => {
      e.stopPropagation();
      const isMobile = window.innerWidth <= 800 || (document.getElementById('playerContainer') && document.getElementById('playerContainer').classList.contains('player-vertical-mode'));
      if (isMobile) {
        playerSidebarEl.classList.remove('collapsed');
        playerSidebarEl.classList.toggle('mobile-open');
      } else {
        playerSidebarEl.classList.toggle('collapsed');
      }
      resetOverlayTimer();
    });
  }

  // Cập nhật giao diện Sidebar tập phim & Bỏ qua Intro trong playVideo
  function updateSidebarAndControls(movie, detail, epIndex, serverIndex) {
    const sTitle = document.getElementById('sidebarMovieTitle');
    const sSub = document.getElementById('sidebarMovieSub');
    const sServers = document.getElementById('sidebarServersList');
    const sGrid = document.getElementById('sidebarEpisodesGrid');

    if (sTitle) sTitle.textContent = movie.name || '';
    if (sSub) sSub.textContent = `${movie.originName || ''} (${movie.year || '2026'})`;

    if (!sServers || !sGrid) return;

    // NẾU LÀ TRUYỀN HÌNH HOẶC TRẬN ĐẤU BÓNG ĐÁ TRỰC TIẾP (Không có detail hoặc episodes rỗng)
    // BẮT BUỘC DỌN SẠCH DANH SÁCH TẬP CỦA PHIM CŨ ĐỂ KHÔNG HIỆN NHẦM TẬP PHIM NGẮN!
    if (!detail || !detail.episodes || detail.episodes.length === 0) {
      sServers.innerHTML = '<span style="color: var(--accent-cyan); font-weight: 800; font-size: 13px;">🔴 TRUYỀN HÌNH TRỰC TIẾP</span>';
      sGrid.innerHTML = '<div style="padding: 24px; color: #94a3b8; font-size: 13px; text-align: center; grid-column: 1 / -1; line-height: 1.6;">⚽ Đang phát sóng trận đấu trực tiếp.<br><span style="color: #64748b; font-size: 12px;">Kênh không có danh sách tập phim.</span></div>';
      return;
    }
    sServers.innerHTML = '';
    sGrid.innerHTML = '';

    const episodesData = detail.episodes || [];
    if (episodesData.length === 0) return;

    // Render Server Tabs
    episodesData.forEach((srv, sIdx) => {
      const sBtn = document.createElement('button');
      sBtn.className = `btn-sidebar-server ${sIdx === (serverIndex || 0) ? 'active' : ''}`;
      sBtn.textContent = srv.server_name || `Server ${sIdx + 1}`;
      sBtn.addEventListener('click', () => {
        const curEps = srv.server_data || [];
        const nextEp = curEps[epIndex] || curEps[0];
        if (nextEp) {
          playVideo(nextEp.link_m3u8, movie.name, nextEp.name, movie, detail, epIndex, sIdx);
        }
      });
      sServers.appendChild(sBtn);
    });

    // Render Episode Numbers Grid [01] [02] ... (Ảnh 3)
    const activeServer = episodesData[serverIndex || 0] || episodesData[0];
    const epItems = (activeServer && activeServer.server_data) || [];

    epItems.forEach((ep, idx) => {
      const epBtn = document.createElement('button');
      const isCurrent = (idx === (epIndex || 0));
      epBtn.className = `btn-sidebar-ep ${isCurrent ? 'active' : ''}`;

      // Format số tập 01, 02...
      let epLabel = ep.name || String(idx + 1);
      const matchNum = epLabel.match(/\d+/);
      if (matchNum) {
        const num = parseInt(matchNum[0], 10);
        epLabel = num < 10 ? `0${num}` : String(num);
      }
      epBtn.textContent = epLabel;

      epBtn.addEventListener('click', async () => {
        let stream = ep.link_m3u8;
        let sub = ep.subtitleUrl;
        if (stream && stream.startsWith('freereels_unlock:')) {
          showToast('🔄 Đang mở khóa tập...');
          const seriesId = (movie.id || '').replace('freereels:', '');
          const unl = await FreeReelsClient.unlockEpisode(seriesId, ep.slug);
          if (unl && unl.streamUrl) {
            stream = unl.streamUrl;
            if (unl.subtitleUrl) sub = unl.subtitleUrl;
          }
        }
        playVideo(stream, movie.name, ep.name, movie, detail, idx, serverIndex || 0, false, sub, true);
      });
      sGrid.appendChild(epBtn);
    });

    // Cập nhật trạng thái phím Prev / Next dưới thanh điều khiển
    const centerPrevBtn = document.getElementById('btnCenterPrev');
    const centerNextBtn = document.getElementById('btnCenterNext');
    if (centerPrevBtn) {
      centerPrevBtn.disabled = (epIndex <= 0);
      centerPrevBtn.style.opacity = (epIndex <= 0) ? '0.35' : '1';
      centerPrevBtn.style.pointerEvents = (epIndex <= 0) ? 'none' : 'auto';
    }
    if (centerNextBtn) {
      centerNextBtn.disabled = (epIndex >= epItems.length - 1);
      centerNextBtn.style.opacity = (epIndex >= epItems.length - 1) ? '0.35' : '1';
      centerNextBtn.style.pointerEvents = (epIndex >= epItems.length - 1) ? 'none' : 'auto';
    }

    // Mở Sidebar mặc định trên Windows / Desktop, đóng trên Mobile
    if (window.innerWidth > 800) {
      playerSidebarEl.classList.remove('collapsed');
    } else {
      playerSidebarEl.classList.add('collapsed');
      playerSidebarEl.classList.remove('mobile-open');
    }
  }
})();
