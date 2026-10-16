package com.huycabuonca.mobile.ui

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.huycabuonca.mobile.R
import com.huycabuonca.mobile.api.MovieRepository
import com.huycabuonca.mobile.databinding.ActivityMainBinding
import com.huycabuonca.mobile.model.FilterItem
import com.huycabuonca.mobile.model.MovieItem
import com.huycabuonca.mobile.model.MovieSource
import com.huycabuonca.mobile.ui.adapter.MovieAdapter
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var adapter: MovieAdapter
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

        setupUI()
        setupSourceSelectors()
        updateDynamicFilters()
        loadMovies(reset = true)
    }

    private fun setupUI() {
        adapter = MovieAdapter { movie ->
            val intent = Intent(this, DetailActivity::class.java).apply {
                putExtra("EXTRA_MOVIE", movie)
            }
            startActivity(intent)
        }

        layoutManager = GridLayoutManager(this, 3)
        binding.recyclerMovies.layoutManager = layoutManager
        binding.recyclerMovies.adapter = adapter

        binding.swipeRefresh.setOnRefreshListener {
            loadMovies(reset = true)
        }

        // Infinite Scroll (Tải hết phim vô hạn khi người dùng cuộn xuống)
        binding.recyclerMovies.addOnScrollListener(object : RecyclerView.OnScrollListener() {
            override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
                super.onScrolled(recyclerView, dx, dy)
                if (dy > 0) {
                    val visibleItemCount = layoutManager.childCount
                    val totalItemCount = layoutManager.itemCount
                    val firstVisibleItemPosition = layoutManager.findFirstVisibleItemPosition()

                    if (!isLoading && !isLastPage && (visibleItemCount + firstVisibleItemPosition) >= totalItemCount - 6) {
                        loadMoreMovies()
                    }
                }
            }
        })

        binding.btnSearch.setOnClickListener {
            startActivity(Intent(this, SearchActivity::class.java))
        }
    }

    private fun setupSourceSelectors() {
        binding.btnSourceKKPhim.setOnClickListener {
            switchSource(MovieSource.KKPHIM)
        }

        binding.btnSourceAnimeHay.setOnClickListener {
            switchSource(MovieSource.ANIMEHAY)
        }

        binding.btnSourceKKPhim.isSelected = true
        binding.btnSourceAnimeHay.isSelected = false
    }

    private fun switchSource(source: MovieSource) {
        if (currentSource == source) return
        currentSource = source
        binding.btnSourceKKPhim.isSelected = (source == MovieSource.KKPHIM)
        binding.btnSourceAnimeHay.isSelected = (source == MovieSource.ANIMEHAY)

        updateDynamicFilters()
        loadMovies(reset = true)
    }

    // Cập nhật bộ lọc động thay đổi theo nguồn (Mô hình vBook)
    private fun updateDynamicFilters() {
        binding.layoutDynamicFilters.removeAllViews()
        val filters = MovieRepository.getFiltersForSource(currentSource)
        if (filters.isEmpty()) return

        currentFilterUrl = filters.first().endpointUrl

        filters.forEachIndexed { index, filter ->
            val filterBtn = Button(this).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    resources.getDimensionPixelSize(android.R.dimen.app_icon_size).coerceAtMost(90)
                ).apply {
                    setMargins(0, 0, 16, 0)
                }
                setBackgroundResource(R.drawable.bg_btn_selector)
                text = filter.title
                setTextColor(Color.WHITE)
                textSize = 11f
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
            val items = MovieRepository.getMovies(currentSource, currentFilterUrl, currentPage)
            binding.progressBar.visibility = View.GONE
            binding.swipeRefresh.isRefreshing = false
            isLoading = false

            if (items.isNotEmpty()) {
                movieList.addAll(items)
                adapter.submitList(movieList.toList())
                binding.txtStatus.visibility = View.GONE

                // Ở lần đầu, tải thêm trang 2 ngay lập tức để có sẵn nhiều phim
                if (reset && currentPage == 1 && items.size >= 10) {
                    loadMoreMovies()
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
            val items = MovieRepository.getMovies(currentSource, currentFilterUrl, currentPage)
            binding.progressLoadMore.visibility = View.GONE
            isLoading = false

            if (items.isNotEmpty()) {
                movieList.addAll(items)
                adapter.submitList(movieList.toList())
            } else {
                isLastPage = true
            }
        }
    }
}
