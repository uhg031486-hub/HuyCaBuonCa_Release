import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Maximize2, 
  Minimize2, 
  X, 
  PictureInPicture2, 
  Tv,
  ListVideo,
  SkipForward,
  RotateCcw,
  ExternalLink
} from 'lucide-react';
import Hls from 'hls.js';

export default function CinematicPlayer({ 
  currentMovie, 
  isPlaying, 
  onClose,
  isMiniMode,
  setIsMiniMode,
  onSwitchEpisode
}) {
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const [isPlayingState, setIsPlayingState] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showControls, setShowControls] = useState(true);
  const [showEpisodeDrawer, setShowEpisodeDrawer] = useState(false);
  const [activeSubText, setActiveSubText] = useState('');
  const [useIframeEmbed, setUseIframeEmbed] = useState(false);
  const [playbackError, setPlaybackError] = useState(null);
  const controlsTimeoutRef = useRef(null);

  // Reset embed state khi đổi phim
  useEffect(() => {
    setUseIframeEmbed(false);
    setPlaybackError(null);
  }, [currentMovie?.id, currentMovie?.currentEpisode, currentMovie?.videoUrl]);

  // Khởi tạo Video, HLS Stream với cơ chế Auto-Proxy Fallback
  useEffect(() => {
    if (!currentMovie || !videoRef.current || useIframeEmbed) return;

    const video = videoRef.current;
    let url = currentMovie.videoUrl || currentMovie.streamUrl;
    const subUrl = currentMovie.subtitleUrl || null;

    setActiveSubText('');
    setPlaybackError(null);
    video.querySelectorAll('track').forEach(t => t.remove());

    // Nạp phụ đề tiếng Việt nếu có (Phim ngắn ReelShort / FreeReels)
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
      if (currentMovie.embedUrl) {
        setUseIframeEmbed(true);
      }
      return;
    }

    let hlsInstance = null;
    let isProxied = url.includes('/api/proxy');

    const handleVideoError = () => {
      console.warn('Native video error, checking fallback...');
      if (!isProxied && url && url.startsWith('http')) {
        console.log('Retrying native video via proxy fallback:', url);
        isProxied = true;
        video.src = `/api/proxy?url=${encodeURIComponent(url)}`;
        video.load();
        video.play().catch(() => {});
      } else if (currentMovie.embedUrl) {
        console.log('Switching to embed iframe player fallback...');
        setUseIframeEmbed(true);
      } else {
        setPlaybackError('Không thể tải luồng phát video này. Bạn có thể thử tập khác hoặc đổi Server!');
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
          video.play().then(() => setIsPlayingState(true)).catch(() => {});
        });

        // BẮT LỖI CORS & MẠNG: Tự động chạy qua Cloudflare /api/proxy
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
                if (currentMovie.embedUrl) {
                  setUseIframeEmbed(true);
                  return;
                }
                hlsInstance.startLoad();
                break;
              case Hls.ErrorTypes.MEDIA_ERROR:
                hlsInstance.recoverMediaError();
                break;
              default:
                if (currentMovie.embedUrl) {
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
        video.play().then(() => setIsPlayingState(true)).catch(() => {});
      }
    } else {
      video.src = url;
      video.play().then(() => setIsPlayingState(true)).catch(() => {});
    }

    if (window.innerWidth <= 768 && !currentMovie.isShortDrama && screen.orientation && screen.orientation.lock) {
      screen.orientation.lock('landscape').catch(() => {});
    }

    return () => {
      video.removeEventListener('error', handleVideoError);
      if (hlsInstance) {
        hlsInstance.destroy();
      }
      if (screen.orientation && screen.orientation.unlock) {
        try { screen.orientation.unlock(); } catch (e) {}
      }
    };
  }, [currentMovie?.videoUrl, currentMovie?.streamUrl, currentMovie?.currentEpisode, useIframeEmbed]);

  const handleMouseMove = () => {
    setShowControls(true);
    if (controlsTimeoutRef.current) clearTimeout(controlsTimeoutRef.current);
    controlsTimeoutRef.current = setTimeout(() => {
      if (!isMiniMode && isPlayingState && !showEpisodeDrawer) {
        setShowControls(false);
      }
    }, 3500);
  };

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (videoRef.current.paused) {
      videoRef.current.play();
      setIsPlayingState(true);
    } else {
      videoRef.current.pause();
      setIsPlayingState(false);
    }
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !videoRef.current.muted;
    setIsMuted(videoRef.current.muted);
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    setCurrentTime(videoRef.current.currentTime);
    setDuration(videoRef.current.duration || 0);
    setProgress((videoRef.current.currentTime / videoRef.current.duration) * 100 || 0);
  };

  const handleSeek = (e) => {
    if (!videoRef.current || !duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    videoRef.current.currentTime = pos * duration;
  };

  const requestFullscreen = () => {
    if (!containerRef.current) return;
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    } else {
      containerRef.current.requestFullscreen().catch(() => {});
    }
  };

  const triggerNativePiP = async () => {
    try {
      if (videoRef.current && document.pictureInPictureEnabled) {
        if (document.pictureInPictureElement) {
          await document.exitPictureInPicture();
        } else {
          await videoRef.current.requestPictureInPicture();
        }
      }
    } catch (err) {
      setIsMiniMode(true);
    }
  };

  const formatTime = (timeInSeconds) => {
    if (isNaN(timeInSeconds)) return "00:00";
    const h = Math.floor(timeInSeconds / 3600);
    const minutes = Math.floor((timeInSeconds % 3600) / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    if (h > 0) {
      return `${h}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!currentMovie) return null;

  const episodes = currentMovie.episodes || [];
  const currentEpName = currentMovie.currentEpisode || (episodes[0]?.name) || '';
  const currentEmbedUrl = currentMovie.embedUrl || episodes.find(e => e.name === currentEpName)?.embedUrl || '';

  // MINI FLOATING PLAYER (IN-APP PiP)
  if (isMiniMode) {
    return (
      <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 w-72 sm:w-96 rounded-2xl overflow-hidden glass-panel border border-[#E50914]/40 shadow-[0_10px_35px_rgba(0,0,0,0.8)] animate-in slide-in-from-bottom-6 duration-300">
        <div className="flex items-center justify-between px-3 py-1.5 bg-[#0B0F17]/90 border-b border-white/10 text-xs">
          <div className="flex items-center gap-1.5 truncate max-w-[70%]">
            <span className="w-2 h-2 rounded-full bg-[#E50914] animate-pulse" />
            <span className="font-bold text-white truncate">{currentMovie.title || currentMovie.name}</span>
          </div>
          <div className="flex items-center gap-1">
            <button 
              onClick={() => setIsMiniMode(false)}
              className="p-1 text-gray-300 hover:text-white hover:bg-white/10 rounded cursor-pointer transition-colors"
              title="Phóng to"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
            <button 
              onClick={onClose}
              className="p-1 text-gray-300 hover:text-[#E50914] hover:bg-white/10 rounded cursor-pointer transition-colors"
              title="Đóng player"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <div className="relative aspect-video bg-black group">
          {useIframeEmbed && currentEmbedUrl ? (
            <iframe
              src={currentEmbedUrl}
              className="w-full h-full border-0"
              allowFullScreen
              allow="autoplay; encrypted-media"
            />
          ) : (
            <video
              ref={videoRef}
              className="w-full h-full object-contain"
              onTimeUpdate={handleTimeUpdate}
              onEnded={() => setIsPlayingState(false)}
              playsInline
              autoPlay
            />
          )}

          {!useIframeEmbed && (
            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
              <button 
                onClick={togglePlay}
                className="p-2 rounded-full bg-[#E50914] text-white shadow-neon-red cursor-pointer"
              >
                {isPlayingState ? <Pause className="w-4 h-4 fill-white" /> : <Play className="w-4 h-4 fill-white ml-0.5" />}
              </button>
              <button 
                onClick={toggleMute}
                className="p-2 rounded-full bg-[#161E2E]/80 text-white cursor-pointer"
              >
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // FULLSCREEN / MODAL PLAYER MODE
  return (
    <div 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      className="fixed inset-0 z-50 bg-black flex items-center justify-center select-none overflow-hidden"
    >
      {/* Video hoặc Iframe Embed */}
      {useIframeEmbed && currentEmbedUrl ? (
        <iframe
          src={currentEmbedUrl}
          className="w-full h-full border-0 bg-black"
          allowFullScreen
          allow="autoplay; encrypted-media; picture-in-picture"
          title={currentMovie.title || "Cinematic Player"}
        />
      ) : (
        <video
          ref={videoRef}
          className="w-full h-full object-contain cursor-pointer"
          onClick={togglePlay}
          onTimeUpdate={handleTimeUpdate}
          onEnded={() => {
            setIsPlayingState(false);
            if (episodes.length > 1 && onSwitchEpisode) {
              const curIdx = episodes.findIndex(e => e.name === currentEpName || e.url === currentMovie.videoUrl);
              if (curIdx >= 0 && curIdx + 1 < episodes.length) {
                const nextEp = episodes[curIdx + 1];
                onSwitchEpisode({
                  ...currentMovie,
                  currentEpisode: nextEp.name,
                  videoUrl: nextEp.url,
                  embedUrl: nextEp.embedUrl || '',
                  subtitleUrl: nextEp.subtitleUrl
                });
              }
            }
          }}
          playsInline
          autoPlay
        />
      )}

      {/* Thông Báo Lỗi Có Nút Thử Lại & Đổi Server */}
      {playbackError && (
        <div className="absolute inset-0 z-40 bg-black/85 flex flex-col items-center justify-center p-6 text-center space-y-4">
          <div className="w-14 h-14 rounded-full bg-red-500/20 border border-red-500/50 flex items-center justify-center text-2xl">
            ⚠️
          </div>
          <h4 className="text-lg font-bold text-white">Chưa thể phát luồng HLS trực tiếp</h4>
          <p className="text-sm text-gray-300 max-w-md">{playbackError}</p>
          <div className="flex items-center gap-3">
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
                  videoRef.current.src = `/api/proxy?url=${encodeURIComponent(currentMovie.videoUrl || '')}`;
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

      {/* Custom Cinema Subtitle Overlay */}
      {activeSubText && (
        <div className="absolute bottom-20 left-1/2 -translate-x-1/2 z-30 max-w-[85%] px-4 py-1.5 rounded-lg bg-black/75 text-white font-semibold text-sm sm:text-base text-center pointer-events-none whitespace-pre-line shadow-lg">
          {activeSubText}
        </div>
      )}

      {/* Top Header Bar Overlay */}
      <div className={`absolute top-0 inset-x-0 p-4 sm:p-6 bg-gradient-to-b from-[#0B0F17]/90 via-[#0B0F17]/40 to-transparent transition-opacity duration-300 flex items-center justify-between z-20 ${
        showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#E50914] flex items-center justify-center shadow-neon-red">
            <Tv className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-white font-extrabold text-sm sm:text-lg flex items-center gap-2">
              <span>{currentMovie.title || currentMovie.name}</span>
              {currentEpName && <span className="text-[#F5C518] text-xs sm:text-sm">• {currentEpName}</span>}
            </h3>
            <p className="text-xs text-gray-400 font-medium">
              {currentMovie.category || currentMovie.group || "Chất Lượng Cao Full HD / 4K"}
            </p>
          </div>
        </div>

        {/* Top Right Controls */}
        <div className="flex items-center gap-2">
          {currentEmbedUrl && (
            <button
              onClick={() => setUseIframeEmbed(!useIframeEmbed)}
              className="px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-[#F5C518] border border-[#F5C518]/30 text-xs font-bold backdrop-blur-md cursor-pointer transition-colors flex items-center gap-1.5"
              title="Đổi giữa Trình phát HLS và Server Embed"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{useIframeEmbed ? 'Đổi HLS Nét' : 'Đổi Server Embed'}</span>
            </button>
          )}

          {episodes.length > 1 && (
            <button
              onClick={() => setShowEpisodeDrawer(!showEpisodeDrawer)}
              className="px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold backdrop-blur-md cursor-pointer transition-colors flex items-center gap-1.5"
              title="Danh sách tập phim"
            >
              <ListVideo className="w-4 h-4 text-[#F5C518]" />
              <span className="hidden sm:inline">Chọn Tập ({episodes.length})</span>
            </button>
          )}

          <button
            onClick={triggerNativePiP}
            className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white backdrop-blur-md cursor-pointer transition-colors"
            title="Chế độ Hình trong hình (PiP)"
          >
            <PictureInPicture2 className="w-5 h-5" />
          </button>

          <button
            onClick={() => setIsMiniMode(true)}
            className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white backdrop-blur-md cursor-pointer transition-colors"
            title="Thu nhỏ duyệt menu (Video không dừng)"
          >
            <Minimize2 className="w-5 h-5" />
          </button>

          <button
            onClick={onClose}
            className="p-2.5 rounded-xl bg-[#E50914] hover:bg-[#F40612] text-white shadow-neon-red cursor-pointer transition-colors"
            title="Đóng trình phát"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Episode Selection Drawer inside Player */}
      {showEpisodeDrawer && episodes.length > 0 && (
        <div className="absolute right-4 top-20 bottom-24 w-72 sm:w-80 bg-[#0B0F17]/95 backdrop-blur-xl border border-white/15 rounded-2xl p-4 z-30 flex flex-col shadow-2xl">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
            <span className="text-sm font-extrabold text-[#F5C518]">DANH SÁCH TẬP ({episodes.length})</span>
            <button onClick={() => setShowEpisodeDrawer(false)} className="text-gray-400 hover:text-white cursor-pointer">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="grid grid-cols-3 gap-2 overflow-y-auto pr-1">
            {episodes.map((ep, idx) => {
              const isAct = ep.name === currentEpName || ep.url === currentMovie.videoUrl;
              return (
                <button
                  key={idx}
                  onClick={() => {
                    setShowEpisodeDrawer(false);
                    if (onSwitchEpisode) {
                      onSwitchEpisode({
                        ...currentMovie,
                        currentEpisode: ep.name,
                        videoUrl: ep.url,
                        embedUrl: ep.embedUrl || '',
                        subtitleUrl: ep.subtitleUrl
                      });
                    }
                  }}
                  className={`py-2 px-2 rounded-lg text-xs font-bold truncate cursor-pointer transition-colors ${
                    isAct ? 'bg-[#E50914] text-white shadow-neon-red' : 'bg-white/10 text-gray-300 hover:bg-white/20'
                  }`}
                >
                  {ep.name}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Bottom Controls Overlay */}
      {!useIframeEmbed && (
        <div className={`absolute bottom-0 inset-x-0 p-4 sm:p-6 bg-gradient-to-t from-[#0B0F17]/95 via-[#0B0F17]/60 to-transparent transition-opacity duration-300 space-y-3 z-20 ${
          showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}>
          {duration > 0 && (
            <div 
              onClick={handleSeek}
              className="relative w-full h-1.5 hover:h-2.5 bg-white/20 rounded-full cursor-pointer transition-all group"
            >
              <div 
                className="absolute top-0 left-0 bottom-0 bg-[#E50914] rounded-full shadow-neon-red"
                style={{ width: `${progress}%` }}
              />
              <div 
                className="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-white rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ left: `calc(${progress}% - 7px)` }}
              />
            </div>
          )}

          <div className="flex items-center justify-between text-white text-sm">
            <div className="flex items-center gap-3 sm:gap-4">
              <button 
                onClick={togglePlay}
                className="p-3 rounded-full bg-[#E50914] hover:bg-[#F40612] text-white shadow-neon-red cursor-pointer transition-transform hover:scale-110 active:scale-95"
              >
                {isPlayingState ? <Pause className="w-5 h-5 fill-white" /> : <Play className="w-5 h-5 fill-white ml-0.5" />}
              </button>

              {episodes.length > 1 && onSwitchEpisode && (
                <button
                  onClick={() => {
                    const curIdx = episodes.findIndex(e => e.name === currentEpName || e.url === currentMovie.videoUrl);
                    if (curIdx >= 0 && curIdx + 1 < episodes.length) {
                      const nextEp = episodes[curIdx + 1];
                      onSwitchEpisode({
                        ...currentMovie,
                        currentEpisode: nextEp.name,
                        videoUrl: nextEp.url,
                        embedUrl: nextEp.embedUrl || '',
                        subtitleUrl: nextEp.subtitleUrl
                      });
                    }
                  }}
                  className="p-2.5 rounded-xl hover:bg-white/10 cursor-pointer transition-colors"
                  title="Tập tiếp theo"
                >
                  <SkipForward className="w-5 h-5" />
                </button>
              )}

              <button 
                onClick={toggleMute}
                className="p-2.5 rounded-xl hover:bg-white/10 cursor-pointer transition-colors"
              >
                {isMuted ? <VolumeX className="w-5 h-5 text-red-400" /> : <Volume2 className="w-5 h-5" />}
              </button>

              {duration > 0 && (
                <span className="text-xs sm:text-sm font-semibold text-gray-300">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </span>
              )}
              {duration === 0 && (
                <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#E50914]/20 border border-[#E50914]/50 text-[#E50914] text-xs font-bold">
                  <span className="w-2 h-2 rounded-full bg-[#E50914] animate-ping" />
                  <span>TRỰC TIẾP LIVE STREAM</span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-2 sm:gap-3">
              <button
                onClick={requestFullscreen}
                className="p-2.5 rounded-xl hover:bg-white/10 text-white cursor-pointer transition-colors"
                title="Toàn màn hình"
              >
                <Maximize2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
