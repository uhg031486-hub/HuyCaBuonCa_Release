package com.huycabuonca.tv.ui.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.huycabuonca.tv.R
import com.huycabuonca.tv.model.FootballMatch

class MatchAdapter(
    private val matches: List<FootballMatch>,
    private val onMatchClick: (FootballMatch) -> Unit
) : RecyclerView.Adapter<MatchAdapter.MatchViewHolder>() {

    class MatchViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val txtTournament: TextView = view.findViewById(R.id.txtMatchTournament)
        val txtTime: TextView = view.findViewById(R.id.txtMatchTime)
        val imgTeamA: ImageView = view.findViewById(R.id.imgTeamA)
        val txtTeamA: TextView = view.findViewById(R.id.txtTeamA)
        val txtScore: TextView = view.findViewById(R.id.txtMatchScore)
        val txtTeamB: TextView = view.findViewById(R.id.txtTeamB)
        val imgTeamB: ImageView = view.findViewById(R.id.imgTeamB)
        val txtChannel: TextView = view.findViewById(R.id.txtMatchChannel)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MatchViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_match, parent, false)
        return MatchViewHolder(view)
    }

    override fun onBindViewHolder(holder: MatchViewHolder, position: Int) {
        val match = matches[position]
        holder.txtTournament.text = match.tournament
        holder.txtTime.text = match.time

        if (match.isLive || match.time.contains("LIVE") || match.time.contains("🔴")) {
            holder.txtTime.setBackgroundColor(android.graphics.Color.parseColor("#D32F2F"))
            holder.txtTime.text = if (match.time.contains("🔴")) match.time else "🔴 LIVE"
        } else if (match.time.contains("Hết Giờ") || match.time.contains("FT")) {
            holder.txtTime.setBackgroundColor(android.graphics.Color.parseColor("#37474F"))
            holder.txtTime.text = "🏁 Hết Giờ"
        } else {
            holder.txtTime.setBackgroundColor(android.graphics.Color.parseColor("#1565C0"))
        }

        holder.txtTeamA.text = match.teamA
        holder.txtScore.text = match.score
        holder.txtTeamB.text = match.teamB
        holder.txtChannel.text = "📺 Kênh: ${match.channelName} • Bấm OK để xem"

        if (match.logoA.isNotEmpty()) {
            Glide.with(holder.itemView.context)
                .load(match.logoA)
                .into(holder.imgTeamA)
            holder.imgTeamA.visibility = View.VISIBLE
        } else {
            holder.imgTeamA.visibility = View.GONE
        }

        if (match.logoB.isNotEmpty()) {
            Glide.with(holder.itemView.context)
                .load(match.logoB)
                .into(holder.imgTeamB)
            holder.imgTeamB.visibility = View.VISIBLE
        } else {
            holder.imgTeamB.visibility = View.GONE
        }

        holder.itemView.setOnFocusChangeListener { v, hasFocus ->
            v.scaleX = if (hasFocus) 1.02f else 1.0f
            v.scaleY = if (hasFocus) 1.02f else 1.0f
        }

        holder.itemView.setOnClickListener {
            onMatchClick(match)
        }
    }

    override fun getItemCount(): Int = matches.size
}
