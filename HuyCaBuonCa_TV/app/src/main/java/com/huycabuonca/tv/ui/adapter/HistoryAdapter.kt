package com.huycabuonca.tv.ui.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.resource.drawable.DrawableTransitionOptions
import com.huycabuonca.tv.R
import com.huycabuonca.tv.databinding.ItemHistoryTvBinding
import com.huycabuonca.tv.model.MovieSource
import com.huycabuonca.tv.util.HistoryItem
import com.huycabuonca.tv.util.TvFocusUtil

class HistoryAdapter(
    private val onItemClick: (HistoryItem) -> Unit,
    private val onItemLongClick: (HistoryItem) -> Unit
) : RecyclerView.Adapter<HistoryAdapter.HistoryViewHolder>() {

    private val items = mutableListOf<HistoryItem>()

    fun submitList(newItems: List<HistoryItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): HistoryViewHolder {
        val binding = ItemHistoryTvBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return HistoryViewHolder(binding)
    }

    override fun onBindViewHolder(holder: HistoryViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    inner class HistoryViewHolder(private val binding: ItemHistoryTvBinding) :
        RecyclerView.ViewHolder(binding.root) {

        init {
            TvFocusUtil.setupFocusScale(binding.root, 1.08f)
            binding.root.setOnClickListener {
                val pos = bindingAdapterPosition
                if (pos != RecyclerView.NO_POSITION) {
                    onItemClick(items[pos])
                }
            }
            binding.root.setOnLongClickListener {
                val pos = bindingAdapterPosition
                if (pos != RecyclerView.NO_POSITION) {
                    onItemLongClick(items[pos])
                    true
                } else false
            }
        }

        fun bind(item: HistoryItem) {
            val movie = item.movie
            binding.txtHistoryTitle.text = movie.name
            
            val epText = if (item.episodeName.isNotEmpty()) {
                if (movie.source == MovieSource.XEMTIVI) "📺 ${item.episodeName} • Xem tiếp"
                else "▶ ${item.episodeName} • Xem tiếp"
            } else "▶ Xem tiếp"
            binding.txtHistoryEpisode.text = epText

            if (item.durationMs > 0 && item.positionMs > 0) {
                val percent = ((item.positionMs.toFloat() / item.durationMs.toFloat()) * 100).toInt().coerceIn(5, 100)
                binding.progressHistoryBar.visibility = View.VISIBLE
                binding.progressHistoryBar.progress = percent
            } else if (movie.source == MovieSource.XEMTIVI) {
                binding.progressHistoryBar.visibility = View.GONE
                binding.txtHistoryBadge.text = "TRUYỀN HÌNH"
            } else {
                binding.progressHistoryBar.visibility = View.GONE
                binding.txtHistoryBadge.text = "ĐANG XEM"
            }

            val imgUrl = if (movie.posterUrl.isNotEmpty()) movie.posterUrl else movie.thumbUrl
            val defaultTvLogo = "https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png"
            val finalImg = if (movie.source == MovieSource.XEMTIVI && imgUrl.isEmpty()) defaultTvLogo else imgUrl

            Glide.with(binding.imgHistoryThumb.context)
                .load(finalImg)
                .transition(DrawableTransitionOptions.withCrossFade())
                .placeholder(R.drawable.bg_focus_card)
                .error(R.drawable.bg_btn_secondary)
                .into(binding.imgHistoryThumb)
        }
    }
}
