import os

# 1. Update index.html for LG and Windows
for path in ['HuyCaBuonCa_LG_webOS/index.html', 'HuyCa_Windows/www/index.html']:
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    old_target = '<input type="range" id="seekBar" class="seek-bar focusable" min="0" max="100" value="0">'
    new_target = '''<div id="seekBufferBar" class="seek-buffer-bar" style="width: 0%;"></div>
            <div id="seekPlayedBar" class="seek-played-bar" style="width: 0%;"></div>
            <input type="range" id="seekBar" class="seek-bar" min="0" max="100" value="0" tabindex="-1">'''

    if old_target in content:
        content = content.replace(old_target, new_target)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")
    else:
        print(f"Old target not found in {path}")

# 2. Update app.js across all 3 platforms
for path in ['HuyCa_Web/js/app.js', 'HuyCaBuonCa_LG_webOS/js/app.js', 'HuyCa_Windows/www/js/app.js']:
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Exclude seekBar from getFocusableCandidates
    old_cand = "if (el.disabled || el.getAttribute('aria-hidden') === 'true') return false;"
    new_cand = "if (el.id === 'seekBar' || el.classList.contains('seek-bar') || el.getAttribute('tabindex') === '-1') return false;\n      if (el.disabled || el.getAttribute('aria-hidden') === 'true') return false;"

    if old_cand in content and "el.id === 'seekBar'" not in content:
        content = content.replace(old_cand, new_cand, 1)

    # Add blur listeners to seekBar
    old_input = """  seekBar.addEventListener('input', () => {
    if (video.duration) {
      const pct = parseFloat(seekBar.value);
      video.currentTime = (pct / 100) * video.duration;
      const playedBar = document.getElementById('seekPlayedBar');
      if (playedBar) playedBar.style.width = pct + '%';
      resetOverlayTimer();
    }
  });"""

    new_input = """  seekBar.addEventListener('input', () => {
    if (video.duration) {
      const pct = parseFloat(seekBar.value);
      video.currentTime = (pct / 100) * video.duration;
      const playedBar = document.getElementById('seekPlayedBar');
      if (playedBar) playedBar.style.width = pct + '%';
      resetOverlayTimer();
    }
  });

  seekBar.addEventListener('change', () => {
    seekBar.blur();
  });
  seekBar.addEventListener('mouseup', () => {
    seekBar.blur();
  });"""

    if old_input in content and "seekBar.addEventListener('change'" not in content:
        content = content.replace(old_input, new_input, 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {path}")
