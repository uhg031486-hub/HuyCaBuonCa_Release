import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  RotateCw, 
  Volume2, 
  VolumeX, 
  Maximize2, 
  Minimize2, 
  PictureInPicture2, 
  Settings, 
  Sliders, 
  Check, 
  ChevronDown, 
  ArrowLeft, 
  Bookmark, 
  ThumbsUp, 
  Share2, 
  Flag, 
  Star, 
  Film, 
  Tv, 
  Sparkles, 
  Clock, 
  Calendar, 
  Globe, 
  Eye, 
  Search, 
  ListVideo, 
  ExternalLink, 
  Layers, 
  Radio,
  Monitor
} from 'lucide-react';
import Hls from 'hls.js';
import { resolveMovieDetailAndStream } from '../services/movieApi';

export default function WatchMoviePage({ 
  movie, 
  onBack, 
  onSwitchMovie,
  relatedMovies = [],
  onOpenMiniPiP
}) {
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const controlsTimeoutRef = useRef(null);
  const hasAttemptedAutoRecovery = useRef(false);

  // Playback States
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [progress, setProgress] = useState(0);
  const [buffered, setBuffered] = useState(0);
  const [showControls, setShowControls] = useState(true);
  const [isTheaterMode, setIsTheaterMode] = useState(false);
  const [useIframeEmbed, setUseIframeEmbed] = useState(false);
  const [playbackError, setPlaybackError] = useState(null);
  const [activeSubText, setActiveSubText] = useState('');

  // Dropdown Menus in Player
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);
  const [showAudioSubMenu, setShowAudioSubMenu] = useState(false);
  const [selectedResolution, setSelectedResolution] = useState('1080p FHD');
  const [selectedAudioSub, setSelectedAudioSub] = useState('Vietsub Chuẩn');

  // Interactive User States
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [likeCount, setLikeCount] = useState(1420);
  const [isLiked, setIsLiked] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [episodeSearch, setEpisodeSearch] = useState('');
  const [isSynopsisExpanded, setIsSynopsisExpanded] = useState(false);
  const [activeServerTab, setActiveServerTab] = useState(0);

  // Episodes List
  const episodes = movie?.episodes || [];
  const currentEpName = movie?.currentEpisode || (episodes[0]?.name) || 'Tập 1';
  const currentEmbedUrl = movie?.embedUrl || episodes.find(e => e.name === currentEpName)?.embedUrl || '';

  // Nhóm các tập theo Server nếu có
  const groupedServers = useMemo(() => {
    if (!episodes.length) return [];
    const map = new Map();
    episodes.forEach(ep => {
      const srvName = ep.serverName || 'Server VIP #1';
      if (!map.has(srvName)) map.set(srvName, []);
      map.get(srvName).push(ep);
    });
    return Array.from(map.entries()).map(([name, list]) => ({ name, list }));
  }, [episodes]);

  const currentServerList = groupedServers[activeServerTab]?.list || episodes;

  // Lọc tập theo ô tìm kiếm
  const filteredEpisodes = useMemo(() => {
    if (!episodeSearch.trim()) return currentServerList;
    const q = episodeSearch.toLowerCase().trim();
    return currentServerList.filter(e => e.name.toLowerCase().includes(q));
  }, [currentServerList, episodeSearch]);

  // Toast Helper
  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3000);
  };

  // Đồng bộ Bookmark trong LocalStorage
  useEffect(() => {
    if (!movie?.id) return;
    try {
      const favs = JSON.parse(localStorage.getItem('huyca_cinematic_favs') || '[]');
      setIsBookmarked(favs.some(f => f.id === movie.id));
    } catch(e) {}
  }, [movie?.id]);

  const toggleBookmark = () => {
    if (!movie?.id) return;
    try {
      let favs = JSON.parse(localStorage.getItem('huyca_cinematic_favs') || '[]');
      if (isBookmarked) {
        favs = favs.filter(f => f.id !== movie.id);
        setIsBookmarked(false);
        showToast('Đã xóa khỏi danh sách yêu thích');
      } else {
        favs.push(movie);
        setIsBookmarked(true);
        showToast('⭐ Đã thêm vào danh sách yêu thích!');
      }
      localStorage.setItem('huyca_cinematic_favs', JSON.stringify(favs));
    } catch(e) {}
  };

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      showToast('🔗 Đã sao chép liên kết phim vào clipboard!');
    } else {
      showToast('Đã mở liên kết phim!');
    }
  };

  const handleLike = () => {
    setIsLiked(!isLiked);
    setLikeCount(prev => isLiked ? prev - 1 : prev + 1);
  };

  // Tự động cuộn lên đầu khi nạp trang xem phim
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [movie?.id, movie?.currentEpisode]);

  // =========================================================================
  // VIDEO PLAYER ENGINE (HLS.JS + AUTO CLOUDFLARE PROXY FALLBACK)
  // =========================================================================
  useEffect(() => {
    if (!movie || !videoRef.current || useIframeEmbed) return;

    const video = videoRef.current;
    let url = movie.videoUrl || movie.streamUrl;
    const subUrl = movie.subtitleUrl || null;

    setActiveSubText('');
    setPlaybackError(null);
    video.querySelectorAll('track').forEach(t => t.remove());

    // Nạp phụ đề tiếng Việt
    if (subUrl) {
      video.crossOrigin = 'anonymous';
      const track = document.createElement('track');
      track.kind = 'subtitles';
      track.label = 'Tiếng Việt';
      track.srclang = 'vi';
      track.src = subUrl;
      track.default = true;
      video.appendChild(track);

      const bindTrack = () => {
        if (track.track) {
          track.track.mode = 'hidden';
          track.track.oncuechange = () => {
            const cues = track.track.activeCues;
            if (cues && cues.length > 0) {
              const lines = [];
              for (let i = 0; i < cues.length; i++) {
                const txt = (cues[i].text || '').replace(/<[^>]+>/g, '').trim();
                if (txt) lines.push(txt);
              }
              setActiveSubText(lines.join('\n'));
            } else {
              setActiveSubText('');
            }
          };
        }
      };
      bindTrack();
      track.addEventListener('load', bindTrack);
      setTimeout(bindTrack, 150);
    } else {
      video.removeAttribute('crossorigin');
    }

    if (!url) {
      if (currentEmbedUrl) setUseIframeEmbed(true);
      return;
    }

    let hlsInstance = null;
    let isProxied = url.includes('/api/proxy');

    const triggerAutoRecovery = async () => {
      if (hasAttemptedAutoRecovery.current) return;
      hasAttemptedAutoRecovery.current = true;

      // NẾU LÀ TRUYỀN HÌNH HOẶC THỂ THAO TRỰC TIẾP: TUYỆT ĐỐI KHÔNG FALLBACK SANG PHIM NGẮN!
      if (movie.isLiveTv) {
        console.log('Live sports/TV error, attempting sports live fallbacks...');
        const sportsFallbacks = [
          'https://amg00378-amg00378c4-freelivesports-emea-5637.playouts.now.amagi.tv/playlist.m3u8',
          'https://vtvgolivepre-vtv02.vtvdigital.vn/hls/vtv/live/vtv5__vtv1080p-h264/index.m3u8',
          'https://bein-xtra-bein.amagi.tv/playlist.m3u8',
          'https://vtvgolivepre-vtv02.vtvdigital.vn/hls/vtv/live/vtv1__vtv1080p-h264/index.m3u8'
        ];
        const nextUrl = sportsFallbacks.find(u => u !== url) || sportsFallbacks[0];
        if (nextUrl) {
          onSwitchMovie({
            ...movie,
            videoUrl: nextUrl,
            streamUrl: nextUrl,
            isLiveTv: true,
            episodes: []
          });
          return true;
        }
        return false;
      }

      console.log('Activating Auto-Recovery: resolving live stream for movie...', movie.title);
      try {
        const recovered = await resolveMovieDetailAndStream({
          ...movie,
          videoUrl: '', // Reset dead url
          episodes: []
        });
        if (recovered && recovered.videoUrl && !recovered.videoUrl.includes('commondatastorage.googleapis.com')) {
          console.log('Auto-Recovery success! Switching to live stream:', recovered.videoUrl);
          onSwitchMovie(recovered);
          return true;
        }
      } catch (e) {
        console.warn('Auto-Recovery failed:', e);
      }
      return false;
    };

    // Kiểm tra ngay nếu URL là link sample chết của googleapis -> Phục hồi tức thì
    if (url.includes('commondatastorage.googleapis.com')) {
      triggerAutoRecovery();
      return;
    }

    const handleVideoError = async () => {
      console.warn('Native video error, checking fallback...');
      const recovered = await triggerAutoRecovery();
      if (recovered) return;

      if (!isProxied && url && url.startsWith('http')) {
        console.log('Retrying native video via proxy fallback:', url);
        isProxied = true;
        video.src = `/api/proxy?url=${encodeURIComponent(url)}`;
        video.load();
        video.play().catch(() => {});
      } else if (currentEmbedUrl) {
        setUseIframeEmbed(true);
      } else {
        setPlaybackError('Không thể tải luồng phát video này. Bạn có thể bấm "Tự Động Kết Nối Luồng VIP" bên dưới hoặc chọn tập khác!');
      }
    };

    video.addEventListener('error', handleVideoError);

    if (url.includes('.m3u8')) {
      if (Hls.isSupported()) {
        hlsInstance = new Hls({
          enableWorker: true,
          maxBufferLength: 30,
          maxMaxBufferLength: 60,
          lowLatencyMode: false
        });

        hlsInstance.loadSource(url);
        hlsInstance.attachMedia(video);

        hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
          setPlaybackError(null);
          video.play().then(() => setIsPlaying(true)).catch(() => {});
        });

        hlsInstance.on(Hls.Events.ERROR, (event, data) => {
          console.warn('HLS Event Error:', data.type, data.details, data.fatal);
          if (data.fatal) {
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                if (!isProxied && url && url.startsWith('http')) {
                  console.log('Retrying HLS stream via Cloudflare /api/proxy...');
                  isProxied = true;
                  const proxyUrl = `/api/proxy?url=${encodeURIComponent(url)}`;
                  hlsInstance.loadSource(proxyUrl);
                  hlsInstance.startLoad();
                  return;
                }
                if (currentEmbedUrl) {
                  setUseIframeEmbed(true);
                  return;
                }
                hlsInstance.startLoad();
                break;
              case Hls.ErrorTypes.MEDIA_ERROR:
                hlsInstance.recoverMediaError();
                break;
              default:
                if (currentEmbedUrl) {
                  setUseIframeEmbed(true);
                } else {
                  hlsInstance.destroy();
                  setPlaybackError('Máy chủ phim đang bận. Vui lòng bấm "Thử Lại" hoặc chọn tập khác!');
                }
                break;
            }
          }
        });

      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = url;
        video.play().then(() => setIsPlaying(true)).catch(() => {});
      }
    } else {
      video.src = url;
      video.play().then(() => setIsPlaying(true)).catch(() => {});
    }

    return () => {
      video.removeEventListener('error', handleVideoError);
      if (hlsInstance) hlsInstance.destroy();
    };
  }, [movie?.videoUrl, movie?.streamUrl, movie?.currentEpisode, useIframeEmbed]);

  // Video Event Handlers
  const togglePlay = () => {
    if (!videoRef.current) return;
    if (videoRef.current.paused) {
      videoRef.current.play();
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  const handleSkip = (seconds) => {
    if (!videoRef.current) return;
    videoRef.current.currentTime = Math.max(0, Math.min(videoRef.current.duration || 0, videoRef.current.currentTime + seconds));
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !videoRef.current.muted;
    setIsMuted(videoRef.current.muted);
  };

  const handleVolumeChange = (e) => {
    const val = parseFloat(e.target.value);
    setVolume(val);
    if (videoRef.current) {
      videoRef.current.volume = val;
      videoRef.current.muted = val === 0;
      setIsMuted(val === 0);
    }
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    const cur = videoRef.current.currentTime;
    const dur = videoRef.current.duration || 0;
    setCurrentTime(cur);
    setDuration(dur);
    setProgress(dur ? (cur / dur) * 100 : 0);

    if (videoRef.current.buffered.length > 0) {
      const end = videoRef.current.buffered.end(videoRef.current.buffered.length - 1);
      setBuffered(dur ? (end / dur) * 100 : 0);
    }
  };

  const handleSeek = (e) => {
    if (!videoRef.current || !duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    videoRef.current.currentTime = pos * duration;
  };

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    } else {
      containerRef.current.requestFullscreen().catch(() => {});
    }
  };

  const handleMouseMove = () => {
    setShowControls(true);
    if (controlsTimeoutRef.current) clearTimeout(controlsTimeoutRef.current);
    controlsTimeoutRef.current = setTimeout(() => {
      if (isPlaying && !showSettingsMenu && !showAudioSubMenu) {
        setShowControls(false);
      }
    }, 3500);
  };

  const formatTime = (timeInSeconds) => {
    if (isNaN(timeInSeconds)) return "00:00";
    const h = Math.floor(timeInSeconds / 3600);
    const m = Math.floor((timeInSeconds % 3600) / 60);
    const s = Math.floor(timeInSeconds % 60);
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-[#070A0F] text-gray-100 flex flex-col font-sans pb-24 selection:bg-[#E50914] selection:text-white">
      
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-6 z-50 px-4 py-2.5 rounded-xl bg-[#161E2E]/95 border border-[#F5C518]/60 text-white text-xs sm:text-sm font-bold shadow-2xl backdrop-blur-md animate-in slide-in-from-top-4 duration-300">
          {toastMessage}
        </div>
      )}

      {/* Top Breadcrumb & Return Bar */}
      <div className="sticky top-0 z-40 bg-[#0B0F17]/90 backdrop-blur-xl border-b border-white/10 px-4 sm:px-8 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/15 border border-white/10 text-xs sm:text-sm font-bold text-gray-200 hover:text-white transition-all cursor-pointer group"
          >
            <ArrowLeft className="w-4 h-4 text-[#F5C518] group-hover:-translate-x-0.5 transition-transform" />
            <span>Quay lại kho phim</span>
          </button>

          {/* Breadcrumb path */}
          <div className="hidden md:flex items-center gap-2 text-xs text-gray-400">
            <span>/</span>
            <span className="text-gray-300 font-medium">{movie.category || 'Phim Điện Ảnh'}</span>
            <span>/</span>
            <span className="text-[#F5C518] font-bold truncate max-w-xs">{movie.title}</span>
            {currentEpName && (
              <>
                <span>/</span>
                <span className="text-white font-extrabold">{currentEpName}</span>
              </>
            )}
          </div>
        </div>

        {/* Server Quality Pill */}
        <div className="flex items-center gap-2 text-xs">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#161E2E] border border-white/10 text-emerald-400 font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="hidden sm:inline">Server VIP Siêu Tốc</span>
            <span className="text-white font-bold">{selectedResolution}</span>
          </div>
          {currentEmbedUrl && (
            <button
              onClick={() => setUseIframeEmbed(!useIframeEmbed)}
              className="px-2.5 py-1 rounded-full bg-white/10 hover:bg-[#E50914] text-gray-200 hover:text-white text-xs font-bold transition-all cursor-pointer flex items-center gap-1"
              title="Đổi giữa HLS tốc độ cao và Server Embed"
            >
              <ExternalLink className="w-3 h-3 text-[#F5C518]" />
              <span className="hidden sm:inline">{useIframeEmbed ? 'Đổi HLS' : 'Đổi Embed'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Watch View Area */}
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 pt-4 sm:pt-6 w-full space-y-6">

        {/* =====================================================================
            1. VIDEO PLAYER CONTAINER WITH AMBIENT LIGHT GLOW
           ===================================================================== */}
        <div className={`relative mx-auto transition-all duration-500 ${isTheaterMode ? 'w-full max-w-full' : 'w-full max-w-5xl'}`}>
          
          {/* AMBIENT LIGHT GLOW (Đổ bóng màu phát sáng điện ảnh theo poster phim) */}
          <div className="absolute -inset-2 sm:-inset-5 rounded-3xl overflow-hidden pointer-events-none -z-10 transition-opacity duration-700 opacity-60">
            <img
              src={movie.backdrop || movie.poster}
              alt=""
              className="w-full h-full object-cover filter blur-3xl scale-110 opacity-70"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#070A0F] via-transparent to-transparent opacity-90" />
          </div>

          {/* Player Box (16:9 Frame) */}
          <div
            ref={containerRef}
            onMouseMove={handleMouseMove}
            className="relative aspect-video rounded-2xl overflow-hidden bg-black border border-white/15 shadow-[0_20px_60px_rgba(0,0,0,0.9)] group select-none"
          >
            {/* Real Video or Embed Iframe */}
            {useIframeEmbed && currentEmbedUrl ? (
              <iframe
                src={currentEmbedUrl}
                className="w-full h-full border-0 bg-black"
                allowFullScreen
                allow="autoplay; encrypted-media; picture-in-picture"
                title={movie.title}
              />
            ) : (
              <video
                ref={videoRef}
                className="w-full h-full object-contain cursor-pointer"
                onClick={togglePlay}
                onTimeUpdate={handleTimeUpdate}
                playsInline
                autoPlay
              />
            )}

            {/* Subtitle Overlay */}
            {activeSubText && (
              <div className="absolute bottom-20 left-1/2 -translate-x-1/2 z-30 max-w-[85%] px-4 py-1.5 rounded-lg bg-black/80 text-white font-semibold text-sm sm:text-base text-center pointer-events-none whitespace-pre-line shadow-2xl border border-white/10">
                {activeSubText}
              </div>
            )}

            {/* Playback Error Dialog */}
            {playbackError && (
              <div className="absolute inset-0 z-40 bg-black/90 flex flex-col items-center justify-center p-6 text-center space-y-4">
                <div className="w-14 h-14 rounded-full bg-red-500/20 border border-red-500/50 flex items-center justify-center text-2xl">
                  ⚠️
                </div>
                <h4 className="text-lg font-bold text-white">Chưa thể phát luồng HLS trực tiếp</h4>
                <p className="text-sm text-gray-300 max-w-md">{playbackError}</p>
                <div className="flex flex-wrap items-center justify-center gap-3">
                  {/* Nút Tự Động Kết Nối Luồng VIP Cứu Nguy */}
                  <button
                    onClick={async () => {
                      setPlaybackError(null);
                      showToast('⚡ Đang tự động kết nối luồng phim VIP tốc độ cao...');
                      const rec = await resolveMovieDetailAndStream({
                        ...movie,
                        videoUrl: '',
                        episodes: []
                      });
                      if (rec && rec.videoUrl) onSwitchMovie(rec);
                    }}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#F5C518] to-amber-500 text-black font-extrabold text-sm shadow-[0_0_20px_rgba(245,197,24,0.6)] cursor-pointer hover:scale-105 transition-all flex items-center gap-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    Tự Động Kết Nối Luồng VIP
                  </button>

                  {currentEmbedUrl && (
                    <button
                      onClick={() => {
                        setPlaybackError(null);
                        setUseIframeEmbed(true);
                      }}
                      className="px-5 py-2.5 rounded-xl bg-[#E50914] text-white font-extrabold text-sm shadow-neon-red cursor-pointer hover:scale-105 transition-all flex items-center gap-2"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Chuyển Sang Server Embed Dự Phòng
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setPlaybackError(null);
                      if (videoRef.current) {
                        videoRef.current.src = `/api/proxy?url=${encodeURIComponent(movie.videoUrl || '')}`;
                        videoRef.current.load();
                        videoRef.current.play().catch(() => {});
                      }
                    }}
                    className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-sm cursor-pointer flex items-center gap-2"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Thử Lại Qua Proxy
                  </button>
                </div>
              </div>
            )}

            {/* Custom Cinema Video Controls Bar */}
            {!useIframeEmbed && (
              <div className={`absolute bottom-0 inset-x-0 p-3 sm:p-5 bg-gradient-to-t from-black/65 via-black/25 to-transparent backdrop-blur-[2px] transition-opacity duration-300 space-y-2 z-20 ${
                showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
              }`}>
                
                {/* Progress Bar with Buffer indicator */}
                <div 
                  onClick={handleSeek}
                  className="relative w-full h-1.5 hover:h-2.5 bg-white/20 rounded-full cursor-pointer transition-all group/seek"
                >
                  {/* Buffer Bar */}
                  <div 
                    className="absolute top-0 left-0 bottom-0 bg-white/30 rounded-full transition-all"
                    style={{ width: `${buffered}%` }}
                  />
                  {/* Played Bar */}
                  <div 
                    className="absolute top-0 left-0 bottom-0 bg-[#E50914] rounded-full shadow-[0_0_12px_rgba(229,9,20,0.8)]"
                    style={{ width: `${progress}%` }}
                  />
                  {/* Thumb Scrubber */}
                  <div 
                    className="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-white rounded-full shadow-lg opacity-0 group-hover/seek:opacity-100 transition-opacity"
                    style={{ left: `calc(${progress}% - 7px)` }}
                  />
                </div>

                {/* Controls Row */}
                <div className="flex items-center justify-between text-white text-xs sm:text-sm">
                  
                  {/* Left Controls: Play, Skip 10s, Volume, Time */}
                  <div className="flex items-center gap-2 sm:gap-4">
                    <button 
                      onClick={togglePlay}
                      className="p-2 sm:p-2.5 rounded-full bg-[#E50914] hover:bg-[#F40612] text-white shadow-neon-red cursor-pointer transition-transform hover:scale-110 active:scale-95"
                      title={isPlaying ? "Tạm dừng" : "Phát"}
                    >
                      {isPlaying ? <Pause className="w-4 h-4 sm:w-5 sm:h-5 fill-white" /> : <Play className="w-4 h-4 sm:w-5 sm:h-5 fill-white ml-0.5" />}
                    </button>

                    {/* Skip -10s */}
                    <button 
                      onClick={() => handleSkip(-10)}
                      className="p-1.5 sm:p-2 rounded-lg hover:bg-white/10 text-gray-200 hover:text-white transition-colors cursor-pointer"
                      title="Lùi 10 giây"
                    >
                      <RotateCcw className="w-4 h-4 sm:w-5 sm:h-5" />
                    </button>

                    {/* Skip +10s */}
                    <button 
                      onClick={() => handleSkip(10)}
                      className="p-1.5 sm:p-2 rounded-lg hover:bg-white/10 text-gray-200 hover:text-white transition-colors cursor-pointer"
                      title="Tiến 10 giây"
                    >
                      <RotateCw className="w-4 h-4 sm:w-5 sm:h-5" />
                    </button>

                    {/* Volume Hover Control */}
                    <div className="flex items-center gap-1.5 group/vol">
                      <button 
                        onClick={toggleMute}
                        className="p-1.5 rounded-lg hover:bg-white/10 text-gray-200 hover:text-white cursor-pointer"
                        title={isMuted ? "Bật tiếng" : "Tắt tiếng"}
                      >
                        {isMuted ? <VolumeX className="w-4 h-4 sm:w-5 sm:h-5 text-red-400" /> : <Volume2 className="w-4 h-4 sm:w-5 sm:h-5" />}
                      </button>
                      <input 
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value={isMuted ? 0 : volume}
                        onChange={handleVolumeChange}
                        className="w-0 group-hover/vol:w-16 sm:group-hover/vol:w-20 accent-[#E50914] transition-all duration-200 cursor-pointer h-1.5 rounded-full"
                      />
                    </div>

                    {/* Time Counter */}
                    <span className="text-[11px] sm:text-xs font-mono font-semibold text-gray-300">
                      {formatTime(currentTime)} / {formatTime(duration)}
                    </span>
                  </div>

                  {/* Right Controls: Resolution, Subtitle, PiP, Theater, Fullscreen */}
                  <div className="flex items-center gap-1.5 sm:gap-3">
                    
                    {/* Resolution Selector Dropdown */}
                    <div className="relative">
                      <button 
                        onClick={() => {
                          setShowSettingsMenu(!showSettingsMenu);
                          setShowAudioSubMenu(false);
                        }}
                        className="px-2 sm:px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-white font-extrabold text-[11px] sm:text-xs flex items-center gap-1 cursor-pointer transition-colors"
                        title="Chọn độ phân giải"
                      >
                        <Settings className="w-3.5 h-3.5 text-[#F5C518]" />
                        <span>{selectedResolution}</span>
                      </button>

                      {showSettingsMenu && (
                        <div className="absolute bottom-9 right-0 w-44 bg-[#0B0F17]/95 border border-white/15 rounded-xl p-1.5 shadow-2xl backdrop-blur-xl z-30 space-y-1">
                          <div className="text-[10px] uppercase font-bold text-gray-400 px-2 py-1">Độ Phân Giải</div>
                          {['4K Ultra HD', '1080p FHD', '720p HD', 'Tự Động (Auto)'].map(res => (
                            <button
                              key={res}
                              onClick={() => {
                                setSelectedResolution(res);
                                setShowSettingsMenu(false);
                                showToast(`Đã chuyển sang chế độ ${res}`);
                              }}
                              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-between cursor-pointer ${
                                selectedResolution === res ? 'bg-[#E50914] text-white' : 'text-gray-300 hover:bg-white/10'
                              }`}
                            >
                              <span>{res}</span>
                              {selectedResolution === res && <Check className="w-3.5 h-3.5" />}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Audio & Subtitle Selector Dropdown */}
                    <div className="relative">
                      <button 
                        onClick={() => {
                          setShowAudioSubMenu(!showAudioSubMenu);
                          setShowSettingsMenu(false);
                        }}
                        className="px-2 sm:px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-white font-extrabold text-[11px] sm:text-xs flex items-center gap-1 cursor-pointer transition-colors"
                        title="Chọn phụ đề / thuyết minh"
                      >
                        <Sliders className="w-3.5 h-3.5 text-[#E50914]" />
                        <span className="hidden sm:inline">{selectedAudioSub}</span>
                      </button>

                      {showAudioSubMenu && (
                        <div className="absolute bottom-9 right-0 w-48 bg-[#0B0F17]/95 border border-white/15 rounded-xl p-1.5 shadow-2xl backdrop-blur-xl z-30 space-y-1">
                          <div className="text-[10px] uppercase font-bold text-gray-400 px-2 py-1">Âm Thanh & Phụ Đề</div>
                          {['Vietsub Chuẩn', 'Thuyết Minh VIP', 'Lồng Tiếng Việt', 'Tắt Phụ Đề'].map(sub => (
                            <button
                              key={sub}
                              onClick={() => {
                                setSelectedAudioSub(sub);
                                setShowAudioSubMenu(false);
                                showToast(`Đã áp dụng ${sub}`);
                              }}
                              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-between cursor-pointer ${
                                selectedAudioSub === sub ? 'bg-[#E50914] text-white' : 'text-gray-300 hover:bg-white/10'
                              }`}
                            >
                              <span>{sub}</span>
                              {selectedAudioSub === sub && <Check className="w-3.5 h-3.5" />}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Theater Mode Toggle */}
                    <button 
                      onClick={() => setIsTheaterMode(!isTheaterMode)}
                      className="p-1.5 sm:p-2 rounded-lg hover:bg-white/10 text-gray-300 hover:text-white cursor-pointer hidden md:flex"
                      title={isTheaterMode ? "Thu nhỏ khung xem" : "Mở rộng khung rạp chiếu (Theater mode)"}
                    >
                      <Monitor className="w-4 h-4" />
                    </button>

                    {/* Fullscreen Button */}
                    <button 
                      onClick={toggleFullscreen}
                      className="p-1.5 sm:p-2 rounded-lg hover:bg-white/10 text-gray-300 hover:text-white cursor-pointer"
                      title="Toàn màn hình"
                    >
                      <Maximize2 className="w-4 h-4 sm:w-5 sm:h-5" />
                    </button>

                  </div>
                </div>

              </div>
            )}
          </div>
        </div>

        {/* =====================================================================
            2. MOVIE DETAILS & INTERACTION TOOLBAR
           ===================================================================== */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
          
          {/* Main Info Column (Left 2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Title & Metadata Header */}
            <div className="space-y-3">
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
                {movie.duration && <span className="text-gray-400 font-medium">• {movie.duration}</span>}
              </div>

              <h1 className="text-2xl sm:text-4xl font-black text-white leading-tight">
                {movie.title}
              </h1>
              {movie.originalTitle && (
                <p className="text-sm sm:text-base text-gray-400 font-semibold">{movie.originalTitle}</p>
              )}
            </div>

            {/* Quick Action Toolbar */}
            <div className="flex flex-wrap items-center gap-3 py-2 border-y border-white/10">
              <button 
                onClick={toggleBookmark}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold border transition-all cursor-pointer ${
                  isBookmarked ? 'bg-[#F5C518] text-black border-[#F5C518]' : 'bg-white/5 hover:bg-white/10 text-white border-white/10'
                }`}
              >
                <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-black' : ''}`} />
                <span>{isBookmarked ? 'Đã Lưu Vào DS' : 'Lưu Xem Sau'}</span>
              </button>

              <button 
                onClick={handleLike}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold border transition-all cursor-pointer ${
                  isLiked ? 'bg-[#E50914] text-white border-[#E50914]' : 'bg-white/5 hover:bg-white/10 text-white border-white/10'
                }`}
              >
                <ThumbsUp className={`w-4 h-4 ${isLiked ? 'fill-white' : ''}`} />
                <span>{likeCount}</span>
              </button>

              <button 
                onClick={handleShare}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white border border-white/10 text-xs sm:text-sm font-bold transition-all cursor-pointer"
              >
                <Share2 className="w-4 h-4 text-cyan-400" />
                <span>Chia Sẻ</span>
              </button>

              <button 
                onClick={() => showToast('Đã gửi phản hồi đến kỹ thuật viên!')}
                className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-white/5 text-gray-400 hover:text-red-400 text-xs font-bold transition-colors cursor-pointer ml-auto"
                title="Báo cáo link hỏng / lỗi phụ đề"
              >
                <Flag className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Báo Lỗi</span>
              </button>
            </div>

            {/* =====================================================================
                3. DANH SÁCH TẬP PHIM HOẶC KÊNH TRUYỀN HÌNH TRỰC TIẾP
               ===================================================================== */}
            {movie.isLiveTv ? (
              <div className="space-y-4 bg-[#121824]/80 p-5 rounded-2xl border border-white/10 shadow-xl">
                <div className="flex items-center justify-between border-b border-white/10 pb-3">
                  <div className="flex items-center gap-2">
                    <Radio className="w-5 h-5 text-emerald-400 animate-pulse" />
                    <h3 className="text-base sm:text-lg font-black text-white">
                      🔴 Truyền Hình & Thể Thao Trực Tiếp
                    </h3>
                  </div>
                  <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/40">
                    LIVE HD 50/60FPS
                  </span>
                </div>
                <div className="text-xs text-gray-300 font-medium">
                  Đang phát sóng trực tiếp từ vệ tinh. Bấm vào kênh dưới đây để chuyển kênh tức thì:
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 pt-1">
                  {[
                    { id: 'tp1', name: 'True Premier Football 1 HD', url: 'https://amg00378-amg00378c4-freelivesports-emea-5637.playouts.now.amagi.tv/playlist.m3u8' },
                    { id: 'vtv5', name: 'VTV5 HD Thể Thao & Bóng Đá', url: 'https://vtvgolivepre-vtv02.vtvdigital.vn/hls/vtv/live/vtv5__vtv1080p-h264/index.m3u8' },
                    { id: 'bein1', name: 'beIN SPORTS 1 HD', url: 'https://bein-xtra-bein.amagi.tv/playlist.m3u8' },
                    { id: 'vtv1', name: 'VTV1 HD Thời Sự', url: 'https://vtvgolivepre-vtv02.vtvdigital.vn/hls/vtv/live/vtv1__vtv1080p-h264/index.m3u8' },
                    { id: 'vtv3', name: 'VTV3 HD Giải Trí', url: 'https://vtvgolivepre-vtv02.vtvdigital.vn/hls/vtv/live/vtv3__vtv1080p-h264/index.m3u8' }
                  ].map((ch, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        onSwitchMovie({
                          id: ch.id,
                          title: ch.name,
                          category: 'Thể Thao Trực Tiếp',
                          videoUrl: ch.url,
                          streamUrl: ch.url,
                          isLiveTv: true,
                          episodes: []
                        });
                      }}
                      className={`p-3 rounded-xl text-xs font-bold text-left transition-all border cursor-pointer ${
                        movie.videoUrl === ch.url || movie.title === ch.name
                          ? 'bg-[#E50914] text-white border-transparent shadow-neon-red'
                          : 'bg-[#161E2E] text-gray-300 hover:text-white hover:bg-white/10 border-white/10'
                      }`}
                    >
                      <div className="truncate">{ch.name}</div>
                    </button>
                  ))}
                </div>
              </div>
            ) : episodes.length > 0 && (
              <div className="space-y-4 bg-[#121824]/80 p-5 rounded-2xl border border-white/10 shadow-xl">
                
                {/* Header & Search */}
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-3">
                  <div className="flex items-center gap-2">
                    <ListVideo className="w-5 h-5 text-[#F5C518]" />
                    <h3 className="text-base sm:text-lg font-black text-white">
                      Danh Sách Tập ({episodes.length} Tập)
                    </h3>
                  </div>

                  {episodes.length > 20 && (
                    <div className="relative w-44 sm:w-56">
                      <Search className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                      <input 
                        type="text"
                        placeholder="Tìm số tập..."
                        value={episodeSearch}
                        onChange={(e) => setEpisodeSearch(e.target.value)}
                        className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-black/40 border border-white/10 text-xs text-white placeholder-gray-400 focus:outline-none focus:border-[#E50914]"
                      />
                    </div>
                  )}
                </div>

                {/* Server Tabs if multiple servers */}
                {groupedServers.length > 1 && (
                  <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
                    {groupedServers.map((srv, idx) => (
                      <button
                        key={idx}
                        onClick={() => setActiveServerTab(idx)}
                        className={`px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap cursor-pointer transition-all ${
                          activeServerTab === idx 
                            ? 'bg-[#E50914] text-white shadow-neon-red' 
                            : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10'
                        }`}
                      >
                        {srv.name} ({srv.list.length})
                      </button>
                    ))}
                  </div>
                )}

                {/* Episodes Grid with Active Glowing State */}
                <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-2 max-h-80 overflow-y-auto pr-1">
                  {filteredEpisodes.map((ep, idx) => {
                    const isActive = ep.name === currentEpName || ep.url === movie.videoUrl;
                    return (
                      <button
                        key={idx}
                        onClick={() => {
                          onSwitchMovie({
                            ...movie,
                            currentEpisode: ep.name,
                            videoUrl: ep.url,
                            embedUrl: ep.embedUrl || '',
                            subtitleUrl: ep.subtitleUrl
                          });
                        }}
                        className={`py-2 px-2 rounded-xl text-xs font-extrabold text-center transition-all duration-200 cursor-pointer relative group ${
                          isActive 
                            ? 'bg-gradient-to-r from-[#F5C518] to-[#eab308] text-black shadow-[0_0_18px_rgba(245,197,24,0.65)] scale-105 border-2 border-[#F5C518] z-10' 
                            : 'bg-[#161E2E] hover:bg-[#E50914] text-gray-300 hover:text-white border border-white/10 hover:border-transparent hover:scale-105'
                        }`}
                      >
                        <div className="truncate">{ep.name}</div>
                        {isActive && (
                          <div className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-[#E50914] rounded-full border border-black animate-ping" />
                        )}
                      </button>
                    );
                  })}
                </div>

              </div>
            )}

            {/* Synopsis / Tóm tắt nội dung */}
            <div className="space-y-2 bg-[#121824]/60 p-5 rounded-2xl border border-white/5">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Tóm Tắt Cốt Truyện</h4>
              <p className={`text-gray-300 text-sm sm:text-base leading-relaxed ${!isSynopsisExpanded ? 'line-clamp-3' : ''}`}>
                {movie.overview || "Bộ phim mang đến những tình tiết hấp dẫn, kỹ xảo đỉnh cao và câu chuyện cuốn hút không thể bỏ lỡ dành cho khán giả yêu mến điện ảnh."}
              </p>
              {movie.overview && movie.overview.length > 200 && (
                <button
                  onClick={() => setIsSynopsisExpanded(!isSynopsisExpanded)}
                  className="text-xs text-[#F5C518] font-bold hover:underline cursor-pointer pt-1"
                >
                  {isSynopsisExpanded ? 'Thu gọn' : 'Xem toàn bộ nội dung...'}
                </button>
              )}
            </div>

            {/* Cast & Director */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-[#121824]/60 p-5 rounded-2xl border border-white/5">
              {movie.director && (
                <div>
                  <span className="text-xs text-gray-400 block font-semibold mb-1">Đạo diễn:</span>
                  <div className="text-white font-bold text-sm sm:text-base">{movie.director}</div>
                </div>
              )}
              {movie.cast && movie.cast.length > 0 && (
                <div>
                  <span className="text-xs text-gray-400 block font-semibold mb-1">Diễn viên chính:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {movie.cast.map((act, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-xs font-medium text-gray-200">
                        {act}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Tags & Genres Chips */}
            <div className="space-y-2">
              <span className="text-xs text-gray-400 uppercase font-bold tracking-wider">Từ Khóa & Thể Loại</span>
              <div className="flex flex-wrap gap-2">
                {[movie.category, movie.audio, movie.quality, 'Phim Chiếu Rạp', 'Huy Cá Cinema', 'Bom Tấn 2026'].filter(Boolean).map((t, i) => (
                  <span key={i} className="px-3 py-1 rounded-full bg-[#161E2E] hover:bg-[#E50914] text-xs font-bold text-gray-300 hover:text-white border border-white/10 transition-colors cursor-pointer">
                    #{t}
                  </span>
                ))}
              </div>
            </div>

          </div>

          {/* Right Info Column (Quick Facts Card) */}
          <div className="space-y-6">
            <div className="bg-[#121824]/80 p-5 rounded-2xl border border-white/10 space-y-4 shadow-xl">
              <h3 className="text-sm font-extrabold text-[#F5C518] uppercase tracking-wider border-b border-white/10 pb-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#F5C518]" />
                Thông Tin Chi Tiết
              </h3>

              <div className="space-y-3 text-xs sm:text-sm">
                <div className="flex items-center justify-between py-1 border-b border-white/5">
                  <span className="text-gray-400 flex items-center gap-1.5"><Film className="w-4 h-4" /> Thể loại:</span>
                  <span className="font-bold text-white text-right">{movie.category || 'Điện Ảnh'}</span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-white/5">
                  <span className="text-gray-400 flex items-center gap-1.5"><Calendar className="w-4 h-4" /> Năm phát hành:</span>
                  <span className="font-bold text-white">{movie.year || '2026'}</span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-white/5">
                  <span className="text-gray-400 flex items-center gap-1.5"><Clock className="w-4 h-4" /> Thời lượng:</span>
                  <span className="font-bold text-white">{movie.duration || '90 Phút'}</span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-white/5">
                  <span className="text-gray-400 flex items-center gap-1.5"><Radio className="w-4 h-4" /> Định dạng:</span>
                  <span className="font-bold text-cyan-400">{selectedResolution} (HLS 60fps)</span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-white/5">
                  <span className="text-gray-400 flex items-center gap-1.5"><Globe className="w-4 h-4" /> Ngôn ngữ:</span>
                  <span className="font-bold text-white">{movie.audio || 'Vietsub / Thuyết Minh'}</span>
                </div>

                <div className="flex items-center justify-between py-1">
                  <span className="text-gray-400 flex items-center gap-1.5"><Eye className="w-4 h-4" /> Lượt xem:</span>
                  <span className="font-bold text-[#F5C518]">{likeCount * 32} lượt</span>
                </div>
              </div>
            </div>

            {/* Poster Thumbnail Mini View */}
            <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-xl group">
              <img 
                src={movie.poster} 
                alt={movie.title} 
                className="w-full h-64 object-cover object-top group-hover:scale-105 transition-transform duration-500" 
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent flex items-end p-4">
                <div className="space-y-1">
                  <span className="text-[10px] font-black uppercase tracking-widest text-[#E50914] bg-white/10 px-2 py-0.5 rounded">HUY CÁ CINEMA</span>
                  <h4 className="text-sm font-bold text-white truncate">{movie.title}</h4>
                </div>
              </div>
            </div>

          </div>

        </div>

        {/* =====================================================================
            4. RELATED MOVIES (PHIM ĐỀ XUẤT TƯƠNG TỰ - CHỈ HIỆN KHI XEM PHIM)
           ===================================================================== */}
        {!movie.isLiveTv && relatedMovies.length > 0 && (
          <div className="pt-8 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-6 bg-[#E50914] rounded-full shadow-neon-red" />
                <h3 className="text-lg sm:text-xl font-black text-white tracking-wide">
                  Có Thể Bạn Muốn Xem Tiếp
                </h3>
              </div>
              <span className="text-xs text-gray-400">Đề xuất phim cùng thể loại</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
              {relatedMovies.slice(0, 6).map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => onSwitchMovie(item)}
                  className="group relative rounded-xl overflow-hidden bg-[#161E2E] border border-white/10 hover:border-[#E50914] transition-all duration-300 hover:scale-105 hover:shadow-2xl cursor-pointer"
                >
                  <div className="aspect-[2/3] w-full overflow-hidden relative">
                    <img
                      src={item.poster}
                      alt={item.title}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-80" />
                    
                    {item.quality && (
                      <span className="absolute top-2 right-2 px-1.5 py-0.5 rounded bg-black/80 text-[10px] font-bold text-white border border-white/20">
                        {item.quality}
                      </span>
                    )}

                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-[2px]">
                      <div className="w-10 h-10 rounded-full bg-[#E50914] text-white flex items-center justify-center shadow-neon-red">
                        <Play className="w-5 h-5 fill-white ml-0.5" />
                      </div>
                    </div>
                  </div>

                  <div className="p-2.5 space-y-1">
                    <h4 className="text-xs font-bold text-white truncate group-hover:text-[#F5C518] transition-colors">
                      {item.title}
                    </h4>
                    <div className="flex items-center justify-between text-[11px] text-gray-400">
                      <span>{item.year || '2026'}</span>
                      <span className="text-[#F5C518] font-bold">★ {item.imdb || '8.5'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
