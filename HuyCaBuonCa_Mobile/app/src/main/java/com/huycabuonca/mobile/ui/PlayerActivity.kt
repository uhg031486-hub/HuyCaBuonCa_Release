package com.huycabuonca.mobile.ui

import android.annotation.SuppressLint
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.KeyEvent
import android.view.View
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.hls.HlsMediaSource
import androidx.media3.datasource.DefaultHttpDataSource
import com.huycabuonca.mobile.databinding.ActivityPlayerBinding

class PlayerActivity : AppCompatActivity() {

    private lateinit var binding: ActivityPlayerBinding
    private var player: ExoPlayer? = null
    private val hideHandler = Handler(Looper.getMainLooper())
    private val hideOverlayRunnable = Runnable { hideOverlays() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPlayerBinding.inflate(layoutInflater)
        setContentView(binding.root)

        hideSystemUI()

        val streamUrl = intent.getStringExtra("EXTRA_STREAM_URL") ?: ""
        val isM3u8 = intent.getBooleanExtra("EXTRA_IS_M3U8", true) || streamUrl.contains(".m3u8")
        val title = intent.getStringExtra("EXTRA_TITLE") ?: ""
        val episode = intent.getStringExtra("EXTRA_EPISODE") ?: ""

        binding.txtPlayerTitle.text = "$title - $episode"
        binding.btnPlayerBack.setOnClickListener { finish() }

        val movie = intent.getSerializableExtra("EXTRA_MOVIE_ITEM") as? com.huycabuonca.mobile.model.MovieItem
        val channelId = intent.getStringExtra("EXTRA_CHANNEL_ID") ?: ""
        val source = intent.getStringExtra("EXTRA_SOURCE") ?: ""

        val isTv = source == com.huycabuonca.mobile.model.MovieSource.XEMTIVI.name || channelId.isNotEmpty()
        val updateFavIcon = {
            val isFav = if (isTv && channelId.isNotEmpty()) {
                com.huycabuonca.mobile.api.MovieRepository.isChannelFavorite(this, channelId)
            } else if (movie != null) {
                com.huycabuonca.mobile.util.FavoriteMovieManager.isFavorite(this, movie.slug)
            } else false
            binding.btnPlayerFav.setColorFilter(if (isFav) android.graphics.Color.parseColor("#FFD700") else android.graphics.Color.WHITE)
        }
        updateFavIcon()

        binding.btnPlayerFav.setOnClickListener {
            if (isTv && channelId.isNotEmpty()) {
                val isFav = com.huycabuonca.mobile.api.MovieRepository.toggleChannelFavorite(this, channelId)
                updateFavIcon()
                android.widget.Toast.makeText(this, if (isFav) "⭐ Đã thêm vào Kênh Yêu Thích" else "Đã bỏ khỏi Kênh Yêu Thích", android.widget.Toast.LENGTH_SHORT).show()
            } else if (movie != null) {
                val isFav = com.huycabuonca.mobile.util.FavoriteMovieManager.toggleFavorite(this, movie)
                updateFavIcon()
                android.widget.Toast.makeText(this, if (isFav) "❤️ Đã thêm vào Phim Yêu Thích" else "Đã bỏ khỏi Phim Yêu Thích", android.widget.Toast.LENGTH_SHORT).show()
            }
        }

        if (isM3u8) {
            initExoPlayer(streamUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }

        scheduleHideOverlays()
    }

    private fun initExoPlayer(url: String) {
        binding.playerView.visibility = View.VISIBLE
        binding.webViewPlayer.visibility = View.GONE
        binding.playerProgress.visibility = View.VISIBLE

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
                        binding.playerProgress.visibility = View.VISIBLE
                    } else {
                        binding.playerProgress.visibility = View.GONE
                    }
                }
            })
        }
        binding.playerView.player = player
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun initWebViewPlayer(url: String) {
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
                KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER -> {
                    if (p.isPlaying) p.pause() else p.play()
                    return true
                }
                else -> {}
            }
        }
        return super.onKeyDown(keyCode, event)
    }

    private fun showOverlays() {
        binding.layoutWatermark.visibility = View.VISIBLE
    }

    private fun hideOverlays() {
        binding.layoutWatermark.visibility = View.GONE
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

    private fun savePlaybackHistory() {
        val movie = intent.getSerializableExtra("EXTRA_MOVIE_ITEM") as? com.huycabuonca.mobile.model.MovieItem
        if (movie != null) {
            val ep = intent.getStringExtra("EXTRA_EPISODE") ?: ""
            val pos = player?.currentPosition ?: 0L
            val dur = player?.duration ?: 0L
            com.huycabuonca.mobile.util.WatchHistoryManager.saveHistory(
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
        player?.release()
        player = null
        binding.webViewPlayer.destroy()
    }
}
