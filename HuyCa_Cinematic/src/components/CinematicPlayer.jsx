import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Maximize2, 
  Minimize2, 
  X, 
  RotateCcw, 
  PictureInPicture2, 
  Tv, 
  Sparkles,
  ExternalLink
} from 'lucide-react';
import Hls from 'hls.js';

export default function CinematicPlayer({ 
  currentMovie, 
  isPlaying, 
  onClose,
  isMiniMode,
  setIsMiniMode
}) {
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const [isPlayingState, setIsPlayingState] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showControls, setShowControls] = useState(true);
  const controlsTimeoutRef = useRef(null);

  // Initialize Video & HLS Stream
  useEffect(() => {
    if (!currentMovie || !videoRef.current) return;

    const video = videoRef.current;
    const url = currentMovie.videoUrl || currentMovie.streamUrl;

    if (!url) return;

    let hlsInstance = null;

    if (url.includes('.m3u8')) {
      if (Hls.isSupported()) {
        hlsInstance = new Hls({ enableWorker: true });
        hlsInstance.loadSource(url);
        hlsInstance.attachMedia(video);
        hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
          video.play().catch(() => {});
        });
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = url;
        video.play().catch(() => {});
      }
    } else {
      video.src = url;
      video.play().catch(() => {});
    }

    // Auto landscape check for mobile screens
    if (window.innerWidth <= 768 && screen.orientation && screen.orientation.lock) {
      screen.orientation.lock('landscape').catch(() => {
        // Fallback or ignore if orientation lock fails
      });
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

  // Handle Controls Hide Timer
  const handleMouseMove = () => {
    setShowControls(true);
    if (controlsTimeoutRef.current) clearTimeout(controlsTimeoutRef.current);
    controlsTimeoutRef.current = setTimeout(() => {
      if (!isMiniMode && isPlayingState) {
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
      console.warn("Native PiP not available, using in-app floating mini player", err);
      setIsMiniMode(true);
    }
  };

  const formatTime = (timeInSeconds) => {
    if (isNaN(timeInSeconds)) return "00:00";
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!currentMovie) return null;

  // MINI FLOATING PLAYER (IN-APP PiP)
  if (isMiniMode) {
    return (
      <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 w-72 sm:w-96 rounded-2xl overflow-hidden glass-panel border border-[#E50914]/40 shadow-[0_10px_35px_rgba(0,0,0,0.8)] animate-in slide-in-from-bottom-6 duration-300">
        
        {/* Mini Header Bar */}
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

        {/* Video Canvas */}
        <div className="relative aspect-video bg-black group">
          <video
            ref={videoRef}
            className="w-full h-full object-contain"
            onTimeUpdate={handleTimeUpdate}
            onEnded={() => setIsPlayingState(false)}
            playsInline
            autoPlay
          />

          {/* Quick Hover Mini Controls */}
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
        onEnded={() => setIsPlayingState(false)}
        playsInline
        autoPlay
      />

      {/* Top Header Bar Overlay */}
      <div className={`absolute top-0 inset-x-0 p-4 sm:p-6 bg-gradient-to-b from-[#0B0F17]/90 via-[#0B0F17]/40 to-transparent transition-opacity duration-300 flex items-center justify-between ${
        showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#E50914] flex items-center justify-center shadow-neon-red">
            <Tv className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-white font-extrabold text-sm sm:text-lg flex items-center gap-2">
              {currentMovie.title || currentMovie.name}
            </h3>
            <p className="text-xs text-gray-400 font-medium">
              {currentMovie.category || currentMovie.group || "Chất Lượng Cao 4K"}
            </p>
          </div>
        </div>

        {/* Top Right Controls */}
        <div className="flex items-center gap-2">
          {/* PiP Button */}
          <button
            onClick={triggerNativePiP}
            className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white backdrop-blur-md cursor-pointer transition-colors"
            title="Chế độ Hình trong hình (PiP)"
          >
            <PictureInPicture2 className="w-5 h-5" />
          </button>

          {/* Minimize to Floating Mini Player */}
          <button
            onClick={() => setIsMiniMode(true)}
            className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white backdrop-blur-md cursor-pointer transition-colors"
            title="Thu nhỏ duyệt menu (Video không dừng)"
          >
            <Minimize2 className="w-5 h-5" />
          </button>

          {/* Close Player */}
          <button
            onClick={onClose}
            className="p-2.5 rounded-xl bg-[#E50914] hover:bg-[#F40612] text-white shadow-neon-red cursor-pointer transition-colors"
            title="Đóng trình phát"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Bottom Controls Overlay */}
      <div className={`absolute bottom-0 inset-x-0 p-4 sm:p-6 bg-gradient-to-t from-[#0B0F17]/95 via-[#0B0F17]/60 to-transparent transition-opacity duration-300 space-y-3 ${
        showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`}>
        
        {/* Progress Bar (Dành cho VOD / Video có thời lượng) */}
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

        {/* Controls Row */}
        <div className="flex items-center justify-between text-white text-sm">
          
          <div className="flex items-center gap-3 sm:gap-4">
            {/* Play/Pause */}
            <button 
              onClick={togglePlay}
              className="p-3 rounded-full bg-[#E50914] hover:bg-[#F40612] text-white shadow-neon-red cursor-pointer transition-transform hover:scale-110 active:scale-95"
            >
              {isPlayingState ? <Pause className="w-5 h-5 fill-white" /> : <Play className="w-5 h-5 fill-white ml-0.5" />}
            </button>

            {/* Mute/Unmute */}
            <button 
              onClick={toggleMute}
              className="p-2.5 rounded-xl hover:bg-white/10 cursor-pointer transition-colors"
            >
              {isMuted ? <VolumeX className="w-5 h-5 text-red-400" /> : <Volume2 className="w-5 h-5" />}
            </button>

            {/* Timestamps */}
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
            {/* Fullscreen Button */}
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
