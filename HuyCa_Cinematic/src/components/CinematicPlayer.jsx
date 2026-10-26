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
  SkipForward
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
  const controlsTimeoutRef = useRef(null);

  // Initialize Video, HLS Stream & Custom Subtitle Track
  useEffect(() => {
    if (!currentMovie || !videoRef.current) return;

    const video = videoRef.current;
    const url = currentMovie.videoUrl || currentMovie.streamUrl;
    const subUrl = currentMovie.subtitleUrl || null;

    setActiveSubText('');
    video.querySelectorAll('track').forEach(t => t.remove());

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

    if (!url) return;

    let hlsInstance = null;

    if (url.includes('.m3u8')) {
      if (Hls.isSupported()) {
        hlsInstance = new Hls({
          enableWorker: true,
          maxBufferLength: 30,
          maxMaxBufferLength: 60
        });
        hlsInstance.loadSource(url);
        hlsInstance.attachMedia(video);
        hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
          video.play().then(() => setIsPlayingState(true)).catch(() => {});
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
      if (hlsInstance) {
        hlsInstance.destroy();
      }
      if (screen.orientation && screen.orientation.unlock) {
        try { screen.orientation.unlock(); } catch (e) {}
      }
    };
  }, [currentMovie]);

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
      document.exitFullscreen();
    } else {
      containerRef.current.requestFullscreen();
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
          <video
            ref={videoRef}
            className="w-full h-full object-contain"
            onTimeUpdate={handleTimeUpdate}
            onEnded={() => setIsPlayingState(false)}
            playsInline
            autoPlay
          />
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
      {/* Video Element */}
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
                subtitleUrl: nextEp.subtitleUrl
              });
            }
          }
        }}
        playsInline
        autoPlay
      />

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
    </div>
  );
}
