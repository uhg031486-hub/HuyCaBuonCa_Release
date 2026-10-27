// Dịch vụ kết nối trực tiếp các kho phim thật (KKPhim, NguonC, FreeReels/ReelShort & Live TV) cho Huy Cá Cinema

const KKPHIM_IMG_BASE = 'https://phimimg.com/';

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
    year: item.year ? String(item.year) : '2026',
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

// Mở chi tiết bộ phim & danh sách tập thật (.m3u8 & embed) từ KKPhim hoặc FreeReels
export async function resolveMovieDetailAndStream(movie) {
  if (!movie) return null;

  // 1. Nếu là Kênh TV hoặc đã có sẵn videoUrl/streamUrl
  if (movie.isLiveTv) {
    return movie;
  }
  if (movie.videoUrl && movie.episodes && movie.episodes.length > 0) {
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
    let data = null;
    try {
      const res = await fetch(`https://phimapi.com/phim/${encodeURIComponent(slug)}`);
      if (res.ok) data = await res.json();
    } catch (e) {}

    // Fallback qua proxy nếu bị chặn
    if (!data || !data.movie) {
      try {
        const pRes = await fetch(`/api/proxy?url=${encodeURIComponent('https://phimapi.com/phim/' + slug)}`);
        if (pRes.ok) data = await pRes.json();
      } catch (e) {}
    }

    // Fallback qua OPhim
    if (!data || !data.movie) {
      try {
        const oRes = await fetch(`https://ophim1.com/phim/${encodeURIComponent(slug)}`);
        if (oRes.ok) data = await oRes.json();
      } catch (e) {}
    }

    if (data && data.movie) {
      const mInfo = data.movie || {};
      const servers = data.episodes || [];
      const allEpisodes = [];
      servers.forEach((srv) => {
        const srvName = srv.server_name || 'VIP';
        (srv.server_data || []).forEach((ep) => {
          if (ep.link_m3u8 || ep.link_embed) {
            allEpisodes.push({
              id: `${srvName}_${ep.slug || ep.name}`,
              name: servers.length > 1 ? `${ep.name} (${srvName.replace(/#[a-zA-Z0-9]+/g, '').trim()})` : ep.name,
              url: ep.link_m3u8 || ep.link_embed,
              m3u8Url: ep.link_m3u8 || '',
              embedUrl: ep.link_embed || '',
              serverName: srvName
            });
          }
        });
      });

      if (allEpisodes.length > 0) {
        const firstEp = allEpisodes[0];
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
          videoUrl: firstEp.url,
          embedUrl: firstEp.embedUrl || '',
          currentEpisode: firstEp.name
        };
      }
    }
  }

  // 4. Nếu là phim mẫu chưa có slug thật -> Tìm kiếm theo tên trên KKPhim
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

// Client kết nối FreeReels (Phim Ngắn Dọc 9:16 có phụ đề tiếng Việt)
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
    await this.authenticate();
    const t = String(Date.now());
    const sign = (typeof md5 === 'function') ? md5(`${this.authKey || ''}${t}${this.APP_SECRET}`) : 'sign_cinematic';
    return {
      'Content-Type': 'application/json',
      'device-id': this.deviceId,
      'device-hash': this.deviceId,
      'auth-key': this.authKey || '',
      'timestamp': t,
      'signature': sign,
      'lang': 'vi'
    };
  },

  async fetchShortDramas(page = 0) {
    try {
      const headers = await this.getHeaders();
      if (!headers) return [];
      const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/recommend/anonymous/home_v2`), { headers });
      if (!resp.ok) return [];
      const res = await resp.json();
      const list = [];
      const columns = res.data?.columns || [];
      columns.forEach(col => {
        (col.list || []).forEach(item => {
          const info = item.info || item;
          const id = info.id || info.series_id;
          const title = info.title;
          const cover = info.cover || info.poster;
          const epCount = info.episodes_num || 80;
          if (id && title && !list.some(x => x.id === `freereels:${id}`)) {
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
