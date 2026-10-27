import os
import re

# 1. Update CSS
css_path = os.path.join(os.path.dirname(__file__), "HuyCa_Web", "css", "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

old_css_start = "/* Nút Next nổi bên phải video (Chuẩn kính trong suốt Glassmorphism) */"
old_css_end = "/* --- SIDEBAR DANH SÁCH TẬP WINDOWS / DESKTOP (Ảnh 3) --- */"

new_css = """/* ==========================================================================
   CINEMA PRO VIDEO PLAYER (Netflix / Apple TV+ High-End Streaming Design)
   ========================================================================== */

/* Overlay điều khiển mượt mà */
.player-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 20;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.player-overlay.controls-hidden {
  opacity: 0 !important;
  pointer-events: none !important;
}

.player-overlay > * {
  pointer-events: auto;
}

/* 1. TOP BAR (Thanh tiêu đề kính mờ thanh thoát) */
.player-top {
  padding: 16px 28px !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.75) 0%, rgba(0, 0, 0, 0.35) 50%, transparent 100%) !important;
  z-index: 22 !important;
}

.player-title-info {
  display: flex;
  align-items: center;
  gap: 14px;
  max-width: 60%;
}

.btn-header-action {
  width: 40px;
  height: 40px;
  min-width: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-header-action:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #facc15;
  border-color: rgba(250, 204, 21, 0.4);
  transform: scale(1.08);
}

.btn-rotate-pill {
  width: auto !important;
  min-width: unset !important;
  border-radius: 20px !important;
  padding: 0 14px !important;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
}

.player-header-text {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.player-title {
  font-size: 16px;
  font-weight: 800;
  color: #ffffff;
  letter-spacing: 0.2px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
}

.player-subtitle-badge {
  font-size: 12px;
  font-weight: 800;
  color: #facc15;
  background: rgba(250, 204, 21, 0.15);
  border: 1px solid rgba(250, 204, 21, 0.3);
  padding: 3px 10px;
  border-radius: 12px;
  backdrop-filter: blur(8px);
  white-space: nowrap;
}

.player-top-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 2. CENTER PLAY RIPPLE / SPLASH (Chuẩn Netflix / YouTube) */
.center-play-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.45);
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  z-index: 25;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.center-play-ripple.animate-pulse-scale {
  animation: centerPulse 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes centerPulse {
  0% { transform: translate(-50%, -50%) scale(0.7); opacity: 0; }
  50% { transform: translate(-50%, -50%) scale(1.15); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1); opacity: 0.9; }
}

.center-ripple-svg {
  width: 34px;
  height: 34px;
}

/* 3. CINEMA PRO BOTTOM DOCK (Thanh điều khiển cao cấp tích hợp dưới đáy) */
.player-bottom-bar {
  padding: 20px 28px 18px 28px !important;
  background: linear-gradient(0deg, rgba(0, 0, 0, 0.88) 0%, rgba(0, 0, 0, 0.45) 60%, transparent 100%) !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 12px !important;
  z-index: 22 !important;
}

/* Thanh Scrubber tiến trình chuẩn Rạp chiếu */
.progress-track-wrapper {
  position: relative;
  width: 100%;
  height: 18px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.seek-bar {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  outline: none;
  cursor: pointer;
  transition: height 0.15s ease;
}

.progress-track-wrapper:hover .seek-bar {
  height: 7px;
}

.seek-bar::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #facc15;
  box-shadow: 0 0 10px rgba(250, 204, 21, 0.8);
  cursor: pointer;
  transition: transform 0.15s ease;
}

.progress-track-wrapper:hover .seek-bar::-webkit-slider-thumb {
  transform: scale(1.3);
}

.seek-hover-time {
  position: absolute;
  top: -26px;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.9);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  font-family: monospace;
  pointer-events: none;
  transform: translateX(-50%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

/* Hàng nút điều khiển Dock */
.player-controls-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.controls-left,
.controls-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-ctrl-action {
  background: none;
  border: none;
  color: #e2e8f0;
  padding: 6px 8px;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-ctrl-action:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
  transform: scale(1.1);
}

.btn-ctrl-action.btn-play-pause-main {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #facc15;
}

.btn-ctrl-action.btn-play-pause-main:hover {
  background: rgba(250, 204, 21, 0.25);
  border-color: #facc15;
  color: #facc15;
  transform: scale(1.12);
}

.ctrl-icon {
  width: 22px;
  height: 22px;
}

/* Volume Slider */
.volume-control-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
}

.volume-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 0;
  opacity: 0;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  outline: none;
  cursor: pointer;
  transition: width 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;
}

.volume-control-wrapper:hover .volume-slider,
.volume-slider:focus {
  width: 70px;
  opacity: 1;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ffffff;
  cursor: pointer;
}

/* Time label */
.player-time-display {
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  margin-left: 6px;
  user-select: none;
}

.time-label {
  color: #ffffff;
}

.time-divider {
  color: #64748b;
  margin: 0 2px;
}

/* Speed Badge & Text Buttons */
.btn-ctrl-badge {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-ctrl-badge:hover {
  background: rgba(250, 204, 21, 0.2);
  border-color: #facc15;
  color: #facc15;
  transform: scale(1.06);
}

.btn-ctrl-text {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.btn-skip-intro-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(250, 204, 21, 0.15);
  border: 1px solid rgba(250, 204, 21, 0.5);
  color: #facc15;
  font-size: 12px;
  font-weight: 800;
  padding: 5px 14px;
  border-radius: 20px;
  cursor: pointer;
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 10px rgba(250, 204, 21, 0.2);
  transition: all 0.2s ease;
}

.btn-skip-intro-pill:hover {
  background: #facc15;
  color: #000000;
  transform: scale(1.06);
}

/* Nút Mở Khóa khi đã Lock màn hình cảm ứng */
.btn-unlock-touch {
  position: absolute;
  top: 24px;
  left: 24px;
  z-index: 60;
  background: rgba(0, 0, 0, 0.7) !important;
  border: 1px solid rgba(250, 204, 21, 0.8) !important;
  color: #facc15 !important;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 0 16px rgba(250, 204, 21, 0.3);
}

"""

norm_css = css.replace("\r\n", "\n")
start_idx = norm_css.find(old_css_start)
end_idx = norm_css.find(old_css_end)

if start_idx != -1 and end_idx != -1:
    norm_css = norm_css[:start_idx] + new_css + norm_css[end_idx:]
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(norm_css)
    print("2. Successfully updated HuyCa_Web/css/style.css with Cinema Pro CSS!")
else:
    print(f"2. WARNING: Could not find markers in style.css! start={start_idx}, end={end_idx}")

# 3. Update HuyCa_Web/js/app.js to support the new SVG play/pause toggle and volume controls
app_path = os.path.join(os.path.dirname(__file__), "HuyCa_Web", "js", "app.js")
with open(app_path, "r", encoding="utf-8") as f:
    app_js = f.read()

# Let's add helper to flash center ripple and toggle play/pause SVGs
js_hook = """  // --- Cinema Pro Player Event Handlers ---
  function updatePlayPauseIcons(isPlaying) {
    const svgPlay = document.getElementById('svgPlay');
    const svgPause = document.getElementById('svgPause');
    if (svgPlay) svgPlay.style.display = isPlaying ? 'none' : 'block';
    if (svgPause) svgPause.style.display = isPlaying ? 'block' : 'none';

    // Flash Center Ripple Animation (Netflix / YouTube Style)
    const ripple = document.getElementById('centerPlayRipple');
    const rPlay = document.getElementById('centerRipplePlaySvg');
    const rPause = document.getElementById('centerRipplePauseSvg');
    if (ripple && rPlay && rPause) {
      rPlay.style.display = isPlaying ? 'none' : 'block';
      rPause.style.display = isPlaying ? 'block' : 'none';
      ripple.style.display = 'flex';
      ripple.classList.remove('animate-pulse-scale');
      void ripple.offsetWidth; // force reflow
      ripple.classList.add('animate-pulse-scale');
      setTimeout(() => {
        if (ripple) ripple.style.display = 'none';
      }, 550);
    }
  }

  // Volume slider binding
  const volumeSliderEl = document.getElementById('volumeSlider');
  const btnVolumeToggleEl = document.getElementById('btnVolumeToggle');
  const svgVolumeHighEl = document.getElementById('svgVolumeHigh');
  const svgVolumeMutedEl = document.getElementById('svgVolumeMuted');
  let lastNonZeroVolume = 1;

  if (volumeSliderEl) {
    volumeSliderEl.addEventListener('input', (e) => {
      const v = document.getElementById('videoPlayer');
      const val = parseFloat(e.target.value);
      if (v) {
        v.volume = val;
        v.muted = (val === 0);
      }
      if (val > 0) lastNonZeroVolume = val;
      if (svgVolumeHighEl) svgVolumeHighEl.style.display = (val === 0) ? 'none' : 'block';
      if (svgVolumeMutedEl) svgVolumeMutedEl.style.display = (val === 0) ? 'block' : 'none';
    });
  }

  if (btnVolumeToggleEl) {
    btnVolumeToggleEl.addEventListener('click', () => {
      const v = document.getElementById('videoPlayer');
      if (!v) return;
      if (v.muted || v.volume === 0) {
        v.muted = false;
        v.volume = lastNonZeroVolume || 1;
        if (volumeSliderEl) volumeSliderEl.value = v.volume;
        if (svgVolumeHighEl) svgVolumeHighEl.style.display = 'block';
        if (svgVolumeMutedEl) svgVolumeMutedEl.style.display = 'none';
      } else {
        lastNonZeroVolume = v.volume;
        v.muted = true;
        v.volume = 0;
        if (volumeSliderEl) volumeSliderEl.value = 0;
        if (svgVolumeHighEl) svgVolumeHighEl.style.display = 'none';
        if (svgVolumeMutedEl) svgVolumeMutedEl.style.display = 'block';
      }
      resetOverlayTimer();
    });
  }
"""

# Hook video play/pause event to updatePlayPauseIcons
old_play_event = """  video.addEventListener('play', () => {
    btnPlayPause.textContent = '⏸️ Tạm Dừng';
  });
  video.addEventListener('pause', () => {
    btnPlayPause.textContent = '▶️ Tiếp Tục';
  });"""

new_play_event = """  video.addEventListener('play', () => {
    updatePlayPauseIcons(true);
  });
  video.addEventListener('pause', () => {
    updatePlayPauseIcons(false);
  });"""

if old_play_event in app_js:
    app_js = app_js.replace(old_play_event, new_play_event)
    print("3a. Replaced old play/pause text events with updatePlayPauseIcons!")

# Insert js_hook before initSources or near player init
target_insertion = "  // Cụm 5 nút nổi trung tâm (Ảnh 2)"
if target_insertion in app_js:
    app_js = app_js.replace(target_insertion, js_hook + "\n  // Cụm 5 nút nổi trung tâm (Ảnh 2)")
    print("3b. Inserted js_hook successfully into app.js!")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_js)

print("Step 2 & 3 completed successfully!")
