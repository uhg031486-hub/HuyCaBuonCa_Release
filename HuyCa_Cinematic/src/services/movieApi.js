// Dịch vụ kết nối trực tiếp các kho phim thật (KKPhim, NguonC, FreeReels/ReelShort & Live TV) cho Huy Cá Cinema

const KKPHIM_IMG_BASE = 'https://phimimg.com/';

function md5(string) {
  function RotateLeft(lValue, iShiftBits) {
    return (lValue << iShiftBits) | (lValue >>> (32 - iShiftBits));
  }
  function AddUnsigned(lX, lY) {
    var lX4, lY4, lX8, lY8, lResult;
    lX8 = (lX & 0x80000000);
    lY8 = (lY & 0x80000000);
    lX4 = (lX & 0x40000000);
    lY4 = (lY & 0x40000000);
    lResult = (lX & 0x3FFFFFFF) + (lY & 0x3FFFFFFF);
    if (lX4 & lY4) return (lResult ^ 0x80000000 ^ lX8 ^ lY8);
    if (lX4 | lY4) {
      if (lResult & 0x40000000) return (lResult ^ 0xC0000000 ^ lX8 ^ lY8);
      else return (lResult ^ 0x40000000 ^ lX8 ^ lY8);
    } else return (lResult ^ lX8 ^ lY8);
  }
  function F(x, y, z) { return (x & y) | ((~x) & z); }
  function G(x, y, z) { return (x & z) | (y & (~z)); }
  function H(x, y, z) { return (x ^ y ^ z); }
  function I(x, y, z) { return (y ^ (x | (~z))); }
  function FF(a, b, c, d, x, s, ac) {
    a = AddUnsigned(a, AddUnsigned(AddUnsigned(F(b, c, d), x), ac));
    return AddUnsigned(RotateLeft(a, s), b);
  }
  function GG(a, b, c, d, x, s, ac) {
    a = AddUnsigned(a, AddUnsigned(AddUnsigned(G(b, c, d), x), ac));
    return AddUnsigned(RotateLeft(a, s), b);
  }
  function HH(a, b, c, d, x, s, ac) {
    a = AddUnsigned(a, AddUnsigned(AddUnsigned(H(b, c, d), x), ac));
    return AddUnsigned(RotateLeft(a, s), b);
  }
  function II(a, b, c, d, x, s, ac) {
    a = AddUnsigned(a, AddUnsigned(AddUnsigned(I(b, c, d), x), ac));
    return AddUnsigned(RotateLeft(a, s), b);
  }
  function ConvertToWordArray(str) {
    var lWordCount;
    var lMessageLength = str.length;
    var lNumberOfWords_temp1 = lMessageLength + 8;
    var lNumberOfWords_temp2 = (lNumberOfWords_temp1 - (lNumberOfWords_temp1 % 64)) / 64;
    var lNumberOfWords = (lNumberOfWords_temp2 + 1) * 16;
    var lWordArray = Array(lNumberOfWords - 1);
    var lBytePosition = 0;
    var lByteCount = 0;
    while (lByteCount < lMessageLength) {
      lWordCount = (lByteCount - (lByteCount % 4)) / 4;
      lBytePosition = (lByteCount % 4) * 8;
      lWordArray[lWordCount] = (lWordArray[lWordCount] | (str.charCodeAt(lByteCount) << lBytePosition));
      lByteCount++;
    }
    lWordCount = (lByteCount - (lByteCount % 4)) / 4;
    lBytePosition = (lByteCount % 4) * 8;
    lWordArray[lWordCount] = lWordArray[lWordCount] | (0x80 << lBytePosition);
    lWordArray[lNumberOfWords - 2] = lMessageLength << 3;
    lWordArray[lNumberOfWords - 1] = lMessageLength >>> 29;
    return lWordArray;
  }
  function WordToHex(lValue) {
    var WordToHexValue = '', WordToHexValue_temp = '', lByte, lCount;
    for (lCount = 0; lCount <= 3; lCount++) {
      lByte = (lValue >>> (lCount * 8)) & 255;
      WordToHexValue_temp = '0' + lByte.toString(16);
      WordToHexValue = WordToHexValue + WordToHexValue_temp.substr(WordToHexValue_temp.length - 2, 2);
    }
    return WordToHexValue;
  }
  var x = ConvertToWordArray(string);
  var k, AA, BB, CC, DD, a, b, c, d;
  var S11 = 7, S12 = 12, S13 = 17, S14 = 22;
  var S21 = 5, S22 = 9, S23 = 14, S24 = 20;
  var S31 = 4, S32 = 11, S33 = 16, S34 = 23;
  var S41 = 6, S42 = 10, S43 = 15, S44 = 21;
  a = 0x67452301; b = 0xEFCDAB89; c = 0x98BADCFE; d = 0x10325476;
  for (k = 0; k < x.length; k += 16) {
    AA = a; BB = b; CC = c; DD = d;
    a = FF(a, b, c, d, x[k + 0], S11, 0xD76AA478); d = FF(d, a, b, c, x[k + 1], S12, 0xE8C7B756);
    c = FF(c, d, a, b, x[k + 2], S13, 0x242070DB); b = FF(b, c, d, a, x[k + 3], S14, 0xC1BDCEEE);
    a = FF(a, b, c, d, x[k + 4], S11, 0xF57C0FAF); d = FF(d, a, b, c, x[k + 5], S12, 0x4787C62A);
    c = FF(c, d, a, b, x[k + 6], S13, 0xA8304613); b = FF(b, c, d, a, x[k + 7], S14, 0xFD469501);
    a = FF(a, b, c, d, x[k + 8], S11, 0x698098D8); d = FF(d, a, b, c, x[k + 9], S12, 0x8B44F7AF);
    c = FF(c, d, a, b, x[k + 10], S13, 0xFFFF5BB1); b = FF(b, c, d, a, x[k + 11], S14, 0x895CD7BE);
    a = FF(a, b, c, d, x[k + 12], S11, 0x6B901122); d = FF(d, a, b, c, x[k + 13], S12, 0xFD987193);
    c = FF(c, d, a, b, x[k + 14], S13, 0xA679438E); b = FF(b, c, d, a, x[k + 15], S14, 0x49B40821);
    a = GG(a, b, c, d, x[k + 1], S21, 0xF61E2562); d = GG(d, a, b, c, x[k + 6], S22, 0xC040B340);
    c = GG(c, d, a, b, x[k + 11], S23, 0x265E5A51); b = GG(b, c, d, a, x[k + 0], S24, 0xE9B6C7AA);
    a = GG(a, b, c, d, x[k + 5], S21, 0xD62F105D); d = GG(d, a, b, c, x[k + 10], S22, 0x2441453);
    c = GG(c, d, a, b, x[k + 15], S23, 0xD8A1E681); b = GG(b, c, d, a, x[k + 4], S24, 0xE7D3FBC8);
    a = GG(a, b, c, d, x[k + 9], S21, 0x21E1CDE6); d = GG(d, a, b, c, x[k + 14], S22, 0xC33707D6);
    c = GG(c, d, a, b, x[k + 3], S23, 0xF4D50D87); b = GG(b, c, d, a, x[k + 8], S24, 0x455A14ED);
    a = GG(a, b, c, d, x[k + 13], S21, 0xA9E3E905); d = GG(d, a, b, c, x[k + 2], S22, 0xFCEFA3F8);
    c = GG(c, d, a, b, x[k + 7], S23, 0x676F02D9); b = GG(b, c, d, a, x[k + 12], S24, 0x8D2A4C8A);
    a = HH(a, b, c, d, x[k + 5], S31, 0xFFFA3942); d = HH(d, a, b, c, x[k + 8], S32, 0x8771F681);
    c = HH(c, d, a, b, x[k + 11], S33, 0x6D9D6122); b = HH(b, c, d, a, x[k + 14], S34, 0xFDE5380C);
    a = HH(a, b, c, d, x[k + 1], S31, 0xA4BEEA44); d = HH(d, a, b, c, x[k + 4], S32, 0x4BDECFA9);
    c = HH(c, d, a, b, x[k + 7], S33, 0xF6BB4B60); b = HH(b, c, d, a, x[k + 10], S34, 0xBEBFBC70);
    a = HH(a, b, c, d, x[k + 13], S31, 0x289B7EC6); d = HH(d, a, b, c, x[k + 0], S32, 0xEAA127FA);
    c = HH(c, d, a, b, x[k + 3], S33, 0xD4EF3085); b = HH(b, c, d, a, x[k + 6], S34, 0x4881D05);
    a = HH(a, b, c, d, x[k + 9], S31, 0xD9D4D039); d = HH(d, a, b, c, x[k + 12], S32, 0xE6DB99E5);
    c = HH(c, d, a, b, x[k + 15], S33, 0x1FA27CF8); b = HH(b, c, d, a, x[k + 2], S34, 0xC4AC5665);
    a = II(a, b, c, d, x[k + 0], S41, 0xF4292244); d = II(d, a, b, c, x[k + 7], S42, 0x432AFF97);
    c = II(c, d, a, b, x[k + 14], S43, 0xAB9423A7); b = II(b, c, d, a, x[k + 5], S44, 0xFC93A039);
    a = II(a, b, c, d, x[k + 12], S41, 0x655B59C3); d = II(d, a, b, c, x[k + 3], S42, 0x8F0CCC92);
    c = II(c, d, a, b, x[k + 10], S43, 0xFFEFF47D); b = II(b, c, d, a, x[k + 1], S44, 0x85845DD1);
    a = II(a, b, c, d, x[k + 8], S41, 0x6FA87E4F); d = II(d, a, b, c, x[k + 15], S42, 0xFE2CE6E0);
    c = II(c, d, a, b, x[k + 6], S43, 0xA3014314); b = II(b, c, d, a, x[k + 13], S44, 0x4E0811A1);
    a = II(a, b, c, d, x[k + 4], S41, 0xF7537E82); d = II(d, a, b, c, x[k + 11], S42, 0xBD3AF235);
    c = II(c, d, a, b, x[k + 2], S43, 0x2AD7D2BB); b = II(b, c, d, a, x[k + 9], S44, 0xEB86D391);
    a = AddUnsigned(a, AA); b = AddUnsigned(b, BB); c = AddUnsigned(c, CC); d = AddUnsigned(d, DD);
  }
  return (WordToHex(a) + WordToHex(b) + WordToHex(c) + WordToHex(d)).toLowerCase();
}

function fixImg(url) {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return KKPHIM_IMG_BASE + url.replace(/^\//, '');
}

function formatKkphimItem(item, categoryOverride) {
  const poster = fixImg(item.poster_url || item.thumb_url);
  const backdrop = fixImg(item.thumb_url || item.poster_url);
  return {
    id: item._id || item.slug,
    slug: item.slug,
    source: 'KKPHIM',
    title: item.name,
    originalTitle: item.origin_name || '',
    poster,
    backdrop,
    year: item.year ? String(item.year) : '2025',
    duration: item.time || 'Full HD',
    quality: item.quality || 'FHD',
    audio: item.lang || 'Vietsub / Thuyết Minh',
    category: categoryOverride || (item.category && item.category[0]?.name) || 'Điện Ảnh',
    imdb: '8.5',
    overview: item.content ? item.content.replace(/<[^>]+>/g, '') : `Thưởng thức bộ phim ${item.name} (${item.origin_name || ''}) chất lượng cao chuẩn điện ảnh với âm thanh sống động và hình ảnh sắc nét.`
  };
}

export async function fetchKkphimList(endpointUrl, categoryLabel = 'Điện Ảnh') {
  try {
    const res = await fetch(endpointUrl);
    if (!res.ok) return [];
    const json = await res.json();
    const items = (json.data && json.data.items) || json.items || [];
    return items.map(it => formatKkphimItem(it, categoryLabel));
  } catch (err) {
    console.warn('fetchKkphimList err:', err);
    return [];
  }
}

// Mở chi tiết bộ phim & danh sách tập thật (.m3u8) từ KKPhim hoặc FreeReels
export async function resolveMovieDetailAndStream(movie) {
  if (!movie) return null;

  // 1. Nếu là Kênh TV hoặc đã có sẵn danh sách tập thực tế (.m3u8)
  if (movie.isLiveTv || (movie.videoUrl && movie.videoUrl.includes('.m3u8'))) {
    return movie;
  }

  // 2. Nếu là Phim Ngắn FreeReels (`freereels:...`)
  if (movie.source === 'FREEREELS' || String(movie.slug || movie.id).startsWith('freereels:')) {
    const seriesId = String(movie.slug || movie.id).replace('freereels:', '');
    const detail = await FreeReelsApi.getDramaDetail(seriesId);
    if (detail && detail.episodes && detail.episodes.length > 0) {
      return {
        ...movie,
        overview: detail.overview || movie.overview,
        duration: `${detail.episodes.length} Tập`,
        episodes: detail.episodes,
        videoUrl: detail.episodes[0].url,
        subtitleUrl: detail.episodes[0].subtitleUrl,
        currentEpisode: detail.episodes[0].name,
        isShortDrama: true
      };
    }
  }

  // 3. Nếu là Phim KKPhim có slug
  const slug = movie.slug || movie.id;
  if (slug && !String(slug).includes(' ')) {
    try {
      const res = await fetch(`https://phimapi.com/phim/${encodeURIComponent(slug)}`);
      if (res.ok) {
        const data = await res.json();
        const mInfo = data.movie || {};
        const servers = data.episodes || [];
        const allEpisodes = [];
        servers.forEach((srv) => {
          const srvName = srv.server_name || 'VIP';
          (srv.server_data || []).forEach((ep) => {
            if (ep.link_m3u8) {
              allEpisodes.push({
                id: `${srvName}_${ep.slug || ep.name}`,
                name: servers.length > 1 ? `${ep.name} (${srvName.replace(/#[a-zA-Z0-9]+/g, '').trim()})` : ep.name,
                url: ep.link_m3u8,
                serverName: srvName
              });
            }
          });
        });

        if (allEpisodes.length > 0) {
          return {
            ...movie,
            title: mInfo.name || movie.title,
            originalTitle: mInfo.origin_name || movie.originalTitle,
            poster: fixImg(mInfo.poster_url || movie.poster),
            backdrop: fixImg(mInfo.thumb_url || movie.backdrop),
            overview: mInfo.content ? mInfo.content.replace(/<[^>]+>/g, '') : movie.overview,
            director: Array.isArray(mInfo.director) ? mInfo.director.join(', ') : movie.director,
            cast: Array.isArray(mInfo.actor) ? mInfo.actor.slice(0, 6) : movie.cast,
            duration: mInfo.time || movie.duration,
            year: mInfo.year ? String(mInfo.year) : movie.year,
            quality: mInfo.quality || movie.quality,
            audio: mInfo.lang || movie.audio,
            episodes: allEpisodes,
            videoUrl: allEpisodes[0].url,
            currentEpisode: allEpisodes[0].name
          };
        }
      }
    } catch (e) {
      console.warn('KKPhim detail fetch failed:', e);
    }
  }

  // 4. Nếu là phim mẫu (Dune, Oppenheimer...) chưa có slug thật -> Tìm kiếm theo tên trên KKPhim
  try {
    const q = encodeURIComponent(movie.title.split(':')[0].trim());
    const sRes = await fetch(`https://phimapi.com/v1/api/tim-kiem?keyword=${q}`);
    if (sRes.ok) {
      const sData = await sRes.json();
      const firstMatch = sData?.data?.items?.[0];
      if (firstMatch && firstMatch.slug) {
        return await resolveMovieDetailAndStream({
          ...movie,
          slug: firstMatch.slug,
          source: 'KKPHIM'
        });
      }
    }
  } catch (e) {}

  return movie;
}

export async function searchAllSources(keyword) {
  if (!keyword || !keyword.trim()) return [];
  const kw = encodeURIComponent(keyword.trim());
  try {
    const [kkRes, shortRes] = await Promise.all([
      fetch(`https://phimapi.com/v1/api/tim-kiem?keyword=${kw}`).then(r => r.ok ? r.json() : null).catch(() => null),
      FreeReelsApi.fetchShortDramas(0)
    ]);
    const kkItems = (kkRes?.data?.items || []).slice(0, 12).map(it => formatKkphimItem(it, 'Kết Quả Tìm Kiếm'));
    const qLower = keyword.toLowerCase();
    const matchedShorts = (shortRes || []).filter(s => s.title.toLowerCase().includes(qLower));
    return [...kkItems, ...matchedShorts];
  } catch (e) {
    return [];
  }
}

export const FreeReelsApi = {
  API_BASE: 'https://apiv2.free-reels.com/frv2-api',
  APP_SECRET: '33221199887766554433221199887766',
  deviceId: 'huyca_cinematic_device_2026',
  authKey: null,
  authSecret: null,

  getProxyUrl(targetUrl) {
    return `/api/proxy?url=${encodeURIComponent(targetUrl)}`;
  },

  async authenticate() {
    if (this.authKey && this.authSecret) return true;
    try {
      const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/anonymous/login`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'device-id': this.deviceId, 'device-hash': this.deviceId },
        body: JSON.stringify({ device_id: this.deviceId })
      });
      if (!resp.ok) return false;
      const res = await resp.json();
      if (res.data && res.data.auth_key) {
        this.authKey = res.data.auth_key;
        this.authSecret = res.data.auth_secret;
        return true;
      }
    } catch (e) {}
    return false;
  },

  async getHeaders() {
    const ok = await this.authenticate();
    if (!ok) return null;
    const oauthSignature = md5(`${this.APP_SECRET}&${this.authSecret}`);
    return {
      'Content-Type': 'application/json',
      'Authorization': `oauth_signature=${oauthSignature},oauth_token=${this.authKey},ts=${Date.now()}`,
      'device-id': this.deviceId,
      'device-hash': this.deviceId,
      'country': 'VN',
      'language': 'vi',
      'app-name': 'com.dramawave.www',
      'app-version': '1.5.70'
    };
  },

  async fetchShortDramas(offset = 0) {
    try {
      const headers = await this.getHeaders();
      if (!headers) return [];
      const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/homepage/v2/tab/feed`), {
        method: 'POST',
        headers,
        body: JSON.stringify({ tab_key: '503', module_key: '1036', next: offset > 0 ? JSON.stringify({ offset }) : '' })
      });
      if (!resp.ok) return [];
      const res = await resp.json();
      const rawItems = res.data?.items || res.data?.list || [];
      const list = [];
      rawItems.forEach(item => {
        const subList = (item.items && Array.isArray(item.items)) ? item.items : [item];
        subList.forEach(d => {
          const info = (d.drama_info && typeof d.drama_info === 'object') ? d.drama_info : d;
          const id = info.key || info.series_id || info.id || '';
          const title = info.title || info.name || '';
          const cover = info.cover || info.poster || '';
          const epCount = info.episode_count || 60;
          if (id && title && cover) {
            list.push({
              id: `freereels:${id}`,
              slug: `freereels:${id}`,
              source: 'FREEREELS',
              title,
              originalTitle: `${epCount} Tập • Tiểu Kịch 9:16`,
              poster: cover,
              backdrop: cover,
              quality: '9:16 HD',
              audio: info.title?.toLowerCase().includes('lồng tiếng') ? 'Lồng Tiếng Việt' : 'Vietsub Chuẩn',
              platform: 'ReelShort / FreeReels',
              episodesCount: `${epCount} Tập`,
              year: '2026',
              imdb: '8.8',
              category: 'Tiểu Kịch ReelShort',
              isShortDrama: true,
              overview: info.desc || `Phim ngắn màn hình dọc ${title} trọn bộ ${epCount} tập với cốt truyện kịch tính, phụ đề và thuyết minh Tiếng Việt.`
            });
          }
        });
      });
      return list;
    } catch (e) {
      return [];
    }
  },

  async getDramaDetail(seriesId) {
    try {
      const headers = await this.getHeaders();
      if (!headers) return null;
      const url = `${this.API_BASE}/drama/info_v2?series_id=${encodeURIComponent(seriesId)}&scene=search`;
      const resp = await fetch(this.getProxyUrl(url), { headers });
      if (!resp.ok) return null;
      const res = await resp.json();
      const data = res.data || {};
      const info = (data.info && typeof data.info === 'object') ? data.info : data;
      const epArray = info.episode_list || [];
      const episodes = [];

      epArray.forEach((el, idx) => {
        const epId = el.id || el.key || '';
        let viSubUrl = null;
        if (Array.isArray(el.subtitle_list)) {
          el.subtitle_list.forEach(s => {
            const lang = (s.language || '').toLowerCase();
            const disp = (s.display_name || '').toLowerCase();
            if (lang.includes('vi') || disp.includes('việt')) {
              viSubUrl = s.subtitle || s.vtt || null;
            }
          });
        }
        if (viSubUrl && viSubUrl.startsWith('http')) {
          viSubUrl = this.getProxyUrl(viSubUrl);
        }
        const rawStream = el.external_audio_h264_m3u8 || el.m3u8_url || el.video_url || '';
        episodes.push({
          id: epId || idx + 1,
          slug: epId,
          seriesId,
          name: `Tập ${idx + 1}`,
          url: rawStream ? this.getProxyUrl(rawStream) : `freereels_unlock:${seriesId}:${epId}`,
          subtitleUrl: viSubUrl
        });
      });

      return {
        overview: info.desc || '',
        episodes
      };
    } catch (e) {
      return null;
    }
  },

  async unlockEpisode(seriesId, episodeId) {
    try {
      const headers = await this.getHeaders();
      if (!headers) return null;
      const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/drama/unlock_episode`), {
        method: 'POST',
        headers,
        body: JSON.stringify({ series_id: seriesId, episode_id: episodeId, lang: 'vi' })
      });
      if (!resp.ok) return null;
      const res = await resp.json();
      const data = res.data || {};
      let stream = data.external_audio_h264_m3u8 || data.m3u8_url || data.video_url || null;
      if (stream && stream.startsWith('http')) stream = this.getProxyUrl(stream);
      let viSubUrl = null;
      if (Array.isArray(data.subtitle_list)) {
        data.subtitle_list.forEach(s => {
          const lang = (s.language || '').toLowerCase();
          const disp = (s.display_name || '').toLowerCase();
          if (lang.includes('vi') || disp.includes('việt')) {
            viSubUrl = s.subtitle || s.vtt || null;
          }
        });
      }
      if (viSubUrl && viSubUrl.startsWith('http')) viSubUrl = this.getProxyUrl(viSubUrl);
      return { url: stream, subtitleUrl: viSubUrl };
    } catch (e) {
      return null;
    }
  }
};
