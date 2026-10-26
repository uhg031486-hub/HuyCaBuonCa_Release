import React from 'react';
import { 
  X, 
  Play, 
  Star, 
  Plus, 
  Clock, 
  Film, 
  Users, 
  Clapperboard, 
  Share2, 
  Check 
} from 'lucide-react';

export default function DetailModal({ 
  movie, 
  isOpen, 
  onClose, 
  onPlay 
}) {
  if (!isOpen || !movie) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto animate-in fade-in duration-200">
      
      {/* Blurred Backdrop Overlay */}
      <div 
        className="fixed inset-0 bg-[#070A0F]/85 backdrop-blur-md transition-opacity" 
        onClick={onClose} 
      />

      {/* Modal Dialog Content */}
      <div className="relative w-full max-w-4xl bg-[#121824] border border-white/15 rounded-2xl shadow-2xl overflow-hidden z-10 max-h-[90vh] flex flex-col my-auto">
        
        {/* Header Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2.5 rounded-full bg-[#0B0F17]/80 hover:bg-[#E50914] text-white border border-white/15 backdrop-blur-md transition-all duration-200 cursor-pointer"
          aria-label="Đóng"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Hero Banner Area */}
        <div className="relative w-full h-64 sm:h-80 md:h-96 flex-shrink-0">
          <img
            src={movie.backdrop || movie.poster}
            alt={movie.title}
            className="w-full h-full object-cover filter brightness-[0.75]"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#121824] via-[#121824]/50 to-transparent" />

          {/* Quick Info Overlay on Banner */}
          <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between">
            <div className="space-y-2 max-w-xl">
              <div className="flex flex-wrap items-center gap-2 text-xs font-bold">
                {movie.imdb && (
                  <span className="flex items-center gap-1 px-2.5 py-1 rounded bg-[#F5C518]/20 border border-[#F5C518]/50 text-[#F5C518]">
                    <Star className="w-3.5 h-3.5 fill-[#F5C518]" /> {movie.imdb} IMDb
                  </span>
                )}
                {movie.quality && (
                  <span className="px-2 py-0.5 rounded bg-white/15 border border-white/20 text-white uppercase text-[11px]">
                    {movie.quality}
                  </span>
                )}
                {movie.audio && (
                  <span className="px-2 py-0.5 rounded bg-[#E50914]/30 border border-[#E50914]/50 text-red-300">
                    {movie.audio}
                  </span>
                )}
                {movie.year && <span className="text-gray-300 font-medium">{movie.year}</span>}
              </div>

              <h2 className="text-2xl sm:text-4xl font-black text-white leading-tight">
                {movie.title}
              </h2>
              {movie.originalTitle && (
                <p className="text-sm text-gray-300 font-medium">{movie.originalTitle}</p>
              )}
            </div>

            {/* Play Button on Modal */}
            <button
              onClick={() => {
                onPlay(movie);
                onClose();
              }}
              className="hidden sm:flex px-6 py-3 rounded-xl bg-[#E50914] hover:bg-[#F40612] text-white font-extrabold text-sm items-center gap-2 shadow-neon-red cursor-pointer transition-all duration-300 hover:scale-105 active:scale-95 flex-shrink-0"
            >
              <Play className="w-5 h-5 fill-white" />
              <span>PHÁT PHIM</span>
            </button>
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          
          {/* Mobile Play Button */}
          <button
            onClick={() => {
              onPlay(movie);
              onClose();
            }}
            className="w-full sm:hidden py-3 rounded-xl bg-[#E50914] hover:bg-[#F40612] text-white font-extrabold text-sm flex items-center justify-center gap-2 shadow-neon-red cursor-pointer"
          >
            <Play className="w-5 h-5 fill-white" />
            <span>PHÁT PHIM NGAY</span>
          </button>

          {/* Synopsis */}
          <div>
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Tóm Tắt Nội Dung</h4>
            <p className="text-gray-200 text-sm sm:text-base leading-relaxed">
              {movie.overview || "Bộ phim mang đến những tình tiết hấp dẫn, kỹ xảo đỉnh cao và câu chuyện cuốn hút không thể bỏ lỡ dành cho khán giả yêu mến điện ảnh."}
            </p>
          </div>

          {/* Director & Cast Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm bg-[#161E2E]/60 p-4 rounded-xl border border-white/5">
            {movie.director && (
              <div>
                <span className="text-xs text-gray-400 block font-semibold">Đạo diễn:</span>
                <span className="text-white font-bold">{movie.director}</span>
              </div>
            )}
            {movie.cast && movie.cast.length > 0 && (
              <div>
                <span className="text-xs text-gray-400 block font-semibold">Diễn viên chính:</span>
                <span className="text-white">{movie.cast.join(', ')}</span>
              </div>
            )}
            {movie.category && (
              <div>
                <span className="text-xs text-gray-400 block font-semibold">Thể loại:</span>
                <span className="text-[#F5C518] font-medium">{movie.category}</span>
              </div>
            )}
            {movie.duration && (
              <div>
                <span className="text-xs text-gray-400 block font-semibold">Thời lượng:</span>
                <span className="text-gray-300">{movie.duration}</span>
              </div>
            )}
          </div>

          {/* Episodes List (Nếu là phim bộ hoặc có tập) */}
          {movie.episodes && movie.episodes.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Danh Sách Tập Phim</h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
                {movie.episodes.map((ep, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      onPlay({ ...movie, currentEpisode: ep.name, videoUrl: ep.url });
                      onClose();
                    }}
                    className="p-3 rounded-xl bg-[#161E2E] hover:bg-[#E50914] border border-white/10 hover:border-transparent text-left transition-all duration-200 cursor-pointer group"
                  >
                    <div className="text-xs text-gray-400 group-hover:text-white/80 font-medium">Tập {idx + 1}</div>
                    <div className="text-sm font-bold text-white truncate">{ep.name}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
