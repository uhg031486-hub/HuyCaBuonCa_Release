import os

new_code = """/* ==========================================================================
   TRIET TIEU 100% MOI VIEN XANH / CYAN / OUTLINE / BOX-SHADOW TREN SEEKBAR (CHUAN YOUTUBE)
   ========================================================================== */
body #seekBar,
body .seek-bar,
body #progressContainer,
body .progress-track-wrapper,
body.mode-tv #seekBar,
body.mode-tv .seek-bar,
body.mode-tv #progressContainer,
body.mode-tv .progress-track-wrapper,
html.mode-tv #seekBar,
html.mode-tv .seek-bar,
html.mode-tv #progressContainer,
html.mode-tv .progress-track-wrapper {
  outline: none !important;
  outline-offset: 0 !important;
  border: none !important;
  border-color: transparent !important;
  box-shadow: none !important;
  -webkit-box-shadow: none !important;
  -webkit-tap-highlight-color: transparent !important;
}

body #seekBar:hover,
body #seekBar:focus,
body #seekBar:focus-visible,
body #seekBar:active,
body #seekBar.focused,
body .seek-bar:hover,
body .seek-bar:focus,
body .seek-bar:focus-visible,
body .seek-bar:active,
body .seek-bar.focused,
body.mode-tv #seekBar:hover,
body.mode-tv #seekBar:focus,
body.mode-tv #seekBar:focus-visible,
body.mode-tv #seekBar:active,
body.mode-tv #seekBar.focused,
body.mode-tv .seek-bar:hover,
body.mode-tv .seek-bar:focus,
body.mode-tv .seek-bar:focus-visible,
body.mode-tv .seek-bar:active,
body.mode-tv .seek-bar.focused,
html.mode-tv #seekBar:hover,
html.mode-tv #seekBar:focus,
html.mode-tv #seekBar:focus-visible,
html.mode-tv #seekBar:active,
html.mode-tv #seekBar.focused,
html.mode-tv .seek-bar:hover,
html.mode-tv .seek-bar:focus,
html.mode-tv .seek-bar:focus-visible,
html.mode-tv .seek-bar:active,
html.mode-tv .seek-bar.focused,
body #progressContainer:hover,
body #progressContainer:focus,
body #progressContainer.focused,
body .progress-track-wrapper:hover,
body .progress-track-wrapper:focus,
body .progress-track-wrapper.focused,
body.mode-tv #progressContainer:hover,
body.mode-tv #progressContainer:focus,
body.mode-tv #progressContainer.focused,
body.mode-tv .progress-track-wrapper:hover,
body.mode-tv .progress-track-wrapper:focus,
body.mode-tv .progress-track-wrapper.focused {
  outline: none !important;
  outline-offset: 0 !important;
  border: none !important;
  border-color: transparent !important;
  box-shadow: none !important;
  -webkit-box-shadow: none !important;
  transform: translateY(-50%) !important;
}

body #seekBar::-webkit-slider-runnable-track,
body .seek-bar::-webkit-slider-runnable-track,
body #seekBar::-moz-range-track,
body .seek-bar::-moz-range-track {
  outline: none !important;
  border: none !important;
  box-shadow: none !important;
}

body #seekBar::-webkit-slider-thumb,
body .seek-bar::-webkit-slider-thumb,
body #seekBar::-moz-range-thumb,
body .seek-bar::-moz-range-thumb {
  outline: none !important;
  border: none !important;
}

/* ==========================================================================
   CLEAN CINEMATIC PLAYER OVERLAY & SEAKBAR (CHUAN YOUTUBE - KHONG MO, KHONG XANH)
   ========================================================================== */
.player-container.controls-hidden,
.player-container.controls-hidden * {
  cursor: none !important;
}

.player-overlay.controls-hidden,
.player-overlay.hide {
  opacity: 0 !important;
  pointer-events: none !important;
  transition: opacity 0.3s ease !important;
}

/* Triet tieu 100% outline/border/vien xanh lo tren moi trinh duyet */
input[type="range"]::-moz-focus-outer {
  border: 0 !important;
}
input[type="range"]:focus,
input[type="range"]:focus-visible {
  outline: none !important;
  box-shadow: none !important;
}

"""

paths = [
    'HuyCa_Web/css/style.css',
    'HuyCaBuonCa_LG_webOS/css/style.css',
    'HuyCa_Windows/www/css/style.css'
]

for p in paths:
    if not os.path.exists(p):
        print(f"Skipping {p}: not found")
        continue
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()

    idx = content.find('/* Triệt tiêu 100% viền xanh/cyan khi trỏ chuột vào thanh play */')
    end_idx = content.find('/* Fullscreen chuẩn YouTube: tràn 100vw x 100vh sạch */')

    if idx != -1 and end_idx != -1:
        content = content[:idx] + new_code + content[end_idx:]
        with open(p, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {p} successfully!")
    else:
        print(f"Markers not found in {p} (idx={idx}, end_idx={end_idx})")
