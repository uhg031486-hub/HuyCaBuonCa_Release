import React from 'react';
import { 
  Film, 
  Sparkles, 
  Flame, 
  Tv, 
  Compass, 
  SlidersHorizontal,
  Layers,
  Heart,
  Skull
} from 'lucide-react';

const CATEGORY_MAP = [
  { name: "Tất Cả", icon: Layers },
  { name: "Phim Chiếu Rạp", icon: Film },
  { name: "Phim Bộ Hot", icon: Sparkles },
  { name: "Hành Động", icon: Flame },
  { name: "Khoa Học Viễn Tưởng", icon: Compass },
  { name: "Kinh Dị & Giật Gân", icon: Skull },
  { name: "Anime Đỉnh Cao", icon: Flame },
  { name: "Tiểu Kịch ReelShort", icon: Film },
  { name: "Truyền Hình Thể Thao", icon: Tv },
];

export default function CategoryFilter({ selectedCategory, onSelectCategory }) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
      <div className="flex items-center gap-2 overflow-x-auto no-scrollbar py-2">
        {CATEGORY_MAP.map((cat) => {
          const Icon = cat.icon;
          const isSelected = selectedCategory === cat.name;
          return (
            <button
              key={cat.name}
              onClick={() => onSelectCategory(cat.name)}
              className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold tracking-wide whitespace-nowrap flex items-center gap-2 transition-all duration-300 cursor-pointer border ${
                isSelected
                  ? 'bg-gradient-to-r from-[#E50914] to-[#B30710] text-white border-transparent shadow-neon-red scale-105'
                  : 'bg-[#161E2E]/80 hover:bg-[#1E293B] text-gray-300 hover:text-white border-white/10'
              }`}
            >
              <Icon className={`w-4 h-4 ${isSelected ? 'text-white' : 'text-gray-400'}`} />
              <span>{cat.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
