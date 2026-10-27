import os

file_path = os.path.join(os.path.dirname(__file__), "HuyCa_Web", "js", "app.js")
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update fetchRealtimePremierLeagueMatches
old_fetch = """  // Tải danh sách trận đấu Ngoại Hạng Anh thời gian thực từ FPL Premier League API
  async function fetchRealtimePremierLeagueMatches() {
    try {
      const leagues = [
        { code: 'eng.1', name: '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh', chName: 'True Premier Football 1 HD', chSlug: 'sports_sat_true_premier_1' },
        { code: 'uefa.champions', name: '🏆 Cúp C1 Châu Âu', chName: 'True Premier Football 2 HD', chSlug: 'sports_sat_true_premier_2' },
        { code: 'esp.1', name: '🇪🇸 La Liga', chName: 'Astro SuperSport 1 HD', chSlug: 'sports_sat_astro_supersport_1' },
        { code: 'ita.1', name: '🇮🇹 Serie A', chName: 'Astro SuperSport 2 HD', chSlug: 'sports_sat_astro_supersport_2' }
      ];

      const matches = [];

      for (const lg of leagues) {
        try {
          const resp = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lg.code}/scoreboard`);
          if (!resp.ok) continue;
          const data = await resp.json();
          const events = data.events || [];
          for (const ev of events) {
            const mId = ev.id || '';
            const dateIso = ev.date || '';
            let timeFormatted = 'Hôm nay';
            if (dateIso) {
              const d = new Date(dateIso);
              const vnHour = String(d.getHours()).padStart(2, '0');
              const vnMin = String(d.getMinutes()).padStart(2, '0');
              const vnDay = String(d.getDate()).padStart(2, '0');
              const vnMonth = String(d.getMonth() + 1).padStart(2, '0');
              timeFormatted = `${vnHour}:${vnMin} • ${vnDay}/${vnMonth}`;
            }

            const state = ev.status?.type?.state || 'pre';
            const detail = ev.status?.type?.detail || '';
            const comps = ev.competitions?.[0]?.competitors || [];
            let teamHome = '', teamAway = '', logoHome = DEFAULT_TV_LOGO, logoAway = DEFAULT_TV_LOGO;
            let scoreHome = '', scoreAway = '';
            for (const item of comps) {
              const tName = item.team?.displayName || '';
              const tLogo = item.team?.logo || DEFAULT_TV_LOGO;
              const sc = item.score || '';
              if (item.homeAway === 'home') {
                teamHome = tName; logoHome = tLogo; scoreHome = sc;
              } else {
                teamAway = tName; logoAway = tLogo; scoreAway = sc;
              }
            }

            const isLive = (state === 'in');
            const isFinished = (state === 'post');
            let scoreStr = timeFormatted;
            if (isLive) {
              scoreStr = `🔴 LIVE • ${scoreHome} - ${scoreAway}`;
            } else if (isFinished) {
              scoreStr = `🏁 FT • ${scoreHome} - ${scoreAway}`;
            }

            matches.push({
              id: `espn_${mId}`,
              tournament: lg.name,
              teamA: teamHome || 'Đội Nhà',
              teamB: teamAway || 'Đội Khách',
              teamALogo: logoHome,
              teamBLogo: logoAway,
              time: scoreStr,
              timeStr: timeFormatted,
              isLive: isLive,
              isFinished: isFinished,
              channelName: lg.chName,
              channelSlug: lg.chSlug
            });
          }
        } catch (e) {
          console.warn('Lỗi fetch giải:', lg.code, e);
        }
      }

      if (matches.length > 0) {
        matches.sort((a, b) => {
          if (a.isLive && !b.isLive) return -1;
          if (!a.isLive && b.isLive) return 1;
          if (!a.isFinished && b.isFinished) return -1;
          if (a.isFinished && !b.isFinished) return 1;
          return 0;
        });
        return matches;
      }
      return [];
    } catch (err) {
      console.warn('ESPN fetch error:', err);
      return [];
    }
  }"""

new_fetch = """  // Tải danh sách trận đấu Ngoại Hạng Anh thời gian thực từ FPL Premier League API
  async function fetchRealtimePremierLeagueMatches() {
    try {
      const leagues = [
        { code: 'eng.1', name: '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh', chName: 'True Premier Football 1 HD', chSlug: 'sports_sat_true_premier_1' },
        { code: 'uefa.champions', name: '🏆 Cúp C1 Châu Âu', chName: 'True Premier Football 2 HD', chSlug: 'sports_sat_true_premier_2' },
        { code: 'esp.1', name: '🇪🇸 La Liga', chName: 'Astro SuperSport 1 HD', chSlug: 'sports_sat_astro_supersport_1' },
        { code: 'ita.1', name: '🇮🇹 Serie A', chName: 'Astro SuperSport 2 HD', chSlug: 'sports_sat_astro_supersport_2' }
      ];

      const fetchLeague = async (lg) => {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 2500);
          const resp = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${lg.code}/scoreboard`, {
            signal: controller.signal
          });
          clearTimeout(timeoutId);
          if (!resp.ok) return [];
          const data = await resp.json();
          const events = data.events || [];
          const res = [];
          for (const ev of events) {
            const mId = ev.id || '';
            const dateIso = ev.date || '';
            let timeFormatted = 'Hôm nay';
            if (dateIso) {
              const d = new Date(dateIso);
              const vnHour = String(d.getHours()).padStart(2, '0');
              const vnMin = String(d.getMinutes()).padStart(2, '0');
              const vnDay = String(d.getDate()).padStart(2, '0');
              const vnMonth = String(d.getMonth() + 1).padStart(2, '0');
              timeFormatted = `${vnHour}:${vnMin} • ${vnDay}/${vnMonth}`;
            }

            const state = ev.status?.type?.state || 'pre';
            const comps = ev.competitions?.[0]?.competitors || [];
            let teamHome = '', teamAway = '', logoHome = DEFAULT_TV_LOGO, logoAway = DEFAULT_TV_LOGO;
            let scoreHome = '', scoreAway = '';
            for (const item of comps) {
              const tName = item.team?.displayName || '';
              const tLogo = item.team?.logo || DEFAULT_TV_LOGO;
              const sc = item.score || '';
              if (item.homeAway === 'home') {
                teamHome = tName; logoHome = tLogo; scoreHome = sc;
              } else {
                teamAway = tName; logoAway = tLogo; scoreAway = sc;
              }
            }

            const isLive = (state === 'in');
            const isFinished = (state === 'post');
            let scoreStr = timeFormatted;
            if (isLive) {
              scoreStr = `🔴 LIVE • ${scoreHome} - ${scoreAway}`;
            } else if (isFinished) {
              scoreStr = `🏁 FT • ${scoreHome} - ${scoreAway}`;
            }

            res.push({
              id: `espn_${mId}`,
              tournament: lg.name,
              teamA: teamHome || 'Đội Nhà',
              teamB: teamAway || 'Đội Khách',
              teamALogo: logoHome,
              teamBLogo: logoAway,
              time: scoreStr,
              timeStr: timeFormatted,
              isLive: isLive,
              isFinished: isFinished,
              channelName: lg.chName,
              channelSlug: lg.chSlug
            });
          }
          return res;
        } catch (e) {
          return [];
        }
      };

      const results = await Promise.allSettled(leagues.map(fetchLeague));
      const matches = [];
      for (const r of results) {
        if (r.status === 'fulfilled' && Array.isArray(r.value)) {
          matches.push(...r.value);
        }
      }

      if (matches.length > 0) {
        matches.sort((a, b) => {
          if (a.isLive && !b.isLive) return -1;
          if (!a.isLive && b.isLive) return 1;
          if (!a.isFinished && b.isFinished) return -1;
          if (a.isFinished && !b.isFinished) return 1;
          return 0;
        });
        return matches;
      }
      return LIVE_MATCHES;
    } catch (err) {
      console.warn('ESPN fetch error:', err);
      return LIVE_MATCHES;
    }
  }"""

if old_fetch in text:
    text = text.replace(old_fetch, new_fetch)
    print("1. Replaced fetchRealtimePremierLeagueMatches successfully!")
else:
    print("1. old_fetch not matched!")

# 2. Update showScheduleModal
old_sched = """  // --- Football Matches Modal ---
  async function showScheduleModal() {
    const modal = document.getElementById('scheduleModal');
    const list = document.getElementById('matchesList');
    list.innerHTML = '<div style="color:#8899a6; padding:20px; text-align:center;">Đang tải lịch thi đấu thời gian thực...</div>';
    modal.style.display = 'flex';

    const matches = await fetchRealtimePremierLeagueMatches();
    const displayList = matches.length > 0 ? matches : LIVE_MATCHES;
    list.innerHTML = '';

    displayList.forEach(m => {
      const card = document.createElement('div');
      card.className = 'match-card focusable';
      card.tabIndex = 0;
      card.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px;">
          ${m.teamALogo ? `<img src="${m.teamALogo}" style="width:24px; height:24px; object-fit:contain;" />` : ''}
          <div>
            <div class="match-league">${m.tournament}</div>
            <div class="match-teams">${m.teamA} vs ${m.teamB}</div>
            <div class="match-channel">📺 Kênh: ${m.channelName || 'Vệ Tinh Trực Tiếp'} • Bấm để xem</div>
          </div>
          ${m.teamBLogo ? `<img src="${m.teamBLogo}" style="width:24px; height:24px; object-fit:contain; margin-left:auto;" />` : ''}
        </div>
        <div class="match-time-badge" style="${m.isLive ? 'background:#d32f2f;' : (m.isFinished ? 'background:#37474f;' : '')}">${m.time}</div>
      `;
      card.addEventListener('click', () => {
        modal.style.display = 'none';
        openMatchServerModal(m);
      });
      list.appendChild(card);
    });
  }"""

new_sched = """  function renderScheduleCards(container, matches, modal) {
    if (!container) return;
    container.innerHTML = '';
    matches.forEach(m => {
      const card = document.createElement('div');
      card.className = 'match-card focusable';
      card.tabIndex = 0;
      card.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px;">
          ${m.teamALogo ? `<img src="${m.teamALogo}" style="width:24px; height:24px; object-fit:contain;" onerror="this.style.display='none'" />` : ''}
          <div>
            <div class="match-league">${m.tournament || 'Trực Tiếp Bóng Đá'}</div>
            <div class="match-teams">${m.teamA} vs ${m.teamB}</div>
            <div class="match-channel">📺 Kênh: ${m.channelName || 'Vệ Tinh Trực Tiếp'} • Bấm để xem</div>
          </div>
          ${m.teamBLogo ? `<img src="${m.teamBLogo}" style="width:24px; height:24px; object-fit:contain; margin-left:auto;" onerror="this.style.display='none'" />` : ''}
        </div>
        <div class="match-time-badge" style="${m.isLive ? 'background:#d32f2f;' : (m.isFinished ? 'background:#37474f;' : '')}">${m.time || 'Trực Tiếp'}</div>
      `;
      card.addEventListener('click', () => {
        modal.style.display = 'none';
        openMatchServerModal(m);
      });
      container.appendChild(card);
    });
  }

  // --- Football Matches Modal ---
  async function showScheduleModal() {
    const modal = document.getElementById('scheduleModal');
    const list = document.getElementById('matchesList');
    if (!modal || !list) return;

    // Render ngay lập tức dữ liệu LIVE_MATCHES để không bao giờ bị chờ đợi hay treo trắng
    renderScheduleCards(list, LIVE_MATCHES, modal);
    modal.style.display = 'flex';

    // Cập nhật ngầm từ API thời gian thực
    const matches = await fetchRealtimePremierLeagueMatches();
    if (matches && matches.length > 0) {
      renderScheduleCards(list, matches, modal);
    }
  }"""

if old_sched in text:
    text = text.replace(old_sched, new_sched)
    print("2. Replaced showScheduleModal successfully!")
else:
    print("2. old_sched not matched!")

# 3. Guard openMovieDetail
old_open_movie = """  // --- Detail Modal ---
  async function openMovieDetail(movie) {
    const modal = document.getElementById('detailModal');"""

new_open_movie = """  // --- Detail Modal ---
  async function openMovieDetail(movie) {
    if (!movie) return;
    // BẢO VỆ CHỐNG NHẦM: Nếu là trận đấu bóng đá hoặc kênh TV, không bao giờ mở trang chi tiết phim!
    if (movie.isEplMatch || movie.rawMatch) {
      openMatchServerModal(movie.rawMatch || movie);
      return;
    }
    if (movie.source === 'XEMTIVI' || movie.isTv || movie.isLiveTv) {
      playTvChannelDirectly(movie);
      return;
    }
    const modal = document.getElementById('detailModal');"""

if old_open_movie in text:
    text = text.replace(old_open_movie, new_open_movie)
    print("3. Replaced openMovieDetail guard successfully!")
else:
    print("3. old_open_movie not matched!")

# 4. In loadMovies for tv://schedule and tv://epl, fallback to LIVE_MATCHES
old_sched_filter = """        if (currentFilter === 'tv://schedule') {
          const eplMatches = await fetchRealtimePremierLeagueMatches();
          const matchCards = eplMatches.map(m => ({"""

new_sched_filter = """        if (currentFilter === 'tv://schedule') {
          const eplMatches = await fetchRealtimePremierLeagueMatches();
          const sourceList = (eplMatches && eplMatches.length > 0) ? eplMatches : LIVE_MATCHES;
          const matchCards = sourceList.map(m => ({"""

if old_sched_filter in text:
    text = text.replace(old_sched_filter, new_sched_filter)
    print("4. Replaced tv://schedule fallback successfully!")
else:
    print("4. old_sched_filter not matched!")

old_epl_filter = """        } else if (currentFilter === 'tv://epl') {
          // 1. Tải danh sách trận đấu Ngoại Hạng Anh FPL thời gian thực
          const eplMatches = await fetchRealtimePremierLeagueMatches();
          
          // Tạo các thẻ trận đấu Ngoại Hạng Anh với icon chuông thông báo độc lập
          const matchCards = eplMatches.map(m => {"""

new_epl_filter = """        } else if (currentFilter === 'tv://epl') {
          // 1. Tải danh sách trận đấu Ngoại Hạng Anh FPL thời gian thực
          const eplMatches = await fetchRealtimePremierLeagueMatches();
          const sourceList = (eplMatches && eplMatches.length > 0) ? eplMatches : LIVE_MATCHES;
          
          // Tạo các thẻ trận đấu Ngoại Hạng Anh với icon chuông thông báo độc lập
          const matchCards = sourceList.map(m => {"""

if old_epl_filter in text:
    text = text.replace(old_epl_filter, new_epl_filter)
    print("5. Replaced tv://epl fallback successfully!")
else:
    print("5. old_epl_filter not matched!")

# 6. Ensure card click check is robust
old_card_click = """      // Click card
      card.addEventListener('click', (e) => {
        if (movie.isEplMatch && movie.rawMatch) {
          // Bấm vào trận đấu Ngoại Hạng Anh: Mở bảng chọn 1 trong 4 Server
          openMatchServerModal(movie.rawMatch);
          return;
        }"""

new_card_click = """      // Click card
      card.addEventListener('click', (e) => {
        if (movie.isEplMatch || movie.rawMatch) {
          // Bấm vào trận đấu Ngoại Hạng Anh: Mở bảng chọn 1 trong 4 Server
          openMatchServerModal(movie.rawMatch || movie);
          return;
        }"""

if old_card_click in text:
    text = text.replace(old_card_click, new_card_click)
    print("6. Replaced card click check successfully!")
else:
    print("6. old_card_click not matched!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("All patches applied to app.js!")
