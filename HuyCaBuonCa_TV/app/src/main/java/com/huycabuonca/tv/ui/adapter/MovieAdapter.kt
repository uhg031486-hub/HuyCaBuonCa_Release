package com.huycabuonca.tv.ui.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.resource.drawable.DrawableTransitionOptions
import com.huycabuonca.tv.R
import com.huycabuonca.tv.api.MovieRepository
import com.huycabuonca.tv.databinding.ItemMovieBinding
import com.huycabuonca.tv.model.MovieItem
import com.huycabuonca.tv.model.MovieSource
import com.huycabuonca.tv.util.FavoriteMovieManager
import com.huycabuonca.tv.util.ImageResolver
import com.huycabuonca.tv.util.TvFocusUtil

class MovieAdapter(
    private val onMovieClick: (MovieItem) -> Unit,
    private val onMovieLongClick: ((MovieItem) -> Unit)?
) : RecyclerView.Adapter<MovieAdapter.MovieViewHolder>() {

    constructor(onMovieClick: (MovieItem) -> Unit) : this(onMovieClick, null)

    private val items = mutableListOf<MovieItem>()

    init {
        stateRestorationPolicy = StateRestorationPolicy.PREVENT_WHEN_EMPTY
    }

    fun submitList(newItems: List<MovieItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    // Nạp thêm phần tử mới mà KHÔNG hủy các ViewHolder cũ -> GIỮ NGUYÊN VỊ TRÍ FOCUS CỦA REMOTE!
    fun addItems(newItems: List<MovieItem>) {
        if (newItems.isEmpty()) return
        val startPos = items.size
        items.addAll(newItems)
        notifyItemRangeInserted(startPos, newItems.size)
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
            binding.root.setOnLongClickListener {
                val pos = bindingAdapterPosition
                if (pos != RecyclerView.NO_POSITION && onMovieLongClick != null) {
                    onMovieLongClick.invoke(items[pos])
                    notifyItemChanged(pos)
                    true
                } else false
            }
        }

        fun bind(item: MovieItem) {
            val context = binding.root.context
            binding.txtTitle.text = item.name
            val yearText = if (item.year.isNotEmpty()) item.year else ""
            val epText = if (item.episodeCurrent.isNotEmpty()) " • ${item.episodeCurrent}" else ""
            binding.txtYear.text = "$yearText$epText"
            binding.txtQuality.text = if (item.quality.isNotEmpty()) item.quality else "HD"

            // Badge yêu thích
            if (item.source == MovieSource.XEMTIVI) {
                val isFav = MovieRepository.isChannelFavorite(context, item.id)
                if (isFav) {
                    binding.txtFavBadge.visibility = View.VISIBLE
                    binding.txtFavBadge.text = "⭐"
                } else {
                    binding.txtFavBadge.visibility = View.GONE
                }
            } else {
                val isFav = FavoriteMovieManager.isFavorite(context, item.slug)
                if (isFav) {
                    binding.txtFavBadge.visibility = View.VISIBLE
                    binding.txtFavBadge.text = "❤️"
                } else {
                    binding.txtFavBadge.visibility = View.GONE
                }
            }

            val isTv = item.source == MovieSource.XEMTIVI
            if (isTv) {
                binding.imgPoster.scaleType = android.widget.ImageView.ScaleType.FIT_CENTER
                val pad = (6 * binding.imgPoster.context.resources.displayMetrics.density).toInt()
                binding.imgPoster.setPadding(pad, pad, pad, pad)
            } else {
                binding.imgPoster.scaleType = android.widget.ImageView.ScaleType.CENTER_CROP
                binding.imgPoster.setPadding(0, 0, 0, 0)
            }

            val defaultTvLogo = "file:///android_asset/logos/tv_default_premium.png"
            val defaultErrorRes = if (isTv) R.mipmap.ic_launcher else R.drawable.bg_btn_secondary

            val primaryUrl = if (isTv) {
                item.posterUrl.ifEmpty { item.thumbUrl }.ifEmpty { defaultTvLogo }
            } else {
                ImageResolver.cleanAndResolve(item.posterUrl, item.thumbUrl)
            }

            val fallbackUrl = if (isTv) {
                defaultTvLogo
            } else {
                ImageResolver.cleanAndResolve(item.thumbUrl, item.posterUrl)
            }

            val primaryGlide = ImageResolver.buildGlideUrl(primaryUrl)
            val fallbackGlide = ImageResolver.buildGlideUrl(fallbackUrl)

            val fallbackRequest = if (fallbackUrl.isNotEmpty() && fallbackUrl != primaryUrl) {
                Glide.with(binding.imgPoster.context)
                    .load(fallbackGlide)
                    .transition(DrawableTransitionOptions.withCrossFade())
                    .error(defaultErrorRes)
            } else null

            val glideRequest = Glide.with(binding.imgPoster.context)
                .load(primaryGlide)
                .transition(DrawableTransitionOptions.withCrossFade())
                .placeholder(R.drawable.bg_focus_card)

            if (fallbackRequest != null) {
                glideRequest.error(fallbackRequest).into(binding.imgPoster)
            } else {
                glideRequest.error(defaultErrorRes).into(binding.imgPoster)
            }
        }
    }
}
