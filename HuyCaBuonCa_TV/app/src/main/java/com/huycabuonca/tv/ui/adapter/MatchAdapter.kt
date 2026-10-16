package com.huycabuonca.tv.ui.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.huycabuonca.tv.R
import com.huycabuonca.tv.model.FootballMatch

class MatchAdapter(
    private val matches: List<FootballMatch>,
    private val onMatchClick: (FootballMatch) -> Unit
) : RecyclerView.Adapter<MatchAdapter.MatchViewHolder>() {

    class MatchViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val txtTournament: TextView = view.findViewById(R.id.txtMatchTournament)
        val txtTime: TextView = view.findViewById(R.id.txtMatchTime)
        val txtTeamA: TextView = view.findViewById(R.id.txtTeamA)
        val txtScore: TextView = view.findViewById(R.id.txtMatchScore)
        val txtTeamB: TextView = view.findViewById(R.id.txtTeamB)
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
        holder.txtTeamA.text = match.teamA
        holder.txtScore.text = match.score
        holder.txtTeamB.text = match.teamB
        holder.txtChannel.text = "📺 Kênh: ${match.channelName} • Bấm để xem trực tiếp"

        holder.itemView.setOnClickListener {
            onMatchClick(match)
        }
    }

    override fun getItemCount(): Int = matches.size
}
