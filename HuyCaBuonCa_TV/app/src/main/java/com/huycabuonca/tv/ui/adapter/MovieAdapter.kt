package com.huycabuonca.tv.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.resource.drawable.DrawableTransitionOptions
import com.huycabuonca.tv.R
import com.huycabuonca.tv.databinding.ItemMovieBinding
import com.huycabuonca.tv.model.MovieItem
import com.huycabuonca.tv.util.TvFocusUtil

class MovieAdapter(
    private val onMovieClick: (MovieItem) -> Unit
) : RecyclerView.Adapter<MovieAdapter.MovieViewHolder>() {

    private val items = mutableListOf<MovieItem>()

    fun submitList(newItems: List<MovieItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MovieViewHolder {
        val binding = ItemMovieBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return MovieViewHolder(binding)
    }

    override fun onBindViewHolder(holder: MovieViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    inner class MovieViewHolder(private val binding: ItemMovieBinding) :
        RecyclerView.ViewHolder(binding.root) {

        init {
            TvFocusUtil.setupFocusScale(binding.root, 1.08f)
            binding.root.setOnClickListener {
                val pos = bindingAdapterPosition
                if (pos != RecyclerView.NO_POSITION) {
                    onMovieClick(items[pos])
                }
            }
        }

        fun bind(item: MovieItem) {
            binding.txtTitle.text = item.name
            val yearText = if (item.year.isNotEmpty()) item.year else ""
            val epText = if (item.episodeCurrent.isNotEmpty()) " • ${item.episodeCurrent}" else ""
            binding.txtYear.text = "$yearText$epText"
            binding.txtQuality.text = if (item.quality.isNotEmpty()) item.quality else "HD"

            val imgUrl = if (item.posterUrl.isNotEmpty()) item.posterUrl else item.thumbUrl
            if (item.source == com.huycabuonca.tv.model.MovieSource.XEMTIVI) {
                binding.imgPoster.scaleType = android.widget.ImageView.ScaleType.FIT_CENTER
                val pad = (8 * binding.imgPoster.context.resources.displayMetrics.density).toInt()
                binding.imgPoster.setPadding(pad, pad, pad, pad)
            } else {
                binding.imgPoster.scaleType = android.widget.ImageView.ScaleType.CENTER_CROP
                binding.imgPoster.setPadding(0, 0, 0, 0)
            }
            val defaultTvLogo = "https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png"
            val finalImgUrl = if (item.source == com.huycabuonca.tv.model.MovieSource.XEMTIVI && imgUrl.isEmpty()) {
                defaultTvLogo
            } else {
                imgUrl
            }

            Glide.with(binding.imgPoster.context)
                .load(finalImgUrl)
                .transition(DrawableTransitionOptions.withCrossFade())
                .placeholder(R.drawable.bg_focus_card)
                .error(R.drawable.bg_btn_secondary)
                .into(binding.imgPoster)
        }
    }
}
