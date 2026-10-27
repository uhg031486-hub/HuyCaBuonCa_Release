import React, { useState, useEffect, useMemo } from 'react';
import { 
  Film, 
  Sparkles, 
  Flame, 
  Tv, 
  Compass, 
  TrendingUp, 
  Clapperboard
} from 'lucide-react';

import Navbar from './components/Navbar';
import HeroBanner from './components/HeroBanner';
import MovieCarousel from './components/MovieCarousel';
import DetailModal from './components/DetailModal';
import CinematicPlayer from './components/CinematicPlayer';
import WatchMoviePage from './components/WatchMoviePage';
import LiveTvSection from './components/LiveTvSection';
import CategoryFilter from './components/CategoryFilter';
import Footer from './components/Footer';

import { 
  FEATURED_MOVIES, 
  TRENDING_MOVIES, 
  LATEST_SERIES, 
  SHORT_DRAMAS, 
  TV_CHANNELS 
} from './data/mockMovies';

import {
  fetchKkphimList,
  resolveMovieDetailAndStream,
  searchAllSources,
  FreeReelsApi
} from './services/movieApi';

export default function App() {
  const [activeTab, setActiveTab] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('Tất Cả');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Player & Modal State
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [currentPlayingMovie, setCurrentPlayingMovie] = useState(null);
  const [isMiniMode, setIsMiniMode] = useState(false);
  const [isLoadingStream, setIsLoadingStream] = useState(false);

  // Live Catalog States
  const [liveFeatured, setLiveFeatured] = useState([]);
  const [liveSingleMovies, setLiveSingleMovies] = useState([]);
  const [liveSeriesMovies, setLiveSeriesMovies] = useState([]);
  const [liveAnimeMovies, setLiveAnimeMovies] = useState([]);
  const [liveShortDramas, setLiveShortDramas] = useState([]);
  const [liveSearchResults, setLiveSearchResults] = useState([]);

  useEffect(() => {
    // 1. Tải Phim Mới Cập Nhật Đang Chiếu (Live HLS Streams hoạt động 100%)
    fetchKkphimList('https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=1', 'Phim Mới Cập Nhật')
      .then(list => {
        if (list.length > 0) {
          setLiveFeatured(list.slice(0, 6));
          setLiveSingleMovies(list);
        } else {
          setLiveFeatured(FEATURED_MOVIES);
          setLiveSingleMovies(TRENDING_MOVIES);
        }
      })
      .catch(() => {
        setLiveFeatured(FEATURED_MOVIES);
        setLiveSingleMovies(TRENDING_MOVIES);
      });

    // 2. Tải Phim Bộ Hot Nhất
    fetchKkphimList('https://phimapi.com/v1/api/danh-sach/phim-bo?page=1', 'Phim Bộ Hot')
      .then(list => {
        if (list.length > 0) setLiveSeriesMovies(list);
        else setLiveSeriesMovies(LATEST_SERIES);
      })
      .catch(() => setLiveSeriesMovies(LATEST_SERIES));

    // 3. Tải Hoạt Hình & Anime Đỉnh Cao
    fetchKkphimList('https://phimapi.com/v1/api/danh-sach/hoat-hinh?page=1', 'Anime Đỉnh Cao')
      .then(list => {
        if (list.length > 0) setLiveAnimeMovies(list);
      })
      .catch(() => {});

    // 4. Tải Kho Tiểu Kịch Live Thật (Tổng Tài, Trọng Sinh, DramaBox & ReelShort)
    Promise.all([
      fetchKkphimList('https://phimapi.com/v1/api/tim-kiem?keyword=tổng tài', 'Tiểu Kịch Tổng Tài'),
      fetchKkphimList('https://phimapi.com/v1/api/tim-kiem?keyword=trọng sinh', 'Tiểu Kịch Trọng Sinh')
    ])
      .then(([tongTaiList, trongSinhList]) => {
        const combined = [...(tongTaiList || []), ...(trongSinhList || [])];
        if (combined.length > 0) {
          setLiveShortDramas(combined);
        } else {
          setLiveShortDramas(SHORT_DRAMAS);
        }
      })
      .catch(() => setLiveShortDramas(SHORT_DRAMAS));
  }, []);

  // Live Search Debounce
  useEffect(() => {
    const q = searchQuery.trim();
    if (!q) {
      setLiveSearchResults([]);
      return;
    }
    const timer = setTimeout(() => {
      searchAllSources(q).then(res => {
        if (res && res.length > 0) {
          setLiveSearchResults(res);
        }
      });
    }, 320);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Tổng hợp tất cả phim hiện có để lọc tức thì
  const allMoviesList = useMemo(() => {
    return [
      ...liveSingleMovies,
      ...liveSeriesMovies,
      ...liveAnimeMovies,
      ...liveShortDramas
    ];
  }, [liveSingleMovies, liveSeriesMovies, liveAnimeMovies, liveShortDramas]);

  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    if (liveSearchResults.length > 0) return liveSearchResults;
    const q = searchQuery.toLowerCase();
    return allMoviesList.filter(m => 
      m.title?.toLowerCase().includes(q) || 
      m.originalTitle?.toLowerCase().includes(q)
    );
  }, [searchQuery, liveSearchResults, allMoviesList]);

  // Lọc theo nút Category
  const handleSelectCategory = (cat) => {
    setSelectedCategory(cat);
    if (cat === 'Phim Chiếu Rạp' || cat === 'Phim Mới Cập Nhật') setActiveTab('movies');
    else if (cat === 'Phim Bộ Hot') setActiveTab('series');
    else if (cat === 'Anime Đỉnh Cao') setActiveTab('anime');
    else if (cat === 'Tiểu Kịch ReelShort') setActiveTab('short_drama');
    else if (cat === 'Truyền Hình Thể Thao') setActiveTab('tv');
    else if (cat === 'Hành Động') {
      fetchKkphimList('https://phimapi.com/v1/api/the-loai/hanh-dong?page=1', 'Hành Động').then(l => {
        if (l.length > 0) setLiveSingleMovies(l);
      });
      setActiveTab('movies');
    } else if (cat === 'Khoa Học Viễn Tưởng') {
      fetchKkphimList('https://phimapi.com/v1/api/the-loai/vien-tuong?page=1', 'Khoa Học Viễn Tưởng').then(l => {
        if (l.length > 0) setLiveSingleMovies(l);
      });
      setActiveTab('movies');
    } else if (cat === 'Kinh Dị & Giật Gân') {
      fetchKkphimList('https://phimapi.com/v1/api/the-loai/kinh-di?page=1', 'Kinh Dị & Giật Gân').then(l => {
        if (l.length > 0) setLiveSingleMovies(l);
      });
      setActiveTab('movies');
    } else {
      setActiveTab('all');
    }
  };

  // Khi bấm Phát Phim -> Tự động lấy luồng HLS (.m3u8) thật 100% trước khi mở Player
  const handlePlayMovie = async (movie) => {
    if (!movie) return;
    setIsLoadingStream(true);
    try {
      let resolved = movie;

      // Nếu phim chưa có luồng phát trực tiếp, hoặc link cũ là sample googleapis bị chặn, hoặc chưa nạp danh sách tập
      const isBadUrl = !movie.videoUrl || movie.videoUrl.includes('commondatastorage.googleapis.com');
      if (isBadUrl || !movie.episodes || movie.episodes.length === 0) {
        resolved = await resolveMovieDetailAndStream(movie);
      }

      let videoUrl = resolved.videoUrl || resolved.streamUrl || '';
      let subtitleUrl = resolved.subtitleUrl || null;

      // Nếu tập phim ngắn cần mở khóa (freereels_unlock:seriesId:epId)
      if (videoUrl.startsWith('freereels_unlock:')) {
        const parts = videoUrl.split(':');
        const unl = await FreeReelsApi.unlockEpisode(parts[1], parts[2]);
        if (unl && unl.url) {
          videoUrl = unl.url;
          if (unl.subtitleUrl) subtitleUrl = unl.subtitleUrl;
        }
      }

      setCurrentPlayingMovie({
        ...resolved,
        videoUrl,
        subtitleUrl
      });
      setIsMiniMode(false);
    } finally {
      setIsLoadingStream(false);
    }
  };

  // Khi bấm vào Card Phim -> Lấy đầy đủ thông tin chi tiết & danh sách tập thật
  const handleOpenDetail = async (movie) => {
    if (!movie) return;
    setSelectedMovie({ ...movie, isLoadingEpisodes: true });
    try {
      const fullDetail = await resolveMovieDetailAndStream(movie);
      setSelectedMovie({ ...fullDetail, isLoadingEpisodes: false });
    } catch (e) {
      setSelectedMovie({ ...movie, isLoadingEpisodes: false });
    }
  };

  const handleClosePlayer = () => {
    setCurrentPlayingMovie(null);
    setIsMiniMode(false);
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] text-gray-100 flex flex-col font-sans relative selection:bg-[#E50914] selection:text-white">
      
      {/* Loading Stream Indicator */}
      {isLoadingStream && (
        <div className="fixed inset-0 z-[60] bg-black/70 backdrop-blur-sm flex flex-col items-center justify-center gap-3">
          <div className="w-12 h-12 rounded-full border-4 border-[#E50914] border-t-transparent animate-spin" />
          <p className="text-sm font-bold text-white tracking-wide">Đang kết nối máy chủ phát phim tốc độ cao...</p>
        </div>
      )}

      {/* Khi đang chọn xem phim: Hiển thị giao diện Watch Movie Page cao cấp */}
      {currentPlayingMovie && !isMiniMode ? (
        <WatchMoviePage
          movie={currentPlayingMovie}
          onBack={handleClosePlayer}
          onSwitchMovie={handlePlayMovie}
          relatedMovies={allMoviesList.filter(m => m.id !== currentPlayingMovie.id)}
          onOpenMiniPiP={() => setIsMiniMode(true)}
        />
      ) : (
        <>
          {/* Top Sticky Glassmorphism Navbar */}
          <Navbar
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            searchResults={searchResults}
            onSelectMovie={handleOpenDetail}
          />

          {/* Main Content Area */}
          <main className="flex-1 pb-16">
            
            {/* Full-width Hero Banner Hoành Tráng */}
            {liveFeatured.length > 0 && (
              <HeroBanner
                featuredMovies={liveFeatured}
                onPlayMovie={handlePlayMovie}
                onOpenDetail={handleOpenDetail}
              />
            )}

            {/* Category Pill Filters */}
            <CategoryFilter
              selectedCategory={selectedCategory}
              onSelectCategory={handleSelectCategory}
            />

            {/* Carousel 1: Phim Lẻ & Chiếu Rạp Mới Nhất */}
            {(activeTab === 'all' || activeTab === 'movies') && liveSingleMovies.length > 0 && (
              <MovieCarousel
                title="Phim Lẻ & Chiếu Rạp Mới Nhất"
                subtitle="Phát trực tiếp Full HD / 4K Vietsub & Thuyết Minh"
                icon={TrendingUp}
                movies={liveSingleMovies}
                onPlayMovie={handlePlayMovie}
                onOpenDetail={handleOpenDetail}
                accentColor="#E50914"
              />
            )}

            {/* Carousel 2: Phim Bộ Bom Tấn Độc Quyền */}
            {(activeTab === 'all' || activeTab === 'series') && liveSeriesMovies.length > 0 && (
              <div id="series">
                <MovieCarousel
                  title="Phim Bộ Bom Tấn Độc Quyền VIP"
                  subtitle="Trọn bộ các tập thuyết minh và vietsub cập nhật liên tục"
                  icon={Sparkles}
                  movies={liveSeriesMovies}
                  onPlayMovie={handlePlayMovie}
                  onOpenDetail={handleOpenDetail}
                  accentColor="#F5C518"
                />
              </div>
            )}

            {/* Carousel 3: Anime & Hoạt Hình 3D */}
            {(activeTab === 'all' || activeTab === 'anime') && liveAnimeMovies.length > 0 && (
              <div id="anime">
                <MovieCarousel
                  title="Anime Nhật Bản & Hoạt Hình 3D"
                  subtitle="Tuyển tập Anime & Tu Tiên 3D mới nhất"
                  icon={Flame}
                  movies={liveAnimeMovies}
                  onPlayMovie={handlePlayMovie}
                  onOpenDetail={handleOpenDetail}
                  accentColor="#E50914"
                />
              </div>
            )}

            {/* Carousel 4: Kho Tiểu Kịch Đa Nền Tảng (ReelShort, DramaBox, ShortMax) */}
            {(activeTab === 'all' || activeTab === 'short_drama') && liveShortDramas.length > 0 && (
              <div id="short-drama">
                <MovieCarousel
                  title="Kho Tiểu Kịch Đa Nền Tảng (9:16)"
                  subtitle="ReelShort Âu Mỹ, DramaBox, ShortMax & Phim Lồng Tiếng"
                  icon={Compass}
                  movies={liveShortDramas}
                  onPlayMovie={handlePlayMovie}
                  onOpenDetail={handleOpenDetail}
                  accentColor="#E50914"
                />
              </div>
            )}

            {/* Section: Kênh TV Trực Tuyến & Thể Thao Đỉnh Cao */}
            {(activeTab === 'all' || activeTab === 'tv') && (
              <div id="tv">
                <LiveTvSection
                  onPlayChannel={(channel) => {
                    handlePlayMovie({
                      title: channel.name,
                      category: channel.group,
                      streamUrl: channel.streamUrl,
                      videoUrl: channel.streamUrl,
                      isLiveTv: true
                    });
                  }}
                />
              </div>
            )}

          </main>

          {/* Footer */}
          <Footer />
        </>
      )}

      {/* Detail Modal Dialog */}
      <DetailModal
        movie={selectedMovie}
        isOpen={!!selectedMovie}
        onClose={() => setSelectedMovie(null)}
        onPlay={(m) => {
          setSelectedMovie(null);
          handlePlayMovie(m);
        }}
      />

      {/* Floating In-App Mini PiP Player khi người dùng chuyển sang duyệt trang chủ */}
      {currentPlayingMovie && isMiniMode && (
        <CinematicPlayer
          currentMovie={currentPlayingMovie}
          isPlaying={true}
          onClose={handleClosePlayer}
          isMiniMode={true}
          setIsMiniMode={setIsMiniMode}
          onSwitchEpisode={(epMovie) => handlePlayMovie(epMovie)}
        />
      )}

    </div>
  );
}
