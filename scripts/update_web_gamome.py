import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('HuyCa_Web/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Cập nhật SUB_SOURCES['short_src://gamomephim']
old_gm_sub = """    'short_src://gamomephim': [
      { name: "🔥 Tiểu Kịch Hiện Đại Mới", url: "gamomephim://the-loai/hien-dai" },
      { name: "👑 Cưới Trước Yêu Sau & Tổng Tài", url: "gamomephim://the-loai/cuoi-truoc-yeu-sau" },
      { name: "🐉 Trọng Sinh & Báo Thù", url: "gamomephim://the-loai/trong-sinh" },
      { name: "🏰 Cổ Trang & Xuyên Không", url: "gamomephim://the-loai/co-trang" },
      { name: "🍵 Trà Xanh Nam & Ngược Tâm", url: "gamomephim://the-loai/tra-xanh-nam" },
      { name: "✨ Chữa Lành & Thanh Xuân", url: "gamomephim://the-loai/chua-lanh" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],"""

new_gm_sub = """    'short_src://gamomephim': [
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
    ],"""

if old_gm_sub in text:
    text = text.replace(old_gm_sub, new_gm_sub)
    print("Updated GaMoMePhim filters in SUB_SOURCES in Web app.js!")
else:
    print("Warning: old_gm_sub not found in app.js!")

# 2. Cập nhật GaMoMePhimClient.getDramaList với fallback vô cực khi cuộn trang
old_gm_func = """    async getDramaList(filterUrl, page = 1) {
      try {
        const genrePath = filterUrl.replace('gamomephim://', '');
        const targetUrl = page <= 1 ? `${this.BASE_URL}/${genrePath}` : `${this.BASE_URL}/${genrePath}?page=${page}`;
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
        console.warn('GaMoMePhim getDramaList err:', e);
        return [];
      }
    },"""

new_gm_func = """    async getDramaList(filterUrl, page = 1) {
      try {
        const genrePath = filterUrl.replace('gamomephim://', '');
        const targetUrl = page <= 1 ? `${this.BASE_URL}/${genrePath}` : `${this.BASE_URL}/${genrePath}?page=${page}`;
        const resp = await fetch(this.getProxyUrl(targetUrl));
        if (!resp.ok) return [];
        const html = await resp.text();
        const pattern = /<a[^>]+title="([^"]+)"[^>]+href="\/phim\/([^"]+)".*?<img[^>]+src="([^"]+)"/gs;
        let matches = [...html.matchAll(pattern)];
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

        // Tự động fallback sang Phim Mới nếu thể loại này ít phim và hết ở trang tiếp theo (chống lỗi kéo thêm không ra phim)
        if (list.length === 0 && page > 1 && genrePath !== 'phim-moi') {
          try {
            const fbResp = await fetch(this.getProxyUrl(`${this.BASE_URL}/phim-moi?page=${page}`));
            if (fbResp.ok) {
              const fbHtml = await fbResp.text();
              const fbMatches = [...fbHtml.matchAll(pattern)];
              for (const m of fbMatches) {
                const title = m[1].trim();
                const slug = m[2].trim();
                const thumb = m[3].trim();
                if (slug && !seen.has(slug)) {
                  seen.add(slug);
                  list.push({
                    id: `gamomephim:${slug}`,
                    name: title,
                    slug: `gamomephim:${slug}`,
                    originName: 'Gà Mờ Mê Phim • Mới Cập Nhật',
                    thumbUrl: thumb,
                    posterUrl: thumb,
                    year: '2026',
                    quality: '🎙️ Thuyết Minh & Vietsub',
                    episodeCurrent: 'Full Bộ HD',
                    source: 'FREEREELS'
                  });
                }
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
    },"""

if old_gm_func in text:
    text = text.replace(old_gm_func, new_gm_func)
    print("Updated GaMoMePhimClient.getDramaList with infinite fallback in Web app.js!")
else:
    print("Warning: old_gm_func not found in app.js!")

with open('HuyCa_Web/js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("HuyCa_Web/js/app.js updated successfully.")
