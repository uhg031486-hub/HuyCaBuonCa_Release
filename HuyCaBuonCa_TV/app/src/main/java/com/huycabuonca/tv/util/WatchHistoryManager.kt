package com.huycabuonca.tv.util

import android.content.Context
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.huycabuonca.tv.model.MovieItem
import java.io.Serializable

data class HistoryItem(
    val movie: MovieItem,
    val episodeName: String = "",
    val positionMs: Long = 0L,
    val durationMs: Long = 0L,
    val timestamp: Long = System.currentTimeMillis()
) : Serializable

object WatchHistoryManager {

    private const val PREFS_NAME = "watch_history_prefs"
    private const val KEY_HISTORY = "watch_history_items_json"
    private const val MAX_HISTORY_COUNT = 30
    private val gson = Gson()

    fun saveHistory(
        context: Context,
        movie: MovieItem,
        episodeName: String = "",
        positionMs: Long = 0L,
        durationMs: Long = 0L
    ) {
        val list = getHistory(context).toMutableList()
        // Xóa mục cũ nếu đã có (theo slug hoặc id)
        list.removeAll { it.movie.slug == movie.slug || (it.movie.id.isNotEmpty() && it.movie.id == movie.id) }
        
        // Thêm mục mới lên đầu
        val newItem = HistoryItem(
            movie = movie,
            episodeName = episodeName,
            positionMs = positionMs,
            durationMs = durationMs,
            timestamp = System.currentTimeMillis()
        )
        list.add(0, newItem)

        // Giới hạn số lượng
        val trimmedList = if (list.size > MAX_HISTORY_COUNT) list.subList(0, MAX_HISTORY_COUNT) else list

        val sp = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        sp.edit().putString(KEY_HISTORY, gson.toJson(trimmedList)).apply()
    }

    fun getHistory(context: Context): List<HistoryItem> {
        val sp = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val json = sp.getString(KEY_HISTORY, null) ?: return emptyList()
        return try {
            val type = object : TypeToken<List<HistoryItem>>() {}.type
            gson.fromJson(json, type) ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun clearHistory(context: Context) {
        val sp = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        sp.edit().remove(KEY_HISTORY).apply()
    }

    fun removeHistoryItem(context: Context, slug: String) {
        val list = getHistory(context).toMutableList()
        list.removeAll { it.movie.slug == slug || it.movie.id == slug }
        val sp = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        sp.edit().putString(KEY_HISTORY, gson.toJson(list)).apply()
    }
}
