package com.huycabuonca.mobile.ui.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.huycabuonca.mobile.databinding.ItemEpisodeBinding
import com.huycabuonca.mobile.model.EpisodeItem
import com.huycabuonca.mobile.util.TvFocusUtil

class EpisodeAdapter(
    private val onEpisodeClick: (EpisodeItem) -> Unit
) : RecyclerView.Adapter<EpisodeAdapter.EpisodeViewHolder>() {

    private val items = mutableListOf<EpisodeItem>()

    fun submitList(newItems: List<EpisodeItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): EpisodeViewHolder {
        val binding = ItemEpisodeBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return EpisodeViewHolder(binding)
    }

    override fun onBindViewHolder(holder: EpisodeViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int = items.size

    inner class EpisodeViewHolder(private val binding: ItemEpisodeBinding) :
        RecyclerView.ViewHolder(binding.root) {

        init {
            TvFocusUtil.setupFocusScale(binding.btnEpisode, 1.12f)
            binding.btnEpisode.setOnClickListener {
                val pos = bindingAdapterPosition
                if (pos != RecyclerView.NO_POSITION) {
                    onEpisodeClick(items[pos])
                }
            }
        }

        fun bind(item: EpisodeItem) {
            var name = item.name.trim()
            if (!name.lowercase().contains("tập") && name.toIntOrNull() != null) {
                name = "Tập $name"
            }
            binding.btnEpisode.text = name
        }
    }
}
