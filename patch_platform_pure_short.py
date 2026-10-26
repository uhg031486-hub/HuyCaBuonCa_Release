import re
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Web\js\app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """      // =========================================================================
      // XỬ LÝ PHÂN LOẠI PHIM NGẮN THEO TỪNG NỀN TẢNG (REELSHORT, DRAMABOX, SHORTMAX, AI CINEMA...)
      // =========================================================================
      if (currentFilter.startsWith('platform_short://')) {
        const platformType = currentFilter.replace('platform_short://', '');
        let newItems = [];

        if (platformType === 'reelshort') {
          // ReelShort: Nền tảng phim ngắn phương Tây Âu Mỹ - Werewolf, Vampire, Tỷ phú, Mafia
          const kwList = ['werewolf', 'vampire', 'alpha', 'billionaire', 'mafia', 'reelshort'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          const frItems = await FreeReelsClient.search(targetKw, currentPage);
          newItems = newItems.concat(frItems);

          if (currentPage === 1) {
            try {
              const alt1 = await FreeReelsClient.search('werewolf', 1);
              const alt2 = await FreeReelsClient.search('billionaire', 1);
              newItems = newItems.concat(alt1, alt2);
            } catch(e) {}
            try {
              const r = await fetch(`https://phimapi.com/v1/api/quoc-gia/au-my?page=1`);
              if (r.ok) {
                const dj = await r.json();
                const arr = (dj.data && dj.data.items) || [];
                const kkList = arr.map(o => ({
                  id: o._id || o.slug,
                  name: o.name,
                  slug: o.slug,
                  originName: (o.origin_name || '') + ' • ReelShort Âu Mỹ',
                  thumbUrl: o.thumb_url && !o.thumb_url.startsWith('http') ? KKPHIM_IMG_BASE + o.thumb_url.replace(/^\//, '') : (o.thumb_url || ''),
                  posterUrl: o.poster_url && !o.poster_url.startsWith('http') ? KKPHIM_IMG_BASE + o.poster_url.replace(/^\//, '') : (o.poster_url || ''),
                  year: o.year || '2026',
                  quality: 'HD Vietsub',
                  episodeCurrent: o.episode_current || 'Trọn bộ',
                  source: 'KKPHIM'
                }));
                newItems = newItems.concat(kkList);
              }
            } catch(e) {}
          }
        } else if (platformType === 'dramabox') {
          // DramaBox: Nền tảng số 1 thế giới
          const kwList = ['dramabox', 'chiếc lồng son', 'vua cờ bạc', 'thoát khỏi', 'tổng tài'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
          if (currentPage <= 2) {
            try {
              const gm = await GaMoMePhimClient.getDramaList('the-loai/cuoi-truoc-yeu-sau', currentPage);
              newItems = newItems.concat(gm);
            } catch(e) {}
          }
        } else if (platformType === 'shortmax') {
          // ShortMax: Tiểu kịch thịnh hành toàn cầu
          const kwList = ['shortmax', 'zombie', 'pixel', 'nghịch tập'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
        } else if (platformType === 'ai-cinema') {
          // AI Cinema: Diễn viên AI đóng, Sora, Sci-Fi, Viễn tưởng Âu Mỹ
          const kwList = ['ai', 'robot', 'scifi', 'viễn tưởng', 'tương lai', 'future'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
          if (currentPage <= 2) {
            try {
              const r = await fetch(`https://phimapi.com/v1/api/the-loai/vien-tuong?page=${currentPage}`);
              if (r.ok) {
                const dj = await r.json();
                const arr = (dj.data && dj.data.items) || [];
                const kkList = arr.map(o => ({
                  id: o._id || o.slug,
                  name: o.name,
                  slug: o.slug,
                  originName: (o.origin_name || '') + ' • Phim AI Viễn Tưởng',
                  thumbUrl: o.thumb_url && !o.thumb_url.startsWith('http') ? KKPHIM_IMG_BASE + o.thumb_url.replace(/^\//, '') : (o.thumb_url || ''),
                  posterUrl: o.poster_url && !o.poster_url.startsWith('http') ? KKPHIM_IMG_BASE + o.poster_url.replace(/^\//, '') : (o.poster_url || ''),
                  year: o.year || '2026',
                  quality: '🤖 AI Visual',
                  episodeCurrent: o.episode_current || 'Trọn bộ',
                  source: 'KKPHIM'
                }));
                newItems = newItems.concat(kkList);
              }
            } catch(e) {}
          }
        } else if (platformType === 'goodshort') {
          // GoodShort, Sereal+, MoboReels, Kalos
          const kwList = ['goodshort', 'sereal', 'moboreels', 'kalos'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
        } else if (platformType === 'miniseries') {
          // Mini Series Vietsub
          try {
            const r = await fetch(`https://phimapi.com/v1/api/the-loai/phim-ngan?page=${currentPage}`);
            if (r.ok) {
              const dj = await r.json();
              const arr = (dj.data && dj.data.items) || [];
              newItems = arr.map(o => ({
                id: o._id || o.slug,
                name: o.name,
                slug: o.slug,
                originName: o.origin_name || '',
                thumbUrl: o.thumb_url && !o.thumb_url.startsWith('http') ? KKPHIM_IMG_BASE + o.thumb_url.replace(/^\//, '') : (o.thumb_url || ''),
                posterUrl: o.poster_url && !o.poster_url.startsWith('http') ? KKPHIM_IMG_BASE + o.poster_url.replace(/^\//, '') : (o.poster_url || ''),
                year: o.year || '2026',
                quality: 'HD Vietsub',
                episodeCurrent: o.episode_current || 'Trọn bộ',
                source: 'KKPHIM'
              }));
            }
          } catch(e) {}
        }"""

new_block = """      // =========================================================================
      // XỬ LÝ PHÂN LOẠI PHIM NGẮN CHUẨN XÁC 100% TIỂU KỊCH (KHÔNG LẪN PHIM LẺ KKPHIM)
      // =========================================================================
      if (currentFilter.startsWith('platform_short://')) {
        const platformType = currentFilter.replace('platform_short://', '');
        let newItems = [];

        if (platformType === 'reelshort') {
          // ReelShort: Tiểu kịch dọc phương Tây (Người sói, Ma cà rồng, Alpha, Tỷ phú ngầm)
          const kwList = ['werewolf', 'alpha', 'vampire', 'billionaire', 'mafia', 'contract lover', 'rejected mate'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
          if (newItems.length < 10) {
            const alt = kwList[currentPage % kwList.length];
            const altItems = await FreeReelsClient.search(alt, 1);
            newItems = newItems.concat(altItems);
          }
        } else if (platformType === 'dramabox') {
          // DramaBox: Tiểu kịch kịch tính số 1 thế giới
          const kwList = ['dramabox', 'chiếc lồng son', 'vua cờ bạc', 'tổng tài', 'báo thù'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
          // Bổ sung tiểu kịch thuyết minh từ GaMoMePhim
          try {
            const gm = await GaMoMePhimClient.getDramaList('the-loai/cuoi-truoc-yeu-sau', currentPage);
            newItems = newItems.concat(gm);
          } catch(e) {}
        } else if (platformType === 'shortmax') {
          // ShortMax: Tiểu kịch thịnh hành (nghịch tập, pixel, zombie)
          const kwList = ['shortmax', 'nghịch tập', 'chiến thần', 'cao thủ', 'zombie'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
        } else if (platformType === 'ai-cinema') {
          // AI Cinema: Tiểu kịch diễn viên AI, Sora, khoa học tương lai
          const kwList = ['ai', 'robot', 'scifi', 'tương lai', 'thực tế ảo'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
          if (newItems.length < 10) {
            const altItems = await FreeReelsClient.search('future', 1);
            newItems = newItems.concat(altItems);
          }
        } else if (platformType === 'goodshort') {
          // GoodShort & Sereal+: Tiểu kịch lãng mạn quốc tế
          const kwList = ['goodshort', 'sereal', 'moboreels', 'tình yêu', 'hào môn'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
        } else if (platformType === 'miniseries') {
          // Mini Series Vietsub: Tuyển tập tiểu kịch trọn bộ
          const kwList = ['tiểu kịch', 'trọn bộ', 'trùng sinh', 'thiếu gia'];
          const targetKw = kwList[(currentPage - 1) % kwList.length];
          newItems = await FreeReelsClient.search(targetKw, currentPage);
          try {
            const gm = await GaMoMePhimClient.getDramaList('the-loai/hien-dai', currentPage);
            newItems = newItems.concat(gm);
          } catch(e) {}
        }"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Replaced platform_short block successfully!")
else:
    print("Could not find old_block! Checking partial match...")
    idx = content.find("platformType === 'reelshort'")
    print("Index of reelshort:", idx)
