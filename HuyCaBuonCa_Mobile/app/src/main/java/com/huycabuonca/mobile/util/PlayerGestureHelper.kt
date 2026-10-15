package com.huycabuonca.mobile.util

import android.app.Activity
import android.content.Context
import android.media.AudioManager
import android.os.Handler
import android.os.Looper
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.View
import android.widget.ImageView
import android.widget.TextView
import androidx.media3.exoplayer.ExoPlayer
import com.huycabuonca.mobile.R
import kotlin.math.abs

class PlayerGestureHelper(
    private val activity: Activity,
    private val touchView: View,
    private val overlayLayout: View,
    private val iconView: ImageView,
    private val infoView: TextView,
    private val playerGetter: () -> ExoPlayer?,
    private val onSingleTap: () -> Unit
) {

    private val audioManager = activity.getSystemService(Context.AUDIO_SERVICE) as AudioManager
    private val maxVolume = audioManager.getStreamMaxVolume(AudioManager.STREAM_MUSIC).coerceAtLeast(1)
    private val handler = Handler(Looper.getMainLooper())
    private val hideRunnable = Runnable { overlayLayout.visibility = View.GONE }

    private var initialVolume = -1
    private var initialBrightness = -1f
    private var activeMode = Mode.NONE
    var isLocked = false
    var isBrightnessGestureEnabled = true
    var isVolumeGestureEnabled = true
    var seekStepSeconds = 10

    private enum class Mode {
        NONE, VOLUME, BRIGHTNESS
    }

    private val gestureDetector = GestureDetector(activity, object : GestureDetector.SimpleOnGestureListener() {

        override fun onDown(e: MotionEvent): Boolean {
            if (isLocked) return false
            initialVolume = audioManager.getStreamVolume(AudioManager.STREAM_MUSIC)
            initialBrightness = activity.window.attributes.screenBrightness
            if (initialBrightness < 0) initialBrightness = 0.5f // Default
            activeMode = Mode.NONE
            return true
        }

        override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
            onSingleTap()
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            val player = playerGetter() ?: return false
            val width = touchView.width.toFloat()
            val currentPos = player.currentPosition
            val duration = player.duration
            val stepMs = seekStepSeconds * 1000L

            if (e.x < width / 2f) {
                // Double tap LEFT: Tua lùi
                val target = (currentPos - stepMs).coerceAtLeast(0)
                player.seekTo(target)
                showOverlay(R.drawable.ic_seek_rewind, "Tua lùi ${seekStepSeconds}s (◄◄)")
            } else {
                // Double tap RIGHT: Tua tới
                val target = if (duration > 0) (currentPos + stepMs).coerceAtMost(duration) else currentPos + stepMs
                player.seekTo(target)
                showOverlay(R.drawable.ic_seek_forward, "Tua tới ${seekStepSeconds}s (►►)")
            }
            return true
        }

        override fun onScroll(
            e1: MotionEvent?,
            e2: MotionEvent,
            distanceX: Float,
            distanceY: Float
        ): Boolean {
            if (e1 == null) return false

            val width = touchView.width.toFloat()
            val height = touchView.height.toFloat()
            if (height <= 0 || width <= 0) return false

            val deltaY = e1.y - e2.y
            val deltaX = e1.x - e2.x

            if (activeMode == Mode.NONE) {
                if (abs(deltaY) > abs(deltaX) && abs(deltaY) > 20) {
                    if (e1.x < width / 2f && isBrightnessGestureEnabled) {
                        activeMode = Mode.BRIGHTNESS
                    } else if (e1.x >= width / 2f && isVolumeGestureEnabled) {
                        activeMode = Mode.VOLUME
                    } else {
                        return false
                    }
                } else {
                    return false
                }
            }

            val percentChange = (deltaY / height) * 1.5f

            when (activeMode) {
                Mode.BRIGHTNESS -> {
                    var newBrightness = (initialBrightness + percentChange).coerceIn(0.02f, 1.0f)
                    val lp = activity.window.attributes
                    lp.screenBrightness = newBrightness
                    activity.window.attributes = lp
                    val percent = (newBrightness * 100).toInt()
                    showOverlay(R.drawable.ic_brightness, "Độ sáng: $percent%")
                }
                Mode.VOLUME -> {
                    val volumeChange = (percentChange * maxVolume).toInt()
                    val targetVolume = (initialVolume + volumeChange).coerceIn(0, maxVolume)
                    audioManager.setStreamVolume(AudioManager.STREAM_MUSIC, targetVolume, 0)
                    val percent = ((targetVolume.toFloat() / maxVolume) * 100).toInt()
                    showOverlay(R.drawable.ic_volume, "Âm lượng: $percent%")
                }
                else -> {}
            }

            return true
        }
    })

    init {
        touchView.setOnTouchListener { _, event ->
            if (isLocked) {
                return@setOnTouchListener false
            }
            gestureDetector.onTouchEvent(event)
            if (event.action == MotionEvent.ACTION_UP || event.action == MotionEvent.ACTION_CANCEL) {
                activeMode = Mode.NONE
                scheduleHide()
            }
            true
        }
    }

    private fun showOverlay(iconRes: Int, text: String) {
        handler.removeCallbacks(hideRunnable)
        iconView.setImageResource(iconRes)
        infoView.text = text
        overlayLayout.visibility = View.VISIBLE
    }

    private fun scheduleHide() {
        handler.removeCallbacks(hideRunnable)
        handler.postDelayed(hideRunnable, 1000)
    }
}
