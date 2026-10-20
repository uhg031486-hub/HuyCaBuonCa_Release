package com.huycabuonca.mobile.ui

import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.ActivityInfo
import android.content.res.Configuration
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.LinearLayout
import android.widget.SeekBar
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
import com.google.android.material.bottomsheet.BottomSheetBehavior
import com.google.android.material.bottomsheet.BottomSheetDialog
import androidx.media3.ui.CaptionStyleCompat
import android.util.TypedValue
import android.view.LayoutInflater
import android.widget.Button
import android.widget.ImageView
import android.widget.RadioButton
import android.widget.RadioGroup
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.huycabuonca.mobile.R
import com.huycabuonca.mobile.api.MovieRepository
import com.huycabuonca.mobile.api.MovieRepository.toMovieItem
import com.huycabuonca.mobile.api.TvChannelItem
import com.huycabuonca.mobile.databinding.ActivityDetailBinding
import com.huycabuonca.mobile.model.EpisodeItem
import com.huycabuonca.mobile.model.MovieDetail
import com.huycabuonca.mobile.model.MovieItem
import com.huycabuonca.mobile.model.MovieSource
import com.huycabuonca.mobile.model.ServerGroup
import com.huycabuonca.mobile.ui.adapter.EpisodeAdapter
import com.huycabuonca.mobile.util.FavoriteMovieManager
import com.huycabuonca.mobile.ui.adapter.QuickChannelAdapter
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

    // Trạng thái bộ điều khiển (Controls)
    private var areControlsVisible = true
    private var isScreenLocked = false
    private var isUserSeeking = false
    private var hasResumedPositionForCurrentEpisode = false

    // Hẹn giờ tắt (Sleep Timer) & Bỏ qua Intro
    private var sleepTimerMinutes = 0
    private var sleepTimerEndEpisode = false
    private var sleepTimerRunnable: Runnable? = null

    // Bộ hẹn giờ (Handlers)
    private val mainHandler = Handler(Looper.getMainLooper())
    private val hideControlsRunnable = Runnable {
        if (player?.isPlaying == true && !isScreenLocked) {
            hideControls()
        }
    }

    private val updateProgressRunnable = object : Runnable {
        override fun run() {
            val p = player
            if (p != null) {
                val duration = p.duration.coerceAtLeast(0L)
                val currentPos = p.currentPosition.coerceAtLeast(0L)

                if (!isUserSeeking && duration > 0) {
                    binding.videoSeekBar.max = duration.toInt()
                    binding.videoSeekBar.progress = currentPos.toInt()
                    binding.txtCurrentTime.text = formatTime(currentPos)
                    binding.txtTotalDuration.text = formatTime(duration)

                    // Lưu vị trí xem dở (vBook auto resume)
                    savePlaybackPosition(currentPos)
                }

                // Nút Bỏ qua Intro (+85s) tự động xuất hiện trong khoảng 1.000ms đến 95.000ms
                if (duration > 300_000L && currentPos in 1000L..95_000L && !isScreenLocked) {
                    if (binding.btnSkipIntro.visibility != View.VISIBLE) {
                        binding.btnSkipIntro.visibility = View.VISIBLE
                    }
                } else {
                    if (binding.btnSkipIntro.visibility == View.VISIBLE) {
                        binding.btnSkipIntro.visibility = View.GONE
                    }
                }
            }
            mainHandler.postDelayed(this, 500)
        }
    }

    // Cài đặt nâng cao chuẩn vBook
    private lateinit var gestureHelper: PlayerGestureHelper
    private var autoNextEpisode = true
    private var autoResumePosition = true
    private var pipOnHome = true
    private val speeds = listOf(1.0f, 1.25f, 1.5f, 2.0f, 0.75f)
    private var currentSpeedIndex = 0
    private var currentResizeModeIndex = 0
    private val resizeModes = listOf(
        androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FIT to "Vừa màn hình (16:9)",
        androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_ZOOM to "Tràn viền (Cắt viền đen)",
        androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FILL to "Kéo giãn toàn màn hình"
    )

    private var loudnessEnhancer: android.media.audiofx.LoudnessEnhancer? = null
    private var currentGainMb = 0
    private var isDataSaverEnabled = false

    // Quản lý video dọc (Phim ngắn dọc 9:16) & phóng to toàn màn hình dọc
    private var isVerticalVideo = false
    private var isVerticalFullscreen = false

    // Chuyển kênh nhanh TV (Quick Zapping) & Danh sách kênh cùng nhóm
    private var currentTvChannel: TvChannelItem? = null
    private var sameGroupChannels = mutableListOf<TvChannelItem>()

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

        if (movieItem?.source == MovieSource.FREEREELS || movieItem?.slug?.startsWith("freereels_") == true) {
            isVerticalVideo = true
        }

        setupUI()
        setupPlayerControls()
        loadDetail()
    }

    private fun setupUI() {
        val movie = movieItem!!
        val isTv = movie.source == MovieSource.XEMTIVI
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

        if (isTv) {
            binding.btnPrevEpisode.text = "⏮️ Kênh Trước"
            binding.btnNextEpisode.text = "Kênh Sau ⏭️"
            binding.btnSameGroupChannels.visibility = View.VISIBLE

            val allTv = MovieRepository.getAllTvChannels(this)
            currentTvChannel = allTv.find { it.id == movie.slug || it.name.equals(movie.name, ignoreCase = true) }
            if (currentTvChannel != null) {
                sameGroupChannels = MovieRepository.getChannelsInSameGroup(currentTvChannel!!.id, this).toMutableList()
            } else {
                sameGroupChannels = allTv.toMutableList()
            }
            val groupName = currentTvChannel?.group ?: "Truyền Hình"
            binding.btnSameGroupChannels.text = "📋 Nhóm [${groupName}]: ${sameGroupChannels.size} Kênh (Chạm để chọn)"

            binding.btnPrevEpisode.setOnClickListener { switchPreviousChannel() }
            binding.btnNextEpisode.setOnClickListener { switchNextChannel() }
            binding.btnSameGroupChannels.setOnClickListener { showSameGroupChannelsBottomSheet() }
        } else {
            binding.btnSameGroupChannels.visibility = View.GONE
            binding.btnPrevEpisode.setOnClickListener { playPreviousEpisode() }
            binding.btnNextEpisode.setOnClickListener { playNextEpisode() }
        }

        binding.btnDetailFavorite.setOnClickListener { toggleFavorite() }
        updateFavoriteStatus()
    }

    private fun updateFavoriteStatus() {
        val movie = movieItem ?: return
        val isTv = movie.source == MovieSource.XEMTIVI
        val isFav = if (isTv && currentTvChannel != null) {
            MovieRepository.isChannelFavorite(this, currentTvChannel!!.id)
        } else {
            FavoriteMovieManager.isFavorite(this, movie.slug)
        }

        val goldColor = Color.parseColor("#FFD700")
        val whiteColor = Color.WHITE
        val grayColor = Color.parseColor("#8A99AD")

        // Cập nhật nút trên Player bar
        binding.btnPlayerFav.setColorFilter(if (isFav) goldColor else whiteColor)

        // Cập nhật nút dưới Thông tin chi tiết
        binding.imgDetailFav.setColorFilter(if (isFav) goldColor else grayColor)
        binding.txtDetailFav.text = if (isFav) "Đã Thích ⭐" else "Yêu Thích ☆"
        binding.txtDetailFav.setTextColor(if (isFav) goldColor else whiteColor)
    }

    private fun toggleFavorite() {
        val movie = movieItem ?: return
        val isTv = movie.source == MovieSource.XEMTIVI
        if (isTv && currentTvChannel != null) {
            val isFav = MovieRepository.toggleChannelFavorite(this, currentTvChannel!!.id)
            updateFavoriteStatus()
            val msg = if (isFav) "⭐ Đã thêm [${movie.name}] vào Kênh Yêu Thích!" else "Đã xóa [${movie.name}] khỏi Kênh Yêu Thích"
            Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
        } else {
            val isFav = FavoriteMovieManager.toggleFavorite(this, movie)
            updateFavoriteStatus()
            val typeName = when (movie.source) {
                MovieSource.ANIMEHAY -> "Anime"
                MovieSource.FREEREELS -> "Phim Ngắn"
                else -> "Phim"
            }
            val msg = if (isFav) "⭐ Đã thêm [${movie.name}] vào $typeName Yêu Thích!" else "Đã xóa [${movie.name}] khỏi $typeName Yêu Thích"
            Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupPlayerControls() {
        // 0. Nút Dấu Sao Yêu Thích trên Player Bar
        binding.btnPlayerFav.setOnClickListener {
            toggleFavorite()
        }

        // 1. Nút Back
        binding.btnPlayerBack.setOnClickListener {
            if (isVerticalFullscreen) {
                exitVerticalFullscreen()
            } else if (resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE) {
                requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
            } else {
                finish()
            }
        }

        // 2. Chạm vào vùng trống của Overlay để bật/tắt bộ điều khiển
        binding.layoutPlayerControlsOverlay.setOnClickListener {
            toggleControlsVisibility()
        }

        // 3. NÚT PLAY / PAUSE TRUNG TÂM TO RÕ
        binding.btnCenterPlayPause.setOnClickListener {
            togglePlayPause()
        }

        // 4. Nút tua lùi & tua tới 10 giây
        binding.btnRewind10.setOnClickListener {
            seekDelta(-10000L)
        }

        binding.btnForward10.setOnClickListener {
            seekDelta(10000L)
        }

        // 5. Nút tập trước / tập sau trên thanh điều khiển (Hỗ trợ cả đổi kênh TV)
        binding.btnPrevEpPlayer.setOnClickListener {
            if (movieItem?.source == MovieSource.XEMTIVI) switchPreviousChannel() else playPreviousEpisode()
        }

        binding.btnNextEpPlayer.setOnClickListener {
            if (movieItem?.source == MovieSource.XEMTIVI) switchNextChannel() else playNextEpisode()
        }

        // 6. THANH TIẾN TRÌNH SEEKBAR VÀNG KIM (TUA TỚI GIỮA PHIM HOẶC BẤT KỲ ĐOẠN NÀO)
        binding.videoSeekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                if (fromUser) {
                    binding.txtCurrentTime.text = formatTime(progress.toLong())
                }
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {
                isUserSeeking = true
                removeAutoHideTimer()
            }

            override fun onStopTrackingTouch(seekBar: SeekBar?) {
                val targetPos = seekBar?.progress?.toLong() ?: 0L
                player?.seekTo(targetPos)
                isUserSeeking = false
                resetAutoHideTimer()
            }
        })

        // 7. Nút Toàn màn hình / Thu nhỏ
        binding.btnFullscreen.setOnClickListener {
            toggleFullscreen()
        }

        // 8. Nút chọn tập nhanh (BottomSheet chuẩn vBook)
        binding.btnEpisodeSheet.setOnClickListener {
            showEpisodesBottomSheet()
        }

        // 9. Nút Tốc độ phát (Speed)
        binding.btnSpeed.setOnClickListener {
            currentSpeedIndex = (currentSpeedIndex + 1) % speeds.size
            val speed = speeds[currentSpeedIndex]
            player?.setPlaybackSpeed(speed)
            binding.btnSpeed.text = "${speed}x"
            Toast.makeText(this, "Tốc độ phát: ${speed}x", Toast.LENGTH_SHORT).show()
            resetAutoHideTimer()
        }

        // 10. Nút Tỷ lệ khung hình (Aspect Ratio / Resize Mode)
        binding.btnAspectRatio.setOnClickListener {
            currentResizeModeIndex = (currentResizeModeIndex + 1) % resizeModes.size
            val (mode, label) = resizeModes[currentResizeModeIndex]
            binding.playerView.resizeMode = mode
            Toast.makeText(this, "Khung hình: $label", Toast.LENGTH_SHORT).show()
            resetAutoHideTimer()
        }

        // 11. Khóa cảm ứng màn hình (Lock) & Mở khóa
        binding.btnLock.setOnClickListener {
            setScreenLock(true)
        }

        binding.btnUnlock.setOnClickListener {
            setScreenLock(false)
        }

        binding.lockTouchSurface.setOnClickListener {
            binding.btnUnlock.visibility = View.VISIBLE
            binding.btnUnlock.animate().scaleX(1.25f).scaleY(1.25f).setDuration(150).withEndAction {
                binding.btnUnlock.animate().scaleX(1.0f).scaleY(1.0f).setDuration(150).start()
            }.start()
            Toast.makeText(this, "Chạm biểu tượng ổ khóa bên trái để mở khóa màn hình", Toast.LENGTH_SHORT).show()
        }

        // Nút Bỏ qua Intro (+85s)
        binding.btnSkipIntro.setOnClickListener {
            seekDelta(85000L)
            binding.btnSkipIntro.visibility = View.GONE
            Toast.makeText(this, "Đã bỏ qua đoạn mở đầu (+85s)!", Toast.LENGTH_SHORT).show()
        }

        // 12. PiP / Phát trong nền (vBook style)
        binding.btnPip.setOnClickListener {
            enterPipMode()
        }

        // 13. Cài đặt phát chuẩn vBook
        binding.btnSettings.setOnClickListener {
            showVBookSettingsDialog()
        }

        // 14. Cử chỉ vuốt âm lượng / độ sáng / double tap
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
        ).apply {
            onSwipeVerticalShorts = { isNext ->
                if (isNext) {
                    if (currentEpisodeIndex < currentEpisodes.size - 1) {
                        currentEpisodeIndex++
                        playEpisode(currentEpisodes[currentEpisodeIndex])
                        Toast.makeText(this@DetailActivity, "📱 Vuốt lên: Tập tiếp theo (${currentEpisodes[currentEpisodeIndex].name})", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(this@DetailActivity, "Đã là tập cuối cùng!", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    if (currentEpisodeIndex > 0) {
                        currentEpisodeIndex--
                        playEpisode(currentEpisodes[currentEpisodeIndex])
                        Toast.makeText(this@DetailActivity, "📱 Vuốt xuống: Tập trước (${currentEpisodes[currentEpisodeIndex].name})", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(this@DetailActivity, "Đã là tập đầu tiên!", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }

        // Bắt đầu cập nhật SeekBar
        mainHandler.post(updateProgressRunnable)
    }

    private fun togglePlayPause() {
        val p = player ?: return
        if (p.isPlaying) {
            p.pause()
            binding.btnCenterPlayPause.setImageResource(R.drawable.ic_play)
            removeAutoHideTimer()
        } else {
            if (p.playbackState == Player.STATE_ENDED) {
                p.seekTo(0L)
            }
            p.play()
            binding.btnCenterPlayPause.setImageResource(R.drawable.ic_pause)
            resetAutoHideTimer()
        }
    }

    private fun seekDelta(deltaMs: Long) {
        val p = player ?: return
        val current = p.currentPosition
        val duration = p.duration.coerceAtLeast(0L)
        val target = if (duration > 0) {
            (current + deltaMs).coerceIn(0L, duration)
        } else {
            (current + deltaMs).coerceAtLeast(0L)
        }
        p.seekTo(target)
        binding.videoSeekBar.progress = target.toInt()
        binding.txtCurrentTime.text = formatTime(target)
        resetAutoHideTimer()
    }

    private fun playPreviousEpisode() {
        if (currentEpisodeIndex > 0) {
            currentEpisodeIndex--
            playEpisode(currentEpisodes[currentEpisodeIndex])
        } else {
            Toast.makeText(this, "Đây là tập đầu tiên!", Toast.LENGTH_SHORT).show()
        }
    }

    private fun playNextEpisode() {
        if (currentEpisodeIndex < currentEpisodes.size - 1) {
            currentEpisodeIndex++
            playEpisode(currentEpisodes[currentEpisodeIndex])
        } else {
            Toast.makeText(this, "Đây là tập cuối cùng!", Toast.LENGTH_SHORT).show()
        }
    }

    private fun resetAutoHideTimer() {
        mainHandler.removeCallbacks(hideControlsRunnable)
        if (player?.isPlaying == true && !isScreenLocked) {
            mainHandler.postDelayed(hideControlsRunnable, 4000)
        }
    }

    private fun removeAutoHideTimer() {
        mainHandler.removeCallbacks(hideControlsRunnable)
    }

    private fun showControls() {
        areControlsVisible = true
        binding.layoutPlayerControlsOverlay.visibility = View.VISIBLE
        resetAutoHideTimer()
    }

    private fun hideControls() {
        areControlsVisible = false
        binding.layoutPlayerControlsOverlay.visibility = View.GONE
    }

    private fun toggleControlsVisibility() {
        if (isScreenLocked) return
        if (areControlsVisible) {
            hideControls()
        } else {
            showControls()
        }
    }

    private fun setScreenLock(locked: Boolean) {
        isScreenLocked = locked
        gestureHelper.isLocked = locked
        if (locked) {
            hideControls()
            binding.btnSkipIntro.visibility = View.GONE
            binding.lockTouchSurface.visibility = View.VISIBLE
            binding.btnUnlock.visibility = View.VISIBLE
            Toast.makeText(this, "Đã khóa màn hình! Chạm biểu tượng ổ khóa bên trái để mở lại", Toast.LENGTH_SHORT).show()
        } else {
            binding.lockTouchSurface.visibility = View.GONE
            binding.btnUnlock.visibility = View.GONE
            showControls()
            Toast.makeText(this, "Đã mở khóa màn hình", Toast.LENGTH_SHORT).show()
        }
    }

    private fun showEpisodesBottomSheet() {
        if (currentEpisodes.isEmpty()) return
        val dialog = BottomSheetDialog(this)
        val view = layoutInflater.inflate(R.layout.dialog_episodes_sheet, null)
        dialog.setContentView(view)

        dialog.setOnShowListener { dialogInterface ->
            val bottomSheetDialog = dialogInterface as? BottomSheetDialog
            val bottomSheet = bottomSheetDialog?.findViewById<View>(com.google.android.material.R.id.design_bottom_sheet)
            if (bottomSheet != null) {
                val behavior = BottomSheetBehavior.from(bottomSheet)
                behavior.state = BottomSheetBehavior.STATE_EXPANDED
                behavior.skipCollapsed = true
                if (resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE) {
                    behavior.peekHeight = resources.displayMetrics.heightPixels
                    bottomSheet.layoutParams.height = ViewGroup.LayoutParams.MATCH_PARENT
                }
            }
        }

        val txtTitle = view.findViewById<TextView>(R.id.txtSheetTitle)
        val recycler = view.findViewById<androidx.recyclerview.widget.RecyclerView>(R.id.recyclerSheetEpisodes)

        txtTitle?.text = "Danh sách tập (${currentEpisodes.size} tập)"
        val sheetAdapter = EpisodeAdapter { episode ->
            val idx = currentEpisodes.indexOf(episode)
            if (idx != -1) {
                currentEpisodeIndex = idx
            }
            playEpisode(episode)
            dialog.dismiss()
        }

        recycler?.layoutManager = GridLayoutManager(this, 4)
        recycler?.adapter = sheetAdapter
        sheetAdapter.submitList(currentEpisodes.toList())

        dialog.show()
    }

    private fun enterPipMode() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            try {
                val isVertical = (player?.videoSize?.height ?: 0) > (player?.videoSize?.width ?: 0) && (player?.videoSize?.width ?: 0) > 0
                val rational = if (isVertical) android.util.Rational(9, 16) else android.util.Rational(16, 9)
                val params = android.app.PictureInPictureParams.Builder()
                    .setAspectRatio(rational)
                    .build()
                enterPictureInPictureMode(params)
            } catch (e: Exception) {
                Toast.makeText(this, "Không thể bật PiP: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        } else {
            Toast.makeText(this, "Cần Android 8.0 trở lên để dùng tính năng PiP", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onUserLeaveHint() {
        super.onUserLeaveHint()
        if (pipOnHome && player?.isPlaying == true && !isInPictureInPictureModeSafely()) {
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
            hideControls()
            binding.scrollDetails.visibility = View.GONE
            binding.layoutGestureOverlay.visibility = View.GONE
            binding.btnUnlock.visibility = View.GONE
        } else {
            showControls()
            updateOrientationUI(resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE)
        }
    }

    private fun enterVerticalFullscreen() {
        isVerticalFullscreen = true
        val insetsController = WindowCompat.getInsetsController(window, window.decorView)
        insetsController.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        insetsController.hide(WindowInsetsCompat.Type.systemBars())
        binding.scrollDetails.visibility = View.GONE
        binding.layoutPlayerContainer.layoutParams = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
        binding.playerView.resizeMode = androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_ZOOM
        binding.btnFullscreen.setImageResource(R.drawable.ic_fullscreen_exit)
    }

    private fun exitVerticalFullscreen() {
        isVerticalFullscreen = false
        val insetsController = WindowCompat.getInsetsController(window, window.decorView)
        insetsController.show(WindowInsetsCompat.Type.systemBars())
        binding.scrollDetails.visibility = View.VISIBLE
        val dm = resources.displayMetrics
        val playerHeight = (dm.heightPixels * 0.65).toInt()
        binding.layoutPlayerContainer.layoutParams = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            playerHeight
        )
        binding.playerView.resizeMode = androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FIT
        binding.btnFullscreen.setImageResource(R.drawable.ic_fullscreen)
    }

    private fun toggleFullscreen() {
        if (isVerticalVideo) {
            if (isVerticalFullscreen) {
                exitVerticalFullscreen()
            } else {
                enterVerticalFullscreen()
            }
            return
        }
        val isLandscape = resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE
        requestedOrientation = if (isLandscape) {
            ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        } else {
            ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
        }
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            isVerticalFullscreen = false
        }
        updateOrientationUI(newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE)
    }

    private fun updateOrientationUI(isLandscape: Boolean) {
        val insetsController = WindowCompat.getInsetsController(window, window.decorView)
        if (isLandscape) {
            isVerticalFullscreen = false
            insetsController.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            insetsController.hide(WindowInsetsCompat.Type.systemBars())
            binding.scrollDetails.visibility = View.GONE
            binding.layoutPlayerContainer.layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            binding.btnFullscreen.setImageResource(R.drawable.ic_fullscreen_exit)
        } else {
            if (isVerticalFullscreen) {
                enterVerticalFullscreen()
                return
            }
            insetsController.show(WindowInsetsCompat.Type.systemBars())
            binding.scrollDetails.visibility = View.VISIBLE
            val dm = resources.displayMetrics
            val playerHeight = if (isVerticalVideo) (dm.heightPixels * 0.65).toInt() else ((dm.widthPixels * 9) / 16).coerceAtLeast(350)
            binding.layoutPlayerContainer.layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                playerHeight
            )
            binding.btnFullscreen.setImageResource(R.drawable.ic_fullscreen)
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (isScreenLocked) {
            Toast.makeText(this, "Màn hình đang khóa! Vui lòng chạm biểu tượng ổ khóa bên trái để mở", Toast.LENGTH_SHORT).show()
            return
        }
        if (isVerticalFullscreen) {
            exitVerticalFullscreen()
            return
        }
        if (resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        } else {
            super.onBackPressed()
        }
    }

    private fun applySubtitleStyle(sizeSp: Float, colorHex: String) {
        try {
            val colorInt = Color.parseColor(colorHex)
            val style = CaptionStyleCompat(
                colorInt,
                Color.TRANSPARENT,
                Color.TRANSPARENT,
                CaptionStyleCompat.EDGE_TYPE_OUTLINE,
                Color.BLACK,
                null
            )
            binding.playerView.subtitleView?.apply {
                setStyle(style)
                setFixedTextSize(TypedValue.COMPLEX_UNIT_SP, sizeSp)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun setSleepTimer(minutes: Int, endEpisode: Boolean) {
        sleepTimerRunnable?.let { mainHandler.removeCallbacks(it) }
        sleepTimerMinutes = minutes
        sleepTimerEndEpisode = endEpisode

        if (endEpisode) {
            Toast.makeText(this, "Đã hẹn: Tự động dừng phát khi hết tập hiện tại", Toast.LENGTH_LONG).show()
        } else if (minutes > 0) {
            val millis = minutes * 60 * 1000L
            val runnable = Runnable {
                player?.pause()
                Toast.makeText(this, "⏰ Hẹn giờ tắt: Đã hết $minutes phút, tạm dừng phát!", Toast.LENGTH_LONG).show()
            }
            sleepTimerRunnable = runnable
            mainHandler.postDelayed(runnable, millis)
            Toast.makeText(this, "Đã hẹn giờ tắt sau $minutes phút", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "Đã tắt hẹn giờ", Toast.LENGTH_SHORT).show()
        }
    }

    private fun showVBookSettingsDialog() {
        val dialog = BottomSheetDialog(this)
        val view = layoutInflater.inflate(R.layout.dialog_vbook_settings, null)
        dialog.setContentView(view)

        dialog.setOnShowListener { dialogInterface ->
            val bottomSheetDialog = dialogInterface as? BottomSheetDialog
            val bottomSheet = bottomSheetDialog?.findViewById<View>(com.google.android.material.R.id.design_bottom_sheet)
            if (bottomSheet != null) {
                val behavior = BottomSheetBehavior.from(bottomSheet)
                behavior.state = BottomSheetBehavior.STATE_EXPANDED
                behavior.skipCollapsed = true
                behavior.isDraggable = true
                val displayMetrics = resources.displayMetrics
                val isLandscape = resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE
                if (isLandscape) {
                    behavior.peekHeight = displayMetrics.heightPixels
                    behavior.maxHeight = displayMetrics.heightPixels
                    val panelWidth = (displayMetrics.widthPixels * 0.48).toInt().coerceAtLeast((360 * displayMetrics.density).toInt())
                    dialog.window?.let { win ->
                        win.setLayout(panelWidth, ViewGroup.LayoutParams.MATCH_PARENT)
                        win.setGravity(android.view.Gravity.END or android.view.Gravity.TOP)
                    }
                    bottomSheet.layoutParams.height = ViewGroup.LayoutParams.MATCH_PARENT
                    bottomSheet.layoutParams.width = ViewGroup.LayoutParams.MATCH_PARENT
                } else {
                    behavior.peekHeight = (displayMetrics.heightPixels * 0.8).toInt()
                }
            }
        }

        val sp = getSharedPreferences("vbook_playback_prefs", Context.MODE_PRIVATE)

        // Phụ đề (Subtitle Controls)
        val txtSubPreview = view.findViewById<TextView>(R.id.txtSubPreview)
        val rgSubSize = view.findViewById<RadioGroup>(R.id.rgSubSize)
        val rgSubColor = view.findViewById<RadioGroup>(R.id.rgSubColor)

        var curSubSize = sp.getFloat("sub_font_size", 18f)
        var curSubColor = sp.getString("sub_font_color", "#FFD700") ?: "#FFD700"

        txtSubPreview?.textSize = curSubSize
        try {
            txtSubPreview?.setTextColor(Color.parseColor(curSubColor))
        } catch (_: Exception) {}

        when (curSubSize.toInt()) {
            14 -> view.findViewById<RadioButton>(R.id.rbSubSmall)?.isChecked = true
            22 -> view.findViewById<RadioButton>(R.id.rbSubLarge)?.isChecked = true
            26 -> view.findViewById<RadioButton>(R.id.rbSubExtra)?.isChecked = true
            else -> view.findViewById<RadioButton>(R.id.rbSubMedium)?.isChecked = true
        }

        when (curSubColor.uppercase()) {
            "#FFFFFF" -> view.findViewById<RadioButton>(R.id.rbColorWhite)?.isChecked = true
            "#00E5FF" -> view.findViewById<RadioButton>(R.id.rbColorCyan)?.isChecked = true
            "#EEFF41" -> view.findViewById<RadioButton>(R.id.rbColorYellow)?.isChecked = true
            else -> view.findViewById<RadioButton>(R.id.rbColorGold)?.isChecked = true
        }

        rgSubSize?.setOnCheckedChangeListener { _, checkedId ->
            val newSize = when (checkedId) {
                R.id.rbSubSmall -> 14f
                R.id.rbSubLarge -> 22f
                R.id.rbSubExtra -> 26f
                else -> 18f
            }
            curSubSize = newSize
            txtSubPreview?.textSize = newSize
            applySubtitleStyle(newSize, curSubColor)
            sp.edit().putFloat("sub_font_size", newSize).apply()
        }

        rgSubColor?.setOnCheckedChangeListener { _, checkedId ->
            val newColor = when (checkedId) {
                R.id.rbColorWhite -> "#FFFFFF"
                R.id.rbColorCyan -> "#00E5FF"
                R.id.rbColorYellow -> "#EEFF41"
                else -> "#FFD700"
            }
            curSubColor = newColor
            try {
                txtSubPreview?.setTextColor(Color.parseColor(newColor))
            } catch (_: Exception) {}
            applySubtitleStyle(curSubSize, newColor)
            sp.edit().putString("sub_font_color", newColor).apply()
        }

        val switchAutoNext = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchAutoNext)
        val switchPipOnHome = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchPipOnHome)
        val rgSleepTimer = view.findViewById<RadioGroup>(R.id.rgSleepTimer)
        val rgSeekStep = view.findViewById<RadioGroup>(R.id.rgSeekStep)
        val switchBrightnessGesture = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchBrightnessGesture)
        val switchVolumeGesture = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchVolumeGesture)
        val switchKeepScreenOn = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchKeepScreenOn)

        switchAutoNext?.isChecked = autoNextEpisode
        switchAutoNext?.setOnCheckedChangeListener { _, isChecked -> autoNextEpisode = isChecked }

        switchPipOnHome?.isChecked = pipOnHome
        switchPipOnHome?.setOnCheckedChangeListener { _, isChecked -> pipOnHome = isChecked }

        // Khởi tạo trạng thái Sleep Timer
        if (sleepTimerEndEpisode) {
            view.findViewById<RadioButton>(R.id.rbSleepEndEpisode)?.isChecked = true
        } else {
            when (sleepTimerMinutes) {
                15 -> view.findViewById<RadioButton>(R.id.rbSleep15)?.isChecked = true
                30 -> view.findViewById<RadioButton>(R.id.rbSleep30)?.isChecked = true
                60 -> view.findViewById<RadioButton>(R.id.rbSleep60)?.isChecked = true
                else -> view.findViewById<RadioButton>(R.id.rbSleepOff)?.isChecked = true
            }
        }

        rgSleepTimer?.setOnCheckedChangeListener { _, checkedId ->
            when (checkedId) {
                R.id.rbSleep15 -> setSleepTimer(15, false)
                R.id.rbSleep30 -> setSleepTimer(30, false)
                R.id.rbSleep60 -> setSleepTimer(60, false)
                R.id.rbSleepEndEpisode -> setSleepTimer(0, true)
                else -> setSleepTimer(0, false)
            }
        }

        when (gestureHelper.seekStepSeconds) {
            5 -> view.findViewById<RadioButton>(R.id.rbSeek5)?.isChecked = true
            15 -> view.findViewById<RadioButton>(R.id.rbSeek15)?.isChecked = true
            30 -> view.findViewById<RadioButton>(R.id.rbSeek30)?.isChecked = true
            else -> view.findViewById<RadioButton>(R.id.rbSeek10)?.isChecked = true
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

        // 🔊 Khuếch đại âm lượng (Volume Boost 200%)
        val rgVolumeBoost = view.findViewById<RadioGroup>(R.id.rgVolumeBoost)
        val savedBoost = sp.getInt("volume_boost_gain", 0)
        currentGainMb = savedBoost
        when (savedBoost) {
            400 -> view.findViewById<RadioButton>(R.id.rbBoost130)?.isChecked = true
            800 -> view.findViewById<RadioButton>(R.id.rbBoost160)?.isChecked = true
            1500 -> view.findViewById<RadioButton>(R.id.rbBoost200)?.isChecked = true
            else -> view.findViewById<RadioButton>(R.id.rbBoost100)?.isChecked = true
        }

        rgVolumeBoost?.setOnCheckedChangeListener { _, checkedId ->
            val gain = when (checkedId) {
                R.id.rbBoost130 -> 400
                R.id.rbBoost160 -> 800
                R.id.rbBoost200 -> 1500
                else -> 0
            }
            setVolumeBoostGain(gain)
            val label = when (gain) {
                400 -> "130%"
                800 -> "160%"
                1500 -> "200% (Siêu lớn)"
                else -> "100% (Chuẩn)"
            }
            Toast.makeText(this, "Âm lượng khuếch đại: $label", Toast.LENGTH_SHORT).show()
        }

        // 📶 Tiết kiệm dữ liệu (Data Saver 720p)
        val switchDataSaver = view.findViewById<androidx.appcompat.widget.SwitchCompat>(R.id.switchDataSaver)
        isDataSaverEnabled = sp.getBoolean("data_saver", false)
        switchDataSaver?.isChecked = isDataSaverEnabled
        switchDataSaver?.setOnCheckedChangeListener { _, isChecked ->
            isDataSaverEnabled = isChecked
            sp.edit().putBoolean("data_saver", isChecked).apply()
            applyDataSaverSetting()
            if (isChecked) {
                Toast.makeText(this, "Đã bật Tiết Kiệm Dữ Liệu (tối đa 720p)", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Đã tắt Tiết Kiệm Dữ Liệu (chuẩn Full HD)", Toast.LENGTH_SHORT).show()
            }
        }

        dialog.show()
    }

    private fun initLoudnessEnhancer(sessionId: Int) {
        if (sessionId <= 0) return
        try {
            loudnessEnhancer?.release()
            loudnessEnhancer = android.media.audiofx.LoudnessEnhancer(sessionId).apply {
                if (currentGainMb > 0) {
                    setTargetGain(currentGainMb)
                    enabled = true
                } else {
                    enabled = false
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun setVolumeBoostGain(gainMb: Int) {
        currentGainMb = gainMb
        val sp = getSharedPreferences("vbook_playback_prefs", Context.MODE_PRIVATE)
        sp.edit().putInt("volume_boost_gain", gainMb).apply()
        try {
            loudnessEnhancer?.let {
                if (gainMb > 0) {
                    it.setTargetGain(gainMb)
                    it.enabled = true
                } else {
                    it.enabled = false
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun applyDataSaverSetting() {
        val p = player ?: return
        if (isDataSaverEnabled) {
            p.trackSelectionParameters = p.trackSelectionParameters.buildUpon()
                .setMaxVideoSize(1280, 720)
                .build()
        } else {
            p.trackSelectionParameters = p.trackSelectionParameters.buildUpon()
                .clearVideoSizeConstraints()
                .build()
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

        hasResumedPositionForCurrentEpisode = false
        val titleText = "${movieItem?.name} • ${episode.name}"
        binding.txtDetailMeta.text = titleText
        binding.txtPlayerTitle.text = titleText

        // Nếu là tập phim ngắn FreeReels cần giải mã / mở khóa luồng m3u8
        if (streamUrl.startsWith("freereels_unlock:")) {
            val tokens = streamUrl.split(":")
            if (tokens.size >= 3) {
                val sId = tokens[1]
                val epId = tokens[2]
                binding.playerLoading.visibility = View.VISIBLE
                lifecycleScope.launch {
                    val res = MovieRepository.unlockFreeReelsEpisode(sId, epId)
                    binding.playerLoading.visibility = View.GONE
                    if (res != null && res.streamUrl.isNotEmpty()) {
                        val subUrl = res.subtitleUrl ?: episode.subtitleUrl
                        initExoPlayer(res.streamUrl, subUrl)
                    } else {
                        Toast.makeText(this@DetailActivity, "Tập phim ngắn này đang tải luồng phát, vui lòng thử lại!", Toast.LENGTH_SHORT).show()
                    }
                }
                return
            }
        }

        val isM3u8 = episode.linkM3u8 != null || streamUrl.contains(".m3u8")
        if (isM3u8) {
            initExoPlayer(streamUrl, episode.subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }
    }

    private fun initExoPlayer(url: String, subtitleUrl: String? = null) {
        binding.playerView.visibility = View.VISIBLE
        binding.gestureTouchView.visibility = View.VISIBLE
        binding.webViewPlayer.visibility = View.GONE
        binding.playerLoading.visibility = View.VISIBLE

        player?.release()

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
            val subConfig = MediaItem.SubtitleConfiguration.Builder(Uri.parse(subtitleUrl))
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

        val loadControl = androidx.media3.exoplayer.DefaultLoadControl.Builder()
            .setBufferDurationsMs(
                /* minBufferMs = */ 15_000,
                /* maxBufferMs = */ 60_000,
                /* bufferForPlaybackMs = */ 1_500,
                /* bufferForPlaybackAfterRebufferMs = */ 3_000
            )
            .setPrioritizeTimeOverSizeThresholds(true)
            .build()

        player = ExoPlayer.Builder(this)
            .setTrackSelector(trackSelector)
            .setLoadControl(loadControl)
            .build().apply {
            setMediaSource(mediaSource)
            prepare()
            playWhenReady = true
            initLoudnessEnhancer(audioSessionId)
            applyDataSaverSetting()
            addListener(object : Player.Listener {
                override fun onAudioSessionIdChanged(audioSessionId: Int) {
                    initLoudnessEnhancer(audioSessionId)
                }

                override fun onVideoSizeChanged(videoSize: androidx.media3.common.VideoSize) {
                    val isVertical = (videoSize.width > 0 && videoSize.height > videoSize.width) ||
                            (movieItem?.source == MovieSource.FREEREELS) ||
                            (movieItem?.slug?.startsWith("freereels_") == true)
                    isVerticalVideo = isVertical
                    if (isVertical) {
                        // Tự động nhận diện video màn hình dọc 9:16 (Chuẩn TikTok/Reels/Shorts)
                        gestureHelper.isShortsMode = true
                        if (isVerticalFullscreen) {
                            binding.playerView.resizeMode = androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_ZOOM
                            binding.scrollDetails.visibility = View.GONE
                            binding.layoutPlayerContainer.layoutParams = LinearLayout.LayoutParams(
                                ViewGroup.LayoutParams.MATCH_PARENT,
                                ViewGroup.LayoutParams.MATCH_PARENT
                            )
                        } else if (resources.configuration.orientation == Configuration.ORIENTATION_PORTRAIT) {
                            binding.playerView.resizeMode = androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FIT
                            val dm = resources.displayMetrics
                            binding.layoutPlayerContainer.layoutParams.height = (dm.heightPixels * 0.65).toInt()
                            binding.layoutPlayerContainer.requestLayout()
                        }
                        if (!binding.txtDetailMeta.text.contains("📱 Video Dọc")) {
                            binding.txtDetailMeta.text = "${binding.txtDetailMeta.text} • 📱 Video Dọc (9:16)"
                        }
                    } else {
                        // Video ngang chuẩn (kể cả trong FreeReels nếu là phim quay ngang)
                        gestureHelper.isShortsMode = false
                        binding.playerView.resizeMode = androidx.media3.ui.AspectRatioFrameLayout.RESIZE_MODE_FIT
                        if (resources.configuration.orientation == Configuration.ORIENTATION_PORTRAIT) {
                            binding.layoutPlayerContainer.layoutParams.height = (220 * resources.displayMetrics.density).toInt()
                            binding.layoutPlayerContainer.requestLayout()
                        }
                    }
                }

                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                    binding.playerLoading.visibility = View.GONE
                    val servers = movieDetail?.servers
                    if (servers != null && servers.size > 1 && currentServerIndex < servers.size - 1) {
                        val nextIdx = currentServerIndex + 1
                        Toast.makeText(this@DetailActivity, "⚡ Luồng lỗi kết nối, tự động chuyển sang: ${servers[nextIdx].serverName}", Toast.LENGTH_LONG).show()
                        switchServer(nextIdx)
                        return
                    }
                    val ep = currentEpisodes.getOrNull(currentEpisodeIndex)
                    val embedUrl = ep?.linkEmbed
                    if (!embedUrl.isNullOrEmpty() && binding.webViewPlayer.visibility != View.VISIBLE) {
                        Toast.makeText(this@DetailActivity, "M3U8 lỗi phản hồi, đang chuyển sang Server dự phòng...", Toast.LENGTH_SHORT).show()
                        initWebViewPlayer(embedUrl)
                    } else {
                        Toast.makeText(this@DetailActivity, "Tập phim này nguồn phát đang bảo trì. Vui lòng thử tập hoặc phim khác!", Toast.LENGTH_LONG).show()
                    }
                }

                override fun onPlaybackStateChanged(playbackState: Int) {
                    when (playbackState) {
                        Player.STATE_BUFFERING -> {
                            binding.playerLoading.visibility = View.VISIBLE
                        }
                        Player.STATE_READY -> {
                            binding.playerLoading.visibility = View.GONE
                            // Tự động tua tiếp từ vị trí trước (vBook auto resume)
                            if (autoResumePosition && !hasResumedPositionForCurrentEpisode) {
                                hasResumedPositionForCurrentEpisode = true
                                val savedPos = getSavedPlaybackPosition()
                                val dur = duration
                                if (savedPos > 5000L && (dur <= 0L || savedPos < dur - 10000L)) {
                                    seekTo(savedPos)
                                    Toast.makeText(
                                        this@DetailActivity,
                                        "Tiếp tục phát từ ${formatTime(savedPos)}",
                                        Toast.LENGTH_SHORT
                                    ).show()
                                }
                            }
                        }
                        Player.STATE_ENDED -> {
                            binding.playerLoading.visibility = View.GONE
                            binding.btnCenterPlayPause.setImageResource(R.drawable.ic_play)
                            showControls()
                            if (sleepTimerEndEpisode) {
                                sleepTimerEndEpisode = false
                                Toast.makeText(this@DetailActivity, "⏰ Đã xem hết tập! Hẹn giờ dừng phát tự động.", Toast.LENGTH_LONG).show()
                                return
                            }
                            if (autoNextEpisode && currentEpisodeIndex < currentEpisodes.size - 1) {
                                triggerAutoNextCountdown()
                            }
                        }
                        else -> {
                            binding.playerLoading.visibility = View.GONE
                        }
                    }
                }

                override fun onIsPlayingChanged(isPlaying: Boolean) {
                    if (isPlaying) {
                        binding.btnCenterPlayPause.setImageResource(R.drawable.ic_pause)
                        resetAutoHideTimer()
                    } else {
                        binding.btnCenterPlayPause.setImageResource(R.drawable.ic_play)
                        showControls()
                    }
                }
            })
        }
        binding.playerView.player = player
        val sp = getSharedPreferences("vbook_playback_prefs", Context.MODE_PRIVATE)
        val subSize = sp.getFloat("sub_font_size", 18f)
        val subColor = sp.getString("sub_font_color", "#FFD700") ?: "#FFD700"
        applySubtitleStyle(subSize, subColor)
        showControls()
    }

    private fun triggerAutoNextCountdown() {
        val nextIdx = currentEpisodeIndex + 1
        if (nextIdx >= currentEpisodes.size) return
        val nextEp = currentEpisodes[nextIdx]
        var countdown = 5

        val dialog = androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("🎬 Sắp phát Tập Tiếp Theo")
            .setMessage("Tự động phát [${nextEp.name}] sau: $countdown giây...")
            .setCancelable(true)
            .setPositiveButton("PHÁT NGAY") { d, _ ->
                d.dismiss()
                currentEpisodeIndex = nextIdx
                playEpisode(nextEp)
            }
            .setNegativeButton("HỦY", null)
            .create()

        dialog.show()

        val runnable = object : Runnable {
            override fun run() {
                countdown--
                if (countdown > 0) {
                    if (dialog.isShowing) {
                        dialog.setMessage("Tự động phát [${nextEp.name}] sau: $countdown giây...")
                        mainHandler.postDelayed(this, 1000)
                    }
                } else {
                    if (dialog.isShowing) {
                        dialog.dismiss()
                        currentEpisodeIndex = nextIdx
                        playEpisode(nextEp)
                        Toast.makeText(this@DetailActivity, "Đang phát [${nextEp.name}]", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }
        mainHandler.postDelayed(runnable, 1000)
    }

    private fun savePlaybackPosition(pos: Long) {
        val movie = movieItem ?: return
        val ep = currentEpisodes.getOrNull(currentEpisodeIndex) ?: return
        if (pos > 5000L) {
            val sp = getSharedPreferences("vbook_playback_prefs", Context.MODE_PRIVATE)
            sp.edit().putLong("resume_${movie.slug}_ep_${ep.slug}", pos).apply()
            com.huycabuonca.mobile.util.WatchHistoryManager.saveHistory(
                context = this,
                movie = movie,
                episodeName = ep.name,
                positionMs = pos,
                durationMs = player?.duration ?: 0L
            )
        }
    }

    private fun getSavedPlaybackPosition(): Long {
        val movie = movieItem ?: return 0L
        val ep = currentEpisodes.getOrNull(currentEpisodeIndex) ?: return 0L
        val sp = getSharedPreferences("vbook_playback_prefs", Context.MODE_PRIVATE)
        return sp.getLong("resume_${movie.slug}_ep_${ep.slug}", 0L)
    }

    private fun formatTime(millis: Long): String {
        if (millis <= 0) return "00:00"
        val totalSeconds = millis / 1000
        val seconds = totalSeconds % 60
        val minutes = (totalSeconds / 60) % 60
        val hours = totalSeconds / 3600
        return if (hours > 0) {
            String.format("%02d:%02d:%02d", hours, minutes, seconds)
        } else {
            String.format("%02d:%02d", minutes, seconds)
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun initWebViewPlayer(url: String) {
        player?.pause()
        binding.playerView.visibility = View.GONE
        binding.gestureTouchView.visibility = View.GONE
        binding.layoutPlayerControlsOverlay.visibility = View.GONE
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
        loudnessEnhancer?.release()
        loudnessEnhancer = null
        mainHandler.removeCallbacksAndMessages(null)
        player?.release()
        player = null
        binding.webViewPlayer.destroy()
    }

    private fun switchPreviousChannel() {
        if (sameGroupChannels.isEmpty()) return
        val curIdx = sameGroupChannels.indexOfFirst { it.id == currentTvChannel?.id || it.url == currentTvChannel?.url }
        val newIdx = if (curIdx <= 0) sameGroupChannels.size - 1 else curIdx - 1
        switchLiveChannel(sameGroupChannels[newIdx])
    }

    private fun switchNextChannel() {
        if (sameGroupChannels.isEmpty()) return
        val curIdx = sameGroupChannels.indexOfFirst { it.id == currentTvChannel?.id || it.url == currentTvChannel?.url }
        val newIdx = if (curIdx == -1 || curIdx >= sameGroupChannels.size - 1) 0 else curIdx + 1
        switchLiveChannel(sameGroupChannels[newIdx])
    }

    private fun switchLiveChannel(channel: TvChannelItem) {
        currentTvChannel = channel
        movieItem = channel.toMovieItem()
        binding.txtDetailTitle.text = channel.name
        binding.txtDetailMeta.text = "Trực tiếp • Nhóm: ${channel.group}"
        binding.txtPlayerTitle.text = "${channel.name} • [${channel.group}]"
        val groupName = channel.group
        binding.btnSameGroupChannels.text = "📋 Nhóm [${groupName}]: ${sameGroupChannels.size} Kênh (Chạm để chọn)"

        updateFavoriteStatus()
        initExoPlayer(channel.url)
        Toast.makeText(this, "📺 Đang phát: ${channel.name} (${channel.group})", Toast.LENGTH_SHORT).show()
    }

    private fun showSameGroupChannelsBottomSheet() {
        if (sameGroupChannels.isEmpty()) return
        val dialog = BottomSheetDialog(this)
        val view = layoutInflater.inflate(R.layout.dialog_same_group_channels, null)
        dialog.setContentView(view)

        val txtTitle = view.findViewById<TextView>(R.id.txtSheetGroupTitle)
        val btnClose = view.findViewById<Button>(R.id.btnCloseSheet)
        val recycler = view.findViewById<RecyclerView>(R.id.recyclerSameGroupChannels)

        val groupName = currentTvChannel?.group ?: "Kênh Cùng Nhóm"
        txtTitle?.text = "Kênh Thuộc Nhóm: $groupName (${sameGroupChannels.size} kênh)"
        btnClose?.setOnClickListener { dialog.dismiss() }

        val currentId = currentTvChannel?.id ?: ""
        val quickAdapter = QuickChannelAdapter(currentId) { selected ->
            dialog.dismiss()
            switchLiveChannel(selected)
        }
        recycler?.layoutManager = LinearLayoutManager(this)
        recycler?.adapter = quickAdapter
        quickAdapter.submit(sameGroupChannels)

        dialog.show()
    }
}
