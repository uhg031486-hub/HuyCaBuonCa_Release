import React, { useState, useEffect, useMemo } from 'react';
import { 
  Film, 
  Sparkles, 
  Flame, 
  Tv, 
  Compass, 
  TrendingUp, 
  Trophy, 
  Clapperboard, 
  Layers,
  Star,
  Play
} from 'lucide-react';

import Navbar from './components/Navbar';
import HeroBanner from './components/HeroBanner';
import MovieCarousel from './components/MovieCarousel';
import DetailModal from './components/DetailModal';
import CinematicPlayer from './components/CinematicPlayer';
import LiveTvSection from './components/LiveTvSection';
import CategoryFilter from './components/CategoryFilter';
import Footer from './components/Footer';

import { 
  FEATURED_MOVIES, 
  TRENDING_MOVIES, 
  LATEST_SERIES, 
  SHORT_DRAMAS, 
  TV_CHANNELS, 
  CATEGORIES 
} from './data/mockMovies';

export default function App() {
  const [activeTab, setActiveTab] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('Tất Cả');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Player & Modal State
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [currentPlayingMovie, setCurrentPlayingMovie] = useState(null);
  const [isMiniMode, setIsMiniMode] = useState(false);

  // Dynamic API Movies from KKPhim
  const [apiMovies, setApiMovies] = useState([]);

  useEffect(() => {
    // Tải dữ liệu thực tế từ KKPhim để làm giàu kho nội dung trực tiếp
    fetch('https://phimapi.com/danh-sach/phim-moi-cap-nhat?page=1')
      .then(res => res.json())
      .then(data => {
        if (data && data.items) {
          const formatted = data.items.slice(0, 10).map(item => ({
            id: item._id || item.slug,
            title: item.name,
            originalTitle: item.origin_name,
            poster: item.poster_url?.startsWith('http') ? item.poster_url : `https://phimimg.com/${item.poster_url}`,
            backdrop: item.thumb_url?.startsWith('http') ? item.thumb_url : `https://phimimg.com/${item.thumb_url}`,
            year: item.year?.toString() || '2024',
            quality: 'Full HD',
            audio: 'Thuyết Minh',
            category: 'Phim Mới Cập Nhật',
            imdb: '7.9',
            overview: `Bộ phim ${item.name} phát hành năm ${item.year}, với cốt truyện cuốn hút và chất lượng điện ảnh đặc sắc.`,
            videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
          }));
          setApiMovies(formatted);
        }
      })
      .catch(err => {
        console.warn('Lấy dữ liệu API ngoài bị trễ, chuyển sang danh mục tuyển chọn nội bộ.', err);
      });
  }, []);

  // Tổng hợp tất cả phim để tìm kiếm
  const allMoviesList = useMemo(() => {
    return [
      ...FEATURED_MOVIES,
      ...TRENDING_MOVIES,
      ...LATEST_SERIES,
      ...SHORT_DRAMAS,
      ...apiMovies
    ];
  }, [apiMovies]);

  // Bộ lọc tìm kiếm trực tiếp
  const searchResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase();
    return allMoviesList.filter(m => 
      m.title.toLowerCase().includes(q) || 
      (m.originalTitle && m.originalTitle.toLowerCase().includes(q)) ||
      (m.category && m.category.toLowerCase().includes(q))
    );
  }, [searchQuery, allMoviesList]);

  // Bộ lọc theo danh mục / tab
  const filteredTrending = useMemo(() => {
    if (selectedCategory === 'Tất Cả') return TRENDING_MOVIES;
    return TRENDING_MOVIES.filter(m => m.category?.includes(selectedCategory) || selectedCategory.includes(m.category));
  }, [selectedCategory]);

  const handlePlayMovie = (movie) => {
    setCurrentPlayingMovie(movie);
    setIsMiniMode(false);
  };

  const handleOpenDetail = (movie) => {
    setSelectedMovie(movie);
  };

  const handleClosePlayer = () => {
    setCurrentPlayingMovie(null);
    setIsMiniMode(false);
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] text-gray-100 flex flex-col font-sans relative selection:bg-[#E50914] selection:text-white">
      
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
        <HeroBanner
          featuredMovies={FEATURED_MOVIES}
          onPlayMovie={handlePlayMovie}
          onOpenDetail={handleOpenDetail}
        />

        {/* Category Pill Filters */}
        <CategoryFilter
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
        />

        {/* Carousel 1: Xu Hướng Điện Ảnh (Trending Now) */}
        <MovieCarousel
          title="Xu Hướng Điện Ảnh Đỉnh Cao"
          subtitle="Top phim được xem nhiều nhất tuần qua"
          icon={TrendingUp}
          movies={filteredTrending}
          onPlayMovie={handlePlayMovie}
          onOpenDetail={handleOpenDetail}
          accentColor="#E50914"
        />

        {/* Section: Kênh TV Trực Tuyến & Thể Thao Đỉnh Cao */}
        <div id="tv">
          <LiveTvSection
            onPlayChannel={(channel) => {
              handlePlayMovie({
                title: channel.name,
                category: channel.group,
                streamUrl: channel.streamUrl,
                videoUrl: channel.streamUrl
              });
            }}
          />
        </div>

        {/* Carousel 2: Phim Bộ Bom Tấn Mới Nhất */}
        <div id="series">
          <MovieCarousel
            title="Phim Bộ Bom Tấn Độc Quyền VIP"
            subtitle="Trọn bộ thuyết minh và vietsub 4K"
            icon={Sparkles}
            movies={LATEST_SERIES}
            onPlayMovie={handlePlayMovie}
            onOpenDetail={handleOpenDetail}
            accentColor="#F5C518"
          />
        </div>

        {/* Carousel 3: Phim Mới Cập Nhật (API Live) */}
        {apiMovies.length > 0 && (
          <MovieCarousel
            title="Phim Mới Cập Nhật Hôm Nay"
            subtitle="Cập nhật từng giờ từ hệ thống rạp chiếu"
            icon={Film}
            movies={apiMovies}
            onPlayMovie={handlePlayMovie}
            onOpenDetail={handleOpenDetail}
            accentColor="#E50914"
          />
        )}

        {/* Carousel 4: Kho Tiểu Kịch Đa Nền Tảng (ReelShort, DramaBox, ShortMax, AI Cinema) */}
        <div id="short-drama">
          <MovieCarousel
            title="Kho Tiểu Kịch Đa Nền Tảng"
            subtitle="ReelShort Âu Mỹ, DramaBox, AI Cinema và ShortMax trọn bộ"
            icon={Compass}
            movies={SHORT_DRAMAS}
            onPlayMovie={handlePlayMovie}
            onOpenDetail={handleOpenDetail}
            accentColor="#E50914"
          />
        </div>

      </main>

      {/* Footer */}
      <Footer />

      {/* Detail Modal Dialog */}
      <DetailModal
        movie={selectedMovie}
        isOpen={!!selectedMovie}
        onClose={() => setSelectedMovie(null)}
        onPlay={handlePlayMovie}
      />

      {/* Cinematic Player (Cả Fullscreen & Floating In-App PiP) */}
      <CinematicPlayer
        currentMovie={currentPlayingMovie}
        isPlaying={!!currentPlayingMovie}
        onClose={handleClosePlayer}
        isMiniMode={isMiniMode}
        setIsMiniMode={setIsMiniMode}
      />

    </div>
  );
}
