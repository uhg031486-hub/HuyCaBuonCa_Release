package com.huycabuonca.tv.util

import android.content.Context
import android.graphics.Rect
import android.os.Handler
import android.os.Looper
import android.view.View
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView

/**
 * LayoutManager chuyên dụng cho Android TV Box:
 * 1. Khắc phục triệt để lỗi giật / nhảy con trỏ lên đầu màn hình khi cuộn remote nhanh.
 * 2. Tự động canh giữa (Center Align) dòng phim đang focus để luôn nhìn thấy trước dòng phim tiếp theo.
 * 3. Chặn focus thất thoát (Focus Trap) khi ở biên trái, phải và đáy của danh sách phim.
 */
class TvGridLayoutManager(
    context: Context,
    spanCount: Int
) : GridLayoutManager(context, spanCount) {

    private val mainHandler = Handler(Looper.getMainLooper())

    init {
        // Tải trước 3 hàng phim (21 view) trong bộ nhớ đệm để cuộn siêu mượt
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = spanCount * 3
    }

    override fun onInterceptFocusSearch(focused: View, direction: Int): View? {
        val fromPos = getPosition(focused)
        if (fromPos == RecyclerView.NO_POSITION) {
            return super.onInterceptFocusSearch(focused, direction)
        }

        val totalCount = itemCount
        val spans = spanCount

        when (direction) {
            View.FOCUS_DOWN -> {
                val targetPos = fromPos + spans
                if (targetPos < totalCount) {
                    val targetView = findViewByPosition(targetPos)
                    if (targetView != null && targetView.isFocusable) {
                        return targetView
                    }
                    // View bên dưới chưa kịp render do remote lướt nhanh:
                    // Cuộn tới vị trí mục tiêu và giữ focus ở view hiện tại, TUYỆT ĐỐI không để focus rơi lên đầu!
                    scrollToPosition(targetPos)
                    mainHandler.postDelayed({
                        findViewByPosition(targetPos)?.requestFocus()
                    }, 50)
                    return focused
                } else {
                    // Đã ở hàng cuối cùng của toàn bộ danh sách: chặn không cho focus nhảy lên thanh filter
                    return focused
                }
            }

            View.FOCUS_UP -> {
                val targetPos = fromPos - spans
                if (targetPos >= 0) {
                    val targetView = findViewByPosition(targetPos)
                    if (targetView != null && targetView.isFocusable) {
                        return targetView
                    }
                    scrollToPosition(targetPos)
                    mainHandler.postDelayed({
                        findViewByPosition(targetPos)?.requestFocus()
                    }, 50)
                    return focused
                }
                // Nếu đang ở hàng đầu tiên (fromPos < spans): cho phép focus di chuyển lên thanh filter bên trên
                return super.onInterceptFocusSearch(focused, direction)
            }

            View.FOCUS_LEFT -> {
                if (fromPos % spans == 0) {
                    // Cột đầu tiên bên trái: không cho focus thoát ra ngoài
                    return focused
                }
            }

            View.FOCUS_RIGHT -> {
                if ((fromPos % spans == spans - 1) || (fromPos == totalCount - 1)) {
                    // Cột cuối cùng bên phải: không cho focus thoát ra ngoài
                    return focused
                }
            }
        }

        return super.onInterceptFocusSearch(focused, direction)
    }

    /**
     * Tự động canh giữa (Vertical Center Scroll) thẻ phim đang được chọn
     * Giúp người dùng TV Box luôn có tầm nhìn thoáng, không bị khuất viền dưới.
     */
    override fun requestChildRectangleOnScreen(
        parent: RecyclerView,
        child: View,
        rect: Rect,
        immediate: Boolean,
        focusedChildVisible: Boolean
    ): Boolean {
        val parentHeight = parent.height
        val childTop = child.top
        val childBottom = child.bottom
        val childHeight = childBottom - childTop

        val targetTop = (parentHeight - childHeight) / 2
        val dy = childTop - targetTop

        if (dy != 0) {
            if (immediate) {
                parent.scrollBy(0, dy)
            } else {
                parent.smoothScrollBy(0, dy)
            }
            return true
        }
        return false
    }
}
