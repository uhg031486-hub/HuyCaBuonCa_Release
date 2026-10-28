import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = 'HuyCa_Web/js/app.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Sửa videoElem error listener
old_video_error = """  // Video Error Handler with Automatic Proxy Fallback
  let currentActiveStream = '';
  const videoElem = document.getElementById('videoPlayer');
  if (videoElem) {
    videoElem.addEventListener('error', (e) => {
      console.warn('Video playback error detected:', videoElem.error);
      if (currentActiveStream && !videoElem.src.includes('/api/proxy') && currentActiveStream.startsWith('http')) {
        console.log('Retrying video via proxy fallback:', currentActiveStream);
        videoElem.src = `/api/proxy?url=${encodeURIComponent(currentActiveStream)}`;
        videoElem.load();
        videoElem.play().catch(() => {});
      } else {
        showToast('Không thể tải luồng phát video. Vui lòng thử tập khác!');
      }
    });
  }"""

new_video_error = """  // Video Error Handler with Automatic Proxy Fallback
  let currentActiveStream = '';
  const videoElem = document.getElementById('videoPlayer');
  if (videoElem) {
    videoElem.addEventListener('error', (e) => {
      // TUYỆT ĐỐI KHÔNG CAN THIỆP nếu đang phát dạng nhúng (Embed iframe) hoặc videoPlayer đang bị ẩn / src trống:
      if (isEmbedStreamUrl(currentActiveStream) || 
          (videoElem.style.display === 'none') || 
          !videoElem.src || 
          videoElem.src === window.location.href ||
          videoElem.src.endsWith('/')) {
        return;
      }

      console.warn('Video playback error detected:', videoElem.error);
      if (currentActiveStream && !videoElem.src.includes('/api/proxy') && currentActiveStream.startsWith('http')) {
        console.log('Retrying video via proxy fallback:', currentActiveStream);
        videoElem.src = `/api/proxy?url=${encodeURIComponent(currentActiveStream)}`;
        videoElem.load();
        videoElem.play().catch(() => {});
      } else {
        showToast('Không thể tải luồng phát video. Vui lòng thử tập khác!');
      }
    });
  }

  // --- Stream Guard Parent Helper (Giao thức Handshake Chuẩn với Iframe NguonC streamc.xyz) ---
  window.addEventListener('message', (event) => {
    try {
      const data = event.data;
      if (data && data.type === 'stream-guard-hello') {
        const iframe = document.getElementById('playerIframe');
        if (iframe && iframe.contentWindow) {
          iframe.contentWindow.postMessage({
            type: 'stream-parent-state',
            version: 'guard-5',
            id: data.id,
            helperVersion: 'guard-5',
            parentAdblock: 'clear',
            seq: Date.now(),
            supported: true,
            suspected: false
          }, '*');
        }
      }
    } catch(err) {}
  });"""

if old_video_error in content:
    content = content.replace(old_video_error, new_video_error)
    print("✓ Đã vá thành công videoElem error handler & Stream Guard parent helper")
else:
    # Thử normalize line endings
    content_norm = content.replace('\r\n', '\n')
    old_norm = old_video_error.replace('\r\n', '\n')
    new_norm = new_video_error.replace('\r\n', '\n')
    if old_norm in content_norm:
        content = content_norm.replace(old_norm, new_norm)
        print("✓ Đã vá thành công (LF mode)")
    else:
        print("✗ Không tìm thấy old_video_error để thay thế!")
        sys.exit(1)

# 2. Nâng cấp Embed Helper Toolbar trong playVideo
old_embed_block = """        helperBar.innerHTML = `
          <button id="btnSwitchEmbedMirror" class="btn-embed-action focusable" title="Chuyển sang Server Embed dự phòng khi bị lỗi DNS hoặc tải chậm">
            <span>🔄</span> Đổi Server Embed
          </button>
          <a id="btnOpenEmbedNewTab" href="${currentEmbedUrl}" target="_blank" rel="noopener noreferrer" class="btn-embed-action focusable" title="Mở trang phát trực tiếp trong tab mới">
            <span>↗️</span> Mở Tab Mới
          </a>
          <button id="btnReloadEmbed" class="btn-embed-action focusable" title="Tải lại trình phát">
            <span>🔁</span> Tải Lại
          </button>
        `;"""

new_embed_block = """        helperBar.innerHTML = `
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

content_norm = content.replace('\r\n', '\n')
old_eb_norm = old_embed_block.replace('\r\n', '\n')
new_eb_norm = new_embed_block.replace('\r\n', '\n')
if old_eb_norm in content_norm:
    content = content_norm.replace(old_eb_norm, new_eb_norm)
    print("✓ Đã vá thành công Embed Helper Toolbar với Popout Player")
else:
    print("✗ Không tìm thấy old_embed_block")

# Ghi lại file app.js
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Đã cập nhật HuyCa_Web/js/app.js hoàn tất!")
