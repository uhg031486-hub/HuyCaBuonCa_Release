package com.huycabuonca.tv.ui

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.View
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
import com.huycabuonca.tv.ui.adapter.EpisodeAdapter
import com.huycabuonca.tv.util.TvFocusUtil
import com.huycabuonca.tv.util.WatchHistoryManager
import kotlinx.coroutines.launch

class DetailActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDetailBinding
    private lateinit var episodeAdapter: EpisodeAdapter
    private var movieItem: MovieItem? = null
    private var movieDetail: MovieDetail? = null

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
            val firstEp = movieDetail?.servers?.firstOrNull()?.episodes?.firstOrNull()
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
                val allEps = detail.servers.flatMap { it.episodes }
                episodeAdapter.submitList(allEps)
                binding.txtEpisodesHeader.text = "Danh sách tập (${allEps.size} tập):"

                var targetEp: EpisodeItem? = null
                if (!resumeEpisodeName.isNullOrEmpty()) {
                    targetEp = allEps.find {
                        it.name.equals(resumeEpisodeName, ignoreCase = true) ||
                        it.slug.equals(resumeEpisodeName, ignoreCase = true)
                    }
                    if (targetEp == null) {
                        val epNum = Regex("\\d+").find(resumeEpisodeName ?: "")?.value
                        if (epNum != null) {
                            targetEp = allEps.find { Regex("\\d+").find(it.name)?.value == epNum }
                        }
                    }
                }

                val epToPlay = targetEp ?: allEps.firstOrNull()
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
            } else {
                binding.txtDetailDesc.text = "Không tải được thông tin chi tiết phim."
            }
        }
    }

    private fun playEpisode(episode: EpisodeItem, startPositionMs: Long = 0L) {
        val allEps = movieDetail?.servers?.flatMap { it.episodes } ?: emptyList()
        val currentIndex = allEps.indexOfFirst { it.slug == episode.slug || it.name == episode.name }.coerceAtLeast(0)

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
                            putExtra("EXTRA_EPISODES_LIST", ArrayList(allEps))
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
            putExtra("EXTRA_EPISODES_LIST", ArrayList(allEps))
            putExtra("EXTRA_CURRENT_EPISODE_INDEX", currentIndex)
            putExtra("EXTRA_MOVIE_ITEM", movieItem)
            putExtra("EXTRA_START_POSITION", startPositionMs)
        }
        startActivity(intent)
    }
}
