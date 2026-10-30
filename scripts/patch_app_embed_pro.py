import sys

sys.stdout.reconfigure(encoding='utf-8')

app_path = "HuyCa_Web/js/app.js"
with open(app_path, "r", encoding="utf-8") as f:
    app_content = f.read()

# 1. Remove the failed proxy rewrite in playVideo (lines 2917-2920)
target_proxy_rewrite = """    // Tự động chuyển đổi NguonC embed URL sang luồng HLS trực tiếp qua Cloudflare Proxy
    if (streamUrl && (streamUrl.includes('streamc.xyz') || streamUrl.includes('embed.php')) && !streamUrl.includes('/api/proxy')) {
      streamUrl = `/api/proxy?type=nguonc&ext=.m3u8&url=${encodeURIComponent(streamUrl)}`;
    }

"""
if target_proxy_rewrite in app_content:
    app_content = app_content.replace(target_proxy_rewrite, "", 1)
    print("✅ Removed failed proxy rewrite from playVideo")
else:
    print("ℹ️ Proxy rewrite not present or already removed")

# 2. Patch if (isEmbed) block
target_embed_block = """    if (isEmbed) {
      video.style.display = 'none';
      if (iframe) {
        iframe.style.display = 'block';
        iframe.src = streamUrl;
      }
      if (progress) progress.style.display = 'none';
      return;
    } else {
      if (iframe) {
        iframe.src = '';
        iframe.style.display = 'none';
      }
      video.style.display = 'block';
    }"""

replacement_embed_block = """    if (isEmbed) {
      video.style.display = 'none';

      // NGUỒN C EMBED & ĐA TÊN MIỀN DỰ PHÒNG (CHỐNG LỖI DNS ERR_NAME_NOT_RESOLVED)
      const isNguonCEmbed = streamUrl.includes('streamc.xyz') || streamUrl.includes('embed.php?hash=');
      let currentEmbedUrl = streamUrl;
      const embedMirrors = [
        'embed17.streamc.xyz',
        'embed1.streamc.xyz',
        'embed2.streamc.xyz',
        'embed5.streamc.xyz',
        'embed18.streamc.xyz',
        'embed13.streamc.xyz',
        'embed14.streamc.xyz'
      ];
      let currentMirrorIdx = 0;

      if (isNguonCEmbed) {
        const hashMatch = streamUrl.match(/hash=([a-f0-9]+)/i);
        const hash = hashMatch ? hashMatch[1] : '';
        // Tự động chuyển đổi nếu là embed14 (thường bị nhà mạng VN lỗi DNS) sang embed17 hoặc embed1
        if (streamUrl.includes('embed14.streamc.xyz') && hash) {
          currentEmbedUrl = `https://embed17.streamc.xyz/embed.php?hash=${hash}`;
        }

        // Tạo hoặc cập nhật Embed Helper Toolbar trên Player
        let helperBar = document.getElementById('embedHelperBar');
        if (!helperBar) {
          helperBar = document.createElement('div');
          helperBar.id = 'embedHelperBar';
          helperBar.className = 'embed-helper-bar';
          const mainArea = document.getElementById('playerMainArea') || container;
          if (mainArea) mainArea.appendChild(helperBar);
        }
        helperBar.style.display = 'flex';
        helperBar.innerHTML = `
          <button id="btnSwitchEmbedMirror" class="btn-embed-action focusable" title="Chuyển sang Server Embed dự phòng khi bị lỗi DNS hoặc tải chậm">
            <span>🔄</span> Đổi Server Embed
          </button>
          <a id="btnOpenEmbedNewTab" href="${currentEmbedUrl}" target="_blank" rel="noopener noreferrer" class="btn-embed-action focusable" title="Mở trang phát trực tiếp trong tab mới">
            <span>↗️</span> Mở Tab Mới
          </a>
          <button id="btnReloadEmbed" class="btn-embed-action focusable" title="Tải lại trình phát">
            <span>🔁</span> Tải Lại
          </button>
        `;

        const btnSwitch = document.getElementById('btnSwitchEmbedMirror');
        if (btnSwitch) {
          btnSwitch.onclick = (e) => {
            e.stopPropagation();
            if (hash) {
              currentMirrorIdx = (currentMirrorIdx + 1) % embedMirrors.length;
              const nextDomain = embedMirrors[currentMirrorIdx];
              currentEmbedUrl = `https://${nextDomain}/embed.php?hash=${hash}`;
              if (iframe) iframe.src = currentEmbedUrl;
              const btnTab = document.getElementById('btnOpenEmbedNewTab');
              if (btnTab) btnTab.href = currentEmbedUrl;
              showToast(`🔄 Đang chuyển sang Server Embed dự phòng: ${nextDomain}...`);
            } else {
              showToast('⚠️ Không tìm thấy hash tập phim.');
            }
          };
        }

        const btnReload = document.getElementById('btnReloadEmbed');
        if (btnReload) {
          btnReload.onclick = (e) => {
            e.stopPropagation();
            if (iframe) iframe.src = currentEmbedUrl;
            showToast('🔁 Đang tải lại khung phát...');
          };
        }
      } else {
        const helperBar = document.getElementById('embedHelperBar');
        if (helperBar) helperBar.style.display = 'none';
      }

      if (iframe) {
        iframe.style.display = 'block';
        iframe.src = currentEmbedUrl;
      }
      if (progress) progress.style.display = 'none';
      return;
    } else {
      const helperBar = document.getElementById('embedHelperBar');
      if (helperBar) helperBar.style.display = 'none';
      if (iframe) {
        iframe.src = '';
        iframe.style.display = 'none';
      }
      video.style.display = 'block';
    }"""

if target_embed_block in app_content:
    app_content = app_content.replace(target_embed_block, replacement_embed_block, 1)
    print("✅ Patched isEmbed block with mirror rotation and helper bar")
else:
    print("❌ target_embed_block not found in app.js")

# 3. Patch closePlayer to hide embedHelperBar
target_close = """    const iframe = document.getElementById('playerIframe');
    if (iframe) {
      iframe.src = '';
      iframe.style.display = 'none';
    }"""

replacement_close = """    const iframe = document.getElementById('playerIframe');
    if (iframe) {
      iframe.src = '';
      iframe.style.display = 'none';
    }
    const helperBar = document.getElementById('embedHelperBar');
    if (helperBar) helperBar.style.display = 'none';"""

if target_close in app_content and "embedHelperBar" not in app_content[app_content.find("function closePlayer"):]:
    app_content = app_content.replace(target_close, replacement_close, 1)
    print("✅ Patched closePlayer to hide embedHelperBar")
else:
    print("ℹ️ closePlayer already patched or target not found")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_content)

# 4. Patch index.html iframe allow attributes
index_path = "HuyCa_Web/index.html"
with open(index_path, "r", encoding="utf-8") as f:
    index_content = f.read()

target_iframe = '<iframe id="playerIframe" style="display:none; width: 100%; height: 100%; border: none; background: #000;" allow="autoplay; fullscreen; encrypted-media"></iframe>'
replacement_iframe = '<iframe id="playerIframe" style="display:none; width: 100%; height: 100%; border: none; background: #000;" allow="autoplay; fullscreen; encrypted-media; picture-in-picture" referrerpolicy="origin"></iframe>'

if target_iframe in index_content:
    index_content = index_content.replace(target_iframe, replacement_iframe, 1)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print("✅ Patched playerIframe attributes in index.html")
else:
    print("ℹ️ playerIframe attributes already updated")

# 5. Patch style.css for embed helper toolbar
css_path = "HuyCa_Web/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

helper_css = """
/* --- Embed Player Helper Toolbar (NguonC Multi-Mirror & New Tab) --- */
.embed-helper-bar {
  position: absolute;
  top: 14px;
  right: 16px;
  z-index: 99;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(15, 23, 42, 0.88);
  backdrop-filter: blur(10px);
  padding: 6px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
  pointer-events: auto;
}
.btn-embed-action {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  transition: all 0.2s ease;
}
.btn-embed-action:hover, .btn-embed-action:focus {
  background: var(--accent-red, #e50914);
  border-color: var(--accent-red, #e50914);
  color: #fff;
  transform: translateY(-1px);
}
@media (max-width: 600px) {
  .embed-helper-bar {
    top: 8px;
    right: 8px;
    padding: 4px 8px;
    gap: 6px;
  }
  .btn-embed-action {
    font-size: 11px;
    padding: 4px 8px;
  }
}
"""

if ".embed-helper-bar" not in css_content:
    css_content += helper_css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)
    print("✅ Appended .embed-helper-bar styles to style.css")
else:
    print("ℹ️ style.css already contains .embed-helper-bar")

print("🎉 Patch applied successfully!")
