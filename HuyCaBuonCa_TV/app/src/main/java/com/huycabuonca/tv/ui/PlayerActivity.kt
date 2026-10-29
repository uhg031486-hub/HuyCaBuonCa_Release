package com.huycabuonca.tv.ui

import android.annotation.SuppressLint
import android.os.Bundle
import android.os.CountDownTimer
import android.os.Handler
import android.os.Looper
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import java.io.ByteArrayInputStream
import android.webkit.WebResourceResponse
import android.webkit.WebResourceRequest
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.lifecycle.lifecycleScope
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.exoplayer.DefaultLoadControl
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.hls.HlsMediaSource
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.huycabuonca.tv.R
import com.huycabuonca.tv.api.MovieRepository
import com.huycabuonca.tv.api.TvChannelItem
import com.huycabuonca.tv.databinding.ActivityPlayerBinding
import com.huycabuonca.tv.model.EpisodeItem
import com.huycabuonca.tv.model.MovieItem
import com.huycabuonca.tv.model.MovieSource
import com.huycabuonca.tv.util.FavoriteMovieManager
import com.huycabuonca.tv.util.TvFocusUtil
import com.huycabuonca.tv.util.WatchHistoryManager
import kotlinx.coroutines.launch

class PlayerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPlayerBinding
    private var player: ExoPlayer? = null
    private var loudnessEnhancer: android.media.audiofx.LoudnessEnhancer? = null
    private val hideHandler = Handler(Looper.getMainLooper())
    private val hideOverlayRunnable = Runnable { hideOverlays() }
    private val hideBannerRunnable = Runnable { binding.layoutChannelBanner.visibility = View.GONE }
    
    // Quản lý chuyển kênh nhanh theo nhóm (Quick Zapping TV)
    private var isTvMode = false
    private var currentChannelIndex = 0
    private var currentTvChannel: TvChannelItem? = null
    private var sameGroupChannels = mutableListOf<TvChannelItem>()
    private var sideAdapter: QuickChannelTvAdapter? = null

    // Quản lý đệm phím số chọn kênh trực tiếp (Number Key Zapping 0-9)
    private val digitBuffer = StringBuilder()
    private val zapHandler = Handler(Looper.getMainLooper())
    private val zapRunnable = Runnable { executeNumberZapping() }

    // Quản lý tập phim và chuyển tập tự động (Auto-next)
        // Quản lý tập phim và chuyển tập tự động (Auto-next)
    private var episodesList: ArrayList<EpisodeItem> = arrayListOf()
    private var currentEpisodeIndex = 0
    private var autoNextTimer: CountDownTimer? = null

    // Quản lý tiếp tục xem đúng vị trí (Resume Playback)
    private var initialStartPositionMs: Long = 0L
    private var hasResumedPosition: Boolean = false
    private val historySyncHandler = Handler(Looper.getMainLooper())
    private val historySyncRunnable = object : Runnable {
        override fun run() {
            if (player?.isPlaying == true) {
                savePlaybackHistory()
            }
            historySyncHandler.postDelayed(this, 10000)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPlayerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        hideSystemUI()
        MovieRepository.initTvChannels(this)

        val streamUrl = intent.getStringExtra("EXTRA_STREAM_URL") ?: ""
        val isM3u8 = intent.getBooleanExtra("EXTRA_IS_M3U8", true) || streamUrl.contains(".m3u8")
        val title = intent.getStringExtra("EXTRA_TITLE") ?: ""
        val episode = intent.getStringExtra("EXTRA_EPISODE") ?: ""

        binding.txtPlayerTitle.text = "$title - $episode"

        val channelIdExtra = intent.getStringExtra("EXTRA_CHANNEL_ID") ?: ""
        val sourceExtra = intent.getStringExtra("EXTRA_SOURCE") ?: ""

        val rawEps = intent.getSerializableExtra("EXTRA_EPISODES_LIST") as? ArrayList<*>
        if (rawEps != null) {
            episodesList = rawEps.filterIsInstance<EpisodeItem>() as? ArrayList<EpisodeItem> ?: arrayListOf()
        }
        currentEpisodeIndex = intent.getIntExtra("EXTRA_CURRENT_EPISODE_INDEX", 0)

        // Nhận diện xem có phải đang phát kênh truyền hình TV không
        val channels = MovieRepository.getAllTvChannels(this)
        val found = channels.find {
            (channelIdExtra.isNotEmpty() && it.id == channelIdExtra) ||
            it.url == streamUrl ||
            it.name.equals(title, ignoreCase = true)
        }
        if (found != null || sourceExtra == MovieSource.XEMTIVI.name) {
            isTvMode = true
            currentTvChannel = found ?: channels.firstOrNull()
            currentTvChannel?.let { MovieRepository.setLastWatchedChannelId(this, it.id) }

            sameGroupChannels = MovieRepository.getChannelsInSameGroup(currentTvChannel?.id ?: "", this).toMutableList()
            val grpIdx = sameGroupChannels.indexOfFirst { it.id == currentTvChannel?.id || it.url == currentTvChannel?.url }
            if (grpIdx != -1) currentChannelIndex = grpIdx

            android.util.Log.d("TV_ZAP", "TV Mode activated: channel=${currentTvChannel?.name}, group=${currentTvChannel?.group}, totalInGroup=${sameGroupChannels.size}")
            currentTvChannel?.let { ch ->
                binding.txtChannelNumber.text = "KÊNH %02d/%02d".format(currentChannelIndex + 1, sameGroupChannels.size)
                binding.txtChannelName.text = ch.name
                binding.txtChannelGroup.text = "Nhóm: ${ch.group}"
                binding.layoutChannelBanner.visibility = View.VISIBLE
                hideHandler.removeCallbacks(hideBannerRunnable)
                hideHandler.postDelayed(hideBannerRunnable, 3500)
            }
            binding.txtRemoteTips.text = "Điều khiển: [ ▲ / ▼ ] Đổi Kênh Cùng Nhóm  •  [ ◄ ] Danh Sách Kênh  •  [ 0-9 ] Bấm Số Kênh  •  [ OK ] Phát/Dừng"
        } else {
            android.util.Log.d("TV_ZAP", "Movie Mode (not TV): title=$title, url=$streamUrl")
            binding.txtRemoteTips.text = "Điều khiển: [ ▲ / ▼ ] Tập Trước/Sau  •  [ ◄ / ► ] Tua 10s  •  [ OK ] Phát/Dừng"
        }

        binding.btnPlayNextNow.setOnClickListener {
            autoNextTimer?.cancel()
            binding.layoutNextEpCountdown.visibility = View.GONE
            playEpisodeAtIndex(currentEpisodeIndex + 1)
        }

        binding.btnCancelNextEp.setOnClickListener {
            autoNextTimer?.cancel()
            binding.layoutNextEpCountdown.visibility = View.GONE
        }

                initialStartPositionMs = intent.getLongExtra("EXTRA_START_POSITION", 0L)
        if (initialStartPositionMs == 0L && !isTvMode) {
            val movie = intent.getSerializableExtra("EXTRA_MOVIE_ITEM") as? MovieItem
            if (movie != null) {
                val hist = WatchHistoryManager.getHistoryForMovie(this, movie.slug.ifEmpty { movie.id })
                if (hist != null && (hist.episodeName == episode || hist.episodeName.isEmpty())) {
                    initialStartPositionMs = hist.positionMs
                }
            }
        }
        historySyncHandler.postDelayed(historySyncRunnable, 10000)

        val subtitleUrl = intent.getStringExtra("EXTRA_SUBTITLE_URL")

        if (streamUrl.startsWith("freereels_unlock:")) {
            val tokens = streamUrl.split(":")
            if (tokens.size >= 3) {
                val sId = tokens[1].removePrefix("freereels:")
                val epId = tokens[2]
                binding.playerProgress.visibility = View.VISIBLE
                lifecycleScope.launch {
                    val res = MovieRepository.unlockFreeReelsEpisode(sId, epId)
                    binding.playerProgress.visibility = View.GONE
                    if (res != null && res.streamUrl.isNotEmpty()) {
                        initExoPlayer(res.streamUrl, res.subtitleUrl ?: subtitleUrl)
                    } else {
                        Toast.makeText(this@PlayerActivity, "Không thể tải tập phim ngắn này", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        } else if (streamUrl.contains("streamc.xyz") || streamUrl.contains("embed.php")) {
            val cleanM3u8 = "https://huyca.pages.dev/api/nguonc_stream?url=${java.net.URLEncoder.encode(streamUrl, "UTF-8")}"
            initExoPlayer(cleanM3u8, subtitleUrl)
        } else if (isM3u8 || streamUrl.contains(".m3u8") || streamUrl.contains(".mp4") || streamUrl.contains("gamomephim")) {
            initExoPlayer(streamUrl, subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }

        TvFocusUtil.setupFocusScale(binding.btnToggleFavPlayer)
        updateFavPlayerButton()
        binding.btnToggleFavPlayer.setOnClickListener {
            toggleCurrentFavorite()
        }

        scheduleHideOverlays()
    }

    private fun initLoudnessEnhancer(sessionId: Int) {
        if (sessionId <= 0) return
        try {
            loudnessEnhancer?.release()
            loudnessEnhancer = android.media.audiofx.LoudnessEnhancer(sessionId).apply {
                setTargetGain(600) // Default boost on TV
                enabled = true
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun initExoPlayer(url: String, subtitleUrl: String? = null) {
        player?.release()
        binding.playerView.visibility = View.VISIBLE
        binding.webViewPlayer.visibility = View.GONE
        binding.playerProgress.visibility = View.VISIBLE

        val reqHeaders = mutableMapOf<String, String>()
        if (url.contains("phimapi.com") || url.contains("phimimg.com") || url.contains("phim1280.tv")) {
            reqHeaders["Referer"] = "https://player.phimapi.com/"
            reqHeaders["Origin"] = "https://player.phimapi.com"
        } else if (url.contains("huyca.pages.dev") || url.contains("nguonc_stream")) {
            reqHeaders["Referer"] = "https://huyca.pages.dev/"
            reqHeaders["Origin"] = "https://huyca.pages.dev"
        }
        val dataSourceFactory = DefaultHttpDataSource.Factory()
            .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
            .setDefaultRequestProperties(reqHeaders)
            .setAllowCrossProtocolRedirects(true)

        val isHlsStream = url.contains(".m3u8", ignoreCase = true) || 
                          url.contains("m3u8", ignoreCase = true) || 
                          url.contains("nguonc_stream", ignoreCase = true) ||
                          isTvMode

        val mediaItemBuilder = MediaItem.Builder().setUri(url)
        if (isHlsStream) {
            mediaItemBuilder.setMimeType(androidx.media3.common.MimeTypes.APPLICATION_M3U8)
        }

        if (!subtitleUrl.isNullOrEmpty()) {
            val mimeType = if (subtitleUrl.contains(".vtt", ignoreCase = true)) {
                androidx.media3.common.MimeTypes.TEXT_VTT
            } else {
                androidx.media3.common.MimeTypes.APPLICATION_SUBRIP
            }
            val subConfig = MediaItem.SubtitleConfiguration.Builder(android.net.Uri.parse(subtitleUrl))
                .setMimeType(mimeType)
                .setLanguage("vi")
                .setLabel("Tiếng Việt")
                .setSelectionFlags(androidx.media3.common.C.SELECTION_FLAG_DEFAULT or androidx.media3.common.C.SELECTION_FLAG_FORCED)
                .build()
            mediaItemBuilder.setSubtitleConfigurations(listOf(subConfig))
        }

        val mediaItem = mediaItemBuilder.build()
        val baseMediaSource = if (isHlsStream) {
            androidx.media3.exoplayer.hls.HlsMediaSource.Factory(dataSourceFactory)
                .setPlaylistParserFactory(com.huycabuonca.tv.util.AdBlockPlaylistParserFactory())
                .createMediaSource(mediaItem)
        } else {
            androidx.media3.exoplayer.source.ProgressiveMediaSource.Factory(dataSourceFactory)
                .createMediaSource(mediaItem)
        }

        val mediaSource = if (!subtitleUrl.isNullOrEmpty()) {
            val mimeType = if (subtitleUrl.contains(".vtt", ignoreCase = true)) {
                androidx.media3.common.MimeTypes.TEXT_VTT
            } else {
                androidx.media3.common.MimeTypes.APPLICATION_SUBRIP
            }
            val subConfig = MediaItem.SubtitleConfiguration.Builder(android.net.Uri.parse(subtitleUrl))
                .setMimeType(mimeType)
                .setLanguage("vi")
                .setLabel("Tiếng Việt")
                .setSelectionFlags(androidx.media3.common.C.SELECTION_FLAG_DEFAULT or androidx.media3.common.C.SELECTION_FLAG_FORCED)
                .build()
            val subSource = androidx.media3.exoplayer.source.SingleSampleMediaSource.Factory(dataSourceFactory)
                .createMediaSource(subConfig, androidx.media3.common.C.TIME_UNSET)
            androidx.media3.exoplayer.source.MergingMediaSource(baseMediaSource, subSource)
        } else {
            baseMediaSource
        }

        val trackSelector = androidx.media3.exoplayer.trackselection.DefaultTrackSelector(this).apply {
            setParameters(
                buildUponParameters()
                    .setPreferredTextLanguage("vi")
                    .setSelectUndeterminedTextLanguage(true)
                    .setIgnoredTextSelectionFlags(0)
            )
        }

        // Tối ưu Buffer Cache thông minh chống lag giật trên Android TV Box (15s - 60s)
        val loadControl = DefaultLoadControl.Builder()
            .setBufferDurationsMs(
                15_000, // minBufferMs: 15s
                60_000, // maxBufferMs: 60s
                2_500,  // bufferForPlaybackMs: 2.5s
                5_000   // bufferForPlaybackAfterRebufferMs: 5s
            )
            .build()

        player = ExoPlayer.Builder(this)
            .setTrackSelector(trackSelector)
            .setLoadControl(loadControl)
            .build().apply {
            setMediaSource(mediaSource)
            if (initialStartPositionMs > 5_000L) {
                seekTo(initialStartPositionMs)
            }
            prepare()
            playWhenReady = true
            initLoudnessEnhancer(audioSessionId)
            addListener(object : Player.Listener {
                override fun onAudioSessionIdChanged(audioSessionId: Int) {
                    initLoudnessEnhancer(audioSessionId)
                }

                override fun onVideoSizeChanged(videoSize: androidx.media3.common.VideoSize) {
                    val isVertical = videoSize.height > videoSize.width && videoSize.width > 0
                    if (isVertical) {
                        // Tự nhận diện video dọc theo tỉ lệ thực: Giữ đúng tỷ lệ 9:16 ở giữa màn hình TV
                        binding.playerView.resizeMode = androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FIT
                    } else {
                        binding.playerView.resizeMode = androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FIT
                    }
                }

                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                    binding.playerProgress.visibility = View.GONE
                    val embedUrl = intent.getStringExtra("EXTRA_EMBED_URL")
                    if (!embedUrl.isNullOrEmpty() && binding.webViewPlayer.visibility != View.VISIBLE) {
                        initWebViewPlayer(embedUrl)
                    }
                }

                override fun onPlaybackStateChanged(playbackState: Int) {
                    if (playbackState == Player.STATE_BUFFERING) {
                        binding.playerProgress.visibility = View.VISIBLE
                    } else {
                        binding.playerProgress.visibility = View.GONE
                    }

                    if (playbackState == Player.STATE_READY) {
                        if (!hasResumedPosition && initialStartPositionMs > 5_000L) {
                            hasResumedPosition = true
                            seekTo(initialStartPositionMs)
                            val min = (initialStartPositionMs / 60000).toInt()
                            val sec = ((initialStartPositionMs % 60000) / 1000).toInt()
                            Toast.makeText(this@PlayerActivity, "▶ Tiếp tục xem từ %02d:%02d".format(min, sec), Toast.LENGTH_SHORT).show()
                            initialStartPositionMs = 0L
                        }
                    }

                    if (playbackState == Player.STATE_ENDED) {
                        if (!isTvMode && currentEpisodeIndex + 1 < episodesList.size) {
                            triggerAutoNextCountdown()
                        }
                    }
                }
            })
        }
        binding.playerView.player = player
        binding.playerView.subtitleView?.apply {
            visibility = android.view.View.VISIBLE
            setStyle(
                androidx.media3.ui.CaptionStyleCompat(
                    android.graphics.Color.WHITE,
                    android.graphics.Color.argb(160, 0, 0, 0),
                    android.graphics.Color.TRANSPARENT,
                    androidx.media3.ui.CaptionStyleCompat.EDGE_TYPE_OUTLINE,
                    android.graphics.Color.BLACK,
                    null
                )
            )
            setFractionalTextSize(0.058f)
        }
    }

    private fun triggerAutoNextCountdown() {
        val nextEp = episodesList.getOrNull(currentEpisodeIndex + 1) ?: return
        autoNextTimer?.cancel()
        binding.layoutNextEpCountdown.visibility = View.VISIBLE
        binding.btnPlayNextNow.requestFocus()

        autoNextTimer = object : CountDownTimer(5000, 1000) {
            override fun onTick(millisUntilFinished: Long) {
                val sec = (millisUntilFinished / 1000) + 1
                binding.txtNextEpTitle.text = "Đang chuyển sang ${nextEp.name} sau ${sec}s..."
            }

            override fun onFinish() {
                binding.layoutNextEpCountdown.visibility = View.GONE
                playEpisodeAtIndex(currentEpisodeIndex + 1)
            }
        }.start()
    }

    private fun playEpisodeAtIndex(index: Int) {
        if (index !in episodesList.indices) return
        savePlaybackHistory()
        initialStartPositionMs = 0L
        hasResumedPosition = true
        currentEpisodeIndex = index
        val episode = episodesList[index]
        val title = intent.getStringExtra("EXTRA_TITLE") ?: "Xem Phim"
        binding.txtPlayerTitle.text = "$title - ${episode.name}"

        val streamUrl = episode.linkM3u8 ?: episode.linkEmbed
        if (streamUrl.isNullOrEmpty()) {
            Toast.makeText(this, "Không tìm thấy luồng phát của tập này", Toast.LENGTH_SHORT).show()
            return
        }

        if (streamUrl.startsWith("freereels_unlock:")) {
            val tokens = streamUrl.split(":")
            if (tokens.size >= 3) {
                binding.playerProgress.visibility = View.VISIBLE
                lifecycleScope.launch {
                    val res = MovieRepository.unlockFreeReelsEpisode(tokens[1].removePrefix("freereels:"), tokens[2])
                    binding.playerProgress.visibility = View.GONE
                    if (res != null && res.streamUrl.isNotEmpty()) {
                        initExoPlayer(res.streamUrl, res.subtitleUrl ?: episode.subtitleUrl)
                    } else {
                        Toast.makeText(this@PlayerActivity, "Lỗi nạp tập kế tiếp", Toast.LENGTH_SHORT).show()
                    }
                }
                return
            }
        }

        if (streamUrl.contains("streamc.xyz") || streamUrl.contains("embed.php")) {
            val cleanM3u8 = "https://huyca.pages.dev/api/nguonc_stream?url=${java.net.URLEncoder.encode(streamUrl, "UTF-8")}"
            initExoPlayer(cleanM3u8, episode.subtitleUrl)
            return
        }

        if (episode.linkM3u8 != null || streamUrl.contains(".m3u8") || streamUrl.contains(".mp4") || streamUrl.contains("gamomephim")) {
            initExoPlayer(streamUrl, episode.subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }
    }

    private fun executeNumberZapping() {
        val numStr = digitBuffer.toString()
        digitBuffer.clear()
        val channelNum = numStr.toIntOrNull() ?: return
        val allChannels = MovieRepository.getAllTvChannels(this)
        if (allChannels.isEmpty()) return

        if (channelNum in 1..allChannels.size) {
            val targetChannel = allChannels[channelNum - 1]
            currentTvChannel = targetChannel
            MovieRepository.setLastWatchedChannelId(this, targetChannel.id)

            sameGroupChannels = MovieRepository.getChannelsInSameGroup(targetChannel.id, this).toMutableList()
            val grpIdx = sameGroupChannels.indexOfFirst { it.id == targetChannel.id }
            currentChannelIndex = if (grpIdx != -1) grpIdx else 0

            binding.txtChannelNumber.text = "KÊNH %02d/%02d".format(channelNum, allChannels.size)
            binding.txtChannelName.text = targetChannel.name
            binding.txtChannelGroup.text = "Nhóm: ${targetChannel.group}"
            binding.layoutChannelBanner.visibility = View.VISIBLE
            hideHandler.removeCallbacks(hideBannerRunnable)
            hideHandler.postDelayed(hideBannerRunnable, 3500)

            binding.txtPlayerTitle.text = "${targetChannel.name} • [${targetChannel.group}]"
            initExoPlayer(targetChannel.url)
            sideAdapter?.updateCurrent(targetChannel.id)
        } else {
            Toast.makeText(this, "Số kênh $channelNum không tồn tại (1 - ${allChannels.size})", Toast.LENGTH_SHORT).show()
        }
    }

    private fun playChannelInGroup(index: Int) {
        if (sameGroupChannels.isEmpty()) return
        val safeIndex = (index + sameGroupChannels.size) % sameGroupChannels.size
        currentChannelIndex = safeIndex
        val channel = sameGroupChannels[safeIndex]
        currentTvChannel = channel
        MovieRepository.setLastWatchedChannelId(this, channel.id)

        binding.txtChannelNumber.text = "KÊNH %02d/%02d".format(safeIndex + 1, sameGroupChannels.size)
        binding.txtChannelName.text = channel.name
        binding.txtChannelGroup.text = "Nhóm: ${channel.group}"
        binding.layoutChannelBanner.visibility = View.VISIBLE
        hideHandler.removeCallbacks(hideBannerRunnable)
        hideHandler.postDelayed(hideBannerRunnable, 3500)

        binding.txtPlayerTitle.text = "${channel.name} • [${channel.group}]"
        initExoPlayer(channel.url)
        sideAdapter?.updateCurrent(channel.id)
    }

    private fun showSideChannelList() {
        if (sameGroupChannels.isEmpty()) return
        binding.layoutSideChannelList.visibility = View.VISIBLE
        val groupName = currentTvChannel?.group ?: "Cùng Nhóm"
        binding.txtSideGroupTitle.text = "KÊNH NHÓM: $groupName"
        binding.txtSideGroupSub.text = "${sameGroupChannels.size} kênh • Bấm OK để chuyển kênh tức thì"

        sideAdapter = QuickChannelTvAdapter(currentTvChannel?.id ?: "") { ch ->
            hideSideChannelList()
            val targetIdx = sameGroupChannels.indexOfFirst { it.id == ch.id }
            if (targetIdx != -1) {
                playChannelInGroup(targetIdx)
            }
        }
        binding.recyclerSideChannels.layoutManager = LinearLayoutManager(this)
        binding.recyclerSideChannels.adapter = sideAdapter
        sideAdapter?.submit(sameGroupChannels)
        binding.recyclerSideChannels.requestFocus()
    }

    private fun hideSideChannelList() {
        binding.layoutSideChannelList.visibility = View.GONE
        binding.playerView.requestFocus()
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun initWebViewPlayer(url: String) {
        player?.pause()
        binding.playerView.visibility = View.GONE
        binding.webViewPlayer.visibility = View.VISIBLE

        val webView = binding.webViewPlayer
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.mediaPlaybackRequiresUserGesture = false
        settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        settings.userAgentString = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

        // CHẶN ĐỨNG 100% CỬA SỔ POPUP QUẢNG CÁO TRÊN ANDROID TV
        settings.setSupportMultipleWindows(false)
        settings.javaScriptCanOpenWindowsAutomatically = false

        webView.webChromeClient = object : WebChromeClient() {
            override fun onCreateWindow(view: WebView?, isDialog: Boolean, isUserGesture: Boolean, resultMsg: android.os.Message?): Boolean {
                // CHẶN HOÀN TOÀN MỌI CỬA SỔ POPUP TRÊN TV
                return false
            }
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val reqUrl = request?.url?.toString() ?: return false
                val isSafeStream = reqUrl.contains("streamc.xyz") || 
                                   reqUrl.contains("amass17.top") || 
                                   reqUrl.contains("hihihoho4.top") ||
                                   reqUrl.contains("jwpcdn.com") ||
                                   reqUrl.contains("jwplayer.com")
                if (!isSafeStream) {
                    // CHẶN ĐỨNG 100% CÁC LINK QUẢNG CÁO, CÁ ĐỘ, SHOPEE, TÀI XỈU, REDIRECT RA NGOÀI APP
                    return true
                }
                return false
            }

            override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? {
                val reqUrl = request?.url?.toString()?.lowercase() ?: return null
                val isAdResource = reqUrl.contains("ads.js") || 
                                   reqUrl.contains("/ads.") || 
                                   reqUrl.contains("adservice") ||
                                   reqUrl.contains("doubleclick") ||
                                   reqUrl.contains("popads") ||
                                   reqUrl.contains("syndication") ||
                                   reqUrl.contains("bet88") ||
                                   reqUrl.contains("casino") ||
                                   reqUrl.contains("shopee") ||
                                   reqUrl.contains("lazada")
                if (isAdResource) {
                    // TRẢ VỀ EMPTY RESPONSE ĐỂ TRIỆT TIÊU TOÀN BỘ SCRIPT QUẢNG CÁO
                    return WebResourceResponse("text/javascript", "UTF-8", ByteArrayInputStream("".toByteArray()))
                }
                return super.shouldInterceptRequest(view, request)
            }

            override fun onPageFinished(view: WebView?, loadedUrl: String?) {
                binding.playerProgress.visibility = View.GONE
                // TIÊM BỘ BẢO VỆ CHỐNG QUẢNG CÁO VÀ TỰ ĐỘNG PHÁT VIDEO TRÊN ANDROID TV
                val antiAdScript = """
                    (function() {
                        window.open = function() { return null; };
                        window.addEventListener('message', function(e) {
                            if (e.data && e.data.type === 'stream-guard-hello') {
                                window.postMessage({
                                    type: 'stream-parent-state',
                                    version: 'guard-5',
                                    id: e.data.id,
                                    helperVersion: 'guard-5',
                                    parentAdblock: 'clear',
                                    seq: Date.now(),
                                    supported: true,
                                    suspected: false
                                }, '*');
                            }
                        });
                        setInterval(function() {
                            try {
                                var ads = document.querySelectorAll('.stream-ads, [id*="ad"], [class*="ad"], iframe[src*="ad"]');
                                ads.forEach(function(el) {
                                    if (el.id !== 'player' && !el.id.includes('stream') && !el.classList.contains('jwplayer')) {
                                        el.remove();
                                    }
                                });
                            } catch(err) {}
                        }, 1000);
                    })();
                """.trimIndent()
                view?.evaluateJavascript(antiAdScript, null)
            }
        }
        webView.loadUrl(url)
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (event.action == KeyEvent.ACTION_DOWN) {
            val keyCode = event.keyCode
            android.util.Log.d("TV_ZAP", "dispatchKeyEvent: code=$keyCode, isTvMode=$isTvMode, sideVis=${binding.layoutSideChannelList.visibility}")
            showOverlays()
            scheduleHideOverlays()

            // Xử lý khi Side Channel List đang hiển thị
            if (binding.layoutSideChannelList.visibility == View.VISIBLE) {
                when (keyCode) {
                    KeyEvent.KEYCODE_BACK, KeyEvent.KEYCODE_DPAD_RIGHT -> {
                        hideSideChannelList()
                        return true
                    }
                }
            } else {
                when (keyCode) {
                    KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_CHANNEL_UP, KeyEvent.KEYCODE_MEDIA_NEXT, KeyEvent.KEYCODE_BUTTON_R1 -> {
                        if (isTvMode) {
                            playChannelInGroup(currentChannelIndex + 1)
                        } else {
                            if (currentEpisodeIndex > 0) {
                                autoNextTimer?.cancel()
                                binding.layoutNextEpCountdown.visibility = View.GONE
                                playEpisodeAtIndex(currentEpisodeIndex - 1)
                            }
                        }
                        return true
                    }
                    KeyEvent.KEYCODE_DPAD_DOWN, KeyEvent.KEYCODE_CHANNEL_DOWN, KeyEvent.KEYCODE_MEDIA_PREVIOUS, KeyEvent.KEYCODE_BUTTON_L1 -> {
                        if (isTvMode) {
                            playChannelInGroup(currentChannelIndex - 1)
                        } else {
                            if (currentEpisodeIndex + 1 < episodesList.size) {
                                autoNextTimer?.cancel()
                                binding.layoutNextEpCountdown.visibility = View.GONE
                                playEpisodeAtIndex(currentEpisodeIndex + 1)
                            }
                        }
                        return true
                    }
                    KeyEvent.KEYCODE_DPAD_LEFT, KeyEvent.KEYCODE_MENU -> {
                        if (isTvMode) {
                            showSideChannelList()
                        } else {
                            player?.let { p ->
                                val newPos = (p.currentPosition - 10000).coerceAtLeast(0)
                                p.seekTo(newPos)
                            }
                        }
                        return true
                    }
                    KeyEvent.KEYCODE_0, KeyEvent.KEYCODE_1, KeyEvent.KEYCODE_2, KeyEvent.KEYCODE_3,
                    KeyEvent.KEYCODE_4, KeyEvent.KEYCODE_5, KeyEvent.KEYCODE_6, KeyEvent.KEYCODE_7,
                    KeyEvent.KEYCODE_8, KeyEvent.KEYCODE_9 -> {
                        if (isTvMode) {
                            val digit = keyCode - KeyEvent.KEYCODE_0
                            digitBuffer.append(digit)
                            val allCount = MovieRepository.getAllTvChannels(this).size
                            binding.txtChannelNumber.text = "BẤM SỐ CHỌN KÊNH"
                            binding.txtChannelName.text = "🔢 Kênh số: $digitBuffer"
                            binding.txtChannelGroup.text = "Chuyển đến kênh $digitBuffer... (Tổng: $allCount kênh)"
                            binding.layoutChannelBanner.visibility = View.VISIBLE

                            zapHandler.removeCallbacks(zapRunnable)
                            zapHandler.postDelayed(zapRunnable, 1400)
                        }
                        return true
                    }
                    KeyEvent.KEYCODE_DPAD_RIGHT -> {
                        player?.let { p ->
                            val newPos = (p.currentPosition + 10000).coerceAtMost(p.duration)
                            p.seekTo(newPos)
                        }
                        return true
                    }
                    KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER -> {
                        if (digitBuffer.isNotEmpty()) {
                            zapHandler.removeCallbacks(zapRunnable)
                            executeNumberZapping()
                            return true
                        }
                        if (binding.layoutNextEpCountdown.visibility == View.VISIBLE) {
                            autoNextTimer?.cancel()
                            binding.layoutNextEpCountdown.visibility = View.GONE
                            playEpisodeAtIndex(currentEpisodeIndex + 1)
                            return true
                        }
                        player?.let { p ->
                            if (p.isPlaying) {
                                p.pause()
                            } else {
                                if (p.playbackState == Player.STATE_ENDED) {
                                    p.seekTo(0L)
                                }
                                p.play()
                            }
                        }
                        return true
                    }
                }
            }
        }
        return super.dispatchKeyEvent(event)
    }

    private fun showOverlays() {
        binding.layoutWatermark.visibility = View.VISIBLE
        binding.txtRemoteTips.visibility = View.VISIBLE
    }

    private fun hideOverlays() {
        binding.layoutWatermark.visibility = View.GONE
        binding.txtRemoteTips.visibility = View.GONE
    }

    private fun scheduleHideOverlays() {
        hideHandler.removeCallbacks(hideOverlayRunnable)
        hideHandler.postDelayed(hideOverlayRunnable, 4000)
    }

    private fun hideSystemUI() {
        val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
        windowInsetsController.systemBarsBehavior =
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        windowInsetsController.hide(WindowInsetsCompat.Type.systemBars())
    }

    private fun updateFavPlayerButton() {
        if (isTvMode && currentTvChannel != null) {
            val isFav = MovieRepository.isChannelFavorite(this, currentTvChannel!!.id)
            binding.btnToggleFavPlayer.text = if (isFav) "⭐ Đã Thích (Kênh)" else "☆ Thêm Kênh Yêu Thích"
            binding.btnToggleFavPlayer.setTextColor(if (isFav) android.graphics.Color.parseColor("#FFD700") else android.graphics.Color.WHITE)
        } else {
            val movie = intent.getSerializableExtra("EXTRA_MOVIE_ITEM") as? MovieItem
            if (movie != null) {
                val isFav = FavoriteMovieManager.isFavorite(this, movie.slug)
                binding.btnToggleFavPlayer.text = if (isFav) "❤️ Đã Thích" else "🤍 Thêm Yêu Thích"
                binding.btnToggleFavPlayer.setTextColor(if (isFav) android.graphics.Color.parseColor("#FFD700") else android.graphics.Color.WHITE)
            } else {
                binding.btnToggleFavPlayer.visibility = View.GONE
            }
        }
    }

    private fun toggleCurrentFavorite() {
        if (isTvMode && currentTvChannel != null) {
            val isFav = MovieRepository.toggleChannelFavorite(this, currentTvChannel!!.id)
            updateFavPlayerButton()
            val msg = if (isFav) "⭐ Đã thêm [${currentTvChannel!!.name}] vào Kênh Yêu Thích" else "Đã bỏ khỏi Kênh Yêu Thích"
            Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
        } else {
            val movie = intent.getSerializableExtra("EXTRA_MOVIE_ITEM") as? MovieItem
            if (movie != null) {
                val isFav = FavoriteMovieManager.toggleFavorite(this, movie)
                updateFavPlayerButton()
                val msg = if (isFav) "❤️ Đã thêm [${movie.name}] vào Phim Yêu Thích" else "Đã bỏ khỏi Phim Yêu Thích"
                Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun savePlaybackHistory() {
        val movie = intent.getSerializableExtra("EXTRA_MOVIE_ITEM") as? MovieItem
        if (movie != null) {
            val epName = if (isTvMode) {
                currentTvChannel?.group ?: ""
            } else {
                episodesList.getOrNull(currentEpisodeIndex)?.name ?: intent.getStringExtra("EXTRA_EPISODE") ?: ""
            }
            val pos = player?.currentPosition ?: 0L
            val dur = player?.duration ?: 0L
            WatchHistoryManager.saveHistory(
                context = this,
                movie = movie,
                episodeName = epName,
                positionMs = pos,
                durationMs = dur
            )
        }
    }

    override fun onPause() {
        super.onPause()
        savePlaybackHistory()
    }

    override fun onStop() {
        super.onStop()
        savePlaybackHistory()
        player?.pause()
    }

    override fun onDestroy() {
        savePlaybackHistory()
        super.onDestroy()
        historySyncHandler.removeCallbacks(historySyncRunnable)
        hideHandler.removeCallbacks(hideOverlayRunnable)
        hideHandler.removeCallbacks(hideBannerRunnable)
        zapHandler.removeCallbacks(zapRunnable)
        autoNextTimer?.cancel()
        loudnessEnhancer?.release()
        loudnessEnhancer = null
        player?.release()
        player = null
        binding.webViewPlayer.destroy()
    }
}

class QuickChannelTvAdapter(
    private var currentId: String,
    private val onChannelClick: (TvChannelItem) -> Unit
) : RecyclerView.Adapter<QuickChannelTvAdapter.VH>() {
    private var channels = listOf<TvChannelItem>()
    fun submit(list: List<TvChannelItem>) {
        channels = list
        notifyDataSetChanged()
    }
    fun updateCurrent(newId: String) {
        currentId = newId
        notifyDataSetChanged()
    }
    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val imgLogo: ImageView = v.findViewById(R.id.imgQuickChannelLogo)
        val txtName: TextView = v.findViewById(R.id.txtQuickChannelName)
        val txtGroup: TextView = v.findViewById(R.id.txtQuickChannelGroup)
        val txtBadge: TextView = v.findViewById(R.id.txtQuickStatusBadge)
    }
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_quick_channel, parent, false)
        v.isFocusable = true
        TvFocusUtil.setupFocusScale(v)
        return VH(v)
    }
    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = channels[position]
        holder.txtName.text = item.name
        holder.txtGroup.text = "Nhóm: ${item.group}"
        val isCurrent = item.id == currentId || item.url == currentId
        holder.txtBadge.visibility = if (isCurrent) View.VISIBLE else View.GONE
        if (isCurrent) {
            holder.itemView.setBackgroundResource(R.drawable.bg_focus_card)
        } else {
            holder.itemView.setBackgroundResource(R.drawable.bg_btn_secondary)
        }
        val defaultTvLogo = "file:///android_asset/logos/vtv1.png"
        Glide.with(holder.itemView.context)
            .load(if (!item.logo.isNullOrEmpty()) item.logo else defaultTvLogo)
            .placeholder(R.drawable.bg_focus_card)
            .error(R.drawable.bg_btn_secondary)
            .into(holder.imgLogo)
        holder.itemView.setOnClickListener { onChannelClick(item) }
        holder.itemView.setOnKeyListener { _, keyCode, event ->
            if (event.action == KeyEvent.ACTION_DOWN && (keyCode == KeyEvent.KEYCODE_DPAD_CENTER || keyCode == KeyEvent.KEYCODE_ENTER)) {
                onChannelClick(item)
                true
            } else false
        }
    }
    override fun getItemCount() = channels.size
}
