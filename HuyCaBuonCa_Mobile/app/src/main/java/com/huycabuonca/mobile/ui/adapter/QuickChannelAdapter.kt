package com.huycabuonca.mobile.ui.adapter

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.huycabuonca.mobile.R
import com.huycabuonca.mobile.api.TvChannelItem

class QuickChannelAdapter(
    private var currentId: String,
    private val onChannelClick: (TvChannelItem) -> Unit
) : RecyclerView.Adapter<QuickChannelAdapter.VH>() {

    private var channels = listOf<TvChannelItem>()

    fun submit(list: List<TvChannelItem>) {
        channels = list
        notifyDataSetChanged()
    }

    fun updateCurrent(newId: String) {
        currentId = newId
        notifyDataSetChanged()
    }

    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val imgLogo: ImageView = v.findViewById(R.id.imgQuickChannelLogo)
        val txtName: TextView = v.findViewById(R.id.txtQuickChannelName)
        val txtGroup: TextView = v.findViewById(R.id.txtQuickChannelGroup)
        val txtBadge: TextView = v.findViewById(R.id.txtQuickStatusBadge)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_quick_channel, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val ch = channels[position]
        holder.txtName.text = ch.name
        holder.txtGroup.text = ch.group

        val isCurrent = ch.id == currentId || ch.url == currentId
        if (isCurrent) {
            holder.itemView.setBackgroundResource(R.drawable.bg_focus_card)
            holder.txtName.setTextColor(Color.parseColor("#FFD700"))
            holder.txtBadge.visibility = View.VISIBLE
            holder.txtBadge.text = "Đang phát 🟢"
        } else {
            holder.itemView.setBackgroundResource(R.drawable.bg_btn_secondary)
            holder.txtName.setTextColor(Color.WHITE)
            holder.txtBadge.visibility = View.GONE
        }

        val defaultTvLogo = "file:///android_asset/logos/vtv1.png"
        Glide.with(holder.itemView.context)
            .load(if (!ch.logo.isNullOrEmpty()) ch.logo else defaultTvLogo)
            .placeholder(R.drawable.bg_focus_card)
            .error(R.drawable.bg_btn_secondary)
            .into(holder.imgLogo)

        holder.itemView.setOnClickListener {
            onChannelClick(ch)
        }
    }

    override fun getItemCount(): Int = channels.size
}
