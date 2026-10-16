package com.huycabuonca.mobile.ui

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.huycabuonca.mobile.R
import com.huycabuonca.mobile.api.MovieRepository
import com.huycabuonca.mobile.databinding.ActivityMainBinding
import com.huycabuonca.mobile.model.FilterItem
import com.huycabuonca.mobile.model.MovieItem
import com.huycabuonca.mobile.model.MovieSource
import com.huycabuonca.mobile.ui.adapter.MatchAdapter
import com.huycabuonca.mobile.ui.adapter.MovieAdapter
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

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

        MovieRepository.initTvChannels(this)

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

        binding.btnSchedule.setOnClickListener {
            showScheduleDialog()
        }

        binding.btnCustomIptv.setOnClickListener {
            showAddCustomIptvDialog()
        }

        binding.btnBackupSync.setOnClickListener {
            showBackupSyncDialog()
        }

        // Tự động kiểm tra bản cập nhật mới (In-App Auto Update)
        com.huycabuonca.mobile.util.AppUpdateManager.checkForUpdate(this)
    }

    private fun showScheduleDialog() {
        val matches = MovieRepository.getLiveMatches()
        val dialog = androidx.appcompat.app.AlertDialog.Builder(this).create()
        val view = layoutInflater.inflate(R.layout.dialog_football_schedule, null)
        dialog.setView(view)

        val recycler = view.findViewById<RecyclerView>(R.id.recyclerMatches)
        recycler.layoutManager = LinearLayoutManager(this)
        recycler.adapter = MatchAdapter(matches) { match ->
            dialog.dismiss()
            lifecycleScope.launch(Dispatchers.IO) {
                val allTv = MovieRepository.getAllTvChannels(this@MainActivity)
                val found = allTv.find { it.id == match.channelSlug }
                    ?: allTv.find { it.name.contains(match.channelName, ignoreCase = true) }
                    ?: allTv.find { it.name.contains("VTV6", ignoreCase = true) || it.name.contains("Bóng", ignoreCase = true) }

                withContext(Dispatchers.Main) {
                    if (found != null) {
                        val defaultTvLogo = "https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png"
                        val finalLogo = if (found.logo.isNotEmpty()) found.logo else defaultTvLogo
                        val movieItem = MovieItem(
                            id = found.id,
                            name = "${found.name} - ${match.teamA} vs ${match.teamB}",
                            slug = found.id,
                            originName = "[${match.tournament}]",
                            thumbUrl = finalLogo,
                            posterUrl = finalLogo,
                            year = "2026",
                            quality = "LIVE",
                            episodeCurrent = "Trực Tiếp",
                            source = MovieSource.XEMTIVI
                        )
                        startActivity(Intent(this@MainActivity, DetailActivity::class.java).apply {
                            putExtra("EXTRA_MOVIE", movieItem)
                        })
                    } else {
                        Toast.makeText(this@MainActivity, "Kênh trực tiếp cho trận này đang chuẩn bị phát sóng!", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }

        view.findViewById<Button>(R.id.btnCloseSchedule).setOnClickListener {
            dialog.dismiss()
        }

        dialog.show()
    }

    private fun showAddCustomIptvDialog() {
        val dialog = androidx.appcompat.app.AlertDialog.Builder(this).create()
        val view = layoutInflater.inflate(R.layout.dialog_custom_iptv, null)
        dialog.setView(view)

        val edtName = view.findViewById<android.widget.EditText>(R.id.edtChannelName)
        val edtUrl = view.findViewById<android.widget.EditText>(R.id.edtChannelUrl)

        view.findViewById<Button>(R.id.btnCancelIptv).setOnClickListener {
            dialog.dismiss()
        }

        view.findViewById<Button>(R.id.btnAddIptvConfirm).setOnClickListener {
            val name = edtName.text.toString().trim()
            val content = edtUrl.text.toString().trim()
            if (content.isEmpty()) {
                Toast.makeText(this, "Vui lòng nhập đường dẫn luồng hoặc nội dung M3U!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (content.contains("#EXTINF") || content.contains("#EXTM3U")) {
                val count = MovieRepository.importM3uPlaylist(this, content)
                Toast.makeText(this, "Đã nhập thành công $count kênh từ danh sách M3U!", Toast.LENGTH_LONG).show()
            } else {
                val channelName = if (name.isNotEmpty()) name else "Kênh Tự Thêm"
                MovieRepository.addCustomChannel(this, channelName, content)
                Toast.makeText(this, "Đã thêm kênh: $channelName!", Toast.LENGTH_SHORT).show()
            }
            dialog.dismiss()
            switchSource(MovieSource.XEMTIVI)
        }

        dialog.show()
    }

    private fun showBackupSyncDialog() {
        val dialog = androidx.appcompat.app.AlertDialog.Builder(this).create()
        val view = layoutInflater.inflate(R.layout.dialog_backup_sync, null)
        dialog.setView(view)

        val edtJson = view.findViewById<android.widget.EditText>(R.id.edtBackupJson)
        val btnExport = view.findViewById<Button>(R.id.btnExportJson)
        val btnImport = view.findViewById<Button>(R.id.btnImportJson)
        val btnClose = view.findViewById<Button>(R.id.btnCloseBackup)

        btnExport.setOnClickListener {
            val json = MovieRepository.exportBackupData(this)
            edtJson.setText(json)
            val clipboard = getSystemService(android.content.Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
            val clip = android.content.ClipData.newPlainText("HuyCaBuonCa_Backup", json)
            clipboard.setPrimaryClip(clip)
            Toast.makeText(this, "Đã xuất dữ liệu và sao chép vào bộ nhớ tạm (Clipboard)!", Toast.LENGTH_LONG).show()
        }

        btnImport.setOnClickListener {
            val json = edtJson.text.toString().trim()
            if (json.isEmpty()) {
                Toast.makeText(this, "Vui lòng dán mã JSON cần khôi phục vào ô trống!", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val ok = MovieRepository.restoreBackupData(this, json)
            if (ok) {
                Toast.makeText(this, "Khôi phục dữ liệu thành công!", Toast.LENGTH_SHORT).show()
                dialog.dismiss()
                loadMovies(reset = true)
            } else {
                Toast.makeText(this, "Mã JSON không hợp lệ, vui lòng kiểm tra lại!", Toast.LENGTH_LONG).show()
            }
        }

        btnClose.setOnClickListener { dialog.dismiss() }
        dialog.show()
    }

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
                lifecycleScope.launch(Dispatchers.IO) {
                    val channels = MovieRepository.getAllTvChannels(this@MainActivity)
                    val lastCh = channels.find { it.id == lastId }
                    if (lastCh != null) {
                        withContext(Dispatchers.Main) {
                            Toast.makeText(this@MainActivity, "📺 Kênh bạn xem gần nhất: ${lastCh.name}", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            }
        }

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
            val items = MovieRepository.getMovies(currentSource, currentFilterUrl, currentPage, this@MainActivity)
            binding.progressBar.visibility = View.GONE
            binding.swipeRefresh.isRefreshing = false
            isLoading = false

            if (items.isNotEmpty()) {
                val existingIds = movieList.map { it.id }.toSet()
                val newItems = items.filter { it.id !in existingIds }
                if (newItems.isNotEmpty()) {
                    movieList.addAll(newItems)
                    adapter.submitList(movieList.toList())
                    binding.txtStatus.visibility = View.GONE

                    // Ở lần đầu, tải thêm trang 2 ngay lập tức để có sẵn nhiều phim
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
                    adapter.submitList(movieList.toList())
                } else {
                    isLastPage = true
                }
            } else {
                isLastPage = true
            }
        }
    }
}
