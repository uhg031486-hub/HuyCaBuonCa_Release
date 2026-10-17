// Huy Cá Buôn Cà - LG Smart TV webOS Edition (v2.1)
(function () {
  'use strict';

  // --- State ---
  let currentSource = 'KKPHIM'; // KKPHIM, ANIMEHAY, XEMTIVI, FREEREELS
  let currentFilter = '';
  let currentPage = 1;
  let isLoading = false;
  let currentMoviesList = [];
  let currentPlayingMovie = null;
  let currentPlayingDetail = null;
  let currentEpisodeIndex = 0;
  let currentServerIndex = 0;
  let hlsInstance = null;
  let overlayTimeout = null;
  let numberZapBuffer = '';
  let numberZapTimeout = null;

  // --- Constants ---
  const KKPHIM_IMG_BASE = 'https://phimimg.com/';
  const DEFAULT_TV_LOGO = 'https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png';

  // --- Match Schedules ---
  const LIVE_MATCHES = [
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
  ];

  // --- Filters per Source ---
  const FILTERS = {
    KKPHIM: [
      { name: "Mới Cập Nhật", url: "https://phimapi.com/danh-sach/phim-moi-cap-nhat" },
      { name: "Phim Bộ", url: "https://phimapi.com/v1/api/danh-sach/phim-bo" },
      { name: "Phim Lẻ", url: "https://phimapi.com/v1/api/danh-sach/phim-le" },
      { name: "Hoạt Hình", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" },
      { name: "TV Shows", url: "https://phimapi.com/v1/api/danh-sach/tv-shows" },
      { name: "Thuyết Minh", url: "https://phimapi.com/v1/api/danh-sach/phim-thuyet-minh" },
      { name: "Lồng Tiếng", url: "https://phimapi.com/v1/api/danh-sach/phim-long-tieng" },
      { name: "Hành Động", url: "https://phimapi.com/v1/api/the-loai/hanh-dong" },
      { name: "Cổ Trang", url: "https://phimapi.com/v1/api/the-loai/co-trang" },
      { name: "Tình Cảm", url: "https://phimapi.com/v1/api/the-loai/tinh-cam" },
      { name: "Kinh Dị", url: "https://phimapi.com/v1/api/the-loai/kinh-di" },
      { name: "Hàn Quốc", url: "https://phimapi.com/v1/api/quoc-gia/han-quoc" },
      { name: "Trung Quốc", url: "https://phimapi.com/v1/api/quoc-gia/trung-quoc" },
      { name: "Âu Mỹ", url: "https://phimapi.com/v1/api/quoc-gia/au-my" },
      { name: "❤️ Phim Yêu Thích", url: "app://favorites" }
    ],
    ANIMEHAY: [
      { name: "Anime Mới Cập Nhật", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" },
      { name: "Anime Hành Động", url: "https://phimapi.com/v1/api/the-loai/hanh-dong" },
      { name: "Anime Thần Thoại", url: "https://phimapi.com/v1/api/the-loai/than-thoai" },
      { name: "Anime Học Đường", url: "https://phimapi.com/v1/api/the-loai/hoc-duong" },
      { name: "Anime Viễn Tưởng", url: "https://phimapi.com/v1/api/the-loai/vien-tuong" },
      { name: "❤️ Anime Yêu Thích", url: "app://favorites" }
    ],
    XEMTIVI: [
      { name: "Tất Cả Kênh", url: "tv://all" },
      { name: "⚽ Lịch Thi Đấu & Bóng Đá", url: "tv://football" },
      { name: "🏆 Thể Thao ESPN & FOX", url: "tv://sports_intl" },
      { name: "🏎️ Đua Xe & Võ Thuật", url: "tv://racing_combat" },
      { name: "VTV Quốc Gia", url: "tv://vtv" },
      { name: "VTVcab", url: "tv://vtvcab" },
      { name: "SCTV", url: "tv://sctv" },
      { name: "Rạp Phim", url: "tv://movies" },
      { name: "Sự Kiện TV360", url: "tv://live" },
      { name: "Kênh Quốc Tế", url: "tv://intl" },
      { name: "Đài Địa Phương", url: "tv://local" },
      { name: "Radio Trực Tuyến", url: "tv://radio" },
      { name: "⭐ Kênh Yêu Thích", url: "tv://favorites" },
      { name: "➕ Thêm Kênh IPTV", url: "tv://custom" }
    ],
    FREEREELS: [
      { name: "🔥 Thịnh Hành", url: "https://phimapi.com/danh-sach/phim-moi-cap-nhat" },
      { name: "✨ Phim Ngắn Mới", url: "https://phimapi.com/v1/api/danh-sach/phim-bo" },
      { name: "❤️ Phim Ngắn Yêu Thích", url: "app://favorites" }
    ]
  };

  // --- Local Storage Storage Helpers ---
  function getFavorites() {
    try {
      return JSON.parse(localStorage.getItem('huycabuonca_favs') || '[]');
    } catch (e) {
      return [];
    }
  }

  function isFavorite(id) {
    const favs = getFavorites();
    return favs.some(item => item.id === id);
  }

  function toggleFavorite(movie) {
    let favs = getFavorites();
    const idx = favs.findIndex(item => item.id === movie.id);
    let added = false;
    if (idx >= 0) {
      favs.splice(idx, 1);
      added = false;
    } else {
      favs.unshift(movie);
      added = true;
    }
    localStorage.setItem('huycabuonca_favs', JSON.stringify(favs));
    showToast(added ? `⭐ Đã thêm "${movie.name}" vào Yêu Thích` : `Đã bỏ Yêu Thích "${movie.name}"`);
    renderHistoryAndFavs();
    return added;
  }

  function getHistory() {
    try {
      return JSON.parse(localStorage.getItem('huycabuonca_history') || '[]');
    } catch (e) {
      return [];
    }
  }

  function saveHistory(movie, currentSec, durationSec, episodeName) {
    if (!movie || !movie.id) return;
    let hist = getHistory().filter(item => item.id !== movie.id);
    const percent = durationSec > 0 ? Math.min(100, Math.round((currentSec / durationSec) * 100)) : 0;
    hist.unshift({
      id: movie.id,
      name: movie.name,
      slug: movie.slug,
      posterUrl: movie.posterUrl || movie.thumbUrl,
      source: movie.source || currentSource,
      episodeName: episodeName || movie.episodeCurrent || 'Tập 1',
      currentSec: Math.round(currentSec),
      durationSec: Math.round(durationSec),
      percent: percent,
      timestamp: Date.now()
    });
    if (hist.length > 30) hist = hist.slice(0, 30);
    localStorage.setItem('huycabuonca_history', JSON.stringify(hist));
    renderHistoryAndFavs();
  }

  function getCustomChannels() {
    try {
      return JSON.parse(localStorage.getItem('huycabuonca_custom_iptv') || '[]');
    } catch (e) {
      return [];
    }
  }

  function getAllChannels() {
    const base = window.INITIAL_TV_CHANNELS || [];
    const custom = getCustomChannels();
    return [...custom, ...base];
  }

  // --- Clock ---
  function updateClock() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const el = document.getElementById('clockDisplay');
    if (el) el.textContent = `${h}:${m}`;
  }
  setInterval(updateClock, 1000);
  updateClock();

  // --- Toast ---
  function showToast(msg) {
    const toast = document.getElementById('toastBox');
    if (!toast) return;
    toast.textContent = msg;
    toast.style.display = 'block';
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => {
      toast.style.display = 'none';
    }, 2800);
  }

  // --- Source Selection ---
  function initSources() {
    const buttons = document.querySelectorAll('.btn-source');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentSource = btn.dataset.source;
        renderFilterBar();
      });
    });
  }

  // --- Render Filter Bar ---
  function renderFilterBar() {
    const bar = document.getElementById('filterBar');
    bar.innerHTML = '';
    const filters = FILTERS[currentSource] || [];
    if (filters.length === 0) return;

    filters.forEach((f, idx) => {
      const btn = document.createElement('button');
      btn.className = `btn-filter focusable ${idx === 0 ? 'active' : ''}`;
      btn.textContent = f.name;
      btn.dataset.url = f.url;
      btn.addEventListener('click', () => {
        bar.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        handleFilterClick(f);
      });
      bar.appendChild(btn);
    });

    // Tự động load filter đầu tiên
    handleFilterClick(filters[0]);
  }

  function handleFilterClick(filterItem) {
    if (filterItem.url === 'tv://football') {
      showScheduleModal();
      return;
    }
    if (filterItem.url === 'tv://custom') {
      showIptvModal();
      return;
    }
    currentFilter = filterItem.url;
    currentPage = 1;
    loadMovies(true);
  }

  // --- Load Movies & TV Channels ---
  async function loadMovies(reset) {
    if (isLoading) return;
    isLoading = true;
    const grid = document.getElementById('mainGrid');

    if (reset) {
      grid.innerHTML = '<div style="color: #94a3b8; font-size: 18px; padding: 20px;">Đang tải danh sách...</div>';
      currentMoviesList = [];
    }

    try {
      if (currentFilter === 'app://favorites') {
        const favs = getFavorites().filter(f => f.source === currentSource || (currentSource === 'KKPHIM' && !f.source));
        renderCards(favs, reset);
        isLoading = false;
        return;
      }

      if (currentSource === 'XEMTIVI') {
        const allChannels = getAllChannels();
        let filtered = allChannels;

        if (currentFilter === 'tv://favorites') {
          const favs = getFavorites();
          filtered = allChannels.filter(c => favs.some(f => f.id === c.id));
        } else if (currentFilter === 'tv://vtv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtv'));
        } else if (currentFilter === 'tv://vtvcab') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtvcab'));
        } else if (currentFilter === 'tv://sctv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('sctv'));
        } else if (currentFilter === 'tv://sports_intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('ESPN') || (c.group || '').includes('Bóng Rổ'));
        } else if (currentFilter === 'tv://racing_combat') {
          filtered = allChannels.filter(c => (c.group || '').includes('Đua Xe') || (c.group || '').includes('Võ Thuật'));
        } else if (currentFilter === 'tv://movies') {
          filtered = allChannels.filter(c => (c.group || '').includes('Rạp Phim'));
        } else if (currentFilter === 'tv://live') {
          filtered = allChannels.filter(c => (c.group || '').includes('Sự Kiện') || (c.group || '').includes('LIVE'));
        } else if (currentFilter === 'tv://intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('Quốc Tế') || (c.group || '').includes('Hàn Quốc') || (c.group || '').includes('Trung Quốc'));
        } else if (currentFilter === 'tv://local') {
          filtered = allChannels.filter(c => (c.group || '').includes('Địa phương') || (c.group || '').includes('HTV'));
        } else if (currentFilter === 'tv://radio') {
          filtered = allChannels.filter(c => (c.group || '').includes('Radio'));
        }

        const items = filtered.map(c => ({
          id: c.id,
          name: c.name,
          slug: c.id,
          originName: `[${c.group || 'Kênh TV'}]`,
          thumbUrl: c.logo || DEFAULT_TV_LOGO,
          posterUrl: c.logo || DEFAULT_TV_LOGO,
          quality: 'LIVE',
          episodeCurrent: 'Trực Tiếp',
          source: 'XEMTIVI',
          streamUrl: c.url,
          group: c.group
        }));

        renderCards(items, reset);
        isLoading = false;
        return;
      }

      // API KKPhim / AnimeHay
      const sep = currentFilter.includes('?') ? '&' : '?';
      const fetchUrl = `${currentFilter}${sep}page=${currentPage}`;
      const resp = await fetch(fetchUrl);
      if (!resp.ok) throw new Error('Network error');
      const data = await resp.json();

      let items = [];
      if (data.items && Array.isArray(data.items)) {
        items = data.items;
      } else if (data.data && data.data.items && Array.isArray(data.data.items)) {
        items = data.data.items;
      }

      const mapped = items.map(o => {
        let thumb = o.thumb_url || '';
        let poster = o.poster_url || thumb;
        if (thumb && !thumb.startsWith('http')) thumb = KKPHIM_IMG_BASE + thumb.replace(/^\//, '');
        if (poster && !poster.startsWith('http')) poster = KKPHIM_IMG_BASE + poster.replace(/^\//, '');

        return {
          id: o._id || o.slug,
          name: o.name,
          slug: o.slug,
          originName: o.origin_name || '',
          thumbUrl: thumb,
          posterUrl: poster || thumb,
          year: o.year || '2026',
          quality: o.quality || 'HD',
          episodeCurrent: o.episode_current || '',
          source: currentSource
        };
      });

      renderCards(mapped, reset);
    } catch (err) {
      if (reset) {
        grid.innerHTML = '<div style="color: #f87171; font-size: 16px; padding: 20px;">Không thể tải dữ liệu. Vui lòng kiểm tra kết nối mạng!</div>';
      }
    } finally {
      isLoading = false;
    }
  }

  // --- Render Movie Cards (7 Columns) ---
  function renderCards(items, reset) {
    const grid = document.getElementById('mainGrid');
    if (reset) grid.innerHTML = '';

    if (items.length === 0 && reset) {
      grid.innerHTML = '<div style="color: #94a3b8; font-size: 16px; padding: 20px;">Không có nội dung hiển thị trong mục này.</div>';
      return;
    }

    currentMoviesList = reset ? items : [...currentMoviesList, ...items];

    items.forEach(movie => {
      const card = document.createElement('div');
      const isTv = movie.source === 'XEMTIVI';
      card.className = `movie-card focusable ${isTv ? 'tv-card' : ''}`;
      card.tabIndex = 0;

      const favBadge = isFavorite(movie.id) ? '<div class="badge-fav">⭐</div>' : '';
      const qualityBadge = `<div class="badge-quality">${movie.quality || 'HD'}</div>`;
      const epBadge = movie.episodeCurrent ? `<div class="badge-episode">${movie.episodeCurrent}</div>` : '';

      card.innerHTML = `
        <div class="poster-wrapper">
          <img class="card-poster" src="${movie.posterUrl || movie.thumbUrl || DEFAULT_TV_LOGO}" alt="${movie.name}" onerror="this.src='${DEFAULT_TV_LOGO}'" loading="lazy">
          ${qualityBadge}
          ${favBadge}
          ${epBadge}
        </div>
        <div class="card-info">
          <div class="card-title">${movie.name}</div>
          <div class="card-subtitle">${movie.originName || movie.year || ''}</div>
        </div>
      `;

      // Click card
      card.addEventListener('click', () => {
        if (movie.source === 'XEMTIVI') {
          // BẤM VÀO KÊNH TV: VÀO XEM TRỰC TIẾP NGAY LẬP TỨC (Quy tắc v2.1)
          playTvChannelDirectly(movie);
        } else {
          openMovieDetail(movie);
        }
      });

      // Long press / Context menu / Yellow key: Toggle Favorite
      card.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        toggleFavorite(movie);
        loadMovies(true);
      });

      grid.appendChild(card);
    });
  }

  // --- History & Favorites Section ---
  function renderHistoryAndFavs() {
    const historySec = document.getElementById('historySection');
    const historyScroll = document.getElementById('historyScroll');
    const hist = getHistory();

    if (!hist || hist.length === 0) {
      historySec.style.display = 'none';
      return;
    }

    historySec.style.display = 'block';
    historyScroll.innerHTML = '';

    hist.forEach(item => {
      const card = document.createElement('div');
      card.className = 'history-item focusable';
      card.tabIndex = 0;
      card.innerHTML = `
        <img class="history-thumb" src="${item.posterUrl || DEFAULT_TV_LOGO}" onerror="this.src='${DEFAULT_TV_LOGO}'">
        <div class="history-progress-bg">
          <div class="history-progress-bar" style="width: ${item.percent || 0}%"></div>
        </div>
        <div class="history-info">
          <div class="history-name">${item.name}</div>
          <div class="history-sub">${item.episodeName || 'Đang xem'} • ${item.percent || 0}%</div>
        </div>
      `;
      card.addEventListener('click', () => {
        if (item.source === 'XEMTIVI') {
          playTvChannelDirectly({
            id: item.id,
            name: item.name,
            streamUrl: item.streamUrl || (getAllChannels().find(c => c.id === item.id) || {}).url,
            posterUrl: item.posterUrl
          });
        } else {
          openMovieDetail({
            id: item.id,
            name: item.name,
            slug: item.slug || item.id,
            source: item.source
          });
        }
      });
      historyScroll.appendChild(card);
    });
  }

  document.getElementById('btnClearHistory').addEventListener('click', () => {
    localStorage.removeItem('huycabuonca_history');
    renderHistoryAndFavs();
    showToast('Đã xóa toàn bộ lịch sử xem!');
  });

  // --- Detail Modal ---
  async function openMovieDetail(movie) {
    const modal = document.getElementById('detailModal');
    modal.style.display = 'flex';

    document.getElementById('detailTitle').textContent = movie.name;
    document.getElementById('detailSub').textContent = `${movie.originName || ''} • ${movie.year || '2026'}`;
    document.getElementById('detailPoster').src = movie.posterUrl || movie.thumbUrl || DEFAULT_TV_LOGO;
    document.getElementById('detailDesc').textContent = 'Đang tải thông tin chi tiết phim...';
    document.getElementById('episodesGrid').innerHTML = '<div style="color: #94a3b8;">Đang tải danh sách tập...</div>';

    updateDetailFavButton(movie);

    try {
      const resp = await fetch(`https://phimapi.com/phim/${movie.slug}`);
      if (!resp.ok) throw new Error('Detail error');
      const data = await resp.json();
      const m = data.movie;
      currentPlayingDetail = data;

      document.getElementById('detailDesc').textContent = (m.content || '').replace(/<[^>]*>?/gm, '') || 'Không có mô tả chi tiết.';

      const tags = document.getElementById('detailTags');
      tags.innerHTML = `
        <span class="tag-badge">Chất lượng: ${m.quality || 'HD'}</span>
        <span class="tag-badge">Thời lượng: ${m.time || 'Trọn bộ'}</span>
        <span class="tag-badge">Ngôn ngữ: ${m.lang || 'Vietsub'}</span>
        <span class="tag-badge">Tập: ${m.episode_current || 'Đang cập nhật'}</span>
      `;

      // Danh sách tập
      const epGrid = document.getElementById('episodesGrid');
      epGrid.innerHTML = '';

      if (data.episodes && data.episodes.length > 0) {
        const s = data.episodes[0];
        (s.server_data || []).forEach((ep, idx) => {
          const btn = document.createElement('button');
          btn.className = 'btn-episode focusable';
          btn.textContent = ep.name || `Tập ${idx + 1}`;
          btn.addEventListener('click', () => {
            modal.style.display = 'none';
            playVideo(ep.link_m3u8, movie.name, ep.name, movie, data, idx, 0);
          });
          epGrid.appendChild(btn);
        });

        // Nút Xem Tập Đầu
        document.getElementById('btnPlayFirst').onclick = () => {
          modal.style.display = 'none';
          const firstEp = s.server_data[0];
          if (firstEp) {
            playVideo(firstEp.link_m3u8, movie.name, firstEp.name, movie, data, 0, 0);
          }
        };
      }
    } catch (e) {
      document.getElementById('detailDesc').textContent = 'Không thể tải thông tin phim. Vui lòng thử lại sau!';
    }

    document.getElementById('btnCloseDetail').onclick = () => {
      modal.style.display = 'none';
    };

    document.getElementById('btnToggleFavDetail').onclick = () => {
      toggleFavorite(movie);
      updateDetailFavButton(movie);
    };
  }

  function updateDetailFavButton(movie) {
    const btn = document.getElementById('btnToggleFavDetail');
    if (isFavorite(movie.id)) {
      btn.textContent = '❤️ ĐÃ YÊU THÍCH';
      btn.style.color = '#ef4444';
    } else {
      btn.textContent = '⭐ THÊM YÊU THÍCH';
      btn.style.color = '#ffffff';
    }
  }

  // --- Play TV Channel Directly ---
  function playTvChannelDirectly(movie) {
    let url = movie.streamUrl;
    if (!url) {
      const found = getAllChannels().find(c => c.id === movie.id || c.name === movie.name);
      if (found) url = found.url;
    }
    if (!url) {
      showToast('Kênh này hiện chưa có luồng phát trực tiếp!');
      return;
    }

    playVideo(url, movie.name, 'Trực Tiếp', movie, null, 0, 0, true);
    setupQuickZapping(movie);
  }

  // --- Video Player (Hls.js) ---
  function playVideo(streamUrl, title, subtitle, movie, detail, epIndex, serverIndex, isTv = false) {
    if (!streamUrl) {
      showToast('Không tìm thấy link luồng phát video!');
      return;
    }

    currentPlayingMovie = movie;
    currentPlayingDetail = detail;
    currentEpisodeIndex = epIndex;
    currentServerIndex = serverIndex;

    const container = document.getElementById('playerContainer');
    const video = document.getElementById('videoPlayer');
    container.style.display = 'flex';

    document.getElementById('playerTitle').textContent = title;
    document.getElementById('playerSub').textContent = subtitle;

    const zapBtn = document.getElementById('btnQuickZap');
    const nextBtn = document.getElementById('btnNextEpisode');
    const progress = document.getElementById('progressContainer');

    if (isTv) {
      zapBtn.style.display = 'block';
      nextBtn.style.display = 'none';
      progress.style.display = 'none';
    } else {
      zapBtn.style.display = 'none';
      nextBtn.style.display = 'block';
      progress.style.display = 'flex';
    }

    // Reset HLS
    if (hlsInstance) {
      hlsInstance.destroy();
      hlsInstance = null;
    }

    if (Hls.isSupported() && streamUrl.includes('.m3u8')) {
      hlsInstance = new Hls({
        maxBufferLength: 30,
        maxMaxBufferLength: 60,
        enableWorker: true
      });
      hlsInstance.loadSource(streamUrl);
      hlsInstance.attachMedia(video);
      hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(e => console.log('Auto play blocked:', e));
      });
      hlsInstance.on(Hls.Events.ERROR, (event, data) => {
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              hlsInstance.startLoad();
              break;
            case Hls.ErrorTypes.MEDIA_ERROR:
              hlsInstance.recoverMediaError();
              break;
            default:
              hlsInstance.destroy();
              break;
          }
        }
      });
    } else {
      video.src = streamUrl;
      video.play().catch(e => console.log('Auto play blocked:', e));
    }

    // Check last watched position
    if (!isTv) {
      const hist = getHistory().find(h => h.id === movie.id);
      if (hist && hist.currentSec > 10 && hist.currentSec < hist.durationSec - 30) {
        video.currentTime = hist.currentSec;
      }
    }

    resetOverlayTimer();
    showToast(`Đang phát: ${title}`);
  }

  // --- Player Controls ---
  const video = document.getElementById('videoPlayer');
  const seekBar = document.getElementById('seekBar');
  const currentTimeLabel = document.getElementById('currentTime');
  const durationTimeLabel = document.getElementById('durationTime');
  const btnPlayPause = document.getElementById('btnPlayPause');

  video.addEventListener('timeupdate', () => {
    if (video.duration) {
      const cur = video.currentTime;
      const dur = video.duration;
      seekBar.value = (cur / dur) * 100;
      currentTimeLabel.textContent = formatTime(cur);
      durationTimeLabel.textContent = formatTime(dur);

      // Auto save history every 10 seconds
      if (Math.round(cur) % 10 === 0 && currentPlayingMovie) {
        saveHistory(currentPlayingMovie, cur, dur, document.getElementById('playerSub').textContent);
      }
    }
  });

  video.addEventListener('ended', () => {
    if (currentPlayingDetail && currentPlayingDetail.episodes) {
      const eps = currentPlayingDetail.episodes[0].server_data;
      if (currentEpisodeIndex + 1 < eps.length) {
        showToast('Tự động phát tập tiếp theo trong 5s...');
        setTimeout(() => {
          const nextEp = eps[currentEpisodeIndex + 1];
          playVideo(nextEp.link_m3u8, currentPlayingMovie.name, nextEp.name, currentPlayingMovie, currentPlayingDetail, currentEpisodeIndex + 1, currentServerIndex);
        }, 5000);
      }
    }
  });

  seekBar.addEventListener('input', () => {
    if (video.duration) {
      video.currentTime = (seekBar.value / 100) * video.duration;
    }
  });

  btnPlayPause.addEventListener('click', () => {
    if (video.paused) {
      video.play();
      btnPlayPause.textContent = '⏸️ Tạm Dừng';
    } else {
      video.pause();
      btnPlayPause.textContent = '▶️ Tiếp Tục';
    }
    resetOverlayTimer();
  });

  document.getElementById('btnRewind').addEventListener('click', () => {
    video.currentTime = Math.max(0, video.currentTime - 10);
    resetOverlayTimer();
  });

  document.getElementById('btnForward').addEventListener('click', () => {
    video.currentTime = Math.min(video.duration || 0, video.currentTime + 10);
    resetOverlayTimer();
  });

  document.getElementById('btnBackPlayer').addEventListener('click', () => {
    closePlayer();
  });

  document.getElementById('btnToggleFavPlayer').addEventListener('click', () => {
    if (currentPlayingMovie) {
      toggleFavorite(currentPlayingMovie);
    }
  });

  function closePlayer() {
    if (video) {
      if (currentPlayingMovie && video.duration) {
        saveHistory(currentPlayingMovie, video.currentTime, video.duration, document.getElementById('playerSub').textContent);
      }
      video.pause();
      video.src = '';
    }
    if (hlsInstance) {
      hlsInstance.destroy();
      hlsInstance = null;
    }
    document.getElementById('playerContainer').style.display = 'none';
    document.getElementById('zappingPanel').classList.remove('open');
  }

  function resetOverlayTimer() {
    const overlay = document.getElementById('playerOverlay');
    overlay.classList.remove('hide');
    clearTimeout(overlayTimeout);
    overlayTimeout = setTimeout(() => {
      overlay.classList.add('hide');
    }, 4500);
  }

  document.getElementById('playerContainer').addEventListener('mousemove', resetOverlayTimer);

  // --- Quick Zapping ---
  function setupQuickZapping(currentChannel) {
    const panel = document.getElementById('zappingList');
    panel.innerHTML = '';
    const all = getAllChannels();
    const groupChannels = all.filter(c => (c.group || '') === (currentChannel.group || ''));
    const list = groupChannels.length > 0 ? groupChannels : all;

    list.forEach(ch => {
      const item = document.createElement('div');
      item.className = `zapping-item focusable ${ch.id === currentChannel.id ? 'active' : ''}`;
      item.innerHTML = `
        <img class="zapping-logo" src="${ch.logo || DEFAULT_TV_LOGO}" onerror="this.src='${DEFAULT_TV_LOGO}'">
        <span class="zapping-name">${ch.name}</span>
      `;
      item.addEventListener('click', () => {
        document.getElementById('zappingPanel').classList.remove('open');
        playTvChannelDirectly({
          id: ch.id,
          name: ch.name,
          streamUrl: ch.url,
          group: ch.group,
          posterUrl: ch.logo
        });
      });
      panel.appendChild(item);
    });
  }

  document.getElementById('btnQuickZap').addEventListener('click', () => {
    document.getElementById('zappingPanel').classList.toggle('open');
  });
  document.getElementById('btnCloseZap').addEventListener('click', () => {
    document.getElementById('zappingPanel').classList.remove('open');
  });

  // --- Remote Number Quick Zapping (0-9) ---
  function handleNumberZap(numStr) {
    numberZapBuffer += numStr;
    clearTimeout(numberZapTimeout);
    showToast(`Nhảy tới kênh số: ${numberZapBuffer}...`);

    numberZapTimeout = setTimeout(() => {
      const channelIndex = parseInt(numberZapBuffer, 10) - 1;
      numberZapBuffer = '';
      const all = getAllChannels();
      if (channelIndex >= 0 && channelIndex < all.length) {
        const target = all[channelIndex];
        playTvChannelDirectly({
          id: target.id,
          name: target.name,
          streamUrl: target.url,
          group: target.group,
          posterUrl: target.logo
        });
      } else {
        showToast('Số kênh không hợp lệ!');
      }
    }, 1200);
  }

  // --- Football Matches Modal ---
  function showScheduleModal() {
    const modal = document.getElementById('scheduleModal');
    const list = document.getElementById('matchesList');
    list.innerHTML = '';

    LIVE_MATCHES.forEach(m => {
      const card = document.createElement('div');
      card.className = 'match-card focusable';
      card.tabIndex = 0;
      card.innerHTML = `
        <div>
          <div class="match-league">${m.tournament}</div>
          <div class="match-teams">${m.teamA} vs ${m.teamB}</div>
          <div class="match-channel">📺 Kênh: ${m.channelName} • Bấm để xem trực tiếp</div>
        </div>
        <div class="match-time-badge">${m.time}</div>
      `;
      card.addEventListener('click', () => {
        modal.style.display = 'none';
        const channels = getAllChannels();
        const found = channels.find(c => c.id === m.channelSlug) ||
                      channels.find(c => c.name.toLowerCase().includes('vtv6') || c.name.toLowerCase().includes('bóng'));
        if (found) {
          playTvChannelDirectly({
            id: found.id,
            name: `${found.name} - ${m.teamA} vs ${m.teamB}`,
            streamUrl: found.url,
            posterUrl: found.logo
          });
        } else {
          showToast(`Kênh "${m.channelName}" đang được chuẩn bị.`);
        }
      });
      list.appendChild(card);
    });

    modal.style.display = 'flex';
  }

  document.getElementById('btnScheduleHeader').addEventListener('click', showScheduleModal);
  document.getElementById('btnCloseSchedule').addEventListener('click', () => {
    document.getElementById('scheduleModal').style.display = 'none';
  });

  // --- Custom IPTV Modal ---
  function showIptvModal() {
    document.getElementById('iptvModal').style.display = 'flex';
  }
  document.getElementById('btnCloseIptv').addEventListener('click', () => {
    document.getElementById('iptvModal').style.display = 'none';
  });
  document.getElementById('btnAddIptvConfirm').addEventListener('click', () => {
    const name = document.getElementById('iptvName').value.trim();
    const url = document.getElementById('iptvUrl').value.trim();
    if (!name || !url) {
      showToast('Vui lòng nhập đầy đủ tên kênh và link m3u8!');
      return;
    }
    const customs = getCustomChannels();
    customs.unshift({
      id: `custom_${Date.now()}`,
      name: name,
      url: url,
      group: 'Kênh Tự Thêm',
      logo: DEFAULT_TV_LOGO
    });
    localStorage.setItem('huycabuonca_custom_iptv', JSON.stringify(customs));
    document.getElementById('iptvModal').style.display = 'none';
    showToast(`Đã thêm kênh "${name}" thành công!`);
    loadMovies(true);
  });

  // --- Search Modal ---
  document.getElementById('btnSearch').addEventListener('click', () => {
    document.getElementById('searchModal').style.display = 'flex';
    document.getElementById('searchInput').focus();
  });
  document.getElementById('btnCloseSearch').addEventListener('click', () => {
    document.getElementById('searchModal').style.display = 'none';
  });
  document.getElementById('btnDoSearch').addEventListener('click', doSearch);
  document.getElementById('searchInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') doSearch();
  });

  async function doSearch() {
    const kw = document.getElementById('searchInput').value.trim();
    if (!kw) return;
    const resGrid = document.getElementById('searchResultsGrid');
    resGrid.innerHTML = '<div style="color: #94a3b8; padding: 20px;">Đang tìm kiếm...</div>';

    let results = [];
    // 1. Search in TV
    const tvMatches = getAllChannels().filter(c => (c.name || '').toLowerCase().includes(kw.toLowerCase()) || (c.group || '').toLowerCase().includes(kw.toLowerCase()));
    tvMatches.forEach(c => {
      results.push({
        id: c.id,
        name: c.name,
        slug: c.id,
        originName: `[${c.group || 'Kênh TV'}]`,
        thumbUrl: c.logo || DEFAULT_TV_LOGO,
        posterUrl: c.logo || DEFAULT_TV_LOGO,
        quality: 'LIVE',
        source: 'XEMTIVI',
        streamUrl: c.url
      });
    });

    // 2. Search in KKPhim
    try {
      const resp = await fetch(`https://phimapi.com/v1/api/tim-kiem?keyword=${encodeURIComponent(kw)}`);
      if (resp.ok) {
        const d = await resp.json();
        const items = (d.data && d.data.items) || [];
        items.forEach(o => {
          let thumb = o.thumb_url || '';
          if (thumb && !thumb.startsWith('http')) thumb = KKPHIM_IMG_BASE + thumb.replace(/^\//, '');
          results.push({
            id: o._id || o.slug,
            name: o.name,
            slug: o.slug,
            originName: o.origin_name || '',
            thumbUrl: thumb,
            posterUrl: thumb,
            year: o.year || '2026',
            quality: o.quality || 'HD',
            source: 'KKPHIM'
          });
        });
      }
    } catch (e) {}

    resGrid.innerHTML = '';
    if (results.length === 0) {
      resGrid.innerHTML = '<div style="color: #94a3b8; padding: 20px;">Không tìm thấy nội dung phù hợp.</div>';
      return;
    }

    results.forEach(m => {
      const card = document.createElement('div');
      card.className = 'movie-card focusable';
      card.tabIndex = 0;
      card.innerHTML = `
        <div class="poster-wrapper" style="height: 180px;">
          <img class="card-poster" src="${m.posterUrl || DEFAULT_TV_LOGO}" onerror="this.src='${DEFAULT_TV_LOGO}'">
          <div class="badge-quality">${m.quality || 'HD'}</div>
        </div>
        <div class="card-info">
          <div class="card-title">${m.name}</div>
          <div class="card-subtitle">${m.originName || ''}</div>
        </div>
      `;
      card.addEventListener('click', () => {
        document.getElementById('searchModal').style.display = 'none';
        if (m.source === 'XEMTIVI') {
          playTvChannelDirectly(m);
        } else {
          openMovieDetail(m);
        }
      });
      resGrid.appendChild(card);
    });
  }

  // --- Favorite & History Header Buttons ---
  document.getElementById('btnFavHeader').addEventListener('click', () => {
    currentFilter = 'app://favorites';
    loadMovies(true);
  });
  document.getElementById('btnHistoryHeader').addEventListener('click', () => {
    const sec = document.getElementById('historySection');
    sec.style.display = 'block';
    sec.scrollIntoView({ behavior: 'smooth' });
  });

  // --- Remote D-Pad Navigation & LG webOS Keycodes ---
  window.addEventListener('keydown', (e) => {
    const code = e.keyCode || e.which;

    // LG webOS Back Button (461), Escape (27), Backspace (8)
    if (code === 461 || code === 27) {
      e.preventDefault();
      const player = document.getElementById('playerContainer');
      const detail = document.getElementById('detailModal');
      const zap = document.getElementById('zappingPanel');
      const sched = document.getElementById('scheduleModal');
      const iptv = document.getElementById('iptvModal');
      const search = document.getElementById('searchModal');

      if (zap.classList.contains('open')) {
        zap.classList.remove('open');
      } else if (player.style.display === 'flex') {
        closePlayer();
      } else if (detail.style.display === 'flex') {
        detail.style.display = 'none';
      } else if (sched.style.display === 'flex') {
        sched.style.display = 'none';
      } else if (iptv.style.display === 'flex') {
        iptv.style.display = 'none';
      } else if (search.style.display === 'flex') {
        search.style.display = 'none';
      } else {
        showToast('Nhấn Trang chủ trên điều khiển để thoát ứng dụng.');
      }
      return;
    }

    // Number keys 0-9 for Quick Zapping
    if (code >= 48 && code <= 57) {
      const numStr = String.fromCharCode(code);
      handleNumberZap(numStr);
      return;
    }

    // Play/Pause remote keys (415, 19, 413)
    if (code === 415) { // Play
      if (video && video.paused) video.play();
    } else if (code === 19 || code === 413) { // Pause / Stop
      if (video && !video.paused) video.pause();
    }

    // Spatial navigation for D-pad (ArrowUp: 38, ArrowDown: 40, ArrowLeft: 37, ArrowRight: 39)
    if ([37, 38, 39, 40].includes(code)) {
      resetOverlayTimer();
    }
  });

  // Format seconds to mm:ss or hh:mm:ss
  function formatTime(sec) {
    if (isNaN(sec)) return '00:00';
    const s = Math.floor(sec % 60);
    const m = Math.floor((sec / 60) % 60);
    const h = Math.floor(sec / 3600);
    if (h > 0) {
      return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  // --- Initialize App ---
  initSources();
  renderFilterBar();
  renderHistoryAndFavs();
})();
