with open(r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Web\js\app.js", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Bọc viSubUrl trong getDramaDetail
old_sub_detail = """          let viSubUrl = null;
          if (Array.isArray(el.subtitle_list)) {
            el.subtitle_list.forEach(s => {
              const lang = (s.language || '').toLowerCase();
              const disp = (s.display_name || '').toLowerCase();
              if (lang.includes('vi') || disp.includes('việt')) {
                viSubUrl = s.vtt || s.subtitle || null;
              }
            });
          }"""

new_sub_detail = """          let viSubUrl = null;
          if (Array.isArray(el.subtitle_list)) {
            el.subtitle_list.forEach(s => {
              const lang = (s.language || '').toLowerCase();
              const disp = (s.display_name || '').toLowerCase();
              if (lang.includes('vi') || disp.includes('việt')) {
                viSubUrl = s.vtt || s.subtitle || null;
              }
            });
          }
          if (viSubUrl && viSubUrl.startsWith('http')) {
            viSubUrl = this.getProxyUrl(viSubUrl);
          }"""

if old_sub_detail in c:
    c = c.replace(old_sub_detail, new_sub_detail)
    print("1. Proxied viSubUrl in getDramaDetail!")

# 2. Bọc viSubUrl trong unlockEpisode
old_sub_unlock = """        let viSubUrl = null;
        if (Array.isArray(data.subtitle_list)) {
          data.subtitle_list.forEach(s => {
            const lang = (s.language || '').toLowerCase();
            const disp = (s.display_name || '').toLowerCase();
            if (lang.includes('vi') || disp.includes('việt')) {
              viSubUrl = s.vtt || s.subtitle || null;
            }
          });
        }
        return { streamUrl: stream, subtitleUrl: viSubUrl };"""

new_sub_unlock = """        let viSubUrl = null;
        if (Array.isArray(data.subtitle_list)) {
          data.subtitle_list.forEach(s => {
            const lang = (s.language || '').toLowerCase();
            const disp = (s.display_name || '').toLowerCase();
            if (lang.includes('vi') || disp.includes('việt')) {
              viSubUrl = s.vtt || s.subtitle || null;
            }
          });
        }
        if (viSubUrl && viSubUrl.startsWith('http')) {
          viSubUrl = this.getProxyUrl(viSubUrl);
        }
        return { streamUrl: stream, subtitleUrl: viSubUrl };"""

if old_sub_unlock in c:
    c = c.replace(old_sub_unlock, new_sub_unlock)
    print("2. Proxied viSubUrl in unlockEpisode!")

# 3. Thêm crossOrigin cho video khi có sub trong playVideo
old_track_code = """      if (subUrl) {
        const track = document.createElement('track');
        track.kind = 'subtitles';
        track.srclang = 'vi';
        track.label = 'Tiếng Việt';
        track.src = subUrl;
        track.default = true;
        video.appendChild(track);
      }"""

new_track_code = """      if (subUrl) {
        video.crossOrigin = 'anonymous';
        const track = document.createElement('track');
        track.kind = 'subtitles';
        track.srclang = 'vi';
        track.label = 'Tiếng Việt';
        track.src = subUrl;
        track.default = true;
        video.appendChild(track);
      } else {
        video.removeAttribute('crossorigin');
      }"""

if old_track_code in c:
    c = c.replace(old_track_code, new_track_code)
    print("3. Configured crossOrigin for subtitle track!")

with open(r"C:\Users\yoga\Documents\Cac Project Cua Huy\AntiGravity\HuyCa_Web\js\app.js", "w", encoding="utf-8") as f:
    f.write(c)
print("Updated subtitle handling successfully!")
