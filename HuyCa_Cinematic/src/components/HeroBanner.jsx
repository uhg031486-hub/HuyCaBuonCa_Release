import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Plus, 
  Check, 
  Info, 
  Star, 
  Volume2, 
  VolumeX, 
  ChevronLeft, 
  ChevronRight,
  ShieldCheck,
  Film
} from 'lucide-react';

export default function HeroBanner({ 
  featuredMovies = [], 
  onPlayMovie, 
  onOpenDetail 
}) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSaved, setIsSaved] = useState(false);
  const [isMuted, setIsMuted] = useState(true);

  const movie = featuredMovies[currentIndex] || featuredMovies[0];

  useEffect(() => {
    if (!featuredMovies.length) return;
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % featuredMovies.length);
    }, 9000);
    return () => clearInterval(timer);
  }, [featuredMovies.length]);

  if (!movie) return null;

  return (
    <div className="relative w-full h-[78vh] sm:h-[88vh] lg:h-[92vh] min-h-[580px] overflow-hidden select-none">
      
      {/* Background Image / Backdrop */}
      <div className="absolute inset-0">
        <img
          src={movie.backdrop}
          alt={movie.title}
          className="w-full h-full object-cover object-center filter brightness-[0.8] scale-100 transition-all duration-1000 ease-out"
        />
        
        {/* Cinematic Side Shadow Gradient (Vignette) */}
        <div className="absolute inset-0 hero-side-gradient"></div>
        
        {/* Bottom Gradient Fade to Dark Background */}
        <div className="absolute inset-0 hero-gradient-overlay"></div>
      </div>

      {/* Hero Content Container */}
      <div className="relative z-10 max-w-7xl mx-auto h-full px-4 sm:px-6 lg:px-8 flex flex-col justify-end pb-16 sm:pb-24">
        <div className="max-w-2xl sm:max-w-3xl space-y-4 sm:space-y-6 animate-in fade-in slide-in-from-bottom-6 duration-700">
          
          {/* Metadata Badges */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs sm:text-sm font-semibold">
            {/* IMDb Rating with Star Vector */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#F5C518]/15 border border-[#F5C518]/40 text-[#F5C518] shadow-sm">
              <Star className="w-4 h-4 fill-[#F5C518]" />
              <span className="font-extrabold tracking-wide">{movie.imdb} IMDb</span>
            </div>

            {/* Quality Badge */}
            <span className="px-2.5 py-1 rounded-md bg-white/10 border border-white/20 text-white font-bold tracking-wider uppercase text-[11px] sm:text-xs">
              {movie.quality}
            </span>

            {/* Audio / Subtitle Badge */}
            <span className="px-2.5 py-1 rounded-md bg-[#E50914]/20 border border-[#E50914]/40 text-red-300 font-bold tracking-wide">
              {movie.audio}
            </span>

            {/* Year & Duration */}
            <span className="text-gray-300 font-medium hidden sm:inline-block">
              {movie.year} • {movie.duration}
            </span>

            {/* Category */}
            <span className="px-2 py-0.5 rounded text-gray-400 bg-white/5 border border-white/10 text-xs hidden md:inline-block">
              {movie.category}
            </span>
          </div>

          {/* Main Title - Bold Sans-serif with Cinematic Presence */}
          <div className="space-y-1">
            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-tight sm:leading-none drop-shadow-2xl">
              {movie.title}
            </h1>
            {movie.originalTitle && (
              <p className="text-sm sm:text-lg text-gray-400 font-semibold tracking-wide">
                {movie.originalTitle}
              </p>
            )}
          </div>

          {/* Synopsis / Overview */}
          <p className="text-gray-300 text-sm sm:text-base lg:text-lg leading-relaxed line-clamp-3 sm:line-clamp-4 max-w-2xl drop-shadow-md">
            {movie.overview}
          </p>

          {/* Action CTA Buttons */}
          <div className="flex flex-wrap items-center gap-3 sm:gap-4 pt-2">
            
            {/* Primary CTA - Xem Ngay (Play Neon Red) */}
            <button
              onClick={() => onPlayMovie(movie)}
              className="px-6 sm:px-8 py-3.5 sm:py-4 rounded-xl bg-[#E50914] hover:bg-[#F40612] text-white font-extrabold text-sm sm:text-base flex items-center gap-2.5 shadow-neon-red hover:shadow-[0_0_35px_rgba(229,9,20,0.6)] cursor-pointer transition-all duration-300 transform hover:scale-105 active:scale-95"
            >
              <Play className="w-5 h-5 fill-white" />
              <span>XEM NGAY</span>
            </button>

            {/* Secondary CTA - Chi Tiết & Trailer */}
            <button
              onClick={() => onOpenDetail(movie)}
              className="px-5 sm:px-6 py-3.5 sm:py-4 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-bold text-sm sm:text-base flex items-center gap-2 backdrop-blur-md cursor-pointer transition-all duration-300 hover:scale-105 active:scale-95"
            >
              <Info className="w-5 h-5 text-gray-300" />
              <span>Chi Tiết Phim</span>
            </button>

            {/* Tertiary CTA - Thêm Vào Danh Sách Lưu */}
            <button
              onClick={() => setIsSaved(!isSaved)}
              className="p-3.5 sm:p-4 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white backdrop-blur-md cursor-pointer transition-all duration-300 hover:scale-105 active:scale-95"
              title={isSaved ? "Đã lưu vào danh sách" : "Thêm vào danh sách xem sau"}
            >
              {isSaved ? <Check className="w-5 h-5 text-[#F5C518]" /> : <Plus className="w-5 h-5" />}
            </button>

          </div>

        </div>
      </div>

      {/* Carousel Navigation Arrows & Dots */}
      <div className="absolute right-4 sm:right-8 bottom-16 sm:bottom-24 z-20 flex items-center gap-2 sm:gap-3">
        <button
          onClick={() => setCurrentIndex((prev) => (prev - 1 + featuredMovies.length) % featuredMovies.length)}
          className="p-2 sm:p-2.5 rounded-full bg-[#161E2E]/80 hover:bg-[#E50914] border border-white/15 text-white backdrop-blur-md transition-all duration-200 cursor-pointer hover:scale-110"
          aria-label="Phim trước"
        >
          <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />
        </button>

        <div className="flex items-center gap-1.5 px-2">
          {featuredMovies.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentIndex(idx)}
              className={`h-1.5 rounded-full transition-all duration-300 cursor-pointer ${
                idx === currentIndex ? 'w-6 bg-[#E50914] shadow-neon-red' : 'w-2 bg-white/30 hover:bg-white/60'
              }`}
              aria-label={`Slide ${idx + 1}`}
            />
          ))}
        </div>

        <button
          onClick={() => setCurrentIndex((prev) => (prev + 1) % featuredMovies.length)}
          className="p-2 sm:p-2.5 rounded-full bg-[#161E2E]/80 hover:bg-[#E50914] border border-white/15 text-white backdrop-blur-md transition-all duration-200 cursor-pointer hover:scale-110"
          aria-label="Phim tiếp theo"
        >
          <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
      </div>

    </div>
  );
}
