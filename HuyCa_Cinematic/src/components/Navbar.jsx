import React, { useState, useEffect } from 'react';
import { 
  Search, 
  X, 
  Bell, 
  Bookmark, 
  Menu, 
  Tv, 
  Film, 
  Sparkles, 
  Flame, 
  Compass, 
  SlidersHorizontal,
  ChevronDown,
  UserCheck
} from 'lucide-react';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  onSearch, 
  searchQuery, 
  setSearchQuery,
  searchResults = [],
  onSelectMovie
}) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 40) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { id: 'all', label: 'Trang Chủ', icon: Film },
    { id: 'movies', label: 'Phim Lẻ', icon: Film },
    { id: 'series', label: 'Phim Bộ', icon: Sparkles },
    { id: 'anime', label: 'Anime', icon: Flame },
    { id: 'short_drama', label: 'Tiểu Kịch', icon: Compass },
    { id: 'tv', label: 'Xem TV', icon: Tv },
  ];

  return (
    <header className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
      isScrolled ? 'bg-[#0B0F17]/90 backdrop-blur-md border-b border-white/10 shadow-glass' : 'bg-gradient-to-b from-[#0B0F17]/90 via-[#0B0F17]/50 to-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          
          {/* Logo Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('all')}>
            <div className="relative group">
              <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-gradient-to-br from-[#E50914] to-[#990000] p-0.5 shadow-neon-red flex items-center justify-center transition-transform duration-300 group-hover:scale-105">
                <img src="/logo.png" alt="Huy Cá Logo" className="w-full h-full object-cover rounded-[10px]" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-[#F5C518] rounded-full border-2 border-[#0B0F17]" title="VIP Master"></div>
            </div>
            
            <div className="flex flex-col">
              <span className="text-lg sm:text-xl font-black tracking-wider text-white flex items-center gap-1.5 font-sans">
                HUY CÁ <span className="text-[#E50914]">CINEMA</span>
              </span>
              <span className="text-[10px] sm:text-xs text-gray-400 font-medium tracking-widest hidden sm:block">
                PREMIUM STREAMING
              </span>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 lg:gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`px-3 py-2 rounded-lg text-sm font-semibold tracking-wide transition-all duration-200 flex items-center gap-2 cursor-pointer ${
                    isActive 
                      ? 'text-white bg-white/10 shadow-sm border border-white/10' 
                      : 'text-gray-300 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#E50914]' : 'text-gray-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Right Action Icons (Live Search, Notifications, Profile) */}
          <div className="flex items-center gap-2 sm:gap-4">
            
            {/* Live Search Input */}
            <div className="relative">
              <div className={`flex items-center bg-[#161E2E]/80 border transition-all duration-300 rounded-full ${
                isSearchOpen ? 'w-56 sm:w-72 border-[#E50914]/60 shadow-neon-red' : 'w-10 sm:w-64 border-white/10'
              }`}>
                <button 
                  onClick={() => setIsSearchOpen(!isSearchOpen)}
                  className="p-2 sm:pl-3 text-gray-400 hover:text-white cursor-pointer transition-colors"
                  aria-label="Tìm kiếm"
                >
                  <Search className="w-4 h-4 text-gray-300" />
                </button>
                <input
                  type="text"
                  placeholder="Tìm phim, diễn viên, kênh TV..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    if (onSearch) onSearch(e.target.value);
                  }}
                  className={`bg-transparent text-sm text-white placeholder-gray-400 focus:outline-none w-full pr-3 py-2 ${
                    isSearchOpen ? 'block' : 'hidden sm:block'
                  }`}
                />
                {searchQuery && (
                  <button 
                    onClick={() => {
                      setSearchQuery('');
                      if (onSearch) onSearch('');
                    }}
                    className="pr-3 text-gray-400 hover:text-white cursor-pointer"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Quick Search Results Dropdown */}
              {searchQuery.trim().length > 0 && searchResults.length > 0 && (
                <div className="absolute right-0 top-12 w-80 sm:w-96 bg-[#121824]/95 backdrop-blur-xl border border-white/15 rounded-2xl shadow-2xl overflow-hidden z-50 animate-in fade-in duration-200">
                  <div className="p-3 border-b border-white/10 flex items-center justify-between text-xs text-gray-400">
                    <span className="font-semibold text-white">Kết quả tìm kiếm ({searchResults.length})</span>
                    <span className="text-[#F5C518]">Trực tiếp</span>
                  </div>
                  <div className="max-h-80 overflow-y-auto divide-y divide-white/5">
                    {searchResults.map((movie) => (
                      <div
                        key={movie.id}
                        onClick={() => {
                          onSelectMovie(movie);
                          setSearchQuery('');
                        }}
                        className="p-3 flex items-center gap-3 hover:bg-white/10 transition-colors cursor-pointer group"
                      >
                        <img 
                          src={movie.poster} 
                          alt={movie.title} 
                          className="w-12 h-16 object-cover rounded-lg border border-white/10 flex-shrink-0 group-hover:scale-105 transition-transform" 
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-bold text-white truncate group-hover:text-[#E50914] transition-colors">{movie.title}</p>
                          <p className="text-xs text-gray-400 truncate">{movie.originalTitle || movie.category}</p>
                          <div className="flex items-center gap-2 mt-1 text-[11px]">
                            {movie.imdb && <span className="text-[#F5C518] font-bold">★ {movie.imdb}</span>}
                            <span className="px-1.5 py-0.2 rounded bg-white/10 text-gray-300 font-medium">{movie.quality || 'HD'}</span>
                            <span className="text-gray-400">{movie.year}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Notification Bell */}
            <button className="hidden sm:flex p-2 rounded-full text-gray-300 hover:text-white hover:bg-white/10 border border-transparent hover:border-white/10 transition-all cursor-pointer relative" aria-label="Thông báo">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-[#E50914] rounded-full"></span>
            </button>

            {/* VIP User Profile Avatar */}
            <div className="flex items-center gap-2 pl-2 border-l border-white/10 cursor-pointer group">
              <div className="relative">
                <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full ring-2 ring-[#F5C518] overflow-hidden bg-[#161E2E] flex items-center justify-center">
                  <UserCheck className="w-5 h-5 text-[#F5C518]" />
                </div>
                <div className="absolute -bottom-1 -right-1 bg-[#E50914] text-[8px] font-black text-white px-1 rounded-sm uppercase tracking-tighter">
                  VIP
                </div>
              </div>
            </div>

            {/* Mobile Hamburger Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 cursor-pointer"
              aria-label="Mở menu"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>

          </div>
        </div>
      </div>

      {/* Mobile Drawer Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-[#0B0F17]/95 backdrop-blur-xl border-b border-white/10 px-4 pt-2 pb-6 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  setIsMobileMenuOpen(false);
                }}
                className={`w-full px-4 py-3 rounded-xl text-left text-sm font-semibold flex items-center gap-3 cursor-pointer ${
                  isActive ? 'bg-[#E50914] text-white shadow-neon-red' : 'text-gray-300 hover:bg-white/10'
                }`}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
}
