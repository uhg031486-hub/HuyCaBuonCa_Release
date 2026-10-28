import sys

sys.stdout.reconfigure(encoding='utf-8')

for path in [
    'HuyCa_Windows/www/js/app.js',
    'HuyCaBuonCa_LG_webOS/js/app.js'
]:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update filter "gamomephim://the-loai/hien-dai" to "gamomephim://phim-moi"
    content = content.replace(
        '{ name: "✨ Toàn Bộ Tiểu Kịch Mới", url: "gamomephim://the-loai/hien-dai" }',
        '{ name: "✨ Toàn Bộ Tiểu Kịch Mới", url: "gamomephim://phim-moi" }'
    )

    # 2. Add FreeReelsClient.search method
    old_method_end = '''        if (filterUrl === 'freereels://dubbed_vi') {
          const dubbed = list.filter(m => m.name.toLowerCase().includes('lồng tiếng') || m.name.toLowerCase().includes('thuyết minh'));
          if (dubbed.length > 0) return dubbed;
        }
        return list;
      } catch (e) {
        console.warn('FreeReels getDramaList err:', e);
        return [];
      }
    },'''

    new_search_method = '''        if (filterUrl === 'freereels://dubbed_vi') {
          const dubbed = list.filter(m => m.name.toLowerCase().includes('lồng tiếng') || m.name.toLowerCase().includes('thuyết minh'));
          if (dubbed.length > 0) return dubbed;
        }
        return list;
      } catch (e) {
        console.warn('FreeReels getDramaList err:', e);
        return [];
      }
    },

    async search(keyword, page = 1) {
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
        const resp = await fetch(`${this.API_BASE}/search/drama`, {
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
    },'''

    assert old_method_end in content, f"Could not find old_method_end in {path}"
    content = content.replace(old_method_end, new_search_method)

    # 3. Update loadMovies handlers for multi_short:// and gamomephim://
    old_load_handlers = '''      // Xử lý Kho Tiểu Kịch Đa Nền Tảng (KKPhim/NguonC Short)
      if (currentFilter.startsWith('multi_short://')) {
        const kwMap = {
          'multi_short://tong-tai': 'tổng tài',
          'multi_short://trong-sinh': 'trọng sinh',
          'multi_short://chien-than': 'chiến thần',
          'multi_short://thieu-gia': 'thiếu gia',
          'multi_short://co-trang': 'cổ trang',
          'multi_short://hao-mon': 'hào môn'
        };
        const searchKw = kwMap[currentFilter] || 'tổng tài';
        let searchResults = await searchKKPhim(searchKw);
        currentMoviesList = searchResults;
        renderMovieGrid(currentMoviesList, false);
        if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim ngắn theo chủ đề (Trang ${currentPage})`;
        hideLoading();
        return;
      }

      // Xử lý Phim Ngắn GaMoMePhim Thuyết Minh
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
      }'''

    new_load_handlers = '''      // Xử lý Kho Tiểu Kịch Đa Nền Tảng (FreeReels + GaMoMePhim + KKPhim - Vuốt Vô Cực)
      if (currentFilter.startsWith('multi_short://')) {
        const mapInfo = {
          'multi_short://tong-tai': { kw: 'tổng tài', alts: ['bá đạo', 'boss'], gm: 'the-loai/cuoi-truoc-yeu-sau' },
          'multi_short://trong-sinh': { kw: 'trọng sinh', alts: ['trùng sinh', 'báo thù'], gm: 'the-loai/trong-sinh' },
          'multi_short://chien-than': { kw: 'chiến thần', alts: ['tu tiên', 'cao thủ'], gm: 'the-loai/co-trang' },
          'multi_short://thieu-gia': { kw: 'thiếu gia', alts: ['đại gia', 'tỷ phú'], gm: 'the-loai/hien-dai' },
          'multi_short://co-trang': { kw: 'cổ trang', alts: ['cung đấu', 'hoàng phi'], gm: 'the-loai/co-trang' },
          'multi_short://hao-mon': { kw: 'hào môn', alts: ['hôn nhân', 'kết hôn'], gm: 'the-loai/cuoi-truoc-yeu-sau' }
        };
        const info = mapInfo[currentFilter] || { kw: 'tổng tài', alts: ['bá đạo'], gm: 'the-loai/cuoi-truoc-yeu-sau' };

        let newItems = await FreeReelsClient.search(info.kw, currentPage);
        if (newItems.length < 10 && info.alts.length > 0) {
          try {
            const altItems = await FreeReelsClient.search(info.alts[0], currentPage);
            newItems = newItems.concat(altItems);
          } catch(e) {}
        }

        if (currentPage <= 2 && info.gm) {
          try {
            const gmItems = await GaMoMePhimClient.getDramaList(info.gm, currentPage);
            newItems = newItems.concat(gmItems);
          } catch(e) {}
        }

        if (currentPage === 1) {
          try {
            const kkItems = await searchKKPhim(info.kw);
            newItems = newItems.concat(kkItems);
          } catch(e) {}
        }

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
          renderMovieGrid(currentMoviesList, false);
        } else {
          currentMoviesList.push(...uniqueItems);
          renderMovieGrid(currentMoviesList, true);
        }

        if (paginationContainer) paginationContainer.style.display = 'flex';
        if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim ngắn theo chủ đề (Trang ${currentPage})`;
        if (btnLoadMore) {
          btnLoadMore.style.display = 'inline-flex';
          const nextPageEl = document.getElementById('nextPageNum');
          if (nextPageEl) nextPageEl.textContent = currentPage + 1;
        }
        if (spinner) spinner.style.display = 'none';

        // Tự động tải trước trang 2 ở lần đầu để danh sách cực kỳ phong phú
        if (reset && currentPage === 1 && uniqueItems.length >= 10) {
          setTimeout(() => { if (!isLoading) loadMoreMovies(); }, 250);
        }

        hideLoading();
        return;
      }

      // Xử lý Phim Ngắn GaMoMePhim Thuyết Minh (Hỗ trợ phân trang vô cực)
      if (currentFilter.startsWith('gamomephim://')) {
        let gmMovies = await GaMoMePhimClient.getDramaList(currentFilter, currentPage);
        if (reset) {
          currentMoviesList = gmMovies;
          renderMovieGrid(currentMoviesList, false);
        } else {
          const seen = new Set(currentMoviesList.map(m => m.slug));
          const unique = gmMovies.filter(m => !seen.has(m.slug));
          currentMoviesList.push(...unique);
          renderMovieGrid(currentMoviesList, true);
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

        hideLoading();
        return;
      }'''

    assert old_load_handlers in content, f"Could not find old_load_handlers in {path}"
    content = content.replace(old_load_handlers, new_load_handlers)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Successfully updated {path}")
