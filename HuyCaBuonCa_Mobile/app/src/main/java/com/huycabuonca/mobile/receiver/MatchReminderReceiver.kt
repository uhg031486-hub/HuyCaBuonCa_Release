package com.huycabuonca.mobile.receiver

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.media.RingtoneManager
import android.os.Build
import androidx.core.app.NotificationCompat
import com.huycabuonca.mobile.R
import com.huycabuonca.mobile.ui.MainActivity

class MatchReminderReceiver : BroadcastReceiver() {

    companion object {
        const val CHANNEL_ID = "match_reminders_channel"
        const val EXTRA_MATCH_ID = "extra_match_id"
        const val EXTRA_TEAM_A = "extra_team_a"
        const val EXTRA_TEAM_B = "extra_team_b"
        const val EXTRA_TIME_STR = "extra_time_str"
    }

    override fun onReceive(context: Context, intent: Intent) {
        val matchId = intent.getStringExtra(EXTRA_MATCH_ID) ?: return
        val teamA = intent.getStringExtra(EXTRA_TEAM_A) ?: "Đội nhà"
        val teamB = intent.getStringExtra(EXTRA_TEAM_B) ?: "Đội khách"
        val timeStr = intent.getStringExtra(EXTRA_TIME_STR) ?: "15 phút nữa"

        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // Tạo Notification Channel cho Android 8.0+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Nhắc Nhở Trận Đấu Trực Tiếp",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Thông báo cảnh báo trước 15 phút khi trận đấu bắt đầu"
                enableVibration(true)
                enableLights(true)
            }
            notificationManager.createNotificationChannel(channel)
        }

        // Intent mở MainActivity và hiển thị bảng chọn 4 Server cho đúng trận đấu này
        val openIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("OPEN_MATCH_ALERT", matchId)
            putExtra("ALERT_TEAM_A", teamA)
            putExtra("ALERT_TEAM_B", teamB)
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            matchId.hashCode(),
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
        )

        val soundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)

        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle("⚽ Sắp diễn ra: $teamA vs $teamB!")
            .setContentText("Trận đấu sẽ bắt đầu lúc $timeStr. Bấm để chọn Server xem ngay!")
            .setStyle(NotificationCompat.BigTextStyle().bigText("Trận đấu kinh điển giữa $teamA và $teamB sắp bắt đầu sau 15 phút nữa.\nBấm vào đây để chọn 1 trong 4 Server (Thập Cẩm, Xôi Lạc, Về Bờ, Vệ Tinh) xem trực tiếp miễn phí!"))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_EVENT)
            .setAutoCancel(true)
            .setSound(soundUri)
            .setVibrate(longArrayOf(0, 300, 200, 300))
            .setContentIntent(pendingIntent)
            .build()

        notificationManager.notify(matchId.hashCode(), notification)
    }
}
