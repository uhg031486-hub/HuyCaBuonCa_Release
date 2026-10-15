package com.huycabuonca.mobile.ui

import android.annotation.SuppressLint
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
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

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
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
        binding.btnPlayerBack.setOnClickListener { finish() }

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
            val serverBtn = Button(this).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    resources.getDimensionPixelSize(android.R.dimen.app_icon_size).coerceAtMost(80)
                ).apply {
                    setMargins(0, 0, 12, 0)
                }
                setBackgroundResource(R.drawable.bg_btn_selector)
                text = server.serverName
                setTextColor(Color.WHITE)
                textSize = 11f
                isSelected = (index == 0)

                setOnClickListener {
                    for (i in 0 until binding.layoutServers.childCount) {
                        binding.layoutServers.getChildAt(i).isSelected = false
                    }
                    isSelected = true
                    switchServer(index)
                }
            }
            binding.layoutServers.addView(serverBtn)
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
