package com.huycabuonca.mobile.api

import com.google.gson.Gson
import com.google.gson.JsonElement
import com.google.gson.JsonObject
import com.huycabuonca.mobile.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.net.URLEncoder
import java.util.concurrent.TimeUnit
import java.util.regex.Pattern

object MovieRepository {

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()
    private const val KKPHIM_IMG_BASE = "https://phimimg.com/"

    // Extension to safely get String from JsonObject without throwing on JsonNull
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
            MovieSource.NGUONC -> listOf(
                FilterItem("Mới Cập Nhật", "https://phim.nguonc.com/api/films/phim-moi-cap-nhat"),
                FilterItem("Phim Bộ", "https://phim.nguonc.com/api/films/danh-sach/phim-bo"),
                FilterItem("Phim Lẻ", "https://phim.nguonc.com/api/films/danh-sach/phim-le"),
                FilterItem("Hoạt Hình", "https://phim.nguonc.com/api/films/danh-sach/hoat-hinh"),
                FilterItem("Hành Động", "https://phim.nguonc.com/api/films/the-loai/hanh-dong"),
                FilterItem("Cổ Trang", "https://phim.nguonc.com/api/films/the-loai/co-trang"),
                FilterItem("Tình Cảm", "https://phim.nguonc.com/api/films/the-loai/tinh-cam"),
                FilterItem("Trung Quốc", "https://phim.nguonc.com/api/films/quoc-gia/trung-quoc"),
                FilterItem("Hàn Quốc", "https://phim.nguonc.com/api/films/quoc-gia/han-quoc"),
                FilterItem("Âu Mỹ", "https://phim.nguonc.com/api/films/quoc-gia/au-my")
            )
            MovieSource.PHIMFUN -> listOf(
                FilterItem("Phim Mới", "https://phimfun.net/the-loai/phim-moi-1"),
                FilterItem("Cập Nhật", "https://phimfun.net/the-loai/phim-cap-nhat-1"),
                FilterItem("Phim Bộ", "https://phimfun.net/the-loai/phim-bo-1"),
                FilterItem("Phim Lẻ", "https://phimfun.net/the-loai/phim-le-1"),
                FilterItem("Chiếu Rạp", "https://phimfun.net/the-loai/phim-chieu-rap-1"),
                FilterItem("Hoạt Hình", "https://phimfun.net/the-loai/hoat-hinh-1")
            )
            MovieSource.ANIMEHAY -> listOf(
                FilterItem("Anime Mới", "https://phimapi.com/v1/api/danh-sach/hoat-hinh"),
                FilterItem("3D Trung Quốc", "https://phimapi.com/v1/api/the-loai/than-thoai"),
                FilterItem("Hành Động Anime", "https://phimapi.com/v1/api/the-loai/hanh-dong"),
                FilterItem("Học Đường Anime", "https://phimapi.com/v1/api/the-loai/hoc-duong")
            )
        }
    }

    suspend fun getMovies(source: MovieSource, filterUrl: String, page: Int = 1): List<MovieItem> {
        return withContext(Dispatchers.IO) {
            try {
                when (source) {
                    MovieSource.KKPHIM, MovieSource.ANIMEHAY -> fetchKKPhimList(filterUrl, page, source)
                    MovieSource.NGUONC -> fetchNguonCList(filterUrl, page)
                    MovieSource.PHIMFUN -> fetchPhimFunList(filterUrl, page)
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
                when (source) {
                    MovieSource.KKPHIM, MovieSource.ANIMEHAY -> fetchKKPhimDetail(slug, source)
                    MovieSource.NGUONC -> fetchNguonCDetail(slug)
                    MovieSource.PHIMFUN -> fetchPhimFunDetail(slug)
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

    // --- KKPhim API Handlers (Safe parser) ---
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

    // --- NguonC API Handlers ---
    private fun fetchNguonCList(baseFilterUrl: String, page: Int): List<MovieItem> {
        val sep = if (baseFilterUrl.contains("?")) "&" else "?"
        val url = "$baseFilterUrl${sep}page=$page"

        val req = Request.Builder().url(url).header("User-Agent", "Mozilla/5.0").build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return emptyList()
            val body = resp.body?.string() ?: return emptyList()
            val root = gson.fromJson(body, JsonObject::class.java)
            val items = root.getAsJsonArray("items") ?: return emptyList()

            val list = mutableListOf<MovieItem>()
            items.forEach { el ->
                if (el.isJsonObject) {
                    val o = el.asJsonObject
                    list.add(
                        MovieItem(
                            id = o.getSafeString("id"),
                            name = o.getSafeString("name"),
                            slug = o.getSafeString("slug"),
                            originName = o.getSafeString("original_name"),
                            thumbUrl = o.getSafeString("thumb_url"),
                            posterUrl = o.getSafeString("poster_url"),
                            year = o.getSafeString("year"),
                            quality = o.getSafeString("quality", "HD"),
                            episodeCurrent = o.getSafeString("current_episode"),
                            source = MovieSource.NGUONC
                        )
                    )
                }
            }
            return list
        }
    }

    private fun fetchNguonCDetail(slug: String): MovieDetail? {
        val url = "https://phim.nguonc.com/api/film/$slug"
        val req = Request.Builder().url(url).header("User-Agent", "Mozilla/5.0").build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return null
            val body = resp.body?.string() ?: return null
            val root = gson.fromJson(body, JsonObject::class.java)
            val movie = root.getAsJsonObject("movie") ?: return null

            val serverGroups = mutableListOf<ServerGroup>()
            val episodesArray = movie.getAsJsonArray("episodes")
            episodesArray?.forEach { sElement ->
                if (sElement.isJsonObject) {
                    val sObj = sElement.asJsonObject
                    val sName = sObj.getSafeString("server_name", "Nguồn C")
                    val epList = mutableListOf<EpisodeItem>()
                    val sItems = sObj.getAsJsonArray("items")
                    sItems?.forEach { epEl ->
                        if (epEl.isJsonObject) {
                            val epObj = epEl.asJsonObject
                            val m3u8 = epObj.getSafeString("m3u8")
                            val embed = epObj.getSafeString("embed")
                            epList.add(
                                EpisodeItem(
                                    name = epObj.getSafeString("name", "Tập"),
                                    slug = epObj.getSafeString("slug"),
                                    filename = "",
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
                id = movie.getSafeString("id"),
                name = movie.getSafeString("name"),
                slug = slug,
                originName = movie.getSafeString("original_name"),
                content = movie.getSafeString("description").replace("<[^>]*>".toRegex(), ""),
                thumbUrl = movie.getSafeString("thumb_url"),
                posterUrl = movie.getSafeString("poster_url"),
                year = movie.getSafeString("year"),
                time = movie.getSafeString("time"),
                quality = movie.getSafeString("quality", "HD"),
                lang = movie.getSafeString("language", "Vietsub"),
                source = MovieSource.NGUONC,
                servers = serverGroups
            )
        }
    }

    // --- PhimFun Web Handlers ---
    private fun fetchPhimFunList(baseFilterUrl: String, page: Int): List<MovieItem> {
        val requestUrl = baseFilterUrl.replace(Regex("-\\d+$"), "-$page")
        val req = Request.Builder().url(requestUrl)
            .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            .build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return emptyList()
            val html = resp.body?.string() ?: return emptyList()

            val pattern = Pattern.compile(
                "<a href=\"(/phim/[^\"]+)\".*?<img.*?src=\"([^\"]+)\".*?<h3 class=\"Title\">([^<]+)</h3>",
                Pattern.DOTALL
            )
            val matcher = pattern.matcher(html)
            val list = mutableListOf<MovieItem>()
            while (matcher.find()) {
                val link = matcher.group(1) ?: ""
                val img = matcher.group(2) ?: ""
                val title = matcher.group(3) ?: ""
                val fullImg = if (img.startsWith("http")) img else "https://phimfun.net$img"
                val slug = link.substringAfter("/phim/")

                list.add(
                    MovieItem(
                        id = slug,
                        name = android.text.Html.fromHtml(title).toString(),
                        slug = slug,
                        originName = "",
                        thumbUrl = fullImg,
                        posterUrl = fullImg,
                        year = "",
                        quality = "Full HD",
                        episodeCurrent = "",
                        source = MovieSource.PHIMFUN
                    )
                )
            }
            return list
        }
    }

    private fun fetchPhimFunDetail(slug: String): MovieDetail? {
        val watchUrl = "https://phimfun.net/xem-phim/$slug"
        val req = Request.Builder().url(watchUrl)
            .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            .build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return null
            val html = resp.body?.string() ?: return null

            // Extract episodes
            val epPattern = Pattern.compile("<a\\s+href=\"([^\"]+)\"[^>]*>([^<]+)</a>")
            val epMatcher = epPattern.matcher(html)
            val episodes = mutableListOf<EpisodeItem>()

            while (epMatcher.find()) {
                val href = epMatcher.group(1) ?: ""
                val name = epMatcher.group(2)?.trim() ?: ""
                if (href.contains("/xem-phim/")) {
                    val fullUrl = if (href.startsWith("http")) href else "https://phimfun.net$href"
                    episodes.add(
                        EpisodeItem(
                            name = name,
                            slug = href,
                            linkEmbed = fullUrl
                        )
                    )
                }
            }

            if (episodes.isEmpty()) {
                episodes.add(
                    EpisodeItem(
                        name = "Xem Phim",
                        slug = slug,
                        linkEmbed = watchUrl
                    )
                )
            }

            return MovieDetail(
                id = slug,
                name = slug.replace("-", " ").capitalize(),
                slug = slug,
                content = "Xem phim trực tuyến chất lượng cao trên PhimFun",
                thumbUrl = "",
                posterUrl = "",
                source = MovieSource.PHIMFUN,
                servers = listOf(ServerGroup("Server PhimFun", episodes))
            )
        }
    }
}
