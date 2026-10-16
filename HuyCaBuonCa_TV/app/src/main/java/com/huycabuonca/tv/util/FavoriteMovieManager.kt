package com.huycabuonca.tv.util

import android.content.Context
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.huycabuonca.tv.model.MovieItem

object FavoriteMovieManager {

    private const val PREFS_NAME = "favorite_movies_prefs"
    private const val KEY_FAVORITES = "fav_movie_items_json"
    private val gson = Gson()

    fun isFavorite(context: Context, slug: String): Boolean {
        val list = getFavorites(context)
        return list.any { it.slug == slug || it.id == slug }
    }

    fun toggleFavorite(context: Context, movie: MovieItem): Boolean {
        val list = getFavorites(context).toMutableList()
        val index = list.indexOfFirst { it.slug == movie.slug || (it.id.isNotEmpty() && it.id == movie.id) }
        val isFav: Boolean
        if (index >= 0) {
            list.removeAt(index)
            isFav = false
        } else {
            list.add(0, movie)
            isFav = true
        }
        val sp = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        sp.edit().putString(KEY_FAVORITES, gson.toJson(list)).apply()
        return isFav
    }

    fun getFavorites(context: Context): List<MovieItem> {
        val sp = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val json = sp.getString(KEY_FAVORITES, null) ?: return emptyList()
        return try {
            val type = object : TypeToken<List<MovieItem>>() {}.type
            gson.fromJson(json, type) ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun removeFavorite(context: Context, slug: String) {
        val list = getFavorites(context).toMutableList()
        list.removeAll { it.slug == slug || it.id == slug }
        val sp = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        sp.edit().putString(KEY_FAVORITES, gson.toJson(list)).apply()
    }
}
