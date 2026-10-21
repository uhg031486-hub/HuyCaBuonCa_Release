package com.huycabuonca.tv.ui

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.huycabuonca.tv.R
import com.huycabuonca.tv.api.MovieRepository
import com.huycabuonca.tv.databinding.ActivityMainBinding
import com.huycabuonca.tv.model.FilterItem
import com.huycabuonca.tv.model.MovieItem
import com.huycabuonca.tv.model.MovieSource
import com.huycabuonca.tv.ui.adapter.HistoryAdapter
import com.huycabuonca.tv.ui.adapter.MovieAdapter
import com.huycabuonca.tv.util.FavoriteMovieManager
import com.huycabuonca.tv.util.TvFocusUtil
import com.huycabuonca.tv.util.WatchHistoryManager
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var adapter: MovieAdapter
    private lateinit var historyAdapter: HistoryAdapter
    private lateinit var layoutManager: GridLayoutManager

    private var currentSource = MovieSource.KKPHIM
    private var currentFilterUrl = "https://phimapi.com/danh-sach/phim-moi-cap-nhat"
    private var currentPage = 1
    private val movieList = mutableListOf<MovieItem>()
    private var isLoading = false
    private var isLastPage = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        MovieRepository.initTvChannels(this)

        setupUI()
        setupSourceSelectors()
        updateDynamicFilters()
        loadMovies(reset = true)

        // Tự động kiểm tra bản cập nhật mới trên GitHub Release (In-App Auto Update)
        com.huycabuonca.tv.util.AppUpdateManager.checkForUpdate(this)
    }

    private fun setupUI() {
        TvFocusUtil.setupFocusScale(binding.btnSourceKKPhim)
        TvFocusUtil.setupFocusScale(binding.btnSourceAnimeHay)
        TvFocusUtil.setupFocusScale(binding.btnSourceXemTiVi)
        TvFocusUtil.setupFocusScale(binding.btnSourceFreeReels)
        TvFocusUtil.setupFocusScale(binding.btnSearch)
        TvFocusUtil.setupFocusScale(binding.btnClearHistory)

        historyAdapter = HistoryAdapter(
            onItemClick = { item ->
                if (item.movie.source == MovieSource.XEMTIVI) {
                    playTvChannelDirectly(item.movie)
                } else {
                    val intent = Intent(this, DetailActivity::class.java).apply {
                        putExtra("EXTRA_MOVIE", item.movie)
                    }
                    startActivity(intent)
                }
            },
            onItemLongClick = { item ->
                WatchHistoryManager.removeHistoryItem(this, item.movie.slug.ifEmpty { item.movie.id })
                loadHistory()
                Toast.makeText(this, "Đã xóa khỏi lịch sử xem", Toast.LENGTH_SHORT).show()
            }
        )
        binding.recyclerHistory.layoutManager = LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)
        binding.recyclerHistory.adapter = historyAdapter

        binding.btnClearHistory.setOnClickListener {
            WatchHistoryManager.clearHistory(this)
            loadHistory()
            Toast.makeText(this, "Đã xóa toàn bộ lịch sử xem", Toast.LENGTH_SHORT).show()
        }

        adapter = MovieAdapter(
            onMovieClick = { movie ->
                if (movie.source == MovieSource.XEMTIVI) {
                    playTvChannelDirectly(movie)
                } else {
                    val intent = Intent(this, DetailActivity::class.java).apply {
                        putExtra("EXTRA_MOVIE", movie)
                    }
                    startActivity(intent)
                }
            },
            onMovieLongClick = { movie ->
                if (movie.source == MovieSource.XEMTIVI) {
                    val isFav = MovieRepository.toggleChannelFavorite(this, movie.id)
                    val msg = if (isFav) "⭐ Đã thêm [${movie.name}] vào Kênh Yêu Thích!" else "Đã xóa khỏi Kênh Yêu Thích"
                    Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
                    if (currentFilterUrl == "tv://favorites") {
                        loadMovies(reset = true)
                    }
                } else {
                    val isFav = FavoriteMovieManager.toggleFavorite(this, movie)
                    val msg = if (isFav) "❤️ Đã thêm [${movie.name}] vào Phim Yêu Thích!" else "Đã xóa khỏi Phim Yêu Thích"
                    Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
                    if (currentFilterUrl == "app://favorites") {
                        loadMovies(reset = true)
                    }
                }
            }
        )

        // 7 cột card nhỏ gọn để hiển thị được 3 đến 4 hàng phim trên màn hình TV Box
        layoutManager = GridLayoutManager(this, 7)
        binding.recyclerMovies.layoutManager = layoutManager
        binding.recyclerMovies.adapter = adapter

        // Infinite Scroll cho TV Box (Tải hàng ngàn phim khi cuộn remote)
        binding.recyclerMovies.addOnScrollListener(object : RecyclerView.OnScrollListener() {
            override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
                super.onScrolled(recyclerView, dx, dy)
                val visibleItemCount = layoutManager.childCount
                val totalItemCount = layoutManager.itemCount
                val firstVisibleItemPosition = layoutManager.findFirstVisibleItemPosition()

                if (!isLoading && !isLastPage && (visibleItemCount + firstVisibleItemPosition) >= totalItemCount - 6) {
                    loadMoreMovies()
                }
            }
        })

        binding.btnSearch.setOnClickListener {
            startActivity(Intent(this, SearchActivity::class.java))
        }
    }

    override fun onResume() {
        super.onResume()
        loadHistory()
        adapter.notifyDataSetChanged()
    }

    private fun loadHistory() {
        val history = WatchHistoryManager.getHistory(this)
        if (history.isNotEmpty()) {
            binding.layoutContinueWatching.visibility = View.VISIBLE
            historyAdapter.submitList(history)
        } else {
            binding.layoutContinueWatching.visibility = View.GONE
        }
    }

    private fun playTvChannelDirectly(movie: MovieItem) {
        val channels = MovieRepository.getAllTvChannels(this)
        val channel = channels.find { it.id == movie.id || it.name.equals(movie.name, ignoreCase = true) }
        if (channel != null && channel.url.isNotEmpty()) {
            MovieRepository.setLastWatchedChannelId(this, channel.id)
            WatchHistoryManager.saveHistory(
                context = this,
                movie = movie,
                episodeName = channel.group
            )
            val intent = Intent(this, PlayerActivity::class.java).apply {
                putExtra("EXTRA_STREAM_URL", channel.url)
                putExtra("EXTRA_IS_M3U8", true)
                putExtra("EXTRA_TITLE", channel.name)
                putExtra("EXTRA_EPISODE", channel.group)
                putExtra("EXTRA_SOURCE", MovieSource.XEMTIVI.name)
                putExtra("EXTRA_CHANNEL_ID", channel.id)
                putExtra("EXTRA_MOVIE_ITEM", movie)
            }
            startActivity(intent)
        } else {
            Toast.makeText(this, "Không tìm thấy luồng phát của kênh này", Toast.LENGTH_SHORT).show()
        }
    }

    private var currentAnimeSubSource = "anime_sub://vietsub"

    private fun setupSourceSelectors() {
        binding.btnSourceKKPhim.setOnClickListener {
            switchSource(MovieSource.KKPHIM)
        }

        binding.btnSourceAnimeHay.setOnClickListener {
            switchSource(MovieSource.ANIMEHAY)
        }

        binding.btnSourceXemTiVi.setOnClickListener {
            switchSource(MovieSource.XEMTIVI)
        }

        binding.btnSourceFreeReels.setOnClickListener {
            switchSource(MovieSource.FREEREELS)
        }

        val textColors = ContextCompat.getColorStateList(this, R.color.selector_btn_text)
        binding.btnSourceKKPhim.setTextColor(textColors)
        binding.btnSourceAnimeHay.setTextColor(textColors)
        binding.btnSourceXemTiVi.setTextColor(textColors)
        binding.btnSourceFreeReels.setTextColor(textColors)

        binding.btnSourceKKPhim.isSelected = true
        binding.btnSourceAnimeHay.isSelected = false
        binding.btnSourceXemTiVi.isSelected = false
        binding.btnSourceFreeReels.isSelected = false
    }

    private fun switchSource(source: MovieSource) {
        if (currentSource == source) return
        currentSource = source
        binding.btnSourceKKPhim.isSelected = (source == MovieSource.KKPHIM)
        binding.btnSourceAnimeHay.isSelected = (source == MovieSource.ANIMEHAY)
        binding.btnSourceXemTiVi.isSelected = (source == MovieSource.XEMTIVI)
        binding.btnSourceFreeReels.isSelected = (source == MovieSource.FREEREELS)

        if (source == MovieSource.XEMTIVI) {
            val lastId = MovieRepository.getLastWatchedChannelId(this)
            if (!lastId.isNullOrEmpty()) {
                val lastChannel = MovieRepository.getAllTvChannels(this).find { it.id == lastId }
                if (lastChannel != null) {
                    android.widget.Toast.makeText(
                        this,
                        "📺 Kênh xem gần nhất: ${lastChannel.name} • [${lastChannel.group}]",
                        android.widget.Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }

        if (source == MovieSource.ANIMEHAY) {
            binding.scrollAnimeSubSources.visibility = View.VISIBLE
            setupSubSources(MovieRepository.getAnimeSubSources())
        } else if (source == MovieSource.FREEREELS) {
            binding.scrollAnimeSubSources.visibility = View.VISIBLE
            setupSubSources(MovieRepository.getShortDramaSubSources())
        } else {
            binding.scrollAnimeSubSources.visibility = View.GONE
            updateDynamicFilters()
            loadMovies(reset = true)
        }
    }

    private var currentSubSource: String = ""

    private fun setupSubSources(subSources: List<FilterItem>) {
        binding.layoutAnimeSubSources.removeAllViews()
        if (subSources.isEmpty()) return
        currentSubSource = subSources.first().endpointUrl
        val textColors = ContextCompat.getColorStateList(this, R.color.selector_btn_text)

        subSources.forEachIndexed { index, sub ->
            val subBtn = Button(this).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    resources.getDimensionPixelSize(android.R.dimen.app_icon_size).coerceAtMost(90)
                ).apply {
                    setMargins(0, 0, 16, 0)
                }
                setBackgroundResource(R.drawable.bg_btn_selector)
                isFocusable = true
                TvFocusUtil.setupFocusScale(this)
                text = sub.title
                setTextColor(textColors)
                textSize = 11f
                typeface = Typeface.DEFAULT_BOLD
                isSelected = (index == 0)

                setOnClickListener {
                    for (i in 0 until binding.layoutAnimeSubSources.childCount) {
                        binding.layoutAnimeSubSources.getChildAt(i).isSelected = false
                    }
                    isSelected = true
                    currentSubSource = sub.endpointUrl
                    updateSubSourceFilters(currentSubSource)
                }
            }
            binding.layoutAnimeSubSources.addView(subBtn)
        }
        updateSubSourceFilters(currentSubSource)
    }

    private fun updateSubSourceFilters(subSourceUrl: String) {
        binding.layoutDynamicFilters.removeAllViews()
        val filters = if (currentSource == MovieSource.ANIMEHAY) {
            MovieRepository.getAnimeFilters(subSourceUrl)
        } else {
            MovieRepository.getShortDramaFilters(subSourceUrl)
        }
        if (filters.isEmpty()) return

        currentFilterUrl = filters.first().endpointUrl
        val textColors = ContextCompat.getColorStateList(this, R.color.selector_btn_text)

        filters.forEachIndexed { index, filter ->
            val filterBtn = Button(this).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    resources.getDimensionPixelSize(android.R.dimen.app_icon_size).coerceAtMost(90)
                ).apply {
                    setMargins(0, 0, 16, 0)
                }
                setBackgroundResource(R.drawable.bg_btn_selector)
                isFocusable = true
                TvFocusUtil.setupFocusScale(this)
                text = filter.title
                setTextColor(textColors)
                textSize = 12f
                typeface = Typeface.DEFAULT_BOLD
                isSelected = (index == 0)

                setOnClickListener {
                    for (i in 0 until binding.layoutDynamicFilters.childCount) {
                        binding.layoutDynamicFilters.getChildAt(i).isSelected = false
                    }
                    isSelected = true
                    currentFilterUrl = filter.endpointUrl
                    loadMovies(reset = true)
                }
            }
            binding.layoutDynamicFilters.addView(filterBtn)
        }
        loadMovies(reset = true)
    }

    private fun updateDynamicFilters() {
        binding.layoutDynamicFilters.removeAllViews()
        val filters = MovieRepository.getFiltersForSource(currentSource)
        if (filters.isEmpty()) return

        currentFilterUrl = filters.first().endpointUrl
        val textColors = ContextCompat.getColorStateList(this, R.color.selector_btn_text)

        filters.forEachIndexed { index, filter ->
            val filterBtn = Button(this).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    resources.getDimensionPixelSize(android.R.dimen.app_icon_size).coerceAtMost(90)
                ).apply {
                    setMargins(0, 0, 16, 0)
                }
                setBackgroundResource(R.drawable.bg_btn_selector)
                isFocusable = true
                TvFocusUtil.setupFocusScale(this)
                text = filter.title
                setTextColor(textColors)
                textSize = 12f
                typeface = Typeface.DEFAULT_BOLD
                isSelected = (index == 0)

                setOnClickListener {
                    for (i in 0 until binding.layoutDynamicFilters.childCount) {
                        binding.layoutDynamicFilters.getChildAt(i).isSelected = false
                    }
                    isSelected = true
                    currentFilterUrl = filter.endpointUrl
                    loadMovies(reset = true)
                }
            }
            binding.layoutDynamicFilters.addView(filterBtn)
        }
    }

    private fun loadMovies(reset: Boolean) {
        if (isLoading) return
        isLoading = true

        if (reset) {
            currentPage = 1
            isLastPage = false
            movieList.clear()
            adapter.submitList(emptyList())
            binding.progressBar.visibility = View.VISIBLE
            binding.txtStatus.visibility = View.GONE
        }

        lifecycleScope.launch {
            val items = MovieRepository.getMovies(currentSource, currentFilterUrl, currentPage, this@MainActivity)
            binding.progressBar.visibility = View.GONE
            isLoading = false

            if (items.isNotEmpty()) {
                val existingIds = movieList.map { it.id }.toSet()
                val newItems = items.filter { it.id !in existingIds }
                if (newItems.isNotEmpty()) {
                    movieList.addAll(newItems)
                    adapter.submitList(movieList.toList())
                    binding.txtStatus.visibility = View.GONE

                    // Ở lần đầu, tải trước trang 2 để có sẵn nhiều phim cho người dùng cuộn mượt
                    if (reset && currentPage == 1 && items.size >= 10) {
                        loadMoreMovies()
                    }
                } else {
                    isLastPage = true
                }
            } else if (movieList.isEmpty()) {
                binding.txtStatus.visibility = View.VISIBLE
                binding.txtStatus.text = getString(R.string.error_loading)
            } else {
                isLastPage = true
            }
        }
    }

    private fun loadMoreMovies() {
        if (isLoading || isLastPage) return
        isLoading = true
        currentPage++
        binding.progressLoadMore.visibility = View.VISIBLE

        lifecycleScope.launch {
            val items = MovieRepository.getMovies(currentSource, currentFilterUrl, currentPage, this@MainActivity)
            binding.progressLoadMore.visibility = View.GONE
            isLoading = false

            if (items.isNotEmpty()) {
                val existingIds = movieList.map { it.id }.toSet()
                val newItems = items.filter { it.id !in existingIds }
                if (newItems.isNotEmpty()) {
                    movieList.addAll(newItems)
                    adapter.addItems(newItems)
                } else {
                    isLastPage = true
                }
            } else {
                isLastPage = true
            }
        }
    }
}
