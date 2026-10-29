import re

file_path = 'HuyCa_Web/js/app.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block_match = re.search(r'async getDramaList\(filterUrl, page = 1\) \{.*?return list;\s*\}\s*catch \(e\) \{.*?return \[\];\s*\}\s*\},', content, re.DOTALL)
if not old_block_match:
    print("Could not match old getDramaList block!")
else:
    print("Matched old block! Length:", len(old_block_match.group(0)))
    new_block = '''parseHtmlItems(html) {
      const list = [];
      const seen = new Set();
      const aRegex = /<a[^>]+href="\\/phim\\/([^"/]+)"[^>]*>(.*?)<\\/a>/gs;
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
          const hMatch = body.match(/<h[34][^>]*>(.*?)<\\/h[34]>/s);
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
    },'''
    content = content[:old_block_match.start()] + new_block + content[old_block_match.end():]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully patched app.js!")
