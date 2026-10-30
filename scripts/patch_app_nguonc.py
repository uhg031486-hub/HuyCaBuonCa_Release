import sys

sys.stdout.reconfigure(encoding='utf-8')

app_path = "HuyCa_Web/js/app.js"
with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Hide modalServerBar on openMovieDetail
target_1 = "updateDetailFavButton(movie);"
replacement_1 = """const srvBarInit = document.getElementById('modalServerBar');
    if (srvBarInit) srvBarInit.style.display = 'none';
    updateDetailFavButton(movie);"""

if target_1 in content and "const srvBarInit =" not in content:
    content = content.replace(target_1, replacement_1, 1)
    print("✅ Patched 1: Hide modalServerBar on openMovieDetail")
else:
    print("ℹ️ Patch 1 already present or target not found")

# 2. Patch NguonC detail loading
target_2 = """      } else if (movie.slug && movie.slug.startsWith('nguonc:')) {
        const realSlug = movie.slug.replace('nguonc:', '');
        const resp = await fetch(`https://phim.nguonc.com/api/film/${realSlug}`);
        if (!resp.ok) throw new Error('NguonC detail error');
        const data = await resp.json();
        const m = data.movie;
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

        if (m.episodes && m.episodes.length > 0) {
          const s = m.episodes[0];
          const items = s.items || [];
          items.forEach((ep, idx) => {
            const btn = document.createElement('button');
            btn.className = 'btn-episode focusable';
            const epTitle = (ep.name && /^\d+$/.test(ep.name)) ? `Tập ${ep.name}` : (ep.name || `Tập ${idx + 1}`);
            btn.textContent = epTitle;
            btn.addEventListener('click', () => {
              modal.style.display = 'none';
              playVideo(ep.m3u8 || ep.embed, movie.name, epTitle, movie, data, idx, 0);
            });
            epGrid.appendChild(btn);
          });

          document.getElementById('btnPlayFirst').onclick = () => {
            modal.style.display = 'none';
            const firstEp = items[0];
            if (firstEp) {
              const epTitle = (firstEp.name && /^\d+$/.test(firstEp.name)) ? `Tập ${firstEp.name}` : (firstEp.name || 'Tập 1');
              playVideo(firstEp.m3u8 || firstEp.embed, movie.name, epTitle, movie, data, 0, 0, false, null, true);
            }
          };
        }
      } else {"""

replacement_2 = """      } else if (movie.slug && movie.slug.startsWith('nguonc:')) {
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
              const epTitle = (it.name && /^\\d+$/.test(it.name)) ? `Tập ${it.name}` : (it.name || `Tập ${itIdx + 1}`);
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

          document.getElementById('btnPlayFirst').onclick = () => {
            modal.style.display = 'none';
            const curSrv = data.episodes[activeSrvIdx] || data.episodes[0];
            const firstEp = curSrv?.server_data?.[0];
            if (firstEp) {
              playVideo(firstEp.link_m3u8 || firstEp.embed, movie.name, `${firstEp.name} (${curSrv.server_name})`, movie, data, 0, activeSrvIdx, false, null, true);
            }
          };
        }
      } else {"""

if target_2 in content:
    content = content.replace(target_2, replacement_2, 1)
    print("✅ Patched 2: NguonC detail normalization and server selector")
else:
    print("❌ Patch 2 target not found")

# 3. Patch playVideo proxying for NguonC embed URLs
target_3 = """    // Đảm bảo luồng R2 mp4 (Gà Mờ Mê Phim) luôn qua proxy có hỗ trợ Range HTTP 206 & CORS"""
replacement_3 = """    // Tự động chuyển đổi NguonC embed URL sang luồng HLS trực tiếp qua Cloudflare Proxy
    if (streamUrl && (streamUrl.includes('streamc.xyz') || streamUrl.includes('embed.php')) && !streamUrl.includes('/api/proxy')) {
      streamUrl = `/api/proxy?type=nguonc&ext=.m3u8&url=${encodeURIComponent(streamUrl)}`;
    }

    // Đảm bảo luồng R2 mp4 (Gà Mờ Mê Phim) luôn qua proxy có hỗ trợ Range HTTP 206 & CORS"""

if target_3 in content and "type=nguonc" not in content:
    content = content.replace(target_3, replacement_3, 1)
    print("✅ Patched 3: playVideo NguonC embed URL conversion")
else:
    print("ℹ️ Patch 3 already present or target not found")

# 4. Patch Hls.isSupported check
target_4 = "if (window.Hls && Hls.isSupported() && streamUrl.includes('.m3u8')) {"
replacement_4 = "if (window.Hls && Hls.isSupported() && (streamUrl.includes('.m3u8') || streamUrl.includes('type=nguonc'))) {"

if target_4 in content:
    content = content.replace(target_4, replacement_4, 1)
    print("✅ Patched 4: Hls.isSupported condition check")
else:
    print("ℹ️ Patch 4 already present or target not found")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 File app.js updated successfully!")
