import React from 'react';
import { Play, Star, Plus, Info } from 'lucide-react';

export default function MovieCard({ 
  movie, 
  onPlay, 
  onOpenDetail,
  aspect = 'poster' // 'poster' (2:3) or 'backdrop' (16:9)
}) {
  if (!movie) return null;

  const isBackdrop = aspect === 'backdrop';

  return (
    <div 
      className="group relative flex-shrink-0 cursor-pointer select-none"
      onClick={() => onOpenDetail(movie)}
    >
      {/* Outer Card Container */}
      <div className={`relative overflow-hidden rounded-xl bg-[#161E2E] border border-white/10 transition-all duration-300 ease-out transform group-hover:scale-105 group-hover:border-white/30 group-hover:shadow-[0_12px_30px_rgba(0,0,0,0.8)] ${
        isBackdrop ? 'w-64 sm:w-80 aspect-video' : 'w-36 sm:w-44 md:w-52 aspect-[2/3]'
      }`}>
        
        {/* Poster Image */}
        <img
          src={isBackdrop ? (movie.backdrop || movie.poster) : movie.poster}
          alt={movie.title}
          loading="lazy"
          className="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-110"
        />

        {/* Cinematic Vignette Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0B0F17] via-[#0B0F17]/30 to-transparent opacity-80 group-hover:opacity-90 transition-opacity" />

        {/* Top Badges (Quality, Audio, Platform) */}
        <div className="absolute top-2 left-2 right-2 flex items-center justify-between pointer-events-none z-10">
          {movie.quality && (
            <span className="px-1.5 py-0.5 rounded-md bg-[#0B0F17]/80 backdrop-blur-md border border-white/20 text-[10px] sm:text-[11px] font-extrabold text-white tracking-wider uppercase">
              {movie.quality}
            </span>
          )}

          {movie.imdb && (
            <div className="flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-[#F5C518]/20 backdrop-blur-md border border-[#F5C518]/40 text-[#F5C518] text-[10px] sm:text-[11px] font-bold">
              <Star className="w-3 h-3 fill-[#F5C518]" />
              <span>{movie.imdb}</span>
            </div>
          )}

          {movie.platform && (
            <span className="px-1.5 py-0.5 rounded-md bg-[#E50914]/80 text-[10px] font-black text-white uppercase tracking-tight">
              {movie.platform}
            </span>
          )}
        </div>

        {/* Hover Quick Action Buttons (Center Play Button) */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 z-20 backdrop-blur-[2px]">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onPlay(movie);
            }}
            className="w-12 h-12 rounded-full bg-[#E50914] text-white flex items-center justify-center shadow-neon-red transform transition-transform duration-300 hover:scale-110 active:scale-90 cursor-pointer"
            title="Phát nhanh"
          >
            <Play className="w-6 h-6 fill-white ml-0.5" />
          </button>
        </div>

        {/* Bottom Content / Info */}
        <div className="absolute bottom-0 left-0 right-0 p-2.5 sm:p-3 z-10">
          <h3 className="text-xs sm:text-sm font-bold text-white truncate drop-shadow-md group-hover:text-[#E50914] transition-colors">
            {movie.title}
          </h3>
          
          <div className="flex items-center justify-between text-[11px] text-gray-400 mt-1">
            <span className="truncate max-w-[70%]">
              {movie.audio || movie.category || movie.episodesCount || movie.year}
            </span>
            {movie.year && !movie.audio && (
              <span>{movie.year}</span>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
