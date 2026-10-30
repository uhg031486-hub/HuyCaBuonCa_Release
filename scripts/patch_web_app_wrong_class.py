path = "HuyCa_Web/js/app.js"
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update anime default URLs
text = text.replace(
    '{ name: "Anime Mới Cập Nhật", url: "https://phimapi.com/v1/api/quoc-gia/nhat-ban" }',
    '{ name: "Anime Mới Cập Nhật", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" }'
)
text = text.replace(
    '{ name: "3D Mới Cập Nhật", url: "https://phimapi.com/v1/api/quoc-gia/trung-quoc" }',
    '{ name: "3D Mới Cập Nhật", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" }'
)

# 2. Xử lý short_filter và short_dramabox gọi FreeReels thay vì KKPhim tìm kiếm
target_short = """      // Xử lý Tiểu Kịch Vietsub & DramaBox
      let fetchUrl = '';
      if (currentFilter.startsWith('short_filter://') || currentFilter.startsWith('short_dramabox://')) {
        let kw = 'tổng tài';
        if (currentFilter.includes('trong-sinh')) kw = 'trọng sinh';
        if (currentFilter.includes('ngon-tinh')) kw = 'hôn nhân';
        if (currentFilter.includes('hai-huoc')) kw = 'hài hước';
        if (currentFilter.includes('chienthan')) kw = 'chiến thần';
        if (currentFilter.includes('thieugia')) kw = 'thiếu gia';
        if (currentFilter.includes('cotrang')) kw = 'cung đấu';
        fetchUrl = `https://phimapi.com/v1/api/tim-kiem?keyword=${encodeURIComponent(kw)}&page=${currentPage}`;
      } else {
        const sep = currentFilter.includes('?') ? '&' : '?';
        fetchUrl = `${currentFilter}${sep}page=${currentPage}`;
      }"""

replacement_short = """      // Xử lý Tiểu Kịch Vietsub & DramaBox (Gọi trực tiếp FreeReels chuẩn dọc 9:16, không trộn phim dài tập KKPhim)
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
      const fetchUrl = `${currentFilter}${sep}page=${currentPage}`;"""

assert target_short in text, "Target short not found in app.js"
text = text.replace(target_short, replacement_short, 1)

# 3. Chặn phim thường ngồi nhầm lớp sang Anime trong loadMoreMovies
target_anim_filter = """      let items = [];
      if (data.items && Array.isArray(data.items)) {
        items = data.items;
      } else if (data.data && data.data.items && Array.isArray(data.data.items)) {
        items = data.data.items;
      }"""

replacement_anim_filter = """      let items = [];
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
      }"""

assert target_anim_filter in text, "Target anim filter not found in app.js"
text = text.replace(target_anim_filter, replacement_anim_filter, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("HuyCa_Web/js/app.js updated successfully!")
