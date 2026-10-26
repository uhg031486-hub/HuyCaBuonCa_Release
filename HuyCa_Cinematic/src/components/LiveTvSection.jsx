import React from 'react';
import { Tv, Play, Radio, Signal, Trophy } from 'lucide-react';
import { TV_CHANNELS } from '../data/mockMovies';

export default function LiveTvSection({ onPlayChannel }) {
  return (
    <section className="relative py-6 sm:py-8 bg-[#070A0F]/50 border-y border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#E50914]/20 border border-[#E50914]/40 flex items-center justify-center text-[#E50914]">
              <Trophy className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-lg sm:text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
                Kênh TV & Thể Thao Đỉnh Cao
              </h2>
              <p className="text-xs sm:text-sm text-gray-400 font-medium">
                Ngoại Hạng Anh, Cúp C1, Quần Vợt, Golf và Truyền hình 4K siêu nét
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E50914]/20 border border-[#E50914]/40 text-[#E50914] text-xs font-black animate-pulse">
            <Signal className="w-3.5 h-3.5" />
            <span>LIVE 50/60FPS</span>
          </div>
        </div>

        {/* Channels Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {TV_CHANNELS.map((channel) => (
            <div
              key={channel.id}
              onClick={() => onPlayChannel(channel)}
              className="p-4 rounded-2xl bg-[#161E2E]/80 hover:bg-[#1C273C] border border-white/10 hover:border-[#E50914]/60 transition-all duration-300 cursor-pointer group flex items-center gap-4 relative overflow-hidden hover:scale-[1.02] shadow-sm hover:shadow-neon-red/30"
            >
              {/* Channel Logo */}
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl bg-[#0B0F17] p-2 flex items-center justify-center border border-white/10 flex-shrink-0 group-hover:border-white/30 transition-colors">
                <img
                  src={channel.logo}
                  alt={channel.name}
                  className="w-full h-full object-contain filter group-hover:brightness-110 transition-all"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="w-full h-full hidden items-center justify-center text-white">
                  <Tv className="w-6 h-6 text-gray-400" />
                </div>
              </div>

              {/* Channel Meta */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-tight bg-[#E50914] text-white">
                    {channel.status}
                  </span>
                  <span className="text-[11px] text-gray-400 font-medium">
                    {channel.quality}
                  </span>
                </div>
                <h3 className="text-sm sm:text-base font-bold text-white truncate group-hover:text-[#E50914] transition-colors">
                  {channel.name}
                </h3>
                <p className="text-xs text-gray-400 truncate mt-0.5 font-medium">
                  {channel.currentShow}
                </p>
              </div>

              {/* Play Hover Icon */}
              <div className="w-10 h-10 rounded-full bg-[#E50914] text-white flex items-center justify-center shadow-neon-red opacity-0 group-hover:opacity-100 transition-all duration-300 transform scale-75 group-hover:scale-100 flex-shrink-0">
                <Play className="w-4 h-4 fill-white ml-0.5" />
              </div>

            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
