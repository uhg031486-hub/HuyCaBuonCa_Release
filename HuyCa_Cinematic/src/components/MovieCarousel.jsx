import React, { useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import MovieCard from './MovieCard';

export default function MovieCarousel({ 
  title, 
  subtitle, 
  icon: Icon, 
  movies = [], 
  onPlayMovie, 
  onOpenDetail,
  accentColor = '#E50914',
  aspect = 'poster'
}) {
  const scrollRef = useRef(null);

  const scroll = (direction) => {
    if (scrollRef.current) {
      const { scrollLeft, clientWidth } = scrollRef.current;
      const scrollAmount = clientWidth * 0.75;
      scrollRef.current.scrollTo({
        left: direction === 'left' ? scrollLeft - scrollAmount : scrollLeft + scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  if (!movies || movies.length === 0) return null;

  return (
    <section className="relative py-4 sm:py-6 group/section">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex items-end justify-between mb-3 sm:mb-4">
          <div className="flex items-center gap-2.5">
            {Icon && (
              <div 
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white border border-white/10 shadow-sm"
                style={{ backgroundColor: `${accentColor}20`, borderColor: `${accentColor}40` }}
              >
                <Icon className="w-4 h-4" style={{ color: accentColor }} />
              </div>
            )}
            <div>
              <h2 className="text-lg sm:text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
                {title}
              </h2>
              {subtitle && (
                <p className="text-xs sm:text-sm text-gray-400 font-medium">
                  {subtitle}
                </p>
              )}
            </div>
          </div>

          {/* Navigation Controls */}
          <div className="hidden sm:flex items-center gap-2">
            <button
              onClick={() => scroll('left')}
              className="p-2 rounded-xl bg-[#161E2E]/80 hover:bg-[#1E293B] border border-white/10 text-gray-300 hover:text-white backdrop-blur-md transition-all duration-200 cursor-pointer active:scale-90"
              aria-label="Cuộn sang trái"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => scroll('right')}
              className="p-2 rounded-xl bg-[#161E2E]/80 hover:bg-[#1E293B] border border-white/10 text-gray-300 hover:text-white backdrop-blur-md transition-all duration-200 cursor-pointer active:scale-90"
              aria-label="Cuộn sang phải"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Carousel Movie Row */}
        <div 
          ref={scrollRef}
          className="flex items-center gap-3 sm:gap-4 md:gap-5 overflow-x-auto no-scrollbar scroll-smooth py-2 px-1"
        >
          {movies.map((movie) => (
            <MovieCard
              key={movie.id}
              movie={movie}
              onPlay={onPlayMovie}
              onOpenDetail={onOpenDetail}
              aspect={aspect}
            />
          ))}
        </div>

      </div>
    </section>
  );
}
