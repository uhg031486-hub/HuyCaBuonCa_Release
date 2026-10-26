package com.huycabuonca.mobile.ui.adapter

import android.content.Context
import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.huycabuonca.mobile.R
import com.huycabuonca.mobile.model.FootballMatch

class MatchAdapter(
    private val matches: List<FootballMatch>,
    private val onMatchClick: (FootballMatch) -> Unit,
    private val onReminderToggle: ((FootballMatch, Boolean) -> Unit)? = null
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
        val btnReminder: TextView = view.findViewById(R.id.btnMatchReminder)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MatchViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_match, parent, false)
        return MatchViewHolder(view)
    }

    override fun onBindViewHolder(holder: MatchViewHolder, position: Int) {
        val match = matches[position]
        val context = holder.itemView.context
        val sp = context.getSharedPreferences("match_reminders_prefs", Context.MODE_PRIVATE)
        var isReminderSet = sp.getBoolean("remind_${match.id}", false)

        holder.txtTournament.text = match.tournament
        holder.txtTime.text = match.time

        if (match.isLive || match.time.contains("LIVE") || match.time.contains("🔴")) {
            holder.txtTime.setBackgroundColor(Color.parseColor("#D32F2F"))
            holder.txtTime.text = if (match.time.contains("🔴")) match.time else "🔴 LIVE"
        } else if (match.time.contains("Hết Giờ") || match.time.contains("FT")) {
            holder.txtTime.setBackgroundColor(Color.parseColor("#37474F"))
            holder.txtTime.text = "🏁 Hết Giờ"
        } else {
            holder.txtTime.setBackgroundColor(Color.parseColor("#1565C0"))
        }

        holder.txtTeamA.text = match.teamA
        holder.txtScore.text = match.score
        holder.txtTeamB.text = match.teamB
        holder.txtChannel.text = "⚡ 4 Server (Thập Cẩm, Xôi Lạc, Về Bờ, Vệ Tinh)"

        if (match.logoA.isNotEmpty()) {
            Glide.with(context).load(match.logoA).into(holder.imgTeamA)
            holder.imgTeamA.visibility = View.VISIBLE
        } else {
            holder.imgTeamA.visibility = View.GONE
        }

        if (match.logoB.isNotEmpty()) {
            Glide.with(context).load(match.logoB).into(holder.imgTeamB)
            holder.imgTeamB.visibility = View.VISIBLE
        } else {
            holder.imgTeamB.visibility = View.GONE
        }

        fun updateReminderUI(active: Boolean) {
            if (active) {
                holder.btnReminder.text = "🔔 Đã Đặt"
                holder.btnReminder.setTextColor(Color.parseColor("#FFD700"))
                holder.btnReminder.setBackgroundColor(Color.parseColor("#4D3800"))
            } else {
                holder.btnReminder.text = "🔔 Báo Giờ Đá"
                holder.btnReminder.setTextColor(Color.parseColor("#CBD5E1"))
                holder.btnReminder.setBackgroundColor(Color.parseColor("#243048"))
            }
        }

        updateReminderUI(isReminderSet)

        holder.btnReminder.setOnClickListener {
            isReminderSet = !isReminderSet
            sp.edit().putBoolean("remind_${match.id}", isReminderSet).apply()
            updateReminderUI(isReminderSet)
            onReminderToggle?.invoke(match, isReminderSet)
        }

        holder.itemView.setOnClickListener {
            onMatchClick(match)
        }
    }

    override fun getItemCount(): Int = matches.size
}
