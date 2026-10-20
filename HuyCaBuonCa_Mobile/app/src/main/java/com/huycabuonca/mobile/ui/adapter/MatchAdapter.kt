package com.huycabuonca.mobile.ui.adapter

import android.content.Context
import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
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
        val txtTeamA: TextView = view.findViewById(R.id.txtTeamA)
        val txtScore: TextView = view.findViewById(R.id.txtMatchScore)
        val txtTeamB: TextView = view.findViewById(R.id.txtTeamB)
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
        holder.txtTeamA.text = match.teamA
        holder.txtScore.text = match.score
        holder.txtTeamB.text = match.teamB
        holder.txtChannel.text = "⚡ 4 Server (Thập Cẩm, Xôi Lạc, Về Bờ, Vệ Tinh)"

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

        // Chỉ đặt thông báo cho đúng trận này
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
