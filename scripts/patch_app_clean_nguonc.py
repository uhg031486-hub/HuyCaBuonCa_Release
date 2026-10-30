import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('HuyCa_Web/js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ẩn nút directBtn trong Modal Chi Tiết
old_direct = """          // Nút Xem Trực Tiếp / Pop-out cho Nguồn C
          const directBtn = document.getElementById('btnDirectPlayDetail');
          if (directBtn) {
            directBtn.style.display = 'inline-flex';
            directBtn.onclick = () => {
              const curSrv = data.episodes[activeSrvIdx] || data.episodes[0];
              const firstEp = curSrv?.server_data?.[0];
              if (firstEp && (firstEp.embed || firstEp.link_m3u8)) {
                const targetUrl = firstEp.embed || firstEp.link_m3u8;
                window.open(targetUrl, '_blank', 'noopener,noreferrer');
                showToast('↗️ Đang mở luồng phát trực tiếp trong tab mới...');
              }
            };
          }"""

new_direct = """          // Nút Xem Trực Tiếp / Pop-out cho Nguồn C: Ẩn hoàn toàn để bảo vệ người dùng không bị văng ra tab quảng cáo ngoài
          const directBtn = document.getElementById('btnDirectPlayDetail');
          if (directBtn) {
            directBtn.style.display = 'none';
          }"""

assert old_direct in content, "old_direct not found!"
content = content.replace(old_direct, new_direct, 1)

# 2. isEmbedUrl: Thêm /api/nguonc_stream
old_embed_check = "u.includes('chunklist') || u.includes('playlist') || u.includes('/api/proxy')) {"
new_embed_check = "u.includes('chunklist') || u.includes('playlist') || u.includes('/api/proxy') || u.includes('/api/nguonc_stream')) {"
assert old_embed_check in content, "old_embed_check not found!"
content = content.replace(old_embed_check, new_embed_check, 1)

# 3. playVideo: Tự động chuyển đổi streamUrl NguonC sang luồng M3U8 sạch
old_play_head = """    // Đảm bảo luồng R2 mp4 (Gà Mờ Mê Phim) luôn qua proxy có hỗ trợ Range HTTP 206 & CORS
    if (streamUrl && (streamUrl.includes('r2.gamomephim.com') || streamUrl.includes('gamomephim')) && !streamUrl.includes('/api/proxy')) {
      streamUrl = `/api/proxy?url=${encodeURIComponent(streamUrl)}`;
    }"""

new_play_head = """    // GIẢI MÃ VÀ PHÁT LUỒNG NGUỒN C SẠCH 100% (ZERO ADS, NATIVE HLS)
    if (streamUrl && (streamUrl.includes('streamc.xyz') || streamUrl.includes('embed.php?hash='))) {
      streamUrl = `/api/nguonc_stream?url=${encodeURIComponent(streamUrl)}`;
    }

    // Đảm bảo luồng R2 mp4 (Gà Mờ Mê Phim) luôn qua proxy có hỗ trợ Range HTTP 206 & CORS
    if (streamUrl && (streamUrl.includes('r2.gamomephim.com') || streamUrl.includes('gamomephim')) && !streamUrl.includes('/api/proxy')) {
      streamUrl = `/api/proxy?url=${encodeURIComponent(streamUrl)}`;
    }"""

assert old_play_head in content, "old_play_head not found!"
content = content.replace(old_play_head, new_play_head, 1)

# 4. Hls.isSupported() condition
old_hls_cond = "if (window.Hls && Hls.isSupported() && (streamUrl.includes('.m3u8') || streamUrl.includes('type=nguonc'))) {"
new_hls_cond = "if (window.Hls && Hls.isSupported() && (streamUrl.includes('.m3u8') || streamUrl.includes('type=nguonc') || streamUrl.includes('/api/nguonc_stream'))) {"
assert old_hls_cond in content, "old_hls_cond not found!"
content = content.replace(old_hls_cond, new_hls_cond, 1)

# 5. embedHelperBar: Loại bỏ hoàn toàn link mở tab ngoài (btnOpenEmbedNewTab), cập nhật Popout sang popout.html
old_helper_bar = """        helperBar.innerHTML = `
          <button id="btnSwitchEmbedMirror" class="btn-embed-action focusable" title="Chuyển sang Server Embed dự phòng khi bị lỗi DNS hoặc tải chậm">
            <span>🔄</span> Đổi Server
          </button>
          <button id="btnPopoutPlayer" class="btn-embed-action btn-popout-action focusable" title="Mở cửa sổ trình phát độc lập 16:9 sắc nét, không bị kẹt bảo mật iframe">
            <span>🗔</span> Cửa Sổ Riêng
          </button>
          <a id="btnOpenEmbedNewTab" href="${currentEmbedUrl}" target="_blank" rel="noopener noreferrer" class="btn-embed-action btn-direct-tab focusable" title="Mở trang phát trực tiếp trong tab mới">
            <span>↗️</span> Mở Tab Mới
          </a>
          <button id="btnReloadEmbed" class="btn-embed-action focusable" title="Tải lại trình phát">
            <span>🔁</span> Tải Lại
          </button>
        `;

        const btnPop = document.getElementById('btnPopoutPlayer');
        if (btnPop) {
          btnPop.onclick = (e) => {
            e.stopPropagation();
            const w = Math.min(1280, window.screen.availWidth || 1200);
            const h = Math.min(720, window.screen.availHeight || 680);
            const left = Math.max(0, Math.floor((window.screen.availWidth - w) / 2));
            const top = Math.max(0, Math.floor((window.screen.availHeight - h) / 2));
            const popWin = window.open(
              currentEmbedUrl,
              'HuyCaNguonCPlayer',
              `width=${w},height=${h},top=${top},left=${left},menubar=no,toolbar=no,location=no,status=no,resizable=yes,scrollbars=no`
            );
            if (popWin) {
              popWin.focus();
              showToast('🗔 Đã mở trình phát độc lập!');
            } else {
              window.open(currentEmbedUrl, '_blank', 'noopener,noreferrer');
              showToast('↗️ Đã mở luồng phát trực tiếp trong tab mới!');
            }
          };
        }"""

new_helper_bar = """        helperBar.innerHTML = `
          <button id="btnSwitchEmbedMirror" class="btn-embed-action focusable" title="Chuyển sang Server Embed dự phòng khi bị lỗi DNS hoặc tải chậm">
            <span>🔄</span> Đổi Server
          </button>
          <button id="btnPopoutPlayer" class="btn-embed-action btn-popout-action focusable" title="Mở cửa sổ trình phát độc lập 16:9 sắc nét, sạch bóng quảng cáo">
            <span>🗔</span> Cửa Sổ Riêng
          </button>
          <button id="btnReloadEmbed" class="btn-embed-action focusable" title="Tải lại trình phát">
            <span>🔁</span> Tải Lại
          </button>
        `;

        const btnPop = document.getElementById('btnPopoutPlayer');
        if (btnPop) {
          btnPop.onclick = (e) => {
            e.stopPropagation();
            const w = Math.min(1280, window.screen.availWidth || 1200);
            const h = Math.min(720, window.screen.availHeight || 680);
            const left = Math.max(0, Math.floor((window.screen.availWidth - w) / 2));
            const top = Math.max(0, Math.floor((window.screen.availHeight - h) / 2));
            const popUrl = `/popout.html?stream=${encodeURIComponent(currentEmbedUrl)}&title=${encodeURIComponent(currentPlayingMovie ? currentPlayingMovie.name : 'Huy Cá')}`;
            const popWin = window.open(
              popUrl,
              'HuyCaCleanPlayer',
              `width=${w},height=${h},top=${top},left=${left},menubar=no,toolbar=no,location=no,status=no,resizable=yes,scrollbars=no`
            );
            if (popWin) {
              popWin.focus();
              showToast('🗔 Đã mở trình phát độc lập không quảng cáo!');
            }
          };
        }"""

assert old_helper_bar in content, "old_helper_bar not found!"
content = content.replace(old_helper_bar, new_helper_bar, 1)

# Also remove btnTab reference in btnSwitchEmbedMirror
old_switch = """              const btnTab = document.getElementById('btnOpenEmbedNewTab');
              if (btnTab) btnTab.href = currentEmbedUrl;"""
new_switch = """              // btnOpenEmbedNewTab đã được loại bỏ hoàn toàn để bảo vệ người dùng"""
if old_switch in content:
    content = content.replace(old_switch, new_switch, 1)

with open('HuyCa_Web/js/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Đã cập nhật thành công HuyCa_Web/js/app.js!")
