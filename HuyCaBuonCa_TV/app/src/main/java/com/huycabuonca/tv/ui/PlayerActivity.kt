package com.huycabuonca.tv.ui

import android.annotation.SuppressLint
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
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
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
import com.huycabuonca.tv.R
import com.huycabuonca.tv.api.MovieRepository
import com.huycabuonca.tv.api.TvChannelItem
import com.huycabuonca.tv.databinding.ActivityPlayerBinding
import com.huycabuonca.tv.model.MovieSource
import com.huycabuonca.tv.util.TvFocusUtil

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
        } else {
            android.util.Log.d("TV_ZAP", "Movie Mode (not TV): title=$title, url=$streamUrl")
        }

        val subtitleUrl = intent.getStringExtra("EXTRA_SUBTITLE_URL")

        if (isM3u8) {
            initExoPlayer(streamUrl, subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
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

        val dataSourceFactory = DefaultHttpDataSource.Factory()
            .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
            .setDefaultRequestProperties(mapOf(
                "Referer" to "https://player.phimapi.com/",
                "Origin" to "https://player.phimapi.com"
            ))
            .setAllowCrossProtocolRedirects(true)

        val mediaItemBuilder = MediaItem.Builder().setUri(url)

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
        val mediaSource = HlsMediaSource.Factory(dataSourceFactory)
            .createMediaSource(mediaItem)

        val trackSelector = androidx.media3.exoplayer.trackselection.DefaultTrackSelector(this).apply {
            setParameters(
                buildUponParameters()
                    .setPreferredTextLanguage("vi")
                    .setSelectUndeterminedTextLanguage(true)
            )
        }

        player = ExoPlayer.Builder(this)
            .setTrackSelector(trackSelector)
            .build().apply {
            setMediaSource(mediaSource)
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
                        // Tự nhận diện video dọc: Giữ đúng tỷ lệ 9:16 ở giữa màn hình TV, không bị kéo dãn méo
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
                }
            })
        }
        binding.playerView.player = player
    }

    private fun playChannelInGroup(index: Int) {
        if (sameGroupChannels.isEmpty()) return
        val safeIndex = (index + sameGroupChannels.size) % sameGroupChannels.size
        currentChannelIndex = safeIndex
        val channel = sameGroupChannels[safeIndex]
        currentTvChannel = channel

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
        settings.userAgentString = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        webView.webChromeClient = WebChromeClient()
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                binding.playerProgress.visibility = View.GONE
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
                    KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_CHANNEL_UP -> {
                        if (isTvMode) {
                            playChannelInGroup(currentChannelIndex + 1)
                            return true
                        }
                    }
                    KeyEvent.KEYCODE_DPAD_DOWN, KeyEvent.KEYCODE_CHANNEL_DOWN -> {
                        if (isTvMode) {
                            playChannelInGroup(currentChannelIndex - 1)
                            return true
                        }
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
                        val num = keyCode - KeyEvent.KEYCODE_0
                        val targetIdx = (num - 1).coerceAtLeast(0)
                        if (isTvMode) {
                            playChannelInGroup(targetIdx)
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

    override fun onStop() {
        super.onStop()
        player?.pause()
    }

    override fun onDestroy() {
        super.onDestroy()
        hideHandler.removeCallbacks(hideOverlayRunnable)
        hideHandler.removeCallbacks(hideBannerRunnable)
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
        val defaultTvLogo = "https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png"
        Glide.with(holder.itemView.context)
            .load(item.logo.ifEmpty { defaultTvLogo })
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
