package com.huycabuonca.tv.util

import android.view.View
import androidx.core.view.ViewCompat

object TvFocusUtil {
    fun setupFocusScale(view: View, scale: Float = 1.08f) {
        view.setOnFocusChangeListener { v, hasFocus ->
            if (hasFocus) {
                ViewCompat.animate(v)
                    .scaleX(scale)
                    .scaleY(scale)
                    .translationZ(12f)
                    .setDuration(150)
                    .start()
            } else {
                ViewCompat.animate(v)
                    .scaleX(1.0f)
                    .scaleY(1.0f)
                    .translationZ(0f)
                    .setDuration(150)
                    .start()
            }
        }
    }
}
