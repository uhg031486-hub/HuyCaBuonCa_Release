package com.huycabuonca.tv.ui

import android.content.Intent
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
import com.huycabuonca.tv.ui.adapter.EpisodeAdapter
import com.huycabuonca.tv.util.TvFocusUtil
import kotlinx.coroutines.launch

class DetailActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDetailBinding
    private lateinit var episodeAdapter: EpisodeAdapter
    private var movieItem: MovieItem? = null
    private var movieDetail: MovieDetail? = null

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
        TvFocusUtil.setupFocusScale(binding.btnPlayFirst)
        TvFocusUtil.setupFocusScale(binding.btnBack)

        binding.btnBack.setOnClickListener { finish() }

        val movie = movieItem!!
        binding.txtDetailTitle.text = movie.name
        binding.txtDetailQuality.text = if (movie.quality.isNotEmpty()) movie.quality else "HD"
        binding.txtDetailMeta.text = "Năm: ${movie.year} • Nguồn: ${movie.source.displayName}"

        val imgUrl = if (movie.posterUrl.isNotEmpty()) movie.posterUrl else movie.thumbUrl
        Glide.with(this)
            .load(imgUrl)
            .placeholder(R.drawable.bg_focus_card)
            .into(binding.imgDetailPoster)

        episodeAdapter = EpisodeAdapter { episode ->
            playEpisode(episode)
        }

        binding.recyclerEpisodes.layoutManager = GridLayoutManager(this, 6)
        binding.recyclerEpisodes.adapter = episodeAdapter

        binding.btnPlayFirst.setOnClickListener {
            val firstEp = movieDetail?.servers?.firstOrNull()?.episodes?.firstOrNull()
            if (firstEp != null) {
                playEpisode(firstEp)
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
            } else {
                binding.txtDetailDesc.text = "Không tải được thông tin chi tiết phim."
            }
        }
    }

    private fun playEpisode(episode: EpisodeItem) {
        val streamUrl = episode.linkM3u8 ?: episode.linkEmbed
        if (streamUrl.isNullOrEmpty()) {
            Toast.makeText(this, getString(R.string.no_stream_found), Toast.LENGTH_SHORT).show()
            return
        }

        val intent = Intent(this, PlayerActivity::class.java).apply {
            putExtra("EXTRA_STREAM_URL", streamUrl)
            putExtra("EXTRA_EMBED_URL", episode.linkEmbed)
            putExtra("EXTRA_IS_M3U8", episode.linkM3u8 != null)
            putExtra("EXTRA_TITLE", movieItem?.name ?: "Xem Phim")
            putExtra("EXTRA_EPISODE", episode.name)
        }
        startActivity(intent)
    }
}
