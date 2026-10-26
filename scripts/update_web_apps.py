import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"HuyCaBuonCa_LG_webOS\js\app.js"
win_file_path = r"HuyCa_Windows\www\js\app.js"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Thêm GaMoMePhimClient vào trước FreeReelsClient
gamomephim_js = """
  // --- GaMoMePhim Native Client (v2.7) ---
  const GaMoMePhimClient = {
    BASE_URL: 'https://gamomephim.com',
    async getDramaList(filterUrl, page = 1) {
      try {
        const genrePath = filterUrl.replace('gamomephim://', '');
        const targetUrl = page <= 1 ? `${this.BASE_URL}/${genrePath}` : `${this.BASE_URL}/${genrePath}?page=${page}`;
        const resp = await fetch(targetUrl);
        if (!resp.ok) return [];
        const html = await resp.text();
        const pattern = /<a[^>]+title="([^"]+)"[^>]+href="\\/phim\\/([^"]+)".*?<img[^>]+src="([^"]+)"/gs;
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
        console.warn('GaMoMePhim getDramaList err:', e);
        return [];
      }
    },
    async getDramaDetail(cleanSlug) {
      try {
        const targetUrl = `${this.BASE_URL}/${cleanSlug}`;
        const resp = await fetch(targetUrl);
        if (!resp.ok) return null;
        const html = await resp.text();

        let title = '';
        const titleMatch = html.match(/<h1[^>]*>([^<]+)<\\/h1>/);
        if (titleMatch) title = titleMatch[1].trim();
        if (!title) title = cleanSlug.replace(/-/g, ' ');

        let desc = 'Phim ngắn tiểu kịch lồng tiếng/thuyết minh tiếng Việt trọn bộ cực hay.';
        const descMatch = html.match(/description\\\\":\\\\"([^\\\\"]+)\\\\"/);
        if (descMatch) desc = descMatch[1].replace(/\\\\n/g, '\\n');

        let thumb = '';
        const thumbMatch = html.match(/https:\\/\\/r2\\.gamomephim\\.com\\/thumbnails\\/[^"'\\s<>]+/);
        if (thumbMatch) thumb = thumbMatch[0];

        const streamMatches = [...html.matchAll(/https:\\/\\/r2\\.gamomephim\\.com\\/videos\\/[^\\s"'<>]+\\.mp4/g)];
        const streamUrls = [...new Set(streamMatches.map(m => m[0].replace(/\\\\/g, '')))];

        const tmStream = streamUrls.find(s => s.includes('-tm.mp4'));
        const subStream = streamUrls.find(s => s.includes('-sub.mp4'));

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
        const resp = await fetch(targetUrl);
        if (!resp.ok) return [];
        const html = await resp.text();
        const pattern = /<a[^>]+title="([^"]+)"[^>]+href="\\/phim\\/([^"]+)".*?<img[^>]+src="([^"]+)"/gs;
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
"""

if "const GaMoMePhimClient" not in code:
    code = code.replace("  // --- FreeReels Native API Client (v2.5) ---", gamomephim_js + "\n  // --- FreeReels Native API Client (v2.5) ---")

# 2. Cập nhật SUB_SOURCES
old_sub = """    FREEREELS: [
      { name: "📱 FreeReels Dọc (Phụ Đề & Lồng Tiếng)", key: "freereels_sub://freereels" },
      { name: "🇻🇳 Tiểu Kịch Vietsub (KKPhim HD)", key: "freereels_sub://kkphim" },
      { name: "💎 DramaBox Hot (Tuyển Chọn Hay Nhất)", key: "freereels_sub://dramabox" }
    ],"""

new_sub = """    FREEREELS: [
      { name: "🎙️ Gà Mờ Mê Phim (Thuyết Minh & Vietsub)", key: "freereels_sub://gamomephim" },
      { name: "📱 FreeReels Dọc (Phụ Đề & Lồng Tiếng)", key: "freereels_sub://freereels" },
      { name: "🇻🇳 Tiểu Kịch Vietsub (KKPhim HD)", key: "freereels_sub://kkphim" },
      { name: "💎 DramaBox Hot (Tuyển Chọn Hay Nhất)", key: "freereels_sub://dramabox" }
    ],"""

code = code.replace(old_sub, new_sub)

# 3. Cập nhật SUB_FILTERS
old_sub_filters = """    'freereels_sub://freereels': ["""
new_sub_filters = """    'freereels_sub://gamomephim': [
      { name: "🔥 Toàn Bộ Tiểu Kịch Mới", url: "gamomephim://the-loai/hien-dai" },
      { name: "👑 Cưới Trước Yêu Sau & Tổng Tài", url: "gamomephim://the-loai/cuoi-truoc-yeu-sau" },
      { name: "🐉 Trọng Sinh & Báo Thù", url: "gamomephim://the-loai/trong-sinh" },
      { name: "🏰 Cổ Trang & Xuyên Không", url: "gamomephim://the-loai/co-trang" },
      { name: "🍵 Trà Xanh Nam & Ngược Tâm", url: "gamomephim://the-loai/tra-xanh-nam" },
      { name: "✨ Chữa Lành & Thanh Xuân", url: "gamomephim://the-loai/chua-lanh" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'freereels_sub://freereels': ["""

if "'freereels_sub://gamomephim'" not in code:
    code = code.replace(old_sub_filters, new_sub_filters)

# 4. Cập nhật loadMovies
old_load_movies = """      // Xử lý Phim Ngắn FreeReels Bản Quyền Dọc
      if (currentFilter.startsWith('freereels://')) {"""

new_load_movies = """      // Xử lý Phim Ngắn GaMoMePhim Thuyết Minh
      if (currentFilter.startsWith('gamomephim://')) {
        let gmMovies = await GaMoMePhimClient.getDramaList(currentFilter, currentPage);
        if (gmMovies.length > 0) {
          currentMoviesList = gmMovies;
          renderMovieGrid(currentMoviesList, false);
          if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim ngắn (Trang ${currentPage})`;
        } else {
          if (paginationInfo) paginationInfo.textContent = `Đã tải toàn bộ ${currentMoviesList.length} phim ngắn trong danh mục này.`;
        }
        hideLoading();
        return;
      }

      // Xử lý Phim Ngắn FreeReels Bản Quyền Dọc
      if (currentFilter.startsWith('freereels://')) {"""

if "currentFilter.startsWith('gamomephim://')" not in code:
    code = code.replace(old_load_movies, new_load_movies)

# 5. Cập nhật loadDetail
old_load_detail = """      if (movie.slug && movie.slug.startsWith('freereels:')) {"""

new_load_detail = """      if (movie.slug && movie.slug.startsWith('gamomephim:')) {
        const realSlug = movie.slug.replace('gamomephim:', '');
        const data = await GaMoMePhimClient.getDramaDetail(realSlug);
        if (!data) throw new Error('GaMoMePhim detail error');
        currentMovieDetail = data;
        const m = currentMovieDetail;
        document.getElementById('detailTitle').textContent = m.name;
        document.getElementById('detailOriginTitle').textContent = m.originName ? `(${m.originName})` : '';
        document.getElementById('detailDesc').textContent = m.content || 'Phim ngắn tiểu kịch thuyết minh & vietsub Full HD.';
        document.getElementById('detailYear').textContent = m.year || '2026';
        document.getElementById('detailTime').textContent = m.time || 'Trọn bộ';
        document.getElementById('detailQuality').textContent = m.quality || 'Full HD';
        document.getElementById('detailLang').textContent = m.lang || 'Thuyết Minh';
        document.getElementById('detailTags').innerHTML = `
          <span class="tag-badge">Thể loại: Phim Ngắn Tiểu Kịch</span>
          <span class="tag-badge">Nguồn: Gà Mờ Mê Phim</span>
        `;
        document.getElementById('detailPoster').src = m.posterUrl || m.thumbUrl;
        document.getElementById('detailBackdrop').src = m.posterUrl || m.thumbUrl;

        renderServerTabs(m.episodes);
        if (m.episodes.length > 0) {
          renderEpisodesList(m.episodes[0].server_data);
          const firstEp = m.episodes[0].server_data[0];
          playBtn.onclick = () => playEpisode(firstEp);
        }
        showScreen('detail');
        hideLoading();
        return;
      }

      if (movie.slug && movie.slug.startsWith('freereels:')) {"""

if "movie.slug.startsWith('gamomephim:')" not in code:
    code = code.replace(old_load_detail, new_load_detail)

# 6. Cập nhật search
old_search = """    // 2. Search in FreeReels
    try {
      const frResults = await FreeReelsClient.search(kw);"""

new_search = """    // 1.5. Search in GaMoMePhim
    try {
      const gmResults = await GaMoMePhimClient.search(kw);
      if (gmResults && gmResults.length > 0) results.push(...gmResults);
    } catch (e) {
      console.warn('Search GaMoMePhim err:', e);
    }

    // 2. Search in FreeReels
    try {
      const frResults = await FreeReelsClient.search(kw);"""

if "Search in GaMoMePhim" not in code:
    code = code.replace(old_search, new_search)

# Lưu cả 2 file
with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)
with open(win_file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Đã cập nhật GaMoMePhim cho webOS và Windows thành công!")
