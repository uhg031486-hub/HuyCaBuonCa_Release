package com.huycabuonca.mobile.ui

import android.annotation.SuppressLint
import android.graphics.Color
import android.os.Bundle
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
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.hls.HlsMediaSource
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.huycabuonca.mobile.R
import com.huycabuonca.mobile.api.MovieRepository
import com.huycabuonca.mobile.api.MovieRepository.toMovieItem
import com.huycabuonca.mobile.api.TvChannelItem
import com.huycabuonca.mobile.ui.adapter.QuickChannelAdapter
import com.huycabuonca.mobile.databinding.ActivityPlayerBinding
import com.huycabuonca.mobile.model.MovieItem
import com.huycabuonca.mobile.model.MovieSource
import com.huycabuonca.mobile.util.FavoriteMovieManager
import com.huycabuonca.mobile.util.WatchHistoryManager

class PlayerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPlayerBinding
    private var player: ExoPlayer? = null
    private val hideHandler = Handler(Looper.getMainLooper())
    private val hideOverlayRunnable = Runnable { hideOverlays() }
    private val hideBannerRunnable = Runnable { binding.layoutChannelBanner.visibility = View.GONE }

    // Quản lý kênh truyền hình TV (FPT Play / MyTV Style)
    private var isTvMode = false
    private var allTvChannels: List<TvChannelItem> = emptyList()
    private var displayedChannels: List<TvChannelItem> = emptyList()
    private var currentTvChannel: TvChannelItem? = null
    private var currentChannelIndex: Int = 0
    private var selectedGroup: String = "Tất cả"
    private var channelAdapter: QuickChannelAdapter? = null

    // Quản lý phim thông thường
    private var currentMovie: MovieItem? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPlayerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        hideSystemUI()
        MovieRepository.initTvChannels(this)

        val streamUrl = intent.getStringExtra("EXTRA_STREAM_URL") ?: ""
        val subtitleUrl = intent.getStringExtra("EXTRA_SUBTITLE_URL")
        val isM3u8 = intent.getBooleanExtra("EXTRA_IS_M3U8", true) || streamUrl.contains(".m3u8")
        val title = intent.getStringExtra("EXTRA_TITLE") ?: ""
        val episode = intent.getStringExtra("EXTRA_EPISODE") ?: ""
        val channelId = intent.getStringExtra("EXTRA_CHANNEL_ID") ?: ""
        val source = intent.getStringExtra("EXTRA_SOURCE") ?: ""
        currentMovie = intent.getSerializableExtra("EXTRA_MOVIE_ITEM") as? MovieItem

        // Kiểm tra xem có phải kênh TV không
        allTvChannels = MovieRepository.getAllTvChannels(this)
        val matchedChannel = allTvChannels.find {
            (channelId.isNotEmpty() && it.id == channelId) ||
            it.url == streamUrl ||
            it.name.equals(title, ignoreCase = true)
        }

        isTvMode = matchedChannel != null || source == MovieSource.XEMTIVI.name

        binding.btnPlayerBack.setOnClickListener {
            if (binding.layoutSideChannelList.visibility == View.VISIBLE) {
                hideSideChannelList()
            } else {
                finish()
            }
        }

        binding.touchOverlay.setOnClickListener {
            toggleOverlays()
        }

        binding.btnPlayPause.setOnClickListener {
            togglePlayPause()
        }

        if (isTvMode) {
            setupTvMode(matchedChannel, streamUrl, title, episode)
        } else {
            setupMovieMode(streamUrl, isM3u8, title, episode, subtitleUrl)
        }

        updateFavIcon()
        binding.btnPlayerFav.setOnClickListener {
            toggleFavorite()
        }

        scheduleHideOverlays()
    }

    private fun setupTvMode(initialChannel: TvChannelItem?, streamUrl: String, title: String, episode: String) {
        binding.btnOpenChannelList.visibility = View.VISIBLE
        binding.btnPrevChannel.visibility = View.VISIBLE
        binding.btnNextChannel.visibility = View.VISIBLE

        currentTvChannel = initialChannel ?: allTvChannels.firstOrNull { it.url == streamUrl } ?: allTvChannels.firstOrNull()
        displayedChannels = allTvChannels

        val foundIdx = displayedChannels.indexOfFirst { it.id == currentTvChannel?.id }
        currentChannelIndex = if (foundIdx != -1) foundIdx else 0

        // Khởi tạo Drawer danh sách kênh trượt cạnh phải (FPT Play / MyTV Style)
        setupSideChannelDrawer()

        binding.btnOpenChannelList.setOnClickListener {
            if (binding.layoutSideChannelList.visibility == View.VISIBLE) {
                hideSideChannelList()
            } else {
                showSideChannelList()
            }
        }

        binding.btnSideClose.setOnClickListener {
            hideSideChannelList()
        }

        binding.btnNextChannel.setOnClickListener {
            playNextChannel()
        }

        binding.btnPrevChannel.setOnClickListener {
            playPrevChannel()
        }

        // Phát kênh
        currentTvChannel?.let {
            playTvChannel(it)
        } ?: run {
            if (streamUrl.isNotEmpty()) initExoPlayer(streamUrl)
        }
    }

    private fun setupMovieMode(streamUrl: String, isM3u8: Boolean, title: String, episode: String, subtitleUrl: String? = null) {
        binding.btnOpenChannelList.visibility = View.GONE
        binding.btnPrevChannel.visibility = View.GONE
        binding.btnNextChannel.visibility = View.GONE

        binding.txtPlayerTitle.text = if (episode.isNotEmpty()) "$title - $episode" else title

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
                return
            }
        }

        if (streamUrl.contains("streamc.xyz") || streamUrl.contains("embed.php")) {
            val cleanM3u8 = "https://huyca.pages.dev/api/nguonc_stream?url=${java.net.URLEncoder.encode(streamUrl, "UTF-8")}"
            initExoPlayer(cleanM3u8, subtitleUrl)
            return
        }

        val isExo = isM3u8 || streamUrl.contains(".m3u8", ignoreCase = true) || streamUrl.contains(".mp4", ignoreCase = true) || streamUrl.contains("gamomephim")
        if (isExo) {
            initExoPlayer(streamUrl, subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }
    }

    private fun playTvChannel(channel: TvChannelItem) {
        currentTvChannel = channel
        val idx = displayedChannels.indexOfFirst { it.id == channel.id }
        if (idx != -1) currentChannelIndex = idx

        MovieRepository.setLastWatchedChannelId(this, channel.id)
        val movie = channel.toMovieItem()
        WatchHistoryManager.saveHistory(this, movie, channel.group)

        binding.txtPlayerTitle.text = "${channel.name} • ${channel.group}"
        updateFavIcon()

        // Hiển thị OSD Channel Banner (FPT Play / MyTV Style)
        showChannelBanner(channel)

        // Cập nhật vị trí đang phát trong Drawer
        channelAdapter?.updateCurrent(channel.id)

        if (channel.url.isNotEmpty()) {
            initExoPlayer(channel.url)
        } else {
            Toast.makeText(this, "Không có luồng phát của kênh này", Toast.LENGTH_SHORT).show()
        }
    }

    private fun playNextChannel() {
        if (displayedChannels.isEmpty()) return
        val nextIdx = (currentChannelIndex + 1) % displayedChannels.size
        currentChannelIndex = nextIdx
        playTvChannel(displayedChannels[nextIdx])
    }

    private fun playPrevChannel() {
        if (displayedChannels.isEmpty()) return
        val prevIdx = (currentChannelIndex - 1 + displayedChannels.size) % displayedChannels.size
        currentChannelIndex = prevIdx
        playTvChannel(displayedChannels[prevIdx])
    }

    private fun showChannelBanner(channel: TvChannelItem) {
        val allIdx = allTvChannels.indexOfFirst { it.id == channel.id }
        val total = allTvChannels.size.coerceAtLeast(1)
        val numText = if (allIdx != -1) "KÊNH %02d/%02d".format(allIdx + 1, total) else "KÊNH TV"
        binding.txtChannelNumber.text = numText
        binding.txtChannelName.text = channel.name
        binding.txtChannelGroup.text = "Nhóm: ${channel.group}"

        val defaultTvLogo = "file:///android_asset/logos/vtv1.png"
        Glide.with(this)
            .load(if (!channel.logo.isNullOrEmpty()) channel.logo else defaultTvLogo)
            .placeholder(R.drawable.bg_btn_secondary)
            .error(R.drawable.tv_banner)
            .into(binding.imgChannelBannerLogo)

        binding.layoutChannelBanner.visibility = View.VISIBLE
        hideHandler.removeCallbacks(hideBannerRunnable)
        hideHandler.postDelayed(hideBannerRunnable, 3500)
    }

    private fun setupSideChannelDrawer() {
        // 1. Tạo danh sách các nhóm kênh
        val groups = mutableListOf("Tất cả")
        allTvChannels.forEach { ch ->
            if (ch.group.isNotEmpty() && !groups.contains(ch.group)) {
                groups.add(ch.group)
            }
        }

        binding.layoutGroupTabs.removeAllViews()
        groups.forEach { groupName ->
            val tabView = TextView(this).apply {
                text = groupName
                textSize = 12f
                setPadding(
                    (12 * resources.displayMetrics.density).toInt(),
                    (6 * resources.displayMetrics.density).toInt(),
                    (12 * resources.displayMetrics.density).toInt(),
                    (6 * resources.displayMetrics.density).toInt()
                )
                val lp = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply {
                    marginEnd = (6 * resources.displayMetrics.density).toInt()
                }
                layoutParams = lp
                updateTabStyle(this, groupName == selectedGroup)

                setOnClickListener {
                    selectedGroup = groupName
                    for (i in 0 until binding.layoutGroupTabs.childCount) {
                        val child = binding.layoutGroupTabs.getChildAt(i) as? TextView
                        child?.let { updateTabStyle(it, it.text.toString() == selectedGroup) }
                    }
                    filterChannels(groupName)
                }
            }
            binding.layoutGroupTabs.addView(tabView)
        }

        // 2. Khởi tạo RecyclerView danh sách kênh
        binding.recyclerSideChannels.layoutManager = LinearLayoutManager(this)
        channelAdapter = QuickChannelAdapter(currentTvChannel?.id ?: "") { ch ->
            playTvChannel(ch)
            hideSideChannelList()
        }
        binding.recyclerSideChannels.adapter = channelAdapter
        channelAdapter?.submit(displayedChannels)
    }

    private fun updateTabStyle(tv: TextView, isSelected: Boolean) {
        if (isSelected) {
            tv.setBackgroundResource(R.drawable.bg_focus_card)
            tv.setTextColor(Color.parseColor("#FFD700"))
            tv.setTypeface(null, android.graphics.Typeface.BOLD)
        } else {
            tv.setBackgroundResource(R.drawable.bg_btn_secondary)
            tv.setTextColor(Color.WHITE)
            tv.setTypeface(null, android.graphics.Typeface.NORMAL)
        }
    }

    private fun filterChannels(groupName: String) {
        displayedChannels = if (groupName == "Tất cả") {
            allTvChannels
        } else {
            allTvChannels.filter { it.group.equals(groupName, ignoreCase = true) }
        }
        channelAdapter?.submit(displayedChannels)
        val idx = displayedChannels.indexOfFirst { it.id == currentTvChannel?.id }
        if (idx != -1) {
            currentChannelIndex = idx
            binding.recyclerSideChannels.scrollToPosition(idx)
        } else {
            currentChannelIndex = 0
            binding.recyclerSideChannels.scrollToPosition(0)
        }
    }

    private fun showSideChannelList() {
        binding.layoutSideChannelList.visibility = View.VISIBLE
        val curIdx = displayedChannels.indexOfFirst { it.id == currentTvChannel?.id }
        if (curIdx != -1) {
            binding.recyclerSideChannels.scrollToPosition(curIdx)
        }
        hideHandler.removeCallbacks(hideOverlayRunnable)
    }

    private fun hideSideChannelList() {
        binding.layoutSideChannelList.visibility = View.GONE
        scheduleHideOverlays()
    }

    private fun updateFavIcon() {
        val isFav = if (isTvMode && currentTvChannel != null) {
            MovieRepository.isChannelFavorite(this, currentTvChannel!!.id)
        } else if (currentMovie != null) {
            FavoriteMovieManager.isFavorite(this, currentMovie!!.slug)
        } else false
        binding.btnPlayerFav.setColorFilter(if (isFav) Color.parseColor("#FFD700") else Color.WHITE)
    }

    private fun toggleFavorite() {
        if (isTvMode && currentTvChannel != null) {
            val isFav = MovieRepository.toggleChannelFavorite(this, currentTvChannel!!.id)
            updateFavIcon()
            Toast.makeText(this, if (isFav) "⭐ Đã thêm vào Kênh Yêu Thích" else "Đã bỏ khỏi Kênh Yêu Thích", Toast.LENGTH_SHORT).show()
        } else if (currentMovie != null) {
            val isFav = FavoriteMovieManager.toggleFavorite(this, currentMovie!!)
            updateFavIcon()
            Toast.makeText(this, if (isFav) "❤️ Đã thêm vào Phim Yêu Thích" else "Đã bỏ khỏi Phim Yêu Thích", Toast.LENGTH_SHORT).show()
        }
    }

    private fun togglePlayPause() {
        player?.let { p ->
            if (p.isPlaying) {
                p.pause()
                binding.btnPlayPause.setImageResource(R.drawable.ic_play)
            } else {
                p.play()
                binding.btnPlayPause.setImageResource(R.drawable.ic_pause)
            }
        }
        showOverlays()
        scheduleHideOverlays()
    }

    private fun toggleOverlays() {
        if (binding.layoutSideChannelList.visibility == View.VISIBLE) {
            hideSideChannelList()
            return
        }
        if (binding.layoutWatermark.visibility == View.VISIBLE) {
            hideOverlays()
        } else {
            showOverlays()
            scheduleHideOverlays()
        }
    }

    private fun showOverlays() {
        binding.layoutWatermark.visibility = View.VISIBLE
        binding.layoutCenterControls.visibility = View.VISIBLE
        player?.let { p ->
            binding.btnPlayPause.setImageResource(if (p.isPlaying) R.drawable.ic_pause else R.drawable.ic_play)
        }
    }

    private fun hideOverlays() {
        if (binding.layoutSideChannelList.visibility == View.VISIBLE) return
        binding.layoutWatermark.visibility = View.GONE
        binding.layoutCenterControls.visibility = View.GONE
    }

    private fun scheduleHideOverlays() {
        hideHandler.removeCallbacks(hideOverlayRunnable)
        hideHandler.postDelayed(hideOverlayRunnable, 4000)
    }

    private fun initExoPlayer(url: String, subtitleUrl: String? = null) {
        binding.playerView.visibility = View.VISIBLE
        binding.webViewPlayer.visibility = View.GONE
        binding.playerProgress.visibility = View.VISIBLE

        player?.release()

        val reqHeaders = mutableMapOf<String, String>()
        if (url.contains("phimapi.com") || url.contains("phimimg.com") || url.contains("phim1280.tv")) {
            reqHeaders["Referer"] = "https://player.phimapi.com/"
            reqHeaders["Origin"] = "https://player.phimapi.com"
        } else if (url.contains("huyca.pages.dev") || url.contains("nguonc_stream")) {
            reqHeaders["Referer"] = "https://huyca.pages.dev/"
            reqHeaders["Origin"] = "https://huyca.pages.dev"
        }
        val dataSourceFactory = DefaultHttpDataSource.Factory()
            .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
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
            HlsMediaSource.Factory(dataSourceFactory)
                .setPlaylistParserFactory(com.huycabuonca.mobile.util.AdBlockPlaylistParserFactory())
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

        player = ExoPlayer.Builder(this).setTrackSelector(trackSelector).build().apply {
            setMediaSource(mediaSource)
            prepare()
            playWhenReady = true
            addListener(object : Player.Listener {
                override fun onPlaybackStateChanged(playbackState: Int) {
                    if (playbackState == Player.STATE_BUFFERING) {
                        binding.playerProgress.visibility = View.VISIBLE
                    } else {
                        binding.playerProgress.visibility = View.GONE
                        binding.btnPlayPause.setImageResource(if (isPlaying) R.drawable.ic_pause else R.drawable.ic_play)
                    }
                }

                override fun onIsPlayingChanged(isPlaying: Boolean) {
                    binding.btnPlayPause.setImageResource(if (isPlaying) R.drawable.ic_pause else R.drawable.ic_play)
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
            setFractionalTextSize(0.052f)
        }
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
        settings.userAgentString = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        webView.webChromeClient = WebChromeClient()
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                binding.playerProgress.visibility = View.GONE
            }
        }
        webView.loadUrl(url)
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        showOverlays()
        scheduleHideOverlays()

        if (binding.layoutSideChannelList.visibility == View.VISIBLE) {
            if (keyCode == KeyEvent.KEYCODE_BACK || keyCode == KeyEvent.KEYCODE_DPAD_RIGHT) {
                hideSideChannelList()
                return true
            }
        }

        when (keyCode) {
            KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_CHANNEL_UP, KeyEvent.KEYCODE_MEDIA_NEXT -> {
                if (isTvMode) {
                    playNextChannel()
                    return true
                }
            }
            KeyEvent.KEYCODE_DPAD_DOWN, KeyEvent.KEYCODE_CHANNEL_DOWN, KeyEvent.KEYCODE_MEDIA_PREVIOUS -> {
                if (isTvMode) {
                    playPrevChannel()
                    return true
                }
            }
            KeyEvent.KEYCODE_DPAD_LEFT, KeyEvent.KEYCODE_MENU -> {
                if (isTvMode) {
                    showSideChannelList()
                    return true
                }
            }
            KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER -> {
                togglePlayPause()
                return true
            }
        }

        player?.let { p ->
            when (keyCode) {
                KeyEvent.KEYCODE_DPAD_LEFT -> {
                    val newPos = (p.currentPosition - 10000).coerceAtLeast(0)
                    p.seekTo(newPos)
                    return true
                }
                KeyEvent.KEYCODE_DPAD_RIGHT -> {
                    val newPos = (p.currentPosition + 10000).coerceAtMost(p.duration)
                    p.seekTo(newPos)
                    return true
                }
                else -> {}
            }
        }
        return super.onKeyDown(keyCode, event)
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (binding.layoutSideChannelList.visibility == View.VISIBLE) {
            hideSideChannelList()
            return
        }
        super.onBackPressed()
    }

    private fun hideSystemUI() {
        val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
        windowInsetsController.systemBarsBehavior =
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        windowInsetsController.hide(WindowInsetsCompat.Type.systemBars())
    }

    private fun savePlaybackHistory() {
        val movie = currentMovie ?: currentTvChannel?.toMovieItem()
        if (movie != null) {
            val ep = intent.getStringExtra("EXTRA_EPISODE") ?: currentTvChannel?.group ?: ""
            val pos = player?.currentPosition ?: 0L
            val dur = player?.duration ?: 0L
            WatchHistoryManager.saveHistory(
                context = this,
                movie = movie,
                episodeName = ep,
                positionMs = pos,
                durationMs = dur
            )
        }
    }

    override fun onStop() {
        super.onStop()
        savePlaybackHistory()
        player?.pause()
    }

    override fun onDestroy() {
        savePlaybackHistory()
        super.onDestroy()
        hideHandler.removeCallbacks(hideOverlayRunnable)
        hideHandler.removeCallbacks(hideBannerRunnable)
        player?.release()
        player = null
        binding.webViewPlayer.destroy()
    }
}
