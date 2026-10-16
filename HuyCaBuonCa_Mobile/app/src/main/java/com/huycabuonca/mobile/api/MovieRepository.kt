package com.huycabuonca.mobile.api

import android.content.Context
import com.google.gson.Gson
import com.google.gson.JsonObject
import com.google.gson.reflect.TypeToken
import com.huycabuonca.mobile.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.net.URLEncoder
import java.util.concurrent.TimeUnit

data class TvChannelItem(
    val id: String,
    val name: String,
    val group: String,
    val logo: String,
    val url: String
)

object MovieRepository {

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()
    private const val KKPHIM_IMG_BASE = "https://phimimg.com/"
    private var cachedTvChannels: List<TvChannelItem>? = null

    fun initTvChannels(context: Context) {
        if (cachedTvChannels != null) return
        try {
            val jsonString = context.assets.open("tv_channels.json").bufferedReader().use { it.readText() }
            val itemType = object : TypeToken<List<TvChannelItem>>() {}.type
            cachedTvChannels = gson.fromJson(jsonString, itemType)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun TvChannelItem.toMovieItem(): MovieItem {
        val defaultTvLogo = "https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png"
        val finalLogo = if (!logo.isNullOrEmpty()) logo else defaultTvLogo
        val finalId = if (!id.isNullOrEmpty()) id else "tv_${name.hashCode().toUInt().toString(16)}"
        val safeGroup = if (!group.isNullOrEmpty()) group else "Truyền Hình"
        val safeName = if (!name.isNullOrEmpty()) name else "Kênh TV"
        return MovieItem(
            id = finalId,
            name = safeName,
            slug = finalId,
            originName = "[$safeGroup]",
            thumbUrl = finalLogo,
            posterUrl = finalLogo,
            year = "24/7",
            quality = "LIVE",
            episodeCurrent = safeGroup,
            source = MovieSource.XEMTIVI
        )
    }

    private fun JsonObject.getSafeString(key: String, default: String = ""): String {
        if (!has(key)) return default
        val el = get(key)
        if (el == null || el.isJsonNull) return default
        return try {
            el.asString
        } catch (e: Exception) {
            default
        }
    }

    fun getFiltersForSource(source: MovieSource): List<FilterItem> {
        return when (source) {
            MovieSource.KKPHIM -> listOf(
                FilterItem("Mới Cập Nhật", "https://phimapi.com/danh-sach/phim-moi-cap-nhat"),
                FilterItem("Phim Bộ", "https://phimapi.com/v1/api/danh-sach/phim-bo"),
                FilterItem("Phim Lẻ", "https://phimapi.com/v1/api/danh-sach/phim-le"),
                FilterItem("Hoạt Hình", "https://phimapi.com/v1/api/danh-sach/hoat-hinh"),
                FilterItem("TV Shows", "https://phimapi.com/v1/api/danh-sach/tv-shows"),
                FilterItem("Thuyết Minh", "https://phimapi.com/v1/api/danh-sach/phim-thuyet-minh"),
                FilterItem("Lồng Tiếng", "https://phimapi.com/v1/api/danh-sach/phim-long-tieng"),
                FilterItem("Hành Động", "https://phimapi.com/v1/api/the-loai/hanh-dong"),
                FilterItem("Cổ Trang", "https://phimapi.com/v1/api/the-loai/co-trang"),
                FilterItem("Tình Cảm", "https://phimapi.com/v1/api/the-loai/tinh-cam"),
                FilterItem("Kinh Dị", "https://phimapi.com/v1/api/the-loai/kinh-di"),
                FilterItem("Hàn Quốc", "https://phimapi.com/v1/api/quoc-gia/han-quoc"),
                FilterItem("Trung Quốc", "https://phimapi.com/v1/api/quoc-gia/trung-quoc"),
                FilterItem("Âu Mỹ", "https://phimapi.com/v1/api/quoc-gia/au-my")
            )
            MovieSource.ANIMEHAY -> listOf(
                FilterItem("Anime Mới Cập Nhật", "https://phimapi.com/v1/api/danh-sach/hoat-hinh"),
                FilterItem("Anime Hành Động", "https://phimapi.com/v1/api/the-loai/hanh-dong"),
                FilterItem("Anime Thần Thoại", "https://phimapi.com/v1/api/the-loai/than-thoai"),
                FilterItem("Anime Học Đường", "https://phimapi.com/v1/api/the-loai/hoc-duong"),
                FilterItem("Anime Viễn Tưởng", "https://phimapi.com/v1/api/the-loai/vien-tuong")
            )
            MovieSource.XEMTIVI -> listOf(
                FilterItem("Tất Cả Kênh", "tv://all"),
                FilterItem("⚽ Bóng Đá & C1", "tv://football"),
                FilterItem("🏆 Thể Thao ESPN & FOX", "tv://sports_intl"),
                FilterItem("🏎️ Đua Xe & Võ Thuật", "tv://racing_combat"),
                FilterItem("VTV Quốc Gia", "tv://vtv"),
                FilterItem("VTVcab", "tv://vtvcab"),
                FilterItem("SCTV", "tv://sctv"),
                FilterItem("Rạp Phim", "tv://movies"),
                FilterItem("Sự Kiện TV360", "tv://live"),
                FilterItem("Kênh Quốc Tế", "tv://intl"),
                FilterItem("Đài Địa Phương", "tv://local"),
                FilterItem("Radio Trực Tuyến", "tv://radio")
            )
        }
    }

    suspend fun getMovies(source: MovieSource, filterUrl: String, page: Int = 1): List<MovieItem> {
        return withContext(Dispatchers.IO) {
            try {
                if (source == MovieSource.XEMTIVI) {
                    val channels = cachedTvChannels ?: emptyList()
                    val filtered = when (filterUrl) {
                        "tv://vtv" -> channels.filter { it.group.equals("VTV", ignoreCase = true) }
                        "tv://football" -> channels.filter {
                            it.group.contains("Bóng Đá", ignoreCase = true)
                        }
                        "tv://sports_intl" -> channels.filter {
                            it.group.contains("ESPN", ignoreCase = true) ||
                            it.group.contains("Bóng Rổ", ignoreCase = true)
                        }
                        "tv://racing_combat" -> channels.filter {
                            it.group.contains("Đua Xe", ignoreCase = true) ||
                            it.group.contains("Võ Thuật", ignoreCase = true)
                        }
                        "tv://sports" -> channels.filter {
                            it.group.contains("Bóng Đá", ignoreCase = true) ||
                            it.group.contains("Thể thao", ignoreCase = true) ||
                            it.group.contains("THỂ THAO", ignoreCase = true) ||
                            it.group.contains("ESPN", ignoreCase = true) ||
                            it.group.contains("Đua Xe", ignoreCase = true) ||
                            it.group.contains("Võ Thuật", ignoreCase = true) ||
                            it.group.contains("Bóng Rổ", ignoreCase = true)
                        }
                        "tv://vtvcab" -> channels.filter { it.group.contains("VTVcab", ignoreCase = true) }
                        "tv://sctv" -> channels.filter { it.group.contains("SCTV", ignoreCase = true) }
                        "tv://movies" -> channels.filter { it.group.contains("Rạp Phim", ignoreCase = true) }
                        "tv://live" -> channels.filter {
                            it.group.contains("Sự Kiện", ignoreCase = true) ||
                            it.group.contains("LIVE", ignoreCase = true)
                        }
                        "tv://intl" -> channels.filter {
                            it.group.contains("Quốc Tế", ignoreCase = true) ||
                            it.group.contains("Hàn Quốc", ignoreCase = true) ||
                            it.group.contains("Trung Quốc", ignoreCase = true) ||
                            it.group.contains("Israel", ignoreCase = true) ||
                            it.group.contains("TVB", ignoreCase = true)
                        }
                        "tv://local" -> channels.filter { it.group.contains("Địa phương", ignoreCase = true) || it.group.contains("HTV", ignoreCase = true) }
                        "tv://radio" -> channels.filter { it.group.contains("Radio", ignoreCase = true) }
                        else -> channels
                    }
                    if (page == 1) {
                        filtered.map { it.toMovieItem() }
                    } else emptyList()
                } else {
                    fetchKKPhimList(filterUrl, page, source)
                }
            } catch (e: Exception) {
                e.printStackTrace()
                emptyList()
            }
        }
    }

    suspend fun getMovieDetail(source: MovieSource, slug: String): MovieDetail? {
        return withContext(Dispatchers.IO) {
            try {
                if (source == MovieSource.XEMTIVI) {
                    val channel = cachedTvChannels?.find { it.id == slug }
                    if (channel != null) {
                        val defaultTvLogo = "https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png"
                        val finalLogo = if (channel.logo.isNotEmpty()) channel.logo else defaultTvLogo
                        MovieDetail(
                            id = channel.id,
                            name = channel.name,
                            slug = channel.id,
                            originName = "[${channel.group}]",
                            content = "Kênh truyền hình trực tuyến: ${channel.name} thuộc nhóm ${channel.group}. Luồng phát HLS/M3U8 ổn định từ tiện ích Xem tiVi (Chanhnh).",
                            thumbUrl = finalLogo,
                            posterUrl = finalLogo,
                            year = "2026",
                            time = "Phát sóng 24/7",
                            quality = "LIVE",
                            lang = "Tiếng Việt / Thuyết Minh",
                            source = MovieSource.XEMTIVI,
                            servers = listOf(
                                ServerGroup(
                                    serverName = "Luồng Trực Tiếp (Live HLS)",
                                    episodes = listOf(
                                        EpisodeItem(
                                            name = "Trực Tiếp (Live)",
                                            slug = channel.id,
                                            linkM3u8 = channel.url
                                        )
                                    )
                                )
                            )
                        )
                    } else null
                } else {
                    fetchKKPhimDetail(slug, source)
                }
            } catch (e: Exception) {
                e.printStackTrace()
                null
            }
        }
    }

    suspend fun searchMovies(keyword: String): List<MovieItem> {
        return withContext(Dispatchers.IO) {
            val results = mutableListOf<MovieItem>()
            try {
                // 1. Tim trong kenh TV
                val tvMatches = cachedTvChannels?.filter {
                    it.name.contains(keyword, ignoreCase = true) || it.group.contains(keyword, ignoreCase = true)
                } ?: emptyList()
                results.addAll(tvMatches.map { it.toMovieItem() })

                // 2. Tim trong phim KKPhim
                val encoded = URLEncoder.encode(keyword, "UTF-8")
                val urlKK = "https://phimapi.com/v1/api/tim-kiem?keyword=$encoded"
                val req = Request.Builder().url(urlKK).header("User-Agent", "Mozilla/5.0").build()
                client.newCall(req).execute().use { resp ->
                    if (resp.isSuccessful) {
                        val body = resp.body?.string() ?: ""
                        val root = gson.fromJson(body, JsonObject::class.java)
                        val data = root.getAsJsonObject("data")
                        val items = data?.getAsJsonArray("items")
                        items?.forEach { element ->
                            val obj = element.asJsonObject
                            val thumb = obj.getSafeString("thumb_url")
                            val fullThumb = if (thumb.startsWith("http")) thumb else KKPHIM_IMG_BASE + thumb.removePrefix("/")
                            results.add(
                                MovieItem(
                                    id = obj.getSafeString("_id"),
                                    name = obj.getSafeString("name"),
                                    slug = obj.getSafeString("slug"),
                                    originName = obj.getSafeString("origin_name"),
                                    thumbUrl = fullThumb,
                                    posterUrl = fullThumb,
                                    year = obj.getSafeString("year"),
                                    quality = obj.getSafeString("quality", "HD"),
                                    episodeCurrent = obj.getSafeString("episode_current"),
                                    source = MovieSource.KKPHIM
                                )
                            )
                        }
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
            results
        }
    }

    // --- API Handlers (HLS VIP) ---
    private fun fetchKKPhimList(baseFilterUrl: String, page: Int, source: MovieSource): List<MovieItem> {
        val sep = if (baseFilterUrl.contains("?")) "&" else "?"
        val url = "$baseFilterUrl${sep}page=$page"

        val req = Request.Builder().url(url).header("User-Agent", "Mozilla/5.0").build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return emptyList()
            val body = resp.body?.string() ?: return emptyList()
            val root = gson.fromJson(body, JsonObject::class.java)
            
            val itemsArray = if (root.has("items") && !root.get("items").isJsonNull) {
                root.getAsJsonArray("items")
            } else if (root.has("data") && !root.get("data").isJsonNull && root.getAsJsonObject("data").has("items")) {
                root.getAsJsonObject("data").getAsJsonArray("items")
            } else null

            val list = mutableListOf<MovieItem>()
            itemsArray?.forEach { el ->
                if (el.isJsonObject) {
                    val o = el.asJsonObject
                    val thumb = o.getSafeString("thumb_url")
                    val poster = o.getSafeString("poster_url").ifEmpty { thumb }
                    val fullThumb = if (thumb.startsWith("http")) thumb else if (thumb.isNotEmpty()) KKPHIM_IMG_BASE + thumb.removePrefix("/") else ""
                    val fullPoster = if (poster.startsWith("http")) poster else if (poster.isNotEmpty()) KKPHIM_IMG_BASE + poster.removePrefix("/") else fullThumb

                    list.add(
                        MovieItem(
                            id = o.getSafeString("_id"),
                            name = o.getSafeString("name"),
                            slug = o.getSafeString("slug"),
                            originName = o.getSafeString("origin_name"),
                            thumbUrl = fullThumb,
                            posterUrl = fullPoster,
                            year = o.getSafeString("year"),
                            quality = o.getSafeString("quality", "HD"),
                            episodeCurrent = o.getSafeString("episode_current"),
                            source = source
                        )
                    )
                }
            }
            return list
        }
    }

    private fun fetchKKPhimDetail(slug: String, source: MovieSource): MovieDetail? {
        val url = "https://phimapi.com/phim/$slug"
        val req = Request.Builder().url(url).header("User-Agent", "Mozilla/5.0").build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return null
            val body = resp.body?.string() ?: return null
            val root = gson.fromJson(body, JsonObject::class.java)
            val movie = root.getAsJsonObject("movie") ?: return null

            val thumb = movie.getSafeString("thumb_url")
            val poster = movie.getSafeString("poster_url").ifEmpty { thumb }
            val fullThumb = if (thumb.startsWith("http")) thumb else KKPHIM_IMG_BASE + thumb.removePrefix("/")
            val fullPoster = if (poster.startsWith("http")) poster else KKPHIM_IMG_BASE + poster.removePrefix("/")

            val serverGroups = mutableListOf<ServerGroup>()
            val episodesArray = root.getAsJsonArray("episodes")
            episodesArray?.forEach { sElement ->
                if (sElement.isJsonObject) {
                    val sObj = sElement.asJsonObject
                    val sName = sObj.getSafeString("server_name", "Server VIP")
                    val epList = mutableListOf<EpisodeItem>()
                    val sData = sObj.getAsJsonArray("server_data")
                    sData?.forEach { epEl ->
                        if (epEl.isJsonObject) {
                            val epObj = epEl.asJsonObject
                            val m3u8 = epObj.getSafeString("link_m3u8")
                            val embed = epObj.getSafeString("link_embed")
                            epList.add(
                                EpisodeItem(
                                    name = epObj.getSafeString("name", "Tập"),
                                    slug = epObj.getSafeString("slug"),
                                    filename = epObj.getSafeString("filename"),
                                    linkM3u8 = m3u8.ifEmpty { null },
                                    linkEmbed = embed.ifEmpty { null }
                                )
                            )
                        }
                    }
                    if (epList.isNotEmpty()) {
                        serverGroups.add(ServerGroup(serverName = sName, episodes = epList))
                    }
                }
            }

            return MovieDetail(
                id = movie.getSafeString("_id"),
                name = movie.getSafeString("name"),
                slug = slug,
                originName = movie.getSafeString("origin_name"),
                content = movie.getSafeString("content").replace("<[^>]*>".toRegex(), ""),
                thumbUrl = fullThumb,
                posterUrl = fullPoster,
                year = movie.getSafeString("year"),
                time = movie.getSafeString("time"),
                quality = movie.getSafeString("quality", "HD"),
                lang = movie.getSafeString("lang", "Vietsub"),
                source = source,
                servers = serverGroups
            )
        }
    }
}
