package com.huycabuonca.mobile.ui

import android.annotation.SuppressLint
import android.content.pm.ActivityInfo
import android.content.res.Configuration
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.LinearLayout
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
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.hls.HlsMediaSource
import androidx.recyclerview.widget.GridLayoutManager
import com.huycabuonca.mobile.R
import com.huycabuonca.mobile.api.MovieRepository
import com.huycabuonca.mobile.databinding.ActivityDetailBinding
import com.huycabuonca.mobile.model.EpisodeItem
import com.huycabuonca.mobile.model.MovieDetail
import com.huycabuonca.mobile.model.MovieItem
import com.huycabuonca.mobile.model.ServerGroup
import com.huycabuonca.mobile.ui.adapter.EpisodeAdapter
import com.huycabuonca.mobile.util.PlayerGestureHelper
import kotlinx.coroutines.launch

class DetailActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDetailBinding
    private lateinit var episodeAdapter: EpisodeAdapter
    private var movieItem: MovieItem? = null
    private var movieDetail: MovieDetail? = null
    private var player: ExoPlayer? = null

    private var currentServerIndex = 0
    private var currentEpisodeIndex = 0
    private val currentEpisodes = mutableListOf<EpisodeItem>()
    private var areControlsVisible = true
    private lateinit var gestureHelper: PlayerGestureHelper
    private var isScreenLocked = false
    private var autoNextEpisode = true
    private var pipOnHome = true
    private val speeds = listOf(1.0f, 1.25f, 1.5f, 2.0f, 0.75f)
    private var currentSpeedIndex = 0
    private var currentResizeModeIndex = 0
    private val resizeModes = listOf(
        androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FIT to "Vừa màn hình (16:9)",
        androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_ZOOM to "Tràn viền (Cắt viền đen)",
        androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FILL to "Kéo giãn toàn màn hình"
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        binding = ActivityDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

        movieItem = intent.getSerializableExtra("EXTRA_MOVIE") as? MovieItem
        if (movieItem == null) {
            finish()
            return
        }

        setupUI()
        loadDetail()
    }

    private fun setupUI() {
        binding.btnPlayerBack.setOnClickListener {
            if (resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE) {
                requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
            } else {
                finish()
            }
        }

        binding.btnFullscreen.setOnClickListener {
            toggleFullscreen()
        }

        // Cài đặt chuẩn vBook
        binding.btnSettings.setOnClickListener {
            showVBookSettingsDialog()
        }

        // 1. PiP / Xem trong nền (vBook style)
        binding.btnPip.setOnClickListener {
            enterPipMode()
        }

        // 2. Tốc độ phát (Speed)
        binding.btnSpeed.setOnClickListener {
            currentSpeedIndex = (currentSpeedIndex + 1) % speeds.size
            val speed = speeds[currentSpeedIndex]
            player?.setPlaybackSpeed(speed)
            binding.btnSpeed.text = "${speed}x"
            Toast.makeText(this, "Tốc độ phát: ${speed}x", Toast.LENGTH_SHORT).show()
        }

        // 3. Tỷ lệ khung hình (Aspect Ratio / Resize Mode)
        binding.btnAspectRatio.setOnClickListener {
            currentResizeModeIndex = (currentResizeModeIndex + 1) % resizeModes.size
            val (mode, label) = resizeModes[currentResizeModeIndex]
            binding.playerView.resizeMode = mode
            Toast.makeText(this, "Khung hình: $label", Toast.LENGTH_SHORT).show()
        }

        // 4. Khóa cảm ứng màn hình (Lock screen)
        binding.btnLock.setOnClickListener {
            setScreenLock(true)
        }

        binding.btnUnlock.setOnClickListener {
            setScreenLock(false)
        }

        // 5. Cử chỉ vuốt vBook (Swipe Âm lượng/Độ sáng, Double-tap tua ±10s)
        gestureHelper = PlayerGestureHelper(
            activity = this,
            touchView = binding.gestureTouchView,
            overlayLayout = binding.layoutGestureOverlay,
            iconView = binding.imgGestureIcon,
            infoView = binding.txtGestureInfo,
            playerGetter = { player },
            onSingleTap = {
                if (!isScreenLocked) {
                    toggleControlsVisibility()
                }
            }
        )

        val movie = movieItem!!
        binding.txtDetailTitle.text = movie.name
        binding.txtDetailMeta.text = "Nguồn: ${movie.source.displayName} • ${movie.year}"

        episodeAdapter = EpisodeAdapter { episode ->
            val idx = currentEpisodes.indexOf(episode)
            if (idx != -1) {
                currentEpisodeIndex = idx
            }
            playEpisode(episode)
        }

        binding.recyclerEpisodes.layoutManager = GridLayoutManager(this, 4)
        binding.recyclerEpisodes.adapter = episodeAdapter

        binding.btnPrevEpisode.setOnClickListener {
            if (currentEpisodeIndex > 0) {
                currentEpisodeIndex--
                playEpisode(currentEpisodes[currentEpisodeIndex])
            } else {
                Toast.makeText(this, "Đây là tập đầu tiên!", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnNextEpisode.setOnClickListener {
            if (currentEpisodeIndex < currentEpisodes.size - 1) {
                currentEpisodeIndex++
                playEpisode(currentEpisodes[currentEpisodeIndex])
            } else {
                Toast.makeText(this, "Đây là tập cuối cùng!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setScreenLock(locked: Boolean) {
        isScreenLocked = locked
        gestureHelper.isLocked = locked
        if (locked) {
            binding.layoutTopControls.visibility = View.GONE
            binding.btnFullscreen.visibility = View.GONE
            binding.btnUnlock.visibility = View.VISIBLE
            Toast.makeText(this, "Đã khóa màn hình! Chạm vào icon ổ khóa để mở lại", Toast.LENGTH_SHORT).show()
        } else {
            binding.layoutTopControls.visibility = View.VISIBLE
            binding.btnFullscreen.visibility = View.VISIBLE
            binding.btnUnlock.visibility = View.GONE
            Toast.makeText(this, "Đã mở khóa màn hình", Toast.LENGTH_SHORT).show()
        }
    }

    private fun enterPipMode() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            try {
                val params = android.app.PictureInPictureParams.Builder()
                    .setAspectRatio(android.util.Rational(16, 9))
                    .build()
                enterPictureInPictureMode(params)
            } catch (e: Exception) {
                Toast.makeText(this, "Không thể bật PiP: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        } else {
            Toast.makeText(this, "Thiết bị Android cần từ bản 8.0 trở lên để dùng PiP", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onUserLeaveHint() {
        super.onUserLeaveHint()
        if (player?.isPlaying == true && !isInPictureInPictureModeSafely()) {
            enterPipMode()
        }
    }

    private fun isInPictureInPictureModeSafely(): Boolean {
        return if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
            isInPictureInPictureMode
        } else false
    }

    override fun onPictureInPictureModeChanged(isInPictureInPictureMode: Boolean, newConfig: Configuration) {
        super.onPictureInPictureModeChanged(isInPictureInPictureMode, newConfig)
        if (isInPictureInPictureMode) {
            binding.layoutTopControls.visibility = View.GONE
            binding.btnFullscreen.visibility = View.GONE
            binding.scrollDetails.visibility = View.GONE
            binding.layoutGestureOverlay.visibility = View.GONE
            binding.btnUnlock.visibility = View.GONE
        } else {
            binding.layoutTopControls.visibility = View.VISIBLE
            binding.btnFullscreen.visibility = View.VISIBLE
            updateOrientationUI(resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE)
        }
    }

    private fun toggleControlsVisibility() {
        areControlsVisible = !areControlsVisible
        val vis = if (areControlsVisible) View.VISIBLE else View.GONE
        binding.layoutTopControls.visibility = vis
        binding.btnFullscreen.visibility = vis
    }

    private fun toggleFullscreen() {
        val isLandscape = resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE
        if (isLandscape) {
            requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        } else {
            requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE
        }
    }

    private fun showVBookSettingsDialog() {
        val dialog = com.google.android.material.bottomsheet.BottomSheetDialog(this)
        val view = layoutInflater.inflate(R.layout.dialog_vbook_settings, null)
        dialog.setContentView(view)

        val switchAutoNext = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchAutoNext)
        val switchPipOnHome = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchPipOnHome)
        val rgSeekStep = view.findViewById<android.widget.RadioGroup>(R.id.rgSeekStep)
        val switchBrightnessGesture = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchBrightnessGesture)
        val switchVolumeGesture = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchVolumeGesture)
        val switchKeepScreenOn = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchKeepScreenOn)

        switchAutoNext?.isChecked = autoNextEpisode
        switchAutoNext?.setOnCheckedChangeListener { _, isChecked -> autoNextEpisode = isChecked }

        switchPipOnHome?.isChecked = pipOnHome
        switchPipOnHome?.setOnCheckedChangeListener { _, isChecked -> pipOnHome = isChecked }

        when (gestureHelper.seekStepSeconds) {
            5 -> view.findViewById<android.widget.RadioButton>(R.id.rbSeek5)?.isChecked = true
            15 -> view.findViewById<android.widget.RadioButton>(R.id.rbSeek15)?.isChecked = true
            30 -> view.findViewById<android.widget.RadioButton>(R.id.rbSeek30)?.isChecked = true
            else -> view.findViewById<android.widget.RadioButton>(R.id.rbSeek10)?.isChecked = true
        }

        rgSeekStep?.setOnCheckedChangeListener { _, checkedId ->
            gestureHelper.seekStepSeconds = when (checkedId) {
                R.id.rbSeek5 -> 5
                R.id.rbSeek15 -> 15
                R.id.rbSeek30 -> 30
                else -> 10
            }
        }

        switchBrightnessGesture?.isChecked = gestureHelper.isBrightnessGestureEnabled
        switchBrightnessGesture?.setOnCheckedChangeListener { _, isChecked ->
            gestureHelper.isBrightnessGestureEnabled = isChecked
        }

        switchVolumeGesture?.isChecked = gestureHelper.isVolumeGestureEnabled
        switchVolumeGesture?.setOnCheckedChangeListener { _, isChecked ->
            gestureHelper.isVolumeGestureEnabled = isChecked
        }

        switchKeepScreenOn?.isChecked = true
        switchKeepScreenOn?.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            } else {
                window.clearFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            }
        }

        dialog.show()
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        updateOrientationUI(newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE)
    }

    private fun updateOrientationUI(isLandscape: Boolean) {
        val insetsController = WindowCompat.getInsetsController(window, window.decorView)
        if (isLandscape) {
            insetsController.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            insetsController.hide(WindowInsetsCompat.Type.systemBars())
            binding.scrollDetails.visibility = View.GONE
            binding.layoutPlayerContainer.layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            binding.btnFullscreen.setImageResource(R.drawable.ic_fullscreen_exit)
        } else {
            insetsController.show(WindowInsetsCompat.Type.systemBars())
            binding.scrollDetails.visibility = View.VISIBLE
            val playerHeight = (resources.displayMetrics.widthPixels * 9) / 16
            binding.layoutPlayerContainer.layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                playerHeight.coerceAtLeast(350)
            )
            binding.btnFullscreen.setImageResource(R.drawable.ic_fullscreen)
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        } else {
            super.onBackPressed()
        }
    }

    private fun loadDetail() {
        val movie = movieItem ?: return
        binding.progressEpisodes.visibility = View.VISIBLE
        binding.playerLoading.visibility = View.VISIBLE

        lifecycleScope.launch {
            val detail = MovieRepository.getMovieDetail(movie.source, movie.slug)
            binding.progressEpisodes.visibility = View.GONE
            binding.playerLoading.visibility = View.GONE
            movieDetail = detail

            if (detail != null) {
                if (detail.content.isNotEmpty()) {
                    binding.txtDetailDesc.text = detail.content
                }
                setupServerTabs(detail.servers)
            } else {
                binding.txtDetailDesc.text = "Không tải được thông tin chi tiết phim."
            }
        }
    }

    private fun setupServerTabs(servers: List<ServerGroup>) {
        binding.layoutServers.removeAllViews()
        if (servers.isEmpty()) return

        servers.forEachIndexed { index, server ->
            val serverTab = TextView(this).apply {
                val padH = (16 * resources.displayMetrics.density).toInt()
                val padV = (8 * resources.displayMetrics.density).toInt()
                setPadding(padH, padV, padH, padV)
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply {
                    setMargins(0, 0, (10 * resources.displayMetrics.density).toInt(), 0)
                }
                setBackgroundResource(R.drawable.bg_btn_selector)
                text = server.serverName
                setTextColor(Color.WHITE)
                textSize = 12f
                setTypeface(null, android.graphics.Typeface.BOLD)
                gravity = android.view.Gravity.CENTER
                isClickable = true
                isFocusable = true
                isSelected = (index == 0)

                setOnClickListener {
                    for (i in 0 until binding.layoutServers.childCount) {
                        binding.layoutServers.getChildAt(i).isSelected = false
                    }
                    isSelected = true
                    switchServer(index)
                }
            }
            binding.layoutServers.addView(serverTab)
        }

        switchServer(0)
    }

    private fun switchServer(serverIndex: Int) {
        val servers = movieDetail?.servers ?: return
        if (serverIndex !in servers.indices) return

        currentServerIndex = serverIndex
        currentEpisodes.clear()
        currentEpisodes.addAll(servers[serverIndex].episodes)
        episodeAdapter.submitList(currentEpisodes.toList())

        binding.txtEpisodesHeader.text = "Danh sách tập (${currentEpisodes.size} tập):"

        if (currentEpisodes.isNotEmpty()) {
            currentEpisodeIndex = 0
            playEpisode(currentEpisodes[0])
        }
    }

    private fun playEpisode(episode: EpisodeItem) {
        val streamUrl = episode.linkM3u8 ?: episode.linkEmbed
        if (streamUrl.isNullOrEmpty()) {
            Toast.makeText(this, getString(R.string.no_stream_found), Toast.LENGTH_SHORT).show()
            return
        }

        binding.txtDetailMeta.text = "${movieItem?.name} • Đang phát: ${episode.name}"

        val isM3u8 = episode.linkM3u8 != null || streamUrl.contains(".m3u8")
        if (isM3u8) {
            initExoPlayer(streamUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }
    }

    private fun initExoPlayer(url: String) {
        binding.playerView.visibility = View.VISIBLE
        binding.webViewPlayer.visibility = View.GONE
        binding.playerLoading.visibility = View.VISIBLE

        player?.release()

        val dataSourceFactory = DefaultHttpDataSource.Factory()
            .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            .setAllowCrossProtocolRedirects(true)

        val mediaSource = HlsMediaSource.Factory(dataSourceFactory)
            .createMediaSource(MediaItem.fromUri(url))

        player = ExoPlayer.Builder(this).build().apply {
            setMediaSource(mediaSource)
            prepare()
            playWhenReady = true
            addListener(object : Player.Listener {
                override fun onPlaybackStateChanged(playbackState: Int) {
                    if (playbackState == Player.STATE_BUFFERING) {
                        binding.playerLoading.visibility = View.VISIBLE
                    } else {
                        binding.playerLoading.visibility = View.GONE
                    }

                    if (playbackState == Player.STATE_ENDED) {
                        if (autoNextEpisode && currentEpisodeIndex < currentEpisodes.size - 1) {
                            currentEpisodeIndex++
                            playEpisode(currentEpisodes[currentEpisodeIndex])
                            Toast.makeText(this@DetailActivity, "Tự động chuyển sang tập tiếp theo!", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            })
        }
        binding.playerView.player = player
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun initWebViewPlayer(url: String) {
        player?.pause()
        binding.playerView.visibility = View.GONE
        binding.webViewPlayer.visibility = View.VISIBLE
        binding.playerLoading.visibility = View.VISIBLE

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
                binding.playerLoading.visibility = View.GONE
            }
        }
        webView.loadUrl(url)
    }

    override fun onStop() {
        super.onStop()
        player?.pause()
    }

    override fun onDestroy() {
        super.onDestroy()
        player?.release()
        player = null
        binding.webViewPlayer.destroy()
    }
}
