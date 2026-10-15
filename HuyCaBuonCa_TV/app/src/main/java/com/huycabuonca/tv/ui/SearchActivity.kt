package com.huycabuonca.tv.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import com.huycabuonca.tv.api.MovieRepository
import com.huycabuonca.tv.databinding.ActivitySearchBinding
import com.huycabuonca.tv.ui.adapter.MovieAdapter
import com.huycabuonca.tv.util.TvFocusUtil
import kotlinx.coroutines.launch

class SearchActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySearchBinding
    private lateinit var adapter: MovieAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySearchBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
    }

    private fun setupUI() {
        TvFocusUtil.setupFocusScale(binding.btnSearchBack)
        TvFocusUtil.setupFocusScale(binding.btnDoSearch)
        TvFocusUtil.setupFocusScale(binding.edtKeyword)

        binding.btnSearchBack.setOnClickListener { finish() }

        adapter = MovieAdapter { movie ->
            val intent = Intent(this, DetailActivity::class.java).apply {
                putExtra("EXTRA_MOVIE", movie)
            }
            startActivity(intent)
        }

        binding.recyclerSearchResults.layoutManager = GridLayoutManager(this, 5)
        binding.recyclerSearchResults.adapter = adapter

        binding.btnDoSearch.setOnClickListener { doSearch() }

        binding.edtKeyword.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                doSearch()
                true
            } else {
                false
            }
        }

        binding.edtKeyword.requestFocus()
    }

    private fun doSearch() {
        val query = binding.edtKeyword.text.toString().trim()
        if (query.isEmpty()) return

        binding.searchProgress.visibility = View.VISIBLE
        binding.txtSearchEmpty.visibility = View.GONE
        adapter.submitList(emptyList())

        lifecycleScope.launch {
            val results = MovieRepository.searchMovies(query)
            binding.searchProgress.visibility = View.GONE
            if (results.isNotEmpty()) {
                adapter.submitList(results)
                binding.txtSearchEmpty.visibility = View.GONE
            } else {
                binding.txtSearchEmpty.visibility = View.VISIBLE
                binding.txtSearchEmpty.text = "Không tìm thấy phim phù hợp với từ khóa: \"$query\""
            }
        }
    }
}
