import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("=== BẮT ĐẦU NÂNG CẤP HIỂN THỊ ĐỦ 2 BIỂU TƯỢNG (LOGO ĐỘI NHÀ & ĐỘI KHÁCH) TRẬN ĐẤU ===")

# 1. Cập nhật app.js
with open("HuyCa_Web/js/app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# 1.1. Cập nhật LIVE_MATCHES với đầy đủ logo chuẩn ESPN cho cả 2 đội
old_live_matches = """  const LIVE_MATCHES = [
    {
      id: "match_c1_1",
      tournament: "🏆 UEFA Champions League",
      teamA: "Real Madrid",
      teamB: "Manchester City",
      time: "Đang diễn ra • Trực Tiếp",
      channelSlug: "sports_vn_vtv6",
      channelName: "VTV6 Thể Thao HD (FPT)"
    },
    {
      id: "match_epl_1",
      tournament: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh",
      teamA: "Arsenal",
      teamB: "Chelsea",
      time: "Hôm Nay • 20:30",
      channelSlug: "sports_intl_cbs_golazo",
      channelName: "CBS Sports Golazo (Cúp C1 / Serie A)"
    },
    {
      id: "match_laliga_1",
      tournament: "🇪🇸 La Liga Tây Ban Nha",
      teamA: "Barcelona",
      teamB: "Atletico Madrid",
      time: "Hôm Nay • 23:00",
      channelSlug: "sports_intl_bein_xtra",
      channelName: "beIN SPORTS XTRA HD"
    },
    {
      id: "match_aff_1",
      tournament: "🇻🇳 AFF Mitsubishi Electric Cup",
      teamA: "Việt Nam",
      teamB: "Thái Lan",
      time: "Ngày Mai • 19:30",
      channelSlug: "vtv5_tay_nam_bo",
      channelName: "VTV5 Tây Nam Bộ"
    },
    {
      id: "match_uel_1",
      tournament: "🏆 UEFA Europa League",
      teamA: "Manchester United",
      teamB: "AS Roma",
      time: "Hôm Nay • 03:00",
      channelSlug: "sports_intl_eurosport_live",
      channelName: "Eurosport Live HD"
    }
  ];"""

new_live_matches = """  const LIVE_MATCHES = [
    {
      id: "match_c1_1",
      tournament: "🏆 UEFA Champions League",
      teamA: "Real Madrid",
      teamB: "Manchester City",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/86.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
      time: "Đang diễn ra • Trực Tiếp",
      channelSlug: "sports_vn_vtv6",
      channelName: "VTV6 Thể Thao HD (FPT)"
    },
    {
      id: "match_epl_1",
      tournament: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh",
      teamA: "Arsenal",
      teamB: "Chelsea",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/359.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/363.png",
      time: "Hôm Nay • 20:30",
      channelSlug: "sports_intl_cbs_golazo",
      channelName: "CBS Sports Golazo (Cúp C1 / Serie A)"
    },
    {
      id: "match_laliga_1",
      tournament: "🇪🇸 La Liga Tây Ban Nha",
      teamA: "Barcelona",
      teamB: "Atletico Madrid",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/83.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/1068.png",
      time: "Hôm Nay • 23:00",
      channelSlug: "sports_intl_bein_xtra",
      channelName: "beIN SPORTS XTRA HD"
    },
    {
      id: "match_aff_1",
      tournament: "🇻🇳 AFF Mitsubishi Electric Cup",
      teamA: "Việt Nam",
      teamB: "Thái Lan",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/2927.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/2926.png",
      time: "Ngày Mai • 19:30",
      channelSlug: "vtv5_tay_nam_bo",
      channelName: "VTV5 Tây Nam Bộ"
    },
    {
      id: "match_uel_1",
      tournament: "🏆 UEFA Europa League",
      teamA: "Manchester United",
      teamB: "AS Roma",
      teamALogo: "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
      teamBLogo: "https://a.espncdn.com/i/teamlogos/soccer/500/104.png",
      time: "Hôm Nay • 03:00",
      channelSlug: "sports_intl_eurosport_live",
      channelName: "Eurosport Live HD"
    }
  ];"""

if old_live_matches in app_js:
    app_js = app_js.replace(old_live_matches, new_live_matches)
    print(" -> [1.1] Đã cập nhật LIVE_MATCHES với đầy đủ teamALogo và teamBLogo.")
else:
    print(" ⚠️ Không tìm thấy old_live_matches chính xác, kiểm tra lại!")

# 1.2. Cập nhật map matchCards ở tv://schedule và tv://epl
target_schedule_map = """          const matchCards = sourceList.map(m => ({
            id: m.id,
            name: `${m.teamA} vs ${m.teamB}`,
            slug: m.id,
            originName: m.tournament,
            thumbUrl: m.teamALogo || DEFAULT_TV_LOGO,
            posterUrl: m.teamALogo || DEFAULT_TV_LOGO,
            quality: m.isLive ? 'LIVE' : 'EPL',
            episodeCurrent: m.time,
            source: 'XEMTIVI',
            isEplMatch: true,
            rawMatch: m,
            hasReminder: isMatchReminderSet(m.id)
          }));"""

new_schedule_map = """          const matchCards = sourceList.map(m => ({
            id: m.id,
            name: `${m.teamA} vs ${m.teamB}`,
            slug: m.id,
            originName: m.tournament,
            thumbUrl: m.teamALogo || DEFAULT_TV_LOGO,
            posterUrl: m.teamALogo || DEFAULT_TV_LOGO,
            teamA: m.teamA,
            teamB: m.teamB,
            teamALogo: m.teamALogo || DEFAULT_TV_LOGO,
            teamBLogo: m.teamBLogo || DEFAULT_TV_LOGO,
            quality: m.isLive ? 'LIVE' : 'EPL',
            episodeCurrent: m.time,
            source: 'XEMTIVI',
            isEplMatch: true,
            rawMatch: m,
            hasReminder: isMatchReminderSet(m.id)
          }));"""

if target_schedule_map in app_js:
    app_js = app_js.replace(target_schedule_map, new_schedule_map)
    print(" -> [1.2] Đã cập nhật map matchCards ở tv://schedule.")

target_epl_map = """            return {
              id: m.id,
              name: `${m.teamA} vs ${m.teamB}`,
              slug: m.id,
              originName: m.tournament,
              thumbUrl: m.teamALogo || DEFAULT_TV_LOGO,
              posterUrl: m.teamALogo || DEFAULT_TV_LOGO,
              quality: m.isLive ? 'LIVE' : 'EPL',
              episodeCurrent: m.time,
              source: 'XEMTIVI',
              isEplMatch: true,
              rawMatch: m,
              hasReminder: hasReminder
            };"""

new_epl_map = """            return {
              id: m.id,
              name: `${m.teamA} vs ${m.teamB}`,
              slug: m.id,
              originName: m.tournament,
              thumbUrl: m.teamALogo || DEFAULT_TV_LOGO,
              posterUrl: m.teamALogo || DEFAULT_TV_LOGO,
              teamA: m.teamA,
              teamB: m.teamB,
              teamALogo: m.teamALogo || DEFAULT_TV_LOGO,
              teamBLogo: m.teamBLogo || DEFAULT_TV_LOGO,
              quality: m.isLive ? 'LIVE' : 'EPL',
              episodeCurrent: m.time,
              source: 'XEMTIVI',
              isEplMatch: true,
              rawMatch: m,
              hasReminder: hasReminder
            };"""

if target_epl_map in app_js:
    app_js = app_js.replace(target_epl_map, new_epl_map)
    print(" -> [1.3] Đã cập nhật map matchCards ở tv://epl.")

# 1.3. Cập nhật renderCards để vẽ giao diện 2 đội song đấu (Home Logo vs Away Logo)
old_render_card_inner = """      const card = document.createElement('div');
      const isTv = movie.source === 'XEMTIVI';
      card.className = `movie-card focusable ${isTv ? 'tv-card' : ''}`;
      card.tabIndex = 0;
      card.dataset.id = movie.id;

      const favBadge = isFavorite(movie.id) ? '<div class="badge-fav">⭐</div>' : '';
      const qualityBadge = `<div class="badge-quality">${movie.quality || 'HD'}</div>`;
      const epBadge = movie.episodeCurrent ? `<div class="badge-episode">${movie.episodeCurrent}</div>` : '';
      const isDesktopLayout = window.innerWidth > 800 && !(/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent || ''));
      const displayImgUrl = isTv
        ? getTvChannelLogo(movie)
        : (isDesktopLayout
            ? (movie.landscapeUrl || movie.thumbUrl || movie.posterUrl || DEFAULT_TV_LOGO)
            : (movie.portraitUrl || movie.posterUrl || movie.thumbUrl || DEFAULT_TV_LOGO));

      card.innerHTML = `
        <div class="poster-wrapper" style="--poster-bg: url('${displayImgUrl}')">
          <img class="card-poster" src="${displayImgUrl}" alt="${movie.name}" onload="if(window.innerWidth>800 && this.naturalHeight>this.naturalWidth*1.12){this.parentElement.classList.add('is-vertical-img');}" onerror="this.onerror=null; this.src='${isTv ? getTvChannelLogo(movie) : (movie.posterUrl || movie.thumbUrl || DEFAULT_TV_LOGO)}';" loading="lazy">
          ${qualityBadge}
          ${favBadge}
          ${epBadge}
        </div>
        <div class="card-info">
          <div class="card-title">${movie.name}</div>
          <div class="card-subtitle">${movie.originName || movie.year || ''}</div>
          ${movie.isEplMatch ? `
            <div style="margin-top: 6px; display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 11px; color: var(--accent-cyan); font-weight: bold;">4 Server Trực Tiếp</span>
              <button class="btn-bell-reminder ${movie.hasReminder ? 'active' : ''}" data-match-id="${movie.id}" title="Thông báo khi đến giờ đá">
                ${movie.hasReminder ? '🔔 Đã Đặt' : '🔔 Nhắc Tôi'}
              </button>
            </div>
          ` : ''}
        </div>
      `;"""

new_render_card_inner = """      const card = document.createElement('div');
      const isTv = movie.source === 'XEMTIVI';
      const isMatch = !!(movie.isEplMatch || movie.rawMatch);

      if (isMatch) {
        // --- GIAO DIỆN TRẬN ĐẤU BÓNG ĐÁ SONG ĐẤU ĐỦ 2 BIỂU TƯỢNG (HOME & AWAY) ---
        const raw = movie.rawMatch || {};
        const teamA = movie.teamA || raw.teamA || 'Đội Nhà';
        const teamB = movie.teamB || raw.teamB || 'Đội Khách';
        const logoA = movie.teamALogo || raw.teamALogo || DEFAULT_TV_LOGO;
        const logoB = movie.teamBLogo || raw.teamBLogo || DEFAULT_TV_LOGO;
        const tournament = raw.tournament || movie.originName || 'BÓNG ĐÁ';
        const isLive = !!(raw.isLive || movie.quality === 'LIVE');
        const badgeText = isLive ? 'LIVE' : (movie.quality || 'EPL');
        const matchTime = movie.episodeCurrent || raw.time || '';
        const vsOrScore = isLive ? (raw.score || '🔴 LIVE') : (raw.isFinished ? (raw.score || '🏁 FT') : 'VS');

        card.className = 'movie-card focusable match-grid-card tv-card';
        card.tabIndex = 0;
        card.dataset.id = movie.id;

        card.innerHTML = `
          <div class="match-grid-card-inner">
            <div class="match-grid-header">
              <span class="match-grid-tournament" title="${tournament}">${tournament}</span>
              <span class="match-grid-badge ${isLive ? 'live' : ''}">${badgeText}</span>
            </div>

            <div class="match-grid-versus">
              <!-- Cột Đội Nhà -->
              <div class="match-team-item team-home">
                <div class="match-team-logo-wrap">
                  <img class="team-crest" src="${logoA}" alt="${teamA}" onerror="this.onerror=null; this.src='https://assets.coingecko.com/coins/images/2518/small/ball.png';" loading="lazy">
                </div>
                <div class="match-team-title" title="${teamA}">${teamA}</div>
              </div>

              <!-- Cột Trung Tâm: VS / Tỷ Số + Giờ Đá -->
              <div class="match-center-pillar">
                <div class="match-vs-text ${isLive ? 'is-live' : ''}">${vsOrScore}</div>
                <div class="match-time-text">${matchTime}</div>
              </div>

              <!-- Cột Đội Khách -->
              <div class="match-team-item team-away">
                <div class="match-team-logo-wrap">
                  <img class="team-crest" src="${logoB}" alt="${teamB}" onerror="this.onerror=null; this.src='https://assets.coingecko.com/coins/images/2518/small/ball.png';" loading="lazy">
                </div>
                <div class="match-team-title" title="${teamB}">${teamB}</div>
              </div>
            </div>

            <div class="match-grid-footer">
              <span class="match-servers-text">⚡ 4 Server Trực Tiếp</span>
              <button class="btn-bell-reminder ${movie.hasReminder ? 'active' : ''}" data-match-id="${movie.id}" title="Thông báo khi đến giờ đá">
                ${movie.hasReminder ? '🔔 Đã Đặt' : '🔔 Nhắc Tôi'}
              </button>
            </div>
          </div>
        `;
      } else {
        // --- GIAO DIỆN PHIM / KÊNH TV THÔNG THƯỜNG ---
        card.className = `movie-card focusable ${isTv ? 'tv-card' : ''}`;
        card.tabIndex = 0;
        card.dataset.id = movie.id;

        const favBadge = isFavorite(movie.id) ? '<div class="badge-fav">⭐</div>' : '';
        const qualityBadge = `<div class="badge-quality">${movie.quality || 'HD'}</div>`;
        const epBadge = movie.episodeCurrent ? `<div class="badge-episode">${movie.episodeCurrent}</div>` : '';
        const isDesktopLayout = window.innerWidth > 800 && !(/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent || ''));
        const displayImgUrl = isTv
          ? getTvChannelLogo(movie)
          : (isDesktopLayout
              ? (movie.landscapeUrl || movie.thumbUrl || movie.posterUrl || DEFAULT_TV_LOGO)
              : (movie.portraitUrl || movie.posterUrl || movie.thumbUrl || DEFAULT_TV_LOGO));

        card.innerHTML = `
          <div class="poster-wrapper" style="--poster-bg: url('${displayImgUrl}')">
            <img class="card-poster" src="${displayImgUrl}" alt="${movie.name}" onload="if(window.innerWidth>800 && this.naturalHeight>this.naturalWidth*1.12){this.parentElement.classList.add('is-vertical-img');}" onerror="this.onerror=null; this.src='${isTv ? getTvChannelLogo(movie) : (movie.posterUrl || movie.thumbUrl || DEFAULT_TV_LOGO)}';" loading="lazy">
            ${qualityBadge}
            ${favBadge}
            ${epBadge}
          </div>
          <div class="card-info">
            <div class="card-title">${movie.name}</div>
            <div class="card-subtitle">${movie.originName || movie.year || ''}</div>
          </div>
        `;
      }"""

if old_render_card_inner in app_js:
    app_js = app_js.replace(old_render_card_inner, new_render_card_inner)
    print(" -> [1.4] Đã cập nhật renderCards để vẽ cặp đấu 2 đội song đấu (Cả 2 Biểu Tượng).")
else:
    print(" ⚠️ Không tìm thấy old_render_card_inner chính xác, kiểm tra lại!")

# 1.4. Cập nhật openMatchServerModal để hiển thị 2 logo trong modal chọn server
old_server_modal_func = """function openMatchServerModal(match) {
    if (!match) return;
    activeMatchForServer = match;
    selectedMatchForServer = match;
    const modal = document.getElementById('matchServerModal');
    if (!modal) return;

    const leagueEl = document.getElementById('serverModalLeague');
    const teamsEl = document.getElementById('serverModalTeams');
    const timeEl = document.getElementById('serverModalTime');

    if (leagueEl) leagueEl.textContent = match.tournament || '🏴󠁧󠁢󠁥󠁮󠁧󠁿 NGOẠI HẠNG ANH';
    if (teamsEl) teamsEl.textContent = `${match.teamA} vs ${match.teamB}`;
    if (timeEl) timeEl.textContent = match.time || 'Trực Tiếp';

    modal.style.display = 'flex';
  }"""

new_server_modal_func = """function openMatchServerModal(match) {
    if (!match) return;
    activeMatchForServer = match;
    selectedMatchForServer = match;
    const modal = document.getElementById('matchServerModal');
    if (!modal) return;

    const leagueEl = document.getElementById('serverModalLeague');
    const teamsEl = document.getElementById('serverModalTeams');
    const timeEl = document.getElementById('serverModalTime');

    if (leagueEl) leagueEl.textContent = match.tournament || '🏴󠁧󠁢󠁥󠁮󠁧󠁿 NGOẠI HẠNG ANH';
    if (teamsEl) {
      const logoA = match.teamALogo || DEFAULT_TV_LOGO;
      const logoB = match.teamBLogo || DEFAULT_TV_LOGO;
      teamsEl.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; gap: 14px; margin: 8px 0; flex-wrap: wrap;">
          <img src="${logoA}" style="width: 44px; height: 44px; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));" onerror="this.style.display='none'">
          <span style="font-size: 20px; font-weight: 900; color: #ffffff;">${match.teamA}</span>
          <span style="font-size: 15px; font-weight: 900; color: #facc15; padding: 2px 8px; background: rgba(250,204,21,0.15); border-radius: 6px;">VS</span>
          <span style="font-size: 20px; font-weight: 900; color: #ffffff;">${match.teamB}</span>
          <img src="${logoB}" style="width: 44px; height: 44px; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));" onerror="this.style.display='none'">
        </div>
      `;
    }
    if (timeEl) timeEl.textContent = match.time || 'Trực Tiếp';

    modal.style.display = 'flex';
  }"""

if old_server_modal_func in app_js:
    app_js = app_js.replace(old_server_modal_func, new_server_modal_func)
    print(" -> [1.5] Đã cập nhật openMatchServerModal với 2 logo đội bóng.")
else:
    print(" ⚠️ Không tìm thấy old_server_modal_func chính xác, kiểm tra lại!")

with open("HuyCa_Web/js/app.js", "w", encoding="utf-8") as f:
    f.write(app_js)
print(" -> Đã ghi đè cập nhật vào HuyCa_Web/js/app.js thành công!")

# 2. Cập nhật CSS trong style.css
with open("HuyCa_Web/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

match_grid_css = """
/* ==========================================================================
   CHUYÊN BIỆT: THẺ TRẬN ĐẤU BÓNG ĐÁ LƯỚI ĐỦ 2 BIỂU TƯỢNG (HUY CÁ v3.3.2)
   ========================================================================== */
.movie-card.match-grid-card {
  background: linear-gradient(145deg, #131b2e 0%, #0d1322 100%) !important;
  border: 1px solid #24324d !important;
  padding: 10px 12px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  min-height: 155px !important;
  height: auto !important;
  box-sizing: border-box !important;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.movie-card.match-grid-card:hover {
  border-color: #00e5ff !important;
  background: linear-gradient(145deg, #18233c 0%, #10182b 100%) !important;
}

body.mode-tv .movie-card.match-grid-card.focused,
body.mode-tv .movie-card.match-grid-card:focus {
  border-color: #00e5ff !important;
  box-shadow: 0 0 16px rgba(0, 229, 255, 0.8), 0 0 6px #00e5ff !important;
  transform: scale(1.04) !important;
  z-index: 10 !important;
}

.match-grid-card-inner {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}

.match-grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  width: 100%;
}

.match-grid-tournament {
  font-size: 11px;
  font-weight: 700;
  color: #38bdf8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 75%;
}

.match-grid-badge {
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  background: #ef4444;
  color: #ffffff;
  text-transform: uppercase;
  flex-shrink: 0;
}

.match-grid-badge.live {
  background: #dc2626;
  animation: pulse-live 1.5s infinite;
}

@keyframes pulse-live {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
  100% { opacity: 1; transform: scale(1); }
}

.match-grid-versus {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  margin: 4px 0 8px 0;
  width: 100%;
}

.match-team-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-width: 0;
}

.match-team-logo-wrap {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  padding: 4px;
  margin-bottom: 5px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-sizing: border-box;
}

.match-team-logo-wrap img.team-crest {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5));
}

.match-team-title {
  font-size: 11.5px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.25;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

.match-center-pillar {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 60px;
  padding: 0 4px;
  flex-shrink: 0;
}

.match-vs-text {
  font-size: 15px;
  font-weight: 900;
  color: #facc15;
  letter-spacing: 0.5px;
  text-shadow: 0 0 8px rgba(250, 204, 21, 0.4);
}

.match-vs-text.is-live {
  color: #ef4444;
  font-size: 13px;
}

.match-time-text {
  font-size: 10px;
  font-weight: 600;
  color: #94a3b8;
  margin-top: 3px;
  white-space: nowrap;
}

.match-grid-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 6px;
  margin-top: auto;
  width: 100%;
}

.match-servers-text {
  font-size: 11px;
  font-weight: 700;
  color: #00e5ff;
}
"""

if "match-grid-card" not in css:
    css += match_grid_css
    with open("HuyCa_Web/css/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print(" -> [2] Đã bổ sung CSS match-grid-card vào HuyCa_Web/css/style.css thành công!")
else:
    print(" -> [2] CSS match-grid-card đã tồn tại trong style.css, tiến hành cập nhật...")
    # Thay thế phần cũ
    old_sec = css[css.find("/* ==========================================================================\n   CHUYÊN BIỆT: THẺ TRẬN ĐẤU BÓNG ĐÁ"):]
    css = css[:css.find("/* ==========================================================================\n   CHUYÊN BIỆT: THẺ TRẬN ĐẤU BÓNG ĐÁ")] + match_grid_css
    with open("HuyCa_Web/css/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    print(" -> [2] Đã ghi đè CSS match-grid-card thành công!")

print("\n🎉 HOÀN TẤT NÂNG CẤP MÃ NGUỒN GIAO DIỆN 2 BIỂU TƯỢNG BÓNG ĐÁ!")
