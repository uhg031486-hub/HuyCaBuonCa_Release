import os

css_path = os.path.join(os.path.dirname(__file__), "HuyCa_Web", "css", "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

old_block = """/* Nút Next nổi bên phải video (Ảnh 3) */
.btn-quick-next-floating {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 15;
  transition: all 0.2s ease;
}
.btn-quick-next-floating:hover {
  background: rgba(37, 99, 235, 0.85);
  transform: translateY(-50%) scale(1.1);
}

/* Overlay điều khiển cảm ứng */
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
  transition: opacity 0.3s ease;
}
.player-overlay.controls-hidden {
  opacity: 0 !important;
  pointer-events: none !important;
}
.player-overlay > * {
  pointer-events: auto;
}

/* Top bar điều khiển chuẩn APK (Ảnh 2) */
.player-top {
  padding: 12px 18px !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.92) 0%, rgba(0, 0, 0, 0.6) 60%, transparent 100%) !important;
  z-index: 22 !important;
}
.player-title-info {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 55%;
}
.btn-player-square {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 8px;
  background: rgba(30, 41, 59, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-player-square:hover,
.btn-player-square.active {
  background: #334155;
  border-color: #facc15;
  color: #facc15;
}
.player-header-text {
  font-size: 14px;
  font-weight: 700;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
}
.player-sep {
  color: #94a3b8;
  margin: 0 4px;
}
.player-subtitle {
  color: #facc15;
  font-weight: 700;
}
.player-top-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Cụm 5 nút nổi trung tâm (Ảnh 2) */
.player-center-controls {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 25;
}
.btn-center-pill {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #facc15;
  font-size: 13px;
  font-weight: 800;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  backdrop-filter: blur(6px);
  transition: all 0.2s ease;
}
.btn-center-pill:hover {
  background: #1e293b;
  transform: scale(1.06);
}
.btn-center-round {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(6px);
  transition: all 0.2s ease;
}
.btn-center-round:hover {
  background: #1e293b;
  transform: scale(1.08);
}
.btn-center-main {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.92);
  border: 2px solid rgba(250, 204, 21, 0.85);
  color: #facc15;
  font-size: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 0 24px rgba(250, 204, 21, 0.35);
  backdrop-filter: blur(8px);
  transition: all 0.2s ease;
}
.btn-center-main:hover {
  transform: scale(1.1);
  background: #1e293b;
}

/* Nút Bỏ qua Intro +85s (Ảnh 2) */
.btn-skip-intro {
  position: absolute;
  right: 24px;
  bottom: 64px;
  background: rgba(234, 179, 8, 0.2) !important;
  border: 1px solid #eab308 !important;
  color: #facc15 !important;
  font-size: 12px !important;
  font-weight: 800 !important;
  padding: 8px 18px !important;
  border-radius: 22px !important;
  cursor: pointer !important;
  z-index: 25 !important;
  box-shadow: 0 2px 14px rgba(234, 179, 8, 0.35) !important;
  backdrop-filter: blur(6px) !important;
  transition: all 0.2s ease !important;
}
.btn-skip-intro:hover {
  background: #eab308 !important;
  color: #000000 !important;
  transform: scale(1.06) !important;
}

/* Bottom Bar (Ảnh 2) */
.player-bottom-bar {
  padding: 12px 20px !important;
  background: linear-gradient(0deg, rgba(0, 0, 0, 0.92) 0%, rgba(0, 0, 0, 0.6) 60%, transparent 100%) !important;
  display: flex !important;
  align-items: center !important;
  gap: 14px !important;
  z-index: 22 !important;
}
.progress-track-wrapper {
  flex: 1 !important;
  display: flex !important;
  align-items: center !important;
}
.btn-fullscreen-toggle {
  background: none;
  border: none;
  color: #facc15;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  transition: transform 0.2s ease;
}
.btn-fullscreen-toggle:hover {
  transform: scale(1.15);
}

/* Nút Mở Khóa khi đã Lock màn hình cảm ứng */
.btn-unlock-touch {
  position: absolute;
  top: 24px;
  left: 24px;
  z-index: 60;
  background: rgba(15, 23, 42, 0.92);
  border: 1px solid #facc15;
  color: #facc15;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 0 16px rgba(250, 204, 21, 0.4);
}"""

new_block = """/* Nút Next nổi bên phải video (Chuẩn kính trong suốt Glassmorphism) */
.btn-quick-next-floating {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  color: #ffffff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 15;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease;
}
.btn-quick-next-floating:hover {
  background: rgba(250, 204, 21, 0.25) !important;
  border-color: #facc15 !important;
  color: #facc15 !important;
  transform: translateY(-50%) scale(1.12);
}

/* Overlay điều khiển cảm ứng */
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
  transition: opacity 0.3s ease;
}
.player-overlay.controls-hidden {
  opacity: 0 !important;
  pointer-events: none !important;
}
.player-overlay > * {
  pointer-events: auto;
}

/* Top bar điều khiển chuẩn APK (Dải mờ nhẹ trong suốt, không che phim) */
.player-top {
  padding: 12px 18px !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.5) 0%, rgba(0, 0, 0, 0.15) 60%, transparent 100%) !important;
  z-index: 22 !important;
}
.player-title-info {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 55%;
}
.btn-player-square {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.12) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: #ffffff;
  font-size: 14px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
  transition: all 0.2s ease;
}
.btn-player-square:hover,
.btn-player-square.active {
  background: rgba(250, 204, 21, 0.25) !important;
  border-color: #facc15 !important;
  color: #facc15 !important;
  transform: scale(1.08);
}
#btnRotatePlayer {
  width: auto !important;
  padding: 0 10px !important;
  font-size: 12px !important;
}
.player-header-text {
  font-size: 14px;
  font-weight: 700;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.9);
}
.player-sep {
  color: #94a3b8;
  margin: 0 4px;
}
.player-subtitle {
  color: #facc15;
  font-weight: 700;
}
.player-top-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Cụm 5 nút nổi trung tâm (Trong suốt 100% Glassmorphism, không che phim) */
.player-center-controls {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 25;
}
.btn-center-pill {
  background: rgba(255, 255, 255, 0.12) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  color: #facc15 !important;
  font-size: 13px;
  font-weight: 800;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
  transition: all 0.2s ease;
}
.btn-center-pill:hover {
  background: rgba(250, 204, 21, 0.25) !important;
  border-color: #facc15 !important;
  transform: scale(1.08);
}
.btn-center-round {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  color: #ffffff !important;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease;
}
.btn-center-round:hover {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: #ffffff !important;
  transform: scale(1.1);
}
.btn-center-main {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(250, 204, 21, 0.15) !important;
  border: 2px solid rgba(250, 204, 21, 0.85) !important;
  color: #facc15 !important;
  font-size: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 0 25px rgba(250, 204, 21, 0.35) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  text-shadow: 0 0 10px rgba(250, 204, 21, 0.6);
  transition: all 0.2s ease;
}
.btn-center-main:hover {
  transform: scale(1.12);
  background: rgba(250, 204, 21, 0.3) !important;
}

/* Nút Bỏ qua Intro +85s (Trong suốt) */
.btn-skip-intro {
  position: absolute;
  right: 24px;
  bottom: 64px;
  background: rgba(234, 179, 8, 0.15) !important;
  border: 1px solid rgba(234, 179, 8, 0.6) !important;
  color: #facc15 !important;
  font-size: 12px !important;
  font-weight: 800 !important;
  padding: 8px 18px !important;
  border-radius: 22px !important;
  cursor: pointer !important;
  z-index: 25 !important;
  box-shadow: 0 2px 14px rgba(234, 179, 8, 0.25) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  transition: all 0.2s ease !important;
}
.btn-skip-intro:hover {
  background: rgba(234, 179, 8, 0.35) !important;
  color: #ffffff !important;
  transform: scale(1.06) !important;
}

/* Bottom Bar (Dải mờ nhẹ trong suốt) */
.player-bottom-bar {
  padding: 12px 20px !important;
  background: linear-gradient(0deg, rgba(0, 0, 0, 0.55) 0%, rgba(0, 0, 0, 0.15) 60%, transparent 100%) !important;
  display: flex !important;
  align-items: center !important;
  gap: 14px !important;
  z-index: 22 !important;
}
.progress-track-wrapper {
  flex: 1 !important;
  display: flex !important;
  align-items: center !important;
}
.btn-fullscreen-toggle {
  background: none;
  border: none;
  color: #facc15;
  font-size: 20px;
  cursor: pointer;
  padding: 4px;
  transition: transform 0.2s ease;
}
.btn-fullscreen-toggle:hover {
  transform: scale(1.15);
}

/* Nút Mở Khóa khi đã Lock màn hình cảm ứng */
.btn-unlock-touch {
  position: absolute;
  top: 24px;
  left: 24px;
  z-index: 60;
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(250, 204, 21, 0.8) !important;
  color: #facc15 !important;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 0 16px rgba(250, 204, 21, 0.3);
}"""

# Normalize newlines
norm_css = css.replace("\r\n", "\n")
norm_old = old_block.replace("\r\n", "\n")
norm_new = new_block.replace("\r\n", "\n")

assert norm_old in norm_css, "old_block not found in css!"
norm_css = norm_css.replace(norm_old, norm_new, 1)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(norm_css)
print("Updated HuyCa_Web/css/style.css with transparent glassmorphism player controls!")

# Also update app.js timeout from 4500 to 3000
app_path = os.path.join(os.path.dirname(__file__), "HuyCa_Web", "js", "app.js")
with open(app_path, "r", encoding="utf-8") as f:
    app_js = f.read()

app_js = app_js.replace("}, 4500);", "}, 3000);", 1)
with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_js)
print("Updated overlayHideTimeout to 3000ms in app.js!")
