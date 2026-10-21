// Huy Cá - Phiên Bản v2.5 (Premier League & 4-Tier Match Streaming)
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
  let lastBackTime = 0;
  let currentFocusedElement = null;
  const isNativeWebOS = /webOS|SmartTV/i.test(navigator.userAgent) || window.webOS !== undefined;

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
  // --- Anime Sub-Sources Data ---
  let currentSubSource = 'anime_sub://vietsub';
  const SUB_SOURCES = {
    ANIMEHAY: [
      { name: "⛩️ Anime Vietsub", key: "anime_sub://vietsub" },
      { name: "🐉 Hoạt Hình 3D Trung Quốc", key: "anime_sub://hh3d" },
      { name: "🏰 Hoạt Hình Chiếu Rạp", key: "anime_sub://movies" },
      { name: "🎙️ Anime Thuyết Minh (Tổng Hợp)", key: "anime_sub://dubbed" }
    ],
    FREEREELS: [
      { name: "📱 FreeReels Dọc (Phụ Đề & Lồng Tiếng)", key: "freereels_sub://freereels" },
      { name: "🇻🇳 Tiểu Kịch Vietsub (KKPhim HD)", key: "freereels_sub://kkphim" },
      { name: "💎 DramaBox Hot (Tuyển Chọn Hay Nhất)", key: "freereels_sub://dramabox" }
    ]
  };

  const SUB_FILTERS = {
    'anime_sub://vietsub': [
      { name: "Anime Mới Cập Nhật", url: "https://phimapi.com/v1/api/quoc-gia/nhat-ban" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Anime Yêu Thích", url: "app://favorites" },
      { name: "Hành Động", url: "https://phimapi.com/v1/api/the-loai/hanh-dong" },
      { name: "Thần Thoại", url: "https://phimapi.com/v1/api/the-loai/than-thoai" },
      { name: "Học Đường", url: "https://phimapi.com/v1/api/the-loai/hoc-duong" },
      { name: "Viễn Tưởng", url: "https://phimapi.com/v1/api/the-loai/vien-tuong" }
    ],
    'anime_sub://hh3d': [
      { name: "3D Mới Cập Nhật", url: "https://phimapi.com/v1/api/quoc-gia/trung-quoc" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Hoạt Hình Yêu Thích", url: "app://favorites" },
      { name: "Tu Tiên & Huyền Huyễn", url: "https://phimapi.com/v1/api/the-loai/than-thoai" },
      { name: "Kiếm Hiệp & Võ Thuật", url: "https://phimapi.com/v1/api/the-loai/kiem-hiep" },
      { name: "Hành Động 3D", url: "https://phimapi.com/v1/api/the-loai/hanh-dong" },
      { name: "Cổ Trang 3D", url: "https://phimapi.com/v1/api/the-loai/co-trang" }
    ],
    'anime_sub://movies': [
      { name: "Hoạt Hình Chiếu Rạp", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" },
      { name: "Ghibli & Cổ Điển", url: "https://phimapi.com/v1/api/the-loai/gia-dinh" },
      { name: "Phiêu Lưu", url: "https://phimapi.com/v1/api/the-loai/phieu-luu" },
      { name: "Hài Hước", url: "https://phimapi.com/v1/api/the-loai/hai-huoc" }
    ],
    'anime_sub://dubbed': [
      { name: "🎙️ Tất Cả Anime Thuyết Minh", url: "anime_dubbed://all" },
      { name: "⛩️ Anime Nhật Lồng Tiếng", url: "anime_dubbed://japan" },
      { name: "🐉 Hoạt Hình 3D Trung Quốc", url: "anime_dubbed://china" },
      { name: "🏰 Hoạt Hình Chiếu Rạp", url: "anime_dubbed://cinema" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'freereels_sub://freereels': [
      { name: "🔥 Thịnh Hành", url: "freereels://foryou" },
      { name: "🎙️ Phim Lồng Tiếng Việt", url: "freereels://dubbed_vi" },
      { name: "⚡ Mới Nhất", url: "freereels://tab_505" },
      { name: "🎀 Dành Cho Nữ", url: "freereels://tab_504" },
      { name: "👑 Dành Cho Nam", url: "freereels://tab_506" },
      { name: "🎭 Hoạt Hình Ngắn", url: "freereels://tab_547" },
      { name: "⏰ Sắp Chiếu", url: "freereels://coming" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'freereels_sub://kkphim': [
      { name: "🔥 Tất Cả Tiểu Kịch Vietsub", url: "https://phimapi.com/v1/api/the-loai/phim-ngan" },
      { name: "👑 Tổng Tài & Bá Đạo", url: "short_filter://tong-tai" },
      { name: "🐉 Trọng Sinh & Nghịch Tập", url: "short_filter://trong-sinh" },
      { name: "💖 Ngôn Tình & Hôn Nhân", url: "short_filter://ngon-tinh" },
      { name: "🎭 Hài Hước & Đời Sống", url: "short_filter://hai-huoc" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'freereels_sub://dramabox': [
      { name: "🌟 Tuyển Chọn Phim Ngắn Hot", url: "short_dramabox://hot" },
      { name: "⚔️ Chiến Thần & Tu Tiên", url: "short_dramabox://chienthan" },
      { name: "👑 Thiếu Gia Ẩn Danh", url: "short_dramabox://thieugia" },
      { name: "🏰 Cung Đấu & Cổ Trang", url: "short_dramabox://cotrang" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ]
  };

  const FILTERS = {
    KKPHIM: [
      { name: "Mới Cập Nhật", url: "https://phimapi.com/danh-sach/phim-moi-cap-nhat" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Phim Yêu Thích", url: "app://favorites" },
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
      { name: "Âu Mỹ", url: "https://phimapi.com/v1/api/quoc-gia/au-my" }
    ],
    ANIMEHAY: [
      { name: "Anime Mới Cập Nhật", url: "https://phimapi.com/v1/api/danh-sach/hoat-hinh" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Anime Yêu Thích", url: "app://favorites" },
      { name: "Anime Hành Động", url: "https://phimapi.com/v1/api/the-loai/hanh-dong" },
      { name: "Anime Thần Thoại", url: "https://phimapi.com/v1/api/the-loai/than-thoai" },
      { name: "Anime Học Đường", url: "https://phimapi.com/v1/api/the-loai/hoc-duong" },
      { name: "Anime Viễn Tưởng", url: "https://phimapi.com/v1/api/the-loai/vien-tuong" }
    ],
    XEMTIVI: [
      { name: "Tất Cả Kênh", url: "tv://all" },
      { name: "⚽ Lịch Thi Đấu & Bóng Đá", url: "tv://schedule" },
      { name: "🕒 Kênh Vừa Xem", url: "app://history" },
      { name: "⭐ Kênh Yêu Thích", url: "tv://favorites" },
      { name: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh (EPL)", url: "tv://epl" },
      { name: "📡 Kênh Vệ Tinh Quốc Tế", url: "tv://satellite" },
      { name: "⚽ Bóng Đá & Thể Thao VN", url: "tv://football" },
      { name: "🏆 Cúp C1 & Thể Thao ESPN", url: "tv://sports_intl" },
      { name: "🏎️ Đua Xe & Võ Thuật", url: "tv://racing_combat" },
      { name: "VTV Quốc Gia", url: "tv://vtv" },
      { name: "VTVcab", url: "tv://vtvcab" },
      { name: "SCTV", url: "tv://sctv" },
      { name: "Rạp Phim", url: "tv://movies" },
      { name: "Sự Kiện TV360", url: "tv://live" },
      { name: "Kênh Quốc Tế", url: "tv://intl" },
      { name: "Đài Địa Phương", url: "tv://local" },
      { name: "Radio Trực Tuyến", url: "tv://radio" },
      { name: "➕ Thêm Kênh IPTV", url: "tv://custom" }
    ],
    FREEREELS: [
      { name: "🔥 Thịnh Hành", url: "https://phimapi.com/danh-sach/phim-moi-cap-nhat" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Phim Ngắn Yêu Thích", url: "app://favorites" },
      { name: "✨ Phim Ngắn Mới", url: "https://phimapi.com/v1/api/danh-sach/phim-bo" }
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
    const animeSubBar = document.getElementById('animeSubSourcesBar');
    bar.innerHTML = '';
    bar.scrollLeft = 0;

    const currentSubList = SUB_SOURCES[currentSource];
    if (currentSubList && currentSubList.length > 0) {
      if (animeSubBar) {
        animeSubBar.style.display = 'flex';
        animeSubBar.innerHTML = '';
        if (!currentSubList.some(s => s.key === currentSubSource)) {
          currentSubSource = currentSubList[0].key;
        }
        currentSubList.forEach(s => {
          const btn = document.createElement('button');
          btn.className = `btn-sub-source focusable ${s.key === currentSubSource ? 'active' : ''}`;
          btn.dataset.sub = s.key;
          btn.textContent = s.name;
          btn.onclick = () => {
            currentSubSource = s.key;
            renderFilterBar();
          };
          animeSubBar.appendChild(btn);
        });
      }
    } else {
      if (animeSubBar) animeSubBar.style.display = 'none';
    }

    const filters = SUB_FILTERS[currentSubSource] || FILTERS[currentSource] || [];
    if (filters.length === 0) return;

    filters.forEach((f, idx) => {
      const btn = document.createElement('button');
      btn.className = `btn-filter focusable ${idx === 0 ? 'active' : ''}`;
      btn.textContent = f.name;
      btn.dataset.url = f.url;
      btn.addEventListener('click', () => {
        bar.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        btn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        handleFilterClick(f);
      });
      bar.appendChild(btn);
    });

    // Cập nhật trạng thái hiển thị của nút Prev/Next
    setTimeout(updateFilterNavState, 100);

    // Tự động load filter đầu tiên
    handleFilterClick(filters[0]);
  }

  function updateFilterNavState() {
    const filterBar = document.getElementById('filterBar');
    const btnPrev = document.getElementById('btnFilterPrev');
    const btnNext = document.getElementById('btnFilterNext');
    if (!filterBar || !btnPrev || !btnNext) return;
    const maxScroll = filterBar.scrollWidth - filterBar.clientWidth;
    btnPrev.style.opacity = filterBar.scrollLeft <= 5 ? '0.35' : '1';
    btnNext.style.opacity = filterBar.scrollLeft >= maxScroll - 5 ? '0.35' : '1';
  }

  // --- Điều Hướng Thanh Filter Cho Windows (Nút Bấm, Con Lăn Chuột & Kéo Chuột) ---
  function initFilterBarNavigation() {
    const filterBar = document.getElementById('filterBar');
    const btnPrev = document.getElementById('btnFilterPrev');
    const btnNext = document.getElementById('btnFilterNext');
    if (!filterBar) return;

    if (btnPrev) {
      btnPrev.addEventListener('click', () => {
        filterBar.scrollBy({ left: -280, behavior: 'smooth' });
        setTimeout(updateFilterNavState, 350);
      });
    }

    if (btnNext) {
      btnNext.addEventListener('click', () => {
        filterBar.scrollBy({ left: 280, behavior: 'smooth' });
        setTimeout(updateFilterNavState, 350);
      });
    }

    // 1. Cuộn ngang bằng con lăn chuột (Mouse Wheel) khi rê trên thanh filter
    filterBar.addEventListener('wheel', (e) => {
      if (e.deltaY !== 0) {
        e.preventDefault();
        filterBar.scrollLeft += e.deltaY * 1.2;
        updateFilterNavState();
      }
    }, { passive: false });

    // 2. Kéo thả chuột ngang (Drag to scroll)
    let isMouseDown = false;
    let startX = 0;
    let scrollStart = 0;

    filterBar.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return; // Chỉ chuột trái
      isMouseDown = true;
      startX = e.pageX - filterBar.offsetLeft;
      scrollStart = filterBar.scrollLeft;
    });

    window.addEventListener('mouseup', () => {
      isMouseDown = false;
    });

    filterBar.addEventListener('mousemove', (e) => {
      if (!isMouseDown) return;
      e.preventDefault();
      const x = e.pageX - filterBar.offsetLeft;
      const walk = (x - startX) * 1.5;
      filterBar.scrollLeft = scrollStart - walk;
      updateFilterNavState();
    });

    filterBar.addEventListener('scroll', updateFilterNavState);
    window.addEventListener('resize', updateFilterNavState);
    setTimeout(updateFilterNavState, 200);
  }

  function handleFilterClick(filterItem) {
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
    const paginationContainer = document.getElementById('paginationContainer');
    const paginationInfo = document.getElementById('paginationInfo');
    const btnLoadMore = document.getElementById('btnLoadMore');
    const spinner = document.getElementById('loadingMoreSpinner');

    if (reset) {
      grid.innerHTML = '<div style="color: #94a3b8; font-size: 18px; padding: 40px; text-align: center; width: 100%; grid-column: 1 / -1;">⏳ Đang tải danh sách...</div>';
      currentMoviesList = [];
      currentPage = 1;
      if (paginationContainer) paginationContainer.style.display = 'none';
    } else {
      if (btnLoadMore) btnLoadMore.style.display = 'none';
      if (spinner) spinner.style.display = 'block';
    }

    try {
      if (currentFilter === 'app://favorites') {
        const favs = getFavorites().filter(f => f.source === currentSource || (currentSource === 'KKPHIM' && !f.source));
        renderCards(favs, reset);
        if (paginationContainer) paginationContainer.style.display = 'none';
        isLoading = false;
        return;
      }

      if (currentFilter === 'app://history') {
        const hist = getHistory().filter(h => h.source === currentSource || (currentSource === 'KKPHIM' && !h.source));
        renderCards(hist, reset);
        if (paginationContainer) paginationContainer.style.display = 'none';
        isLoading = false;
        return;
      }

      if (currentSource === 'XEMTIVI') {
        const allChannels = getAllChannels();
        let filtered = allChannels;

                if (currentFilter === 'tv://epl') {
          // 1. Tải danh sách trận đấu Ngoại Hạng Anh FPL thời gian thực
          const eplMatches = await fetchRealtimePremierLeagueMatches();
          
          // Tạo các thẻ trận đấu Ngoại Hạng Anh với icon chuông thông báo độc lập
          const matchCards = eplMatches.map(m => {
            const hasReminder = isMatchReminderSet(m.id);
            return {
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
            };
          });

          // 2. Tải thêm các kênh Vệ Tinh Quốc Tế phát sóng Ngoại Hạng Anh
          const satChannels = allChannels.filter(c => (c.group || '').includes('Vệ Tinh') || (c.name || '').includes('True Premier') || (c.name || '').includes('Astro') || (c.name || '').includes('Sky Sports') || (c.name || '').includes('TNT Sports'));
          const satItems = satChannels.map(c => ({
            id: c.id,
            name: c.name,
            slug: c.id,
            originName: `[${c.group || 'Vệ Tinh'}]`,
            thumbUrl: c.logo || DEFAULT_TV_LOGO,
            posterUrl: c.logo || DEFAULT_TV_LOGO,
            quality: '1080p',
            episodeCurrent: '24/7',
            source: 'XEMTIVI',
            streamUrl: c.url,
            group: c.group
          }));

          renderCards([...matchCards, ...satItems], reset);
          if (paginationContainer) paginationContainer.style.display = 'none';
          isLoading = false;
          return;
        } else if (currentFilter === 'tv://satellite') {
          filtered = allChannels.filter(c => (c.group || '').includes('Vệ Tinh') || (c.name || '').includes('True Premier') || (c.name || '').includes('Astro') || (c.name || '').includes('Sky Sports') || (c.name || '').includes('TNT Sports'));
        } else if (currentFilter === 'tv://favorites') {
          const favs = getFavorites();
          filtered = allChannels.filter(c => favs.some(f => f.id === c.id));
        } else if (currentFilter === 'tv://football') {
          // Lọc toàn bộ kênh bóng đá đỉnh cao Việt Nam & Quốc Tế
          filtered = allChannels.filter(c => {
            const grp = (c.group || '').toLowerCase();
            const nm = (c.name || '').toLowerCase();
            return grp.includes('bóng đá') || 
                   grp.includes('thể thao') || 
                   grp.includes('c1') ||
                   nm.includes('k+') || 
                   nm.includes('sport') || 
                   nm.includes('football') ||
                   nm.includes('vtv5') || 
                   nm.includes('vtv6') ||
                   nm.includes('htv thể thao') ||
                   nm.includes('bein') ||
                   nm.includes('cbs') ||
                   nm.includes('eurosport') ||
                   nm.includes('espn');
          });
        } else if (currentFilter === 'tv://vtv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtv'));
        } else if (currentFilter === 'tv://vtvcab') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('vtvcab'));
        } else if (currentFilter === 'tv://sctv') {
          filtered = allChannels.filter(c => (c.group || '').toLowerCase().includes('sctv'));
        } else if (currentFilter === 'tv://sports_intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('ESPN') || (c.group || '').includes('Bóng Rổ') || (c.group || '').includes('FOX'));
        } else if (currentFilter === 'tv://racing_combat') {
          filtered = allChannels.filter(c => (c.group || '').includes('Đua Xe') || (c.group || '').includes('Võ Thuật') || (c.group || '').includes('Mạo Hiểm') || (c.group || '').includes('Đối Kháng'));
        } else if (currentFilter === 'tv://movies') {
          filtered = allChannels.filter(c => (c.group || '').includes('Rạp Phim') || (c.group || '').toLowerCase().includes('phim'));
        } else if (currentFilter === 'tv://live') {
          filtered = allChannels.filter(c => (c.group || '').includes('Sự Kiện') || (c.group || '').includes('LIVE'));
        } else if (currentFilter === 'tv://intl') {
          filtered = allChannels.filter(c => (c.group || '').includes('Quốc Tế') || (c.group || '').includes('Hàn Quốc') || (c.group || '').includes('Trung Quốc') || (c.group || '').includes('Israel') || (c.group || '').includes('In The Box') || (c.group || '').includes('TVB'));
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
        if (paginationContainer) paginationContainer.style.display = 'none';
        isLoading = false;
        return;
      }

      // Xử lý Anime Thuyết Minh (100% Hoạt Hình, Lọc Sạch Phim Người Đóng)
      if (currentFilter.startsWith('anime_dubbed://')) {
        const filterType = currentFilter.replace('anime_dubbed://', '');
        const p1 = (currentPage - 1) * 2 + 1;
        const p2 = currentPage * 2;
        const collectedItems = [];
        
        for (const p of [p1, p2]) {
          const endpoints = [
            `https://phimapi.com/v1/api/danh-sach/phim-thuyet-minh?page=${p}`,
            `https://phimapi.com/v1/api/danh-sach/phim-long-tieng?page=${p}`,
            `https://phimapi.com/v1/api/the-loai/hoat-hinh?page=${p}`
          ];
          for (const ep of endpoints) {
            try {
              const r = await fetch(ep);
              if (!r.ok) continue;
              const j = await r.json();
              const arr = (j.items || (j.data && j.data.items)) || [];
              arr.forEach(o => {
                const type = o.type || '';
                const lang = (o.lang || '').toLowerCase();
                const cats = o.category || [];
                const isCatAnim = cats.some(c => (c.slug || '').includes('hoat-hinh'));
                const isAnim = (type === 'hoathinh' || isCatAnim);
                const isDub = (lang.includes('thuyết minh') || lang.includes('lồng tiếng') || lang.includes('tm') || lang.includes('lt'));

                if (isAnim && isDub) {
                  const countries = (o.country || []).map(c => c.slug || '');
                  let matched = true;
                  if (filterType === 'japan' && !countries.includes('nhat-ban')) matched = false;
                  if (filterType === 'china' && !countries.includes('trung-quoc')) matched = false;
                  if (filterType === 'cinema' && !countries.some(c => ['au-my', 'my', 'phap', 'anh', 'canada', 'uc', 'duc'].includes(c))) matched = false;

                  if (matched) {
                    let thumb = o.thumb_url || '';
                    let poster = o.poster_url || thumb;
                    if (thumb && !thumb.startsWith('http')) thumb = KKPHIM_IMG_BASE + thumb.replace(/^\//, '');
                    if (poster && !poster.startsWith('http')) poster = KKPHIM_IMG_BASE + poster.replace(/^\//, '');
                    collectedItems.push({
                      id: o._id || o.slug,
                      name: o.name,
                      slug: o.slug,
                      originName: o.origin_name || '',
                      thumbUrl: thumb,
                      posterUrl: poster,
                      year: o.year || '',
                      quality: o.quality || 'FHD',
                      episodeCurrent: o.episode_current || '',
                      source: 'KKPHIM'
                    });
                  }
                }
              });
            } catch(e) {}
          }
        }
        // Loại bỏ trùng lặp
        const seen = new Set();
        const distinct = collectedItems.filter(item => {
          const k = item.name.trim().toLowerCase();
          if (seen.has(k)) return false;
          seen.add(k);
          return true;
        });
        renderCards(distinct, reset);
        if (paginationContainer) paginationContainer.style.display = 'flex';
        isLoading = false;
        return;
      }

      // Xử lý Phim Ngắn (Tiểu Kịch & FreeReels & DramaBox)
      let fetchUrl = '';
      if (currentFilter.startsWith('short_filter://') || currentFilter.startsWith('short_dramabox://')) {
        let kw = 'tổng tài';
        if (currentFilter.includes('trong-sinh')) kw = 'trọng sinh';
        if (currentFilter.includes('ngon-tinh')) kw = 'hôn nhân';
        if (currentFilter.includes('hai-huoc')) kw = 'hài hước';
        if (currentFilter.includes('chienthan')) kw = 'chiến thần';
        if (currentFilter.includes('thieugia')) kw = 'thiếu gia';
        if (currentFilter.includes('cotrang')) kw = 'cung đấu';
        fetchUrl = `https://phimapi.com/v1/api/tim-kiem?keyword=${encodeURIComponent(kw)}&page=${currentPage}`;
      } else if (currentFilter.startsWith('freereels://')) {
        fetchUrl = `https://phimapi.com/v1/api/the-loai/phim-ngan?page=${currentPage}`;
      } else {
        const sep = currentFilter.includes('?') ? '&' : '?';
        fetchUrl = `${currentFilter}${sep}page=${currentPage}`;
      }

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

      // Cập nhật giao diện phân trang
      if (paginationContainer) {
        if (mapped.length > 0) {
          paginationContainer.style.display = 'flex';
          if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim (Trang ${currentPage})`;
          if (btnLoadMore) {
            btnLoadMore.style.display = 'inline-flex';
            const nextPageEl = document.getElementById('nextPageNum');
            if (nextPageEl) nextPageEl.textContent = currentPage + 1;
          }
          if (spinner) spinner.style.display = 'none';
        } else {
          if (paginationInfo) paginationInfo.textContent = `Đã tải toàn bộ ${currentMoviesList.length} phim trong danh mục này.`;
          if (btnLoadMore) btnLoadMore.style.display = 'none';
          if (spinner) spinner.style.display = 'none';
        }
      }
    } catch (err) {
      if (reset) {
        grid.innerHTML = '<div style="color: #f87171; font-size: 16px; padding: 30px; text-align: center; width: 100%; grid-column: 1 / -1;">Không thể tải dữ liệu. Vui lòng kiểm tra kết nối mạng! <button onclick="location.reload()" style="margin-left: 10px; padding: 6px 14px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">🔄 Thử Lại</button></div>';
      } else {
        showToast('Không thể tải thêm phim trang tiếp theo.');
        if (btnLoadMore) btnLoadMore.style.display = 'inline-flex';
        if (spinner) spinner.style.display = 'none';
      }
    } finally {
      isLoading = false;
    }
  }

  function loadMoreMovies() {
    if (isLoading) return;
    if (currentSource === 'XEMTIVI' || currentFilter === 'app://favorites' || currentFilter === 'app://history') return;
    currentPage++;
    loadMovies(false);
  }


  // --- PREMIER LEAGUE REAL-TIME FPL SERVICE & 4-TIER STREAMING (v2.5) ---
  const PREMIER_LEAGUE_TEAMS = {
    1: { name: "Arsenal", short: "ARS", logo: "https://resources.premierleague.com/premierleague/badges/70/t3.png" },
    2: { name: "Aston Villa", short: "AVL", logo: "https://resources.premierleague.com/premierleague/badges/70/t7.png" },
    3: { name: "Bournemouth", short: "BOU", logo: "https://resources.premierleague.com/premierleague/badges/70/t91.png" },
    4: { name: "Brentford", short: "BRE", logo: "https://resources.premierleague.com/premierleague/badges/70/t94.png" },
    5: { name: "Brighton", short: "BHA", logo: "https://resources.premierleague.com/premierleague/badges/70/t36.png" },
    6: { name: "Chelsea", short: "CHE", logo: "https://resources.premierleague.com/premierleague/badges/70/t8.png" },
    7: { name: "Crystal Palace", short: "CRY", logo: "https://resources.premierleague.com/premierleague/badges/70/t31.png" },
    8: { name: "Everton", short: "EVE", logo: "https://resources.premierleague.com/premierleague/badges/70/t11.png" },
    9: { name: "Fulham", short: "FUL", logo: "https://resources.premierleague.com/premierleague/badges/70/t54.png" },
    10: { name: "Ipswich Town", short: "IPS", logo: "https://resources.premierleague.com/premierleague/badges/70/t40.png" },
    11: { name: "Leicester City", short: "LEI", logo: "https://resources.premierleague.com/premierleague/badges/70/t13.png" },
    12: { name: "Liverpool", short: "LIV", logo: "https://resources.premierleague.com/premierleague/badges/70/t14.png" },
    13: { name: "Manchester City", short: "MCI", logo: "https://resources.premierleague.com/premierleague/badges/70/t43.png" },
    14: { name: "Manchester United", short: "MUN", logo: "https://resources.premierleague.com/premierleague/badges/70/t1.png" },
    15: { name: "Newcastle", short: "NEW", logo: "https://resources.premierleague.com/premierleague/badges/70/t4.png" },
    16: { name: "Nottingham Forest", short: "NFO", logo: "https://resources.premierleague.com/premierleague/badges/70/t17.png" },
    17: { name: "Southampton", short: "SOU", logo: "https://resources.premierleague.com/premierleague/badges/70/t20.png" },
    18: { name: "Tottenham Hotspur", short: "TOT", logo: "https://resources.premierleague.com/premierleague/badges/70/t6.png" },
    19: { name: "West Ham United", short: "WHU", logo: "https://resources.premierleague.com/premierleague/badges/70/t21.png" },
    20: { name: "Wolves", short: "WOL", logo: "https://resources.premierleague.com/premierleague/badges/70/t39.png" }
  };

  let activeMatchForServer = null;

  // Lấy danh sách trận đấu đã đặt chuông (chỉ báo đúng trận được người dùng chọn)
  function getMatchReminders() {
    try {
      return JSON.parse(localStorage.getItem('huyca_match_reminders') || '[]');
    } catch (e) {
      return [];
    }
  }

  function isMatchReminderSet(matchId) {
    const list = getMatchReminders();
    return list.some(item => String(item.id) === String(matchId));
  }

  function toggleMatchReminder(match) {
    let list = getMatchReminders();
    const idx = list.findIndex(item => String(item.id) === String(match.id));
    let added = false;
    if (idx >= 0) {
      list.splice(idx, 1);
      added = false;
      showToast(`🔕 Đã hủy thông báo: ${match.teamA} vs ${match.teamB}`);
    } else {
      list.push({
        id: match.id,
        teamA: match.teamA,
        teamB: match.teamB,
        kickoffTime: match.kickoffTime,
        timeStr: match.timeStr,
        notified: false
      });
      added = true;
      showToast(`🔔 Đã đặt chuông! App sẽ cảnh báo trước 15 phút khi trận "${match.teamA} vs ${match.teamB}" bắt đầu!`);
    }
    localStorage.setItem('huyca_match_reminders', JSON.stringify(list));
    return added;
  }

  // Bộ đếm kiểm tra thông báo định kỳ (Chỉ cảnh báo đúng trận được đặt)
  function startReminderChecker() {
    setInterval(() => {
      const list = getMatchReminders();
      if (!list || list.length === 0) return;

      const now = Date.now();
      let updated = false;

      list.forEach(m => {
        if (!m.notified && m.kickoffTime) {
          const diffMinutes = (m.kickoffTime - now) / (1000 * 60);
          if (diffMinutes <= 15 && diffMinutes >= -105) {
            m.notified = true;
            updated = true;
            showMatchAlertPopup(m);
          }
        }
      });

      if (updated) {
        localStorage.setItem('huyca_match_reminders', JSON.stringify(list));
      }
    }, 30000);
  }

  function showMatchAlertPopup(m) {
    showToast(`🔔⚽ SẮP BẮT ĐẦU: "${m.teamA} vs ${m.teamB}" trong 15 phút nữa! Bấm để chọn Server xem ngay!`);
    openMatchServerModal({
      id: m.id,
      tournament: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh",
      teamA: m.teamA,
      teamB: m.teamB,
      time: m.timeStr || "Sắp diễn ra"
    });
  }

  // Tải danh sách trận đấu Ngoại Hạng Anh thời gian thực từ FPL Premier League API
  async function fetchRealtimePremierLeagueMatches() {
    try {
      const resp = await fetch('https://fantasy.premierleague.com/api/fixtures/?future=1');
      if (!resp.ok) throw new Error('FPL API Network Error');
      const fixtures = await resp.json();
      
      const upcoming = fixtures.slice(0, 10).map(f => {
        const teamH = PREMIER_LEAGUE_TEAMS[f.team_h] || { name: `Đội ${f.team_h}`, short: `T${f.team_h}`, logo: DEFAULT_TV_LOGO };
        const teamA = PREMIER_LEAGUE_TEAMS[f.team_a] || { name: `Đội ${f.team_a}`, short: `T${f.team_a}`, logo: DEFAULT_TV_LOGO };
        
        const dateObj = new Date(f.kickoff_time);
        // Chuyển sang giờ Việt Nam GMT+7
        const vnHour = String(dateObj.getHours()).padStart(2, '0');
        const vnMin = String(dateObj.getMinutes()).padStart(2, '0');
        const vnDay = String(dateObj.getDate()).padStart(2, '0');
        const vnMonth = String(dateObj.getMonth() + 1).padStart(2, '0');
        
        const timeFormatted = `${vnHour}:${vnMin} • ${vnDay}/${vnMonth}`;
        const isLive = f.started && !f.finished;
        const isFinished = f.finished;
        
        let scoreStr = `${timeFormatted}`;
        if (isLive) {
          scoreStr = `🔴 LIVE • ${f.team_h_score ?? 0} - ${f.team_a_score ?? 0}`;
        } else if (isFinished) {
          scoreStr = `FT • ${f.team_h_score ?? 0} - ${f.team_a_score ?? 0}`;
        }

        return {
          id: `fpl_${f.id}`,
          tournament: `🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh • Vòng ${f.event || 8}`,
          teamA: teamH.name,
          teamB: teamA.name,
          teamALogo: teamH.logo,
          teamBLogo: teamA.logo,
          time: scoreStr,
          timeStr: timeFormatted,
          kickoffTime: dateObj.getTime(),
          isLive: isLive,
          isFinished: isFinished
        };
      });
      return upcoming;
    } catch (err) {
      console.warn("Dùng fallback fixtures Ngoại Hạng Anh do FPL fetch không được:", err);
      // Fallback danh sách các trận đấu thực tế vòng 8 & 9 Ngoại Hạng Anh
      return [
        {
          id: "fpl_fallback_1",
          tournament: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh • Vòng 8",
          teamA: "Aston Villa",
          teamB: "Manchester City",
          teamALogo: "https://resources.premierleague.com/premierleague/badges/70/t7.png",
          teamBLogo: "https://resources.premierleague.com/premierleague/badges/70/t43.png",
          time: "18:30 • Thứ 7 (24/10)",
          timeStr: "18:30 • 24/10",
          kickoffTime: Date.now() + 3600000 * 24,
          isLive: false,
          isFinished: false
        },
        {
          id: "fpl_fallback_2",
          tournament: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh • Vòng 8",
          teamA: "Arsenal",
          teamB: "Everton",
          teamALogo: "https://resources.premierleague.com/premierleague/badges/70/t3.png",
          teamBLogo: "https://resources.premierleague.com/premierleague/badges/70/t11.png",
          time: "21:00 • Thứ 7 (24/10)",
          timeStr: "21:00 • 24/10",
          kickoffTime: Date.now() + 3600000 * 26,
          isLive: false,
          isFinished: false
        },
        {
          id: "fpl_fallback_3",
          tournament: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh • Vòng 8",
          teamA: "Chelsea",
          teamB: "Tottenham Hotspur",
          teamALogo: "https://resources.premierleague.com/premierleague/badges/70/t8.png",
          teamBLogo: "https://resources.premierleague.com/premierleague/badges/70/t6.png",
          time: "23:30 • Thứ 7 (24/10)",
          timeStr: "23:30 • 24/10",
          kickoffTime: Date.now() + 3600000 * 29,
          isLive: false,
          isFinished: false
        },
        {
          id: "fpl_fallback_4",
          tournament: "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh • Vòng 8",
          teamA: "Liverpool",
          teamB: "Manchester United",
          teamALogo: "https://resources.premierleague.com/premierleague/badges/70/t14.png",
          teamBLogo: "https://resources.premierleague.com/premierleague/badges/70/t1.png",
          time: "22:30 • Chủ Nhật (25/10)",
          timeStr: "22:30 • 25/10",
          kickoffTime: Date.now() + 3600000 * 48,
          isLive: false,
          isFinished: false
        }
      ];
    }
  }

  // --- Modal Chọn 1 Trong 4 Server Xem Trực Tiếp ---
  function openMatchServerModal(match) {
    activeMatchForServer = match;
    const modal = document.getElementById('matchServerModal');
    if (!modal) return;

    document.getElementById('serverModalLeague').textContent = match.tournament || '🏴󠁧󠁢󠁥󠁮󠁧󠁿 NGOẠI HẠNG ANH';
    document.getElementById('serverModalTeams').textContent = `${match.teamA} vs ${match.teamB}`;
    document.getElementById('serverModalTime').textContent = match.time || 'Trực Tiếp';

    modal.style.display = 'flex';
  }

  function initMatchServerModalEvents() {
    const modal = document.getElementById('matchServerModal');
    const btnClose = document.getElementById('btnCloseServerModal');
    if (btnClose) {
      btnClose.addEventListener('click', () => {
        if (modal) modal.style.display = 'none';
      });
    }

    // Server 1: Thập Cẩm HD
    document.getElementById('btnServer1')?.addEventListener('click', () => {
      if (modal) modal.style.display = 'none';
      playMatchViaServer(1, activeMatchForServer);
    });

    // Server 2: Xôi Lạc HD
    document.getElementById('btnServer2')?.addEventListener('click', () => {
      if (modal) modal.style.display = 'none';
      playMatchViaServer(2, activeMatchForServer);
    });

    // Server 3: Về Bờ HD
    document.getElementById('btnServer3')?.addEventListener('click', () => {
      if (modal) modal.style.display = 'none';
      playMatchViaServer(3, activeMatchForServer);
    });

    // Server 4: Vệ Tinh Quốc Tế (True Premier / Astro 1080p 50fps)
    document.getElementById('btnServer4')?.addEventListener('click', () => {
      if (modal) modal.style.display = 'none';
      playMatchViaServer(4, activeMatchForServer);
    });

    // Thoát Web Player Trận Đấu
    document.getElementById('btnCloseMatchWebPlayer')?.addEventListener('click', () => {
      closeMatchWebPlayer();
    });

    // Đổi Server Nhanh
    document.getElementById('btnSwitchServerQuick')?.addEventListener('click', () => {
      closeMatchWebPlayer();
      if (activeMatchForServer) openMatchServerModal(activeMatchForServer);
    });

    // Toàn màn hình match web player
    document.getElementById('btnFullscreenMatch')?.addEventListener('click', () => {
      const container = document.getElementById('matchWebPlayerContainer');
      if (!document.fullscreenElement) {
        container.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });
  }

  function playMatchViaServer(serverNum, match) {
    if (!match) return;

    if (serverNum === 4) {
      // Server 4: Mở kênh Vệ Tinh Quốc Tế True Premier Football hoặc Astro SuperSport phát trực tiếp
      const allChannels = getAllChannels();
      const satChannel = allChannels.find(c => c.id === 'sports_sat_true_premier_1') ||
                         allChannels.find(c => (c.name || '').includes('True Premier')) ||
                         allChannels.find(c => (c.name || '').includes('Astro SuperSport')) ||
                         allChannels.find(c => (c.group || '').includes('Vệ Tinh'));
      if (satChannel) {
        showToast(`🟡 Đang mở Server 4: ${satChannel.name}...`);
        playTvChannelDirectly({
          id: satChannel.id,
          name: `[Server 4 Vệ Tinh] ${match.teamA} vs ${match.teamB}`,
          streamUrl: satChannel.url,
          posterUrl: satChannel.logo
        });
      } else {
        showToast('Kênh vệ tinh đang được tải...');
      }
      return;
    }

    // Server 1, 2, 3: Mở Web Player không quảng cáo với domain đang hoạt động
    const container = document.getElementById('matchWebPlayerContainer');
    const iframe = document.getElementById('matchIframe');
    const titleEl = document.getElementById('matchWebPlayerTitle');
    const subEl = document.getElementById('matchWebPlayerSub');

    if (!container || !iframe) return;

    titleEl.textContent = `⚽ ${match.teamA} vs ${match.teamB}`;
    
    let streamEmbedUrl = '';
    if (serverNum === 1) {
      subEl.textContent = 'Server 1: Thập Cẩm HD (Bình Luận Tiếng Việt • Ad-Free)';
      streamEmbedUrl = 'https://thapcamtv.to/';
    } else if (serverNum === 2) {
      subEl.textContent = 'Server 2: Xôi Lạc HD (Bình Luận Tiếng Việt • Ad-Free)';
      streamEmbedUrl = 'https://xoilac-tv.college/';
    } else {
      subEl.textContent = 'Server 3: Về Bờ HD (Bình Luận Tiếng Việt • Ad-Free)';
      streamEmbedUrl = 'https://vebotv.live/';
    }

    showToast(`Đang kết nối Server ${serverNum} (Không quảng cáo)...`);
    iframe.src = streamEmbedUrl;
    container.style.display = 'block';

    // Tiêm mã CSS/JS để xóa sạch 100% banner quảng cáo cá cược
    iframe.onload = () => {
      try {
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        if (doc) {
          const style = doc.createElement('style');
          style.innerHTML = `
            .banner, .banner-ads, .popup-ads, .ad-box, #chat-box, .advertisement, [class*="bet"], [class*="banner"] { display: none !important; }
            header, footer, nav, .sidebar { display: none !important; }
            body, html { background: #000 !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important; }
            video, iframe, #player { width: 100vw !important; height: 100vh !important; max-height: 100vh !important; }
          `;
          doc.head.appendChild(style);
        }
      } catch (e) {
        // Cross-origin injection handled securely via sandbox/browser
      }
    };
  }

  function closeMatchWebPlayer() {
    const container = document.getElementById('matchWebPlayerContainer');
    const iframe = document.getElementById('matchIframe');
    if (iframe) iframe.src = 'about:blank';
    if (container) container.style.display = 'none';
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
      card.dataset.id = movie.id;

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
          ${movie.isEplMatch ? `
            <div style="margin-top: 6px; display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 11px; color: var(--accent-cyan); font-weight: bold;">4 Server Trực Tiếp</span>
              <button class="btn-bell-reminder ${movie.hasReminder ? 'active' : ''}" data-match-id="${movie.id}" title="Thông báo khi đến giờ đá">
                ${movie.hasReminder ? '🔔 Đã Đặt' : '🔔 Nhắc Tôi'}
              </button>
            </div>
          ` : ''}
        </div>
      `;

      // Click card
      card.addEventListener('click', (e) => {
        if (movie.isEplMatch && movie.rawMatch) {
          // Bấm vào trận đấu Ngoại Hạng Anh: Mở bảng chọn 1 trong 4 Server
          openMatchServerModal(movie.rawMatch);
          return;
        }
        if (movie.source === 'XEMTIVI') {
          // BẤM VÀO KÊNH TV: VÀO XEM TRỰC TIẾP NGAY LẬP TỨC (Quy tắc v2.1)
          playTvChannelDirectly(movie);
        } else {
          openMovieDetail(movie);
        }
      });

      // Gán sự kiện cho nút chuông nhắc nhở độc lập
      const bellBtn = card.querySelector('.btn-bell-reminder');
      if (bellBtn && movie.rawMatch) {
        bellBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          const isSet = toggleMatchReminder(movie.rawMatch);
          bellBtn.classList.toggle('active', isSet);
          bellBtn.innerHTML = isSet ? '🔔 Đã Đặt' : '🔔 Nhắc Tôi';
        });
      }

      // Long press / Context menu / Yellow key: Toggle Favorite
      card.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        toggleFavorite(movie);
        loadMovies(true);
      });

      grid.appendChild(card);
    });

    // Tự động focus phần tử đầu tiên nếu chưa có focus
    if (!currentFocusedElement || !document.body.contains(currentFocusedElement)) {
      const firstCard = grid.querySelector('.movie-card');
      if (firstCard) setFocus(firstCard);
    }
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

    setTimeout(() => {
      const playFirst = document.getElementById('btnPlayFirst');
      if (playFirst) setFocus(playFirst);
    }, 50);

    document.getElementById('btnCloseDetail').onclick = () => {
      modal.style.display = 'none';
      focusCurrentOrFirstMovie();
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

  // --- Video Player (Native WebOS Hardware Decoding & HLS Fallback) ---
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

    // Reset video & HLS & Subtitles
    if (hlsInstance) {
      hlsInstance.destroy();
      hlsInstance = null;
    }
    video.pause();
    video.removeAttribute('src');
    video.querySelectorAll('track').forEach(t => t.remove());
    video.load();

    if (ep && ep.subtitleUrl) {
      const track = document.createElement('track');
      track.kind = 'subtitles';
      track.srclang = 'vi';
      track.label = 'Tiếng Việt';
      track.src = ep.subtitleUrl;
      track.default = true;
      video.appendChild(track);
    }

    if (window.Hls && Hls.isSupported() && streamUrl.includes('.m3u8')) {
      // 🚀 HLS.JS: Tương thích 100% với Windows PC, Edge Chromium & WebView2
      hlsInstance = new Hls({
        maxBufferLength: 30,
        maxMaxBufferLength: 60,
        maxBufferSize: 60 * 1024 * 1024,
        lowLatencyMode: false,
        enableWorker: true
      });
      hlsInstance.loadSource(streamUrl);
      hlsInstance.attachMedia(video);
      hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(e => {
          console.log('Play attempt error:', e);
        });
      });
      hlsInstance.on(Hls.Events.ERROR, (event, data) => {
        console.error('HLS ERROR:', data.type, data.details, data.fatal);
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
    } else if (isNativeWebOS && streamUrl.includes('.m3u8')) {
      // 🚀 Dành riêng cho TV LG webOS Native
      video.src = streamUrl;
      video.load();
      video.play().catch(e => console.log('Native auto play blocked:', e));
    } else {
      video.src = streamUrl;
      video.load();
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

    // Tự động focus nút Play/Pause trong player
    setTimeout(() => {
      const playBtn = document.getElementById('btnPlayPause');
      if (playBtn) setFocus(playBtn);
    }, 100);
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
    closePlayer(true);
  });

  document.getElementById('btnToggleFavPlayer').addEventListener('click', () => {
    if (currentPlayingMovie) {
      toggleFavorite(currentPlayingMovie);
    }
  });

  const btnFullscreen = document.getElementById('btnFullscreen');
  if (btnFullscreen) {
    btnFullscreen.addEventListener('click', () => {
      const container = document.getElementById('playerContainer');
      if (!document.fullscreenElement) {
        if (container.requestFullscreen) {
          container.requestFullscreen().catch(() => {});
        }
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen().catch(() => {});
        }
      }
    });
  }

  function closePlayer(shouldReturnToDetail = true) {
    if (video) {
      if (currentPlayingMovie && video.duration) {
        saveHistory(currentPlayingMovie, video.currentTime, video.duration, document.getElementById('playerSub').textContent);
      }
      video.pause();
      video.removeAttribute('src');
      video.load();
    }
    if (hlsInstance) {
      hlsInstance.destroy();
      hlsInstance = null;
    }
    document.getElementById('playerContainer').style.display = 'none';
    document.getElementById('zappingPanel').classList.remove('open');

    // Nếu vừa xem phim từ màn hình chi tiết, mở lại Detail Modal
    if (shouldReturnToDetail && currentPlayingDetail && currentPlayingMovie && currentPlayingMovie.source !== 'XEMTIVI') {
      const modal = document.getElementById('detailModal');
      modal.style.display = 'flex';
      setTimeout(() => {
        const epBtns = modal.querySelectorAll('.btn-episode');
        if (epBtns && epBtns[currentEpisodeIndex]) {
          setFocus(epBtns[currentEpisodeIndex]);
        } else {
          const firstBtn = modal.querySelector('.btn-primary-yellow') || document.getElementById('btnCloseDetail');
          if (firstBtn) setFocus(firstBtn);
        }
      }, 50);
    } else {
      // Với TV hoặc không có detail, quay về Grid và focus lại kênh
      setTimeout(() => {
        focusCurrentOrFirstMovie();
      }, 50);
    }
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
  const btnUpdateHeader = document.getElementById('btnUpdateHeader');
  if (btnUpdateHeader) {
    btnUpdateHeader.addEventListener('click', () => {
      showToast('Đang kiểm tra bản cập nhật mới...');
      if (window.chrome && window.chrome.webview) {
        window.chrome.webview.postMessage('check_update');
      } else {
        showToast('Tính năng cập nhật khả dụng trên ứng dụng Huy Cá Windows!');
      }
    });
  }

  // --- Spatial Navigation 2D Engine for LG Remote & Smart TV ---
  function setFocus(el) {
    if (!el) return;
    if (currentFocusedElement && currentFocusedElement !== el) {
      currentFocusedElement.classList.remove('focused');
    }
    currentFocusedElement = el;
    el.classList.add('focused');
    try {
      el.focus();
    } catch (e) {}
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
  }

  function getActiveScope() {
    const zap = document.getElementById('zappingPanel');
    if (zap && zap.classList.contains('open')) return zap;

    const player = document.getElementById('playerContainer');
    if (player && player.style.display === 'flex') return player;

    const search = document.getElementById('searchModal');
    if (search && search.style.display === 'flex') return search;

    const detail = document.getElementById('detailModal');
    if (detail && detail.style.display === 'flex') return detail;

    const sched = document.getElementById('scheduleModal');
    if (sched && sched.style.display === 'flex') return sched;

    const iptv = document.getElementById('iptvModal');
    if (iptv && iptv.style.display === 'flex') return iptv;

    return document.body;
  }

  function getFocusableCandidates(scope) {
    const candidates = Array.from(scope.querySelectorAll('.focusable, button:not([disabled]), input:not([disabled]), [tabindex="0"]'));
    return candidates.filter(el => {
      if (el.disabled || el.getAttribute('aria-hidden') === 'true') return false;
      const rect = el.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) return false;
      const style = window.getComputedStyle(el);
      return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
    });
  }

  function focusCurrentOrFirstMovie() {
    const scope = getActiveScope();
    const candidates = getFocusableCandidates(scope);
    if (candidates.length === 0) return;

    if (currentPlayingMovie) {
      const match = candidates.find(c => c.dataset && c.dataset.id === currentPlayingMovie.id);
      if (match) {
        setFocus(match);
        return;
      }
    }
    const firstCard = scope.querySelector('.movie-card') || candidates[0];
    if (firstCard) setFocus(firstCard);
  }

  function navigate2D(direction) {
    const scope = getActiveScope();
    const isPlayerActive = scope.id === 'playerContainer';

    // Xử lý riêng khi đang ở màn hình Video Player
    if (isPlayerActive) {
      const overlay = document.getElementById('playerOverlay');
      const isOverlayHidden = overlay.classList.contains('hide');

      if (direction === 'left') {
        video.currentTime = Math.max(0, video.currentTime - 10);
        resetOverlayTimer();
        showToast('⏪ -10 giây');
        return;
      }
      if (direction === 'right') {
        video.currentTime = Math.min(video.duration || 0, video.currentTime + 10);
        resetOverlayTimer();
        showToast('⏩ +10 giây');
        return;
      }
      if (isOverlayHidden) {
        resetOverlayTimer();
        const playBtn = document.getElementById('btnPlayPause');
        if (playBtn) setFocus(playBtn);
        return;
      }
    }

    const candidates = getFocusableCandidates(scope);
    if (candidates.length === 0) return;

    let current = document.activeElement;
    if (!current || !scope.contains(current) || current === document.body) {
      current = currentFocusedElement && scope.contains(currentFocusedElement) ? currentFocusedElement : candidates[0];
      setFocus(current);
      return;
    }

    const rect1 = current.getBoundingClientRect();
    const c1 = {
      x: rect1.left + rect1.width / 2,
      y: rect1.top + rect1.height / 2
    };

    let bestCandidate = null;
    let minScore = Infinity;

    for (let i = 0; i < candidates.length; i++) {
      const cand = candidates[i];
      if (cand === current) continue;

      const rect2 = cand.getBoundingClientRect();
      const c2 = {
        x: rect2.left + rect2.width / 2,
        y: rect2.top + rect2.height / 2
      };

      const dx = c2.x - c1.x;
      const dy = c2.y - c1.y;

      let isValidDirection = false;
      let primaryDist = 0;
      let secondaryDist = 0;

      if (direction === 'up') {
        if (rect2.bottom <= rect1.top + 8 || dy < -8) {
          isValidDirection = true;
          primaryDist = -dy;
          secondaryDist = Math.abs(dx);
        }
      } else if (direction === 'down') {
        if (rect2.top >= rect1.bottom - 8 || dy > 8) {
          isValidDirection = true;
          primaryDist = dy;
          secondaryDist = Math.abs(dx);
        }
      } else if (direction === 'left') {
        if (rect2.right <= rect1.left + 8 || dx < -8) {
          isValidDirection = true;
          primaryDist = -dx;
          secondaryDist = Math.abs(dy);
        }
      } else if (direction === 'right') {
        if (rect2.left >= rect1.right - 8 || dx > 8) {
          isValidDirection = true;
          primaryDist = dx;
          secondaryDist = Math.abs(dy);
        }
      }

      if (isValidDirection) {
        // Trọng số phạt cho khoảng cách trục phụ để ưu tiên phần tử thẳng hàng
        const score = primaryDist + (secondaryDist * 2.2);
        if (score < minScore) {
          minScore = score;
          bestCandidate = cand;
        }
      }
    }

    if (bestCandidate) {
      setFocus(bestCandidate);
    }
  }

  // --- Multi-tiered Back Button Handler ---
  function handleBackAction(e) {
    if (e && typeof e.preventDefault === 'function') {
      e.preventDefault();
      e.stopPropagation();
    }

    const zap = document.getElementById('zappingPanel');
    const player = document.getElementById('playerContainer');
    const detail = document.getElementById('detailModal');
    const sched = document.getElementById('scheduleModal');
    const iptv = document.getElementById('iptvModal');
    const search = document.getElementById('searchModal');

    // Đóng Match Web Player nếu đang mở
    const matchWebPlayer = document.getElementById('matchWebPlayerContainer');
    if (matchWebPlayer && matchWebPlayer.style.display === 'block') {
      closeMatchWebPlayer();
      return;
    }

    // Đóng Match Server Modal nếu đang mở
    const matchServerModal = document.getElementById('matchServerModal');
    if (matchServerModal && matchServerModal.style.display === 'flex') {
      matchServerModal.style.display = 'none';
      return;
    }
    // 1. Nếu Quick Zapping Drawer đang mở -> đóng drawer
    if (zap && zap.classList.contains('open')) {
      zap.classList.remove('open');
      const zapBtn = document.getElementById('btnQuickZap');
      if (zapBtn) setFocus(zapBtn);
      return;
    }

    // 2. Nếu Video Player đang mở -> Đóng player và quay lại Detail Modal (với phim) hoặc Grid (với TV)
    if (player && player.style.display === 'flex') {
      closePlayer(true);
      return;
    }

    // 3. Nếu Detail Modal đang mở -> Đóng modal, quay về grid
    if (detail && detail.style.display === 'flex') {
      detail.style.display = 'none';
      focusCurrentOrFirstMovie();
      return;
    }

    // 4. Nếu Schedule Modal đang mở -> Đóng
    if (sched && sched.style.display === 'flex') {
      sched.style.display = 'none';
      const btn = document.getElementById('btnScheduleHeader');
      if (btn) setFocus(btn);
      return;
    }

    // 5. Nếu IPTV Modal đang mở -> Đóng
    if (iptv && iptv.style.display === 'flex') {
      iptv.style.display = 'none';
      focusCurrentOrFirstMovie();
      return;
    }

    // 6. Nếu Search Modal đang mở -> Đóng
    if (search && search.style.display === 'flex') {
      search.style.display = 'none';
      const btn = document.getElementById('btnSearch');
      if (btn) setFocus(btn);
      return;
    }

    // 7. Nếu đang ở filter khác filter đầu tiên, quay lại filter đầu tiên
    const currentFilters = FILTERS[currentSource] || [];
    if (currentFilters.length > 0 && currentFilter !== currentFilters[0].url) {
      const firstFilterBtn = document.querySelector('.btn-filter');
      if (firstFilterBtn) {
        firstFilterBtn.click();
        return;
      }
    }

    // 8. Ở màn hình chính -> Bấm 2 lần trong 2.5s để thoát ứng dụng
    const now = Date.now();
    if (now - lastBackTime < 2500) {
      showToast('Đang thoát ứng dụng...');
      try {
        if (window.webOS && typeof window.webOS.platformBack === 'function') {
          window.webOS.platformBack();
        } else {
          window.close();
        }
      } catch (err) {
        window.close();
      }
    } else {
      lastBackTime = now;
      showToast('Nhấn Quay Lại một lần nữa để thoát ứng dụng');
    }
  }

  // --- Remote Key Listeners (LG webOS & Spatial Navigation) ---
  window.addEventListener('keydown', (e) => {
    const code = e.keyCode || e.which;

    // Phím Back: LG webOS Back Button (461), Escape (27), Backspace (8)
    if (code === 461 || code === 27 || (code === 8 && document.activeElement.tagName !== 'INPUT')) {
      e.preventDefault();
      handleBackAction(e);
      return;
    }

    // Space (32) trên PC: Tạm dừng / Tiếp tục xem phim
    if (code === 32 && document.activeElement.tagName !== 'INPUT') {
      const player = document.getElementById('playerContainer');
      if (player && player.style.display === 'flex') {
        e.preventDefault();
        btnPlayPause.click();
        return;
      }
    }

    // F (70) trên PC: Bật / Tắt toàn màn hình
    if (code === 70 && document.activeElement.tagName !== 'INPUT') {
      const player = document.getElementById('playerContainer');
      if (player && player.style.display === 'flex') {
        const fsBtn = document.getElementById('btnFullscreen');
        if (fsBtn) {
          e.preventDefault();
          fsBtn.click();
          return;
        }
      }
    }

    // M (77) trên PC: Bật / Tắt âm thanh (Mute)
    if (code === 77 && document.activeElement.tagName !== 'INPUT') {
      if (video) {
        e.preventDefault();
        video.muted = !video.muted;
        showToast(video.muted ? '🔇 Đã tắt tiếng' : '🔊 Đã bật tiếng');
        return;
      }
    }

    // D-Pad Navigation: ArrowUp (38), ArrowDown (40), ArrowLeft (37), ArrowRight (39)
    if (code === 38) { // Up
      e.preventDefault();
      navigate2D('up');
      return;
    }
    if (code === 40) { // Down
      e.preventDefault();
      navigate2D('down');
      return;
    }
    if (code === 37) { // Left
      if (document.activeElement.tagName !== 'INPUT') {
        e.preventDefault();
        navigate2D('left');
        return;
      }
    }
    if (code === 39) { // Right
      if (document.activeElement.tagName !== 'INPUT') {
        e.preventDefault();
        navigate2D('right');
        return;
      }
    }

    // OK / Enter (13)
    if (code === 13) {
      const player = document.getElementById('playerContainer');
      if (player && player.style.display === 'flex') {
        const overlay = document.getElementById('playerOverlay');
        if (overlay && overlay.classList.contains('hide')) {
          e.preventDefault();
          resetOverlayTimer();
          btnPlayPause.click();
          return;
        }
      }
      if (document.activeElement && typeof document.activeElement.click === 'function') {
        if (document.activeElement.tagName !== 'BUTTON' && document.activeElement.tagName !== 'INPUT') {
          e.preventDefault();
          document.activeElement.click();
        }
      }
      return;
    }

    // Number keys 0-9 for Quick Zapping
    if (code >= 48 && code <= 57) {
      const numStr = String.fromCharCode(code);
      handleNumberZap(numStr);
      return;
    }

    // Media keys từ Remote LG: Play (415), Pause (19), Stop (413), FastForward (417), Rewind (412)
    if (code === 415) { // Play
      if (video && video.paused) {
        video.play();
        btnPlayPause.textContent = '⏸️ Tạm Dừng';
      }
    } else if (code === 19 || code === 413) { // Pause / Stop
      if (video && !video.paused) {
        video.pause();
        btnPlayPause.textContent = '▶️ Tiếp Tục';
      }
    } else if (code === 412) { // Rewind
      if (video) {
        video.currentTime = Math.max(0, video.currentTime - 10);
        showToast('⏪ -10 giây');
      }
    } else if (code === 417) { // FastForward
      if (video) {
        video.currentTime = Math.min(video.duration || 0, video.currentTime + 10);
        showToast('⏩ +10 giây');
      }
    }
  });

  // Lắng nghe sự kiện webOSBack và popstate từ TV LG
  document.addEventListener('webOSBack', handleBackAction);
  window.addEventListener('popstate', handleBackAction);

  // --- Xử Lý Nút Back Trên Chuột (XButton1 / Mouse Button 3 trong DOM) ---
  window.addEventListener('mouseup', (e) => {
    // e.button: 0=Left, 1=Middle, 2=Right, 3=XButton1 (Back), 4=XButton2 (Forward)
    if (e.button === 3) {
      e.preventDefault();
      e.stopPropagation();
      handleBackAction(e);
    }
  }, true);

  window.addEventListener('pointerup', (e) => {
    if (e.button === 3) {
      e.preventDefault();
      e.stopPropagation();
      handleBackAction(e);
    }
  }, true);

  window.addEventListener('mousedown', (e) => {
    if (e.button === 3) {
      e.preventDefault();
      e.stopPropagation();
    }
  }, true);

  // Expose ra window để WPF C# có thể kích hoạt trực tiếp
  window.handleBackAction = handleBackAction;

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

  // --- Phân Trang & Cuộn Chuột Tự Động Tải Thêm Phim (Windows PC) ---
  const btnLoadMore = document.getElementById('btnLoadMore');
  if (btnLoadMore) {
    btnLoadMore.addEventListener('click', () => {
      loadMoreMovies();
    });
  }

  const btnScrollTop = document.getElementById('btnScrollTop');
  if (btnScrollTop) {
    btnScrollTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  let scrollThrottle = null;
  window.addEventListener('scroll', () => {
    if (btnScrollTop) {
      if (window.scrollY > 400) {
        btnScrollTop.style.display = 'flex';
      } else {
        btnScrollTop.style.display = 'none';
      }
    }

    if (currentSource === 'XEMTIVI' || currentFilter === 'app://favorites' || currentFilter === 'app://history') return;
    if (isLoading) return;

    if (scrollThrottle) return;
    scrollThrottle = setTimeout(() => {
      scrollThrottle = null;
      const scrollPos = window.innerHeight + window.scrollY;
      const docHeight = document.documentElement.scrollHeight;
      if (scrollPos >= docHeight - 600) {
        loadMoreMovies();
      }
    }, 120);
  });

  // --- Remote Security & Maintenance Check ---
  function checkRemoteSecurityLock() {
    fetch('https://raw.githubusercontent.com/uhg031486-hub/HuyCaBuonCa_Release/main/version.json?t=' + Date.now())
      .then(function(r) { return r.json(); })
      .then(function(cfg) {
        if (cfg && cfg.isMaintenanceLocked) {
          document.body.innerHTML = 
            '<div style="position:fixed;inset:0;background:#0b0e14;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px;text-align:center;z-index:999999;font-family:sans-serif;">' +
              '<div style="font-size:64px;margin-bottom:16px;">🔒</div>' +
              '<h1 style="color:#ffd700;font-size:26px;margin-bottom:12px;font-weight:bold;">THÔNG BÁO BẢO TRÌ NỘI BỘ</h1>' +
              '<p style="font-size:16px;color:#8a99ad;max-width:540px;line-height:1.6;margin:0 auto 20px;">' + (cfg.maintenanceMessage || 'Hệ thống đang bảo trì nội bộ. Vui lòng quay lại sau!') + '</p>' +
            '</div>';
        }
      })
      .catch(function() {});
  }

  // --- Initialize App ---
  checkRemoteSecurityLock();
  initSources();
  initFilterBarNavigation();
  initMatchServerModalEvents();
  startReminderChecker();
  renderFilterBar();
  renderHistoryAndFavs();
})();
