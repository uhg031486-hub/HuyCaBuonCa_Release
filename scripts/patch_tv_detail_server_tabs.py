import sys

path = "HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/ui/DetailActivity.kt"

content = """package com.huycabuonca.tv.ui

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import com.bumptech.glide.Glide
import com.huycabuonca.tv.R
import com.huycabuonca.tv.api.MovieRepository
import com.huycabuonca.tv.databinding.ActivityDetailBinding
import com.huycabuonca.tv.model.EpisodeItem
import com.huycabuonca.tv.model.MovieDetail
import com.huycabuonca.tv.model.MovieItem
import com.huycabuonca.tv.model.MovieSource
import com.huycabuonca.tv.model.ServerGroup
import com.huycabuonca.tv.ui.adapter.EpisodeAdapter
import com.huycabuonca.tv.util.TvFocusUtil
import com.huycabuonca.tv.util.WatchHistoryManager
import kotlinx.coroutines.launch

class DetailActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDetailBinding
    private lateinit var episodeAdapter: EpisodeAdapter
    private var movieItem: MovieItem? = null
    private var movieDetail: MovieDetail? = null

    // Quản lý đa server (Phụ đề / Vietsub / Thuyết Minh)
    private var currentServerIndex = 0
    private val currentEpisodes = mutableListOf<EpisodeItem>()

    // Quản lý xem tiếp đúng tập và đúng vị trí
    private var resumeEpisodeName: String? = null
    private var resumePositionMs: Long = 0L
    private var shouldAutoPlay: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

        movieItem = intent.getSerializableExtra("EXTRA_MOVIE") as? MovieItem
        if (movieItem == null) {
            finish()
            return
        }

        resumeEpisodeName = intent.getStringExtra("EXTRA_RESUME_EPISODE")
        resumePositionMs = intent.getLongExtra("EXTRA_RESUME_POSITION", 0L)
        shouldAutoPlay = intent.getBooleanExtra("EXTRA_AUTO_PLAY", false)

        if (resumeEpisodeName.isNullOrEmpty()) {
            val hist = WatchHistoryManager.getHistoryForMovie(this, movieItem?.slug ?: "")
                ?: WatchHistoryManager.getHistoryForMovie(this, movieItem?.id ?: "")
            if (hist != null) {
                resumeEpisodeName = hist.episodeName
                resumePositionMs = hist.positionMs
            }
        }

        setupUI()
        loadDetail()
    }

    private fun setupUI() {
        TvFocusUtil.setupFocusScale(binding.btnPlayFirst)
        TvFocusUtil.setupFocusScale(binding.btnFavDetail)
        TvFocusUtil.setupFocusScale(binding.btnBack)

        binding.btnBack.setOnClickListener { finish() }

        val movie = movieItem!!
        binding.txtDetailTitle.text = movie.name
        binding.txtDetailQuality.text = if (movie.quality.isNotEmpty()) movie.quality else "HD"
        binding.txtDetailMeta.text = "Năm: ${movie.year} • Nguồn: ${movie.source.displayName}"

        val isTv = movie.source == MovieSource.XEMTIVI
        val updateFavBtnText = {
            val isFav = if (isTv) MovieRepository.isChannelFavorite(this, movie.id)
            else com.huycabuonca.tv.util.FavoriteMovieManager.isFavorite(this, movie.slug)
            if (isFav) {
                binding.btnFavDetail.text = if (isTv) "★ Đã Thích (Kênh)" else "★ Đã Yêu Thích"
                binding.btnFavDetail.setTextColor(Color.parseColor("#FFD700"))
            } else {
                binding.btnFavDetail.text = if (isTv) "+ Thêm Kênh Yêu Thích" else "♡ Thêm Vào Yêu Thích"
                binding.btnFavDetail.setTextColor(Color.parseColor("#FFFFFF"))
            }
        }
        updateFavBtnText()

        binding.btnFavDetail.setOnClickListener {
            if (isTv) {
                val isFav = MovieRepository.toggleChannelFavorite(this, movie.id)
                val msg = if (isFav) "★ Đã thêm [${movie.name}] vào Kênh Yêu Thích!" else "Đã xóa khỏi Kênh Yêu Thích"
                Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
            } else {
                val isFav = com.huycabuonca.tv.util.FavoriteMovieManager.toggleFavorite(this, movie)
                val msg = if (isFav) "★ Đã thêm [${movie.name}] vào Phim Yêu Thích!" else "Đã xóa khỏi Phim Yêu Thích"
                Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
            }
            updateFavBtnText()
        }

        val imgUrl = if (movie.posterUrl.isNotEmpty()) movie.posterUrl else movie.thumbUrl
        Glide.with(this)
            .load(imgUrl)
            .placeholder(R.drawable.bg_focus_card)
            .into(binding.imgDetailPoster)

        episodeAdapter = EpisodeAdapter { episode ->
            val isResumeEp = !resumeEpisodeName.isNullOrEmpty() && (
                episode.name.equals(resumeEpisodeName, ignoreCase = true) ||
                episode.slug.equals(resumeEpisodeName, ignoreCase = true)
            )
            val startPos = if (isResumeEp) resumePositionMs else 0L
            playEpisode(episode, startPos)
        }

        binding.recyclerEpisodes.layoutManager = GridLayoutManager(this, 6)
        binding.recyclerEpisodes.adapter = episodeAdapter

        if (!resumeEpisodeName.isNullOrEmpty()) {
            val timeStr = if (resumePositionMs > 5000L) {
                val min = (resumePositionMs / 60000).toInt()
                val sec = ((resumePositionMs % 60000) / 1000).toInt()
                " (%02d:%02d)".format(min, sec)
            } else ""
            binding.btnPlayFirst.text = "▶ XEM TIẾP $resumeEpisodeName$timeStr"
        } else {
            binding.btnPlayFirst.text = "▶ XEM PHIM"
        }

        binding.btnPlayFirst.setOnClickListener {
            val firstEp = currentEpisodes.firstOrNull()
            if (firstEp != null) {
                playEpisode(firstEp, 0L)
            } else {
                Toast.makeText(this, "Chưa tải xong danh sách tập!", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnPlayFirst.requestFocus()
    }

    private fun loadDetail() {
        val movie = movieItem ?: return
        binding.progressEpisodes.visibility = View.VISIBLE

        lifecycleScope.launch {
            val detail = MovieRepository.getMovieDetail(movie.source, movie.slug)
            binding.progressEpisodes.visibility = View.GONE
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
        if (servers.isEmpty()) {
            binding.layoutServersContainer.visibility = View.GONE
            return
        }

        binding.layoutServersContainer.visibility = View.VISIBLE
        val density = resources.displayMetrics.density

        servers.forEachIndexed { index, server ->
            val rawName = server.serverName
            val isVietsub = rawName.contains("vietsub", ignoreCase = true) ||
                            rawName.contains("phụ đề", ignoreCase = true) ||
                            rawName.contains("sub", ignoreCase = true)
            val isThuyetMinh = rawName.contains("thuyết minh", ignoreCase = true) ||
                               rawName.contains("tm", ignoreCase = true)
            val isLongTieng = rawName.contains("lồng tiếng", ignoreCase = true) ||
                              rawName.contains("lt", ignoreCase = true)
            val cleanTitle = when {
                isVietsub -> "🇻🇳 [Phụ Đề] $rawName"
                isThuyetMinh -> "🎙️ [Thuyết Minh] $rawName"
                isLongTieng -> "🗣️ [Lồng Tiếng] $rawName"
                else -> "📺 $rawName"
            }

            val serverTab = TextView(this).apply {
                val padH = (14 * density).toInt()
                val padV = (8 * density).toInt()
                setPadding(padH, padV, padH, padV)
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply {
                    setMargins(0, 0, (10 * density).toInt(), 0)
                }
                setBackgroundResource(R.drawable.bg_btn_selector)
                text = cleanTitle
                textSize = 12f
                setTypeface(null, android.graphics.Typeface.BOLD)
                gravity = android.view.Gravity.CENTER
                isClickable = true
                isFocusable = true
                isSelected = (index == currentServerIndex)
                setTextColor(if (isSelected) Color.BLACK else Color.WHITE)

                TvFocusUtil.setupFocusScale(this, 1.06f)

                setOnFocusChangeListener { v, hasFocus ->
                    if (hasFocus) {
                        setTextColor(Color.BLACK)
                        v.animate().scaleX(1.06f).scaleY(1.06f).setDuration(120).start()
                    } else {
                        val isCurr = (index == currentServerIndex)
                        setTextColor(if (isCurr) Color.BLACK else Color.WHITE)
                        v.animate().scaleX(1.0f).scaleY(1.0f).setDuration(120).start()
                    }
                }

                setOnClickListener {
                    for (i in 0 until binding.layoutServers.childCount) {
                        val child = binding.layoutServers.getChildAt(i) as? TextView
                        child?.isSelected = false
                        child?.setTextColor(Color.WHITE)
                    }
                    isSelected = true
                    setTextColor(Color.BLACK)
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
        for (i in 0 until binding.layoutServers.childCount) {
            val child = binding.layoutServers.getChildAt(i) as? TextView
            val isCurrent = (i == serverIndex)
            child?.isSelected = isCurrent
            if (child?.hasFocus() != true) {
                child?.setTextColor(if (isCurrent) Color.BLACK else Color.WHITE)
            }
        }

        currentEpisodes.clear()
        currentEpisodes.addAll(servers[serverIndex].episodes)
        episodeAdapter.submitList(currentEpisodes.toList())

        val sName = servers[serverIndex].serverName
        binding.txtEpisodesHeader.text = "Danh sách tập - $sName (${currentEpisodes.size} tập):"

        var targetEp: EpisodeItem? = null
        if (!resumeEpisodeName.isNullOrEmpty()) {
            targetEp = currentEpisodes.find {
                it.name.equals(resumeEpisodeName, ignoreCase = true) ||
                it.slug.equals(resumeEpisodeName, ignoreCase = true)
            }
            if (targetEp == null) {
                val epNum = Regex("\\\\d+").find(resumeEpisodeName ?: "")?.value
                if (epNum != null) {
                    targetEp = currentEpisodes.find { Regex("\\\\d+").find(it.name)?.value == epNum }
                }
            }
        }

        val epToPlay = targetEp ?: currentEpisodes.firstOrNull()
        if (targetEp != null) {
            val timeStr = if (resumePositionMs > 5000L) {
                val min = (resumePositionMs / 60000).toInt()
                val sec = ((resumePositionMs % 60000) / 1000).toInt()
                " (%02d:%02d)".format(min, sec)
            } else ""
            binding.btnPlayFirst.text = "▶ XEM TIẾP ${targetEp.name}$timeStr"
        } else {
            binding.btnPlayFirst.text = "▶ XEM PHIM"
        }

        binding.btnPlayFirst.setOnClickListener {
            if (epToPlay != null) {
                val pos = if (targetEp != null) resumePositionMs else 0L
                playEpisode(epToPlay, pos)
            } else {
                Toast.makeText(this@DetailActivity, "Chưa tải xong danh sách tập!", Toast.LENGTH_SHORT).show()
            }
        }

        if (shouldAutoPlay && epToPlay != null) {
            shouldAutoPlay = false
            val pos = if (targetEp != null) resumePositionMs else 0L
            playEpisode(epToPlay, pos)
        }
    }

    private fun playEpisode(episode: EpisodeItem, startPositionMs: Long = 0L) {
        val currentIndex = currentEpisodes.indexOfFirst { it.slug == episode.slug || it.name == episode.name }.coerceAtLeast(0)

        val streamUrl = episode.linkM3u8 ?: episode.linkEmbed
        if (streamUrl.isNullOrEmpty()) {
            Toast.makeText(this, getString(R.string.no_stream_found), Toast.LENGTH_SHORT).show()
            return
        }

        if (streamUrl.startsWith("freereels_unlock:")) {
            val tokens = streamUrl.split(":")
            if (tokens.size >= 3) {
                binding.progressEpisodes.visibility = View.VISIBLE
                lifecycleScope.launch {
                    val res = MovieRepository.unlockFreeReelsEpisode(tokens[1], tokens[2])
                    binding.progressEpisodes.visibility = View.GONE
                    if (res != null && res.streamUrl.isNotEmpty()) {
                        val intent = Intent(this@DetailActivity, PlayerActivity::class.java).apply {
                            putExtra("EXTRA_STREAM_URL", res.streamUrl)
                            putExtra("EXTRA_SUBTITLE_URL", res.subtitleUrl ?: episode.subtitleUrl)
                            putExtra("EXTRA_IS_M3U8", true)
                            putExtra("EXTRA_TITLE", movieItem?.name ?: "Phim Ngắn")
                            putExtra("EXTRA_EPISODE", episode.name)
                            putExtra("EXTRA_SOURCE", movieItem?.source?.name)
                            putExtra("EXTRA_CHANNEL_ID", movieItem?.id)
                            putExtra("EXTRA_EPISODES_LIST", ArrayList(currentEpisodes))
                            putExtra("EXTRA_CURRENT_EPISODE_INDEX", currentIndex)
                            putExtra("EXTRA_MOVIE_ITEM", movieItem)
                            putExtra("EXTRA_START_POSITION", startPositionMs)
                        }
                        startActivity(intent)
                    } else {
                        Toast.makeText(this@DetailActivity, "Không thể tải luồng phát tập này, vui lòng thử lại!", Toast.LENGTH_SHORT).show()
                    }
                }
                return
            }
        }

        val intent = Intent(this, PlayerActivity::class.java).apply {
            putExtra("EXTRA_STREAM_URL", streamUrl)
            putExtra("EXTRA_SUBTITLE_URL", episode.subtitleUrl)
            putExtra("EXTRA_EMBED_URL", episode.linkEmbed)
            putExtra("EXTRA_IS_M3U8", episode.linkM3u8 != null)
            putExtra("EXTRA_TITLE", movieItem?.name ?: "Xem Phim")
            putExtra("EXTRA_EPISODE", episode.name)
            putExtra("EXTRA_SOURCE", movieItem?.source?.name)
            putExtra("EXTRA_CHANNEL_ID", movieItem?.id)
            putExtra("EXTRA_EPISODES_LIST", ArrayList(currentEpisodes))
            putExtra("EXTRA_CURRENT_EPISODE_INDEX", currentIndex)
            putExtra("EXTRA_MOVIE_ITEM", movieItem)
            putExtra("EXTRA_START_POSITION", startPositionMs)
        }
        startActivity(intent)
    }
}
"""

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("DetailActivity.kt written successfully!")
