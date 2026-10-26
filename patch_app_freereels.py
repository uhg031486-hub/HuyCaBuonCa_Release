import re
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Web\js\app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Cải tiến unlockEpisode để bọc proxy URL
old_unlock = """    async unlockEpisode(seriesId, episodeId) {
      const headers = await this.getAuthorizedHeaders();
      if (!headers) return null;

      const url = `${this.API_BASE}/drama/unlock_episode`;
      const body = JSON.stringify({ series_id: seriesId, episode_id: episodeId, lang: 'vi' });
      try {
        const resp = await fetch(this.getProxyUrl(url), { method: 'POST', headers, body });
        if (!resp.ok) return null;
        const res = await resp.json();
        const data = res.data || {};
        const stream = data.external_audio_h264_m3u8 || data.m3u8_url || data.video_url || null;
        let viSubUrl = null;
        if (Array.isArray(data.subtitle_list)) {
          data.subtitle_list.forEach(s => {
            const lang = (s.language || '').toLowerCase();
            const disp = (s.display_name || '').toLowerCase();
            if (lang.includes('vi') || disp.includes('việt')) {
              viSubUrl = s.vtt || s.subtitle || null;
            }
          });
        }
        return { streamUrl: stream, subtitleUrl: viSubUrl };
      } catch (e) {
        console.warn('FreeReels unlockEpisode err:', e);
        return null;
      }
    },"""

new_unlock = """    async unlockEpisode(seriesId, episodeId) {
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
            if (lang.includes('vi') || disp.includes('việt')) {
              viSubUrl = s.vtt || s.subtitle || null;
            }
          });
        }
        return { streamUrl: stream, subtitleUrl: viSubUrl };
      } catch (e) {
        console.warn('FreeReels unlockEpisode err:', e);
        return null;
      }
    },"""

if old_unlock in content:
    content = content.replace(old_unlock, new_unlock)
    print("1. Replaced unlockEpisode successfully!")
else:
    print("1. Could not find old_unlock!")

# 2. Xóa hàm search duplicate ở cuối FreeReelsClient
duplicate_search = """    async search(keyword) {
      const headers = await this.getAuthorizedHeaders();
      if (!headers) return [];
      try {
        const url = `${this.API_BASE}/search/feed?keyword=${encodeURIComponent(keyword)}&page=1`;
        const resp = await fetch(this.getProxyUrl(url), { headers });
        if (!resp.ok) return [];
        const res = await resp.json();
        const items = res.data?.items || res.data?.list || [];
        const list = [];
        items.forEach(el => {
          const series = el.series || el.info || el;
          const id = series.id || series.key || '';
          const title = series.title || series.name || '';
          const cover = series.cover || series.poster || '';
          const epCount = series.episode_count || '';
          if (id && title) {
            list.push({
              id: `freereels:${id}`,
              name: title,
              slug: `freereels:${id}`,
              originName: `${epCount} tập • Phim Ngắn FreeReels`,
              thumbUrl: cover,
              posterUrl: cover,
              year: '2026',
              quality: '9:16 HD',
              episodeCurrent: `${epCount} tập`,
              source: 'FREEREELS'
            });
          }
        });
        return list;
      } catch (e) {
        return [];
      }
    }"""

if duplicate_search in content:
    content = content.replace(duplicate_search, "")
    print("2. Removed duplicate search function successfully!")
else:
    print("2. Could not find duplicate search function!")

# 3. Chuẩn hóa hàm search chính của FreeReelsClient hỗ trợ cursor paging
old_search_main = """    async search(keyword, page = 1) {
      const headers = await this.getAuthorizedHeaders();
      if (!headers) return [];
      const offset = (page - 1) * 20;
      const nextCursor = page > 1 ? `offset=${offset}&page_size=20` : '';
      const body = {
        keyword: keyword,
        page_size: 20,
        next: nextCursor,
        timestamp: String(Date.now())
      };
      try {
        const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/search/drama`), {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(body)
        });
        if (!resp.ok) return [];
        const res = await resp.json();
        const data = res.data || {};
        const itemsArr = data.items || data.list || [];
        const list = [];
        itemsArr.forEach(el => {
          if (!el || typeof el !== 'object') return;
          const series = (el.series && typeof el.series === 'object') ? el.series : el;
          const id = series.id || series.key || series.series_id || '';
          const title = series.title || series.name || '';
          const cover = series.cover || series.poster || '';
          const epCount = series.episode_count || '';
          if (id && title) {
            const isDubbed = title.toLowerCase().includes('lồng tiếng') || title.toLowerCase().includes('thuyết minh');
            list.push({
              id: `freereels:${id}`,
              name: title,
              slug: `freereels:${id}`,
              originName: isDubbed ? `${epCount} tập • Lồng Tiếng Việt` : `${epCount} tập • Phụ Đề Tiếng Việt`,
              thumbUrl: cover,
              posterUrl: cover,
              year: '2026',
              quality: isDubbed ? '🎙️ Lồng Tiếng' : '🇻🇳 Phụ Đề',
              episodeCurrent: epCount ? `${epCount} tập` : 'Trọn bộ',
              source: 'FREEREELS'
            });
          }
        });
        return list;
      } catch (e) {
        console.warn('FreeReels search error:', e);
        return [];
      }
    },"""

new_search_main = """    searchCursorMap: {},
    async search(keyword, page = 1) {
      const headers = await this.getAuthorizedHeaders();
      if (!headers) return [];
      const cacheKey = `search_${keyword}`;
      if (page <= 1) {
        this.searchCursorMap[cacheKey] = '';
      }
      const cursor = this.searchCursorMap[cacheKey] || '';
      const body = {
        keyword: keyword,
        next: cursor
      };
      try {
        const resp = await fetch(this.getProxyUrl(`${this.API_BASE}/search/drama`), {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(body)
        });
        if (!resp.ok) return [];
        const res = await resp.json();
        const data = res.data || {};
        if (data.next) {
          this.searchCursorMap[cacheKey] = data.next;
        }
        const itemsArr = data.items || data.list || [];
        const list = [];
        itemsArr.forEach(el => {
          if (!el || typeof el !== 'object') return;
          const series = (el.series && typeof el.series === 'object') ? el.series : el;
          const id = series.id || series.key || series.series_id || '';
          const title = series.title || series.name || '';
          const cover = series.cover || series.poster || '';
          const epCount = series.episode_count || '';
          if (id && title) {
            const isDubbed = title.toLowerCase().includes('lồng tiếng') || title.toLowerCase().includes('thuyết minh');
            list.push({
              id: `freereels:${id}`,
              name: title,
              slug: `freereels:${id}`,
              originName: isDubbed ? `${epCount} tập • Lồng Tiếng Việt` : `${epCount} tập • Phụ Đề Tiếng Việt`,
              thumbUrl: cover,
              posterUrl: cover,
              year: '2026',
              quality: isDubbed ? '🎙️ Lồng Tiếng' : '🇻🇳 Phụ Đề',
              episodeCurrent: epCount ? `${epCount} tập` : 'Trọn bộ',
              source: 'FREEREELS'
            });
          }
        });
        return list;
      } catch (e) {
        console.warn('FreeReels search error:', e);
        return [];
      }
    },"""

if old_search_main in content:
    content = content.replace(old_search_main, new_search_main)
    print("3. Updated main search function successfully!")
else:
    print("3. Could not find old_search_main!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Saved app.js successfully!")
