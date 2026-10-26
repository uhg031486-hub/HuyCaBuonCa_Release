import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

gamomephim_client_code = """
object GaMoMePhimClient {
    private const val BASE_URL = "https://gamomephim.com"

    fun getDramaList(client: OkHttpClient, filterUrl: String, page: Int): List<MovieItem> {
        val list = mutableListOf<MovieItem>()
        try {
            val genrePath = filterUrl.removePrefix("gamomephim://")
            val targetUrl = if (page <= 1) {
                "$BASE_URL/$genrePath"
            } else {
                "$BASE_URL/$genrePath?page=$page"
            }

            val req = Request.Builder()
                .url(targetUrl)
                .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                .build()

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return emptyList()
                val html = resp.body?.string() ?: return emptyList()

                val pattern = java.util.regex.Pattern.compile(
                    \"\"\"<a[^>]+title="([^"]+)"[^>]+href="/phim/([^"]+)".*?<img[^>]+src="([^"]+)""\"\",
                    java.util.regex.Pattern.DOTALL
                )
                val matcher = pattern.matcher(html)
                val seen = mutableSetOf<String>()

                while (matcher.find()) {
                    val title = matcher.group(1)?.trim() ?: ""
                    val slug = matcher.group(2)?.trim() ?: ""
                    val thumb = matcher.group(3)?.trim() ?: ""

                    if (slug.isNotEmpty() && !seen.contains(slug)) {
                        seen.add(slug)
                        list.add(
                            MovieItem(
                                id = "gamomephim:$slug",
                                name = title,
                                slug = "gamomephim:$slug",
                                originName = "Gà Mờ Mê Phim • Thuyết Minh",
                                thumbUrl = thumb,
                                posterUrl = thumb,
                                year = "2026",
                                quality = "🎙️ Thuyết Minh & Vietsub",
                                episodeCurrent = "Full Bộ HD",
                                source = MovieSource.FREEREELS
                            )
                        )
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }

    fun getDramaDetail(client: OkHttpClient, cleanSlug: String): MovieDetail? {
        return try {
            val targetUrl = "$BASE_URL/$cleanSlug"
            val req = Request.Builder()
                .url(targetUrl)
                .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                .build()

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return null
                val html = resp.body?.string() ?: return null

                // Title
                var title = ""
                val titleMatcher = java.util.regex.Pattern.compile(\"\"\"<h1[^>]*>([^<]+)</h1>\"\"\").matcher(html)
                if (titleMatcher.find()) {
                    title = titleMatcher.group(1)?.trim() ?: ""
                }
                if (title.isEmpty()) {
                    title = cleanSlug.replace("-", " ")
                }

                // Description
                var desc = "Phim ngắn tiểu kịch lồng tiếng/thuyết minh tiếng Việt trọn bộ cực hay."
                val descMatcher = java.util.regex.Pattern.compile(\"\"\"description\\\\":\\\\"([^\\\\"]+)\\\\"\"\"\").matcher(html)
                if (descMatcher.find()) {
                    desc = descMatcher.group(1)?.replace("\\\\n", "\\n") ?: desc
                }

                // Thumb / Poster
                var thumb = ""
                val thumbMatcher = java.util.regex.Pattern.compile(\"\"\"https://r2\\.gamomephim\\.com/thumbnails/[^"'\\s<>]+\"\"\").matcher(html)
                if (thumbMatcher.find()) {
                    thumb = thumbMatcher.group()
                }

                // Video Streams (MP4)
                val streamMatcher = java.util.regex.Pattern.compile(\"\"\"https://r2\\.gamomephim\\.com/videos/[^\\s"'<>]+\\.mp4\"\"\").matcher(html)
                val streamUrls = mutableListOf<String>()
                while (streamMatcher.find()) {
                    val sUrl = streamMatcher.group().replace("\\\\", "")
                    if (!streamUrls.contains(sUrl)) {
                        streamUrls.add(sUrl)
                    }
                }

                val tmStream = streamUrls.find { it.contains("-tm.mp4") }
                val subStream = streamUrls.find { it.contains("-sub.mp4") }

                val servers = mutableListOf<ServerGroup>()
                if (tmStream != null) {
                    servers.add(
                        ServerGroup(
                            serverName = "🎙️ Thuyết Minh (Gà Mờ Mê Phim)",
                            episodes = listOf(
                                EpisodeItem(
                                    name = "Tập Full (Thuyết Minh)",
                                    slug = cleanSlug,
                                    filename = "Tập Full (Thuyết Minh)",
                                    linkM3u8 = tmStream,
                                    linkEmbed = null,
                                    subtitleUrl = null
                                )
                            )
                        )
                    )
                }

                if (subStream != null) {
                    servers.add(
                        ServerGroup(
                            serverName = "🇻🇳 Vietsub (Gà Mờ Mê Phim)",
                            episodes = listOf(
                                EpisodeItem(
                                    name = "Tập Full (Vietsub)",
                                    slug = cleanSlug,
                                    filename = "Tập Full (Vietsub)",
                                    linkM3u8 = subStream,
                                    linkEmbed = null,
                                    subtitleUrl = null
                                )
                            )
                        )
                    )
                }

                if (servers.isEmpty() && streamUrls.isNotEmpty()) {
                    servers.add(
                        ServerGroup(
                            serverName = "▶️ Bản Chuẩn HD (Gà Mờ Mê Phim)",
                            episodes = listOf(
                                EpisodeItem(
                                    name = "Tập Full",
                                    slug = cleanSlug,
                                    filename = "Tập Full",
                                    linkM3u8 = streamUrls[0],
                                    linkEmbed = null,
                                    subtitleUrl = null
                                )
                            )
                        )
                    )
                }

                MovieDetail(
                    id = "gamomephim:$cleanSlug",
                    name = title,
                    slug = "gamomephim:$cleanSlug",
                    originName = "Gà Mờ Mê Phim Full Trọn Bộ",
                    content = desc,
                    thumbUrl = thumb,
                    posterUrl = thumb,
                    year = "2026",
                    time = "Trọn bộ",
                    quality = "Full HD",
                    lang = if (tmStream != null) "Thuyết Minh" else "Vietsub",
                    source = MovieSource.FREEREELS,
                    servers = servers
                )
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    fun search(client: OkHttpClient, keyword: String): List<MovieItem> {
        val list = mutableListOf<MovieItem>()
        try {
            val encoded = java.net.URLEncoder.encode(keyword, "UTF-8")
            val targetUrl = "$BASE_URL/tim-kiem?q=$encoded"
            val req = Request.Builder()
                .url(targetUrl)
                .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                .build()

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return emptyList()
                val html = resp.body?.string() ?: return emptyList()

                val pattern = java.util.regex.Pattern.compile(
                    \"\"\"<a[^>]+title="([^"]+)"[^>]+href="/phim/([^"]+)".*?<img[^>]+src="([^"]+)""\"\",
                    java.util.regex.Pattern.DOTALL
                )
                val matcher = pattern.matcher(html)
                val seen = mutableSetOf<String>()

                while (matcher.find()) {
                    val title = matcher.group(1)?.trim() ?: ""
                    val slug = matcher.group(2)?.trim() ?: ""
                    val thumb = matcher.group(3)?.trim() ?: ""

                    if (slug.isNotEmpty() && !seen.contains(slug)) {
                        seen.add(slug)
                        list.add(
                            MovieItem(
                                id = "gamomephim:$slug",
                                name = title,
                                slug = "gamomephim:$slug",
                                originName = "Gà Mờ Mê Phim • Thuyết Minh",
                                thumbUrl = thumb,
                                posterUrl = thumb,
                                year = "2026",
                                quality = "🎙️ Thuyết Minh & Vietsub",
                                episodeCurrent = "Full Bộ HD",
                                source = MovieSource.FREEREELS
                            )
                        )
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }
}
"""

def update_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update getShortDramaSubSources()
    old_sub_sources = """    fun getShortDramaSubSources(): List<FilterItem> {
        return listOf(
            FilterItem("📱 FreeReels Dọc (Phụ Đề & Lồng Tiếng)", "freereels_sub://freereels"),
            FilterItem("🇻🇳 Tiểu Kịch Vietsub (KKPhim HD)", "freereels_sub://kkphim"),
            FilterItem("💎 DramaBox Hot (Tuyển Chọn Hay Nhất)", "freereels_sub://dramabox")
        )
    }"""

    new_sub_sources = """    fun getShortDramaSubSources(): List<FilterItem> {
        return listOf(
            FilterItem("🎙️ Gà Mờ Mê Phim (Thuyết Minh & Vietsub)", "freereels_sub://gamomephim"),
            FilterItem("📱 FreeReels Dọc (Phụ Đề & Lồng Tiếng)", "freereels_sub://freereels"),
            FilterItem("🇻🇳 Tiểu Kịch Vietsub (KKPhim HD)", "freereels_sub://kkphim"),
            FilterItem("💎 DramaBox Hot (Tuyển Chọn Hay Nhất)", "freereels_sub://dramabox")
        )
    }"""

    content = content.replace(old_sub_sources, new_sub_sources)

    # 2. Update getShortDramaFilters(subSourceUrl)
    old_filter_match = """    fun getShortDramaFilters(subSourceUrl: String): List<FilterItem> {
        return when (subSourceUrl) {"""

    new_filter_cases = """    fun getShortDramaFilters(subSourceUrl: String): List<FilterItem> {
        return when (subSourceUrl) {
            "freereels_sub://gamomephim" -> listOf(
                FilterItem("🔥 Toàn Bộ Tiểu Kịch Mới", "gamomephim://the-loai/hien-dai"),
                FilterItem("👑 Cưới Trước Yêu Sau & Tổng Tài", "gamomephim://the-loai/cuoi-truoc-yeu-sau"),
                FilterItem("🐉 Trọng Sinh & Báo Thù", "gamomephim://the-loai/trong-sinh"),
                FilterItem("🏰 Cổ Trang & Xuyên Không", "gamomephim://the-loai/co-trang"),
                FilterItem("🍵 Trà Xanh Nam & Ngược Tâm", "gamomephim://the-loai/tra-xanh-nam"),
                FilterItem("✨ Chữa Lành & Thanh Xuân", "gamomephim://the-loai/chua-lanh"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            ),"""

    content = content.replace(old_filter_match, new_filter_cases)

    # 3. Update getMovieList when source == MovieSource.FREEREELS
    old_get_movie_list = """                } else if (source == MovieSource.FREEREELS) {
                    when {
                        filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://") -> {
                            fetchShortDramaList(filterUrl, page)
                        }
                        filterUrl.startsWith("https://phimapi.com") -> {
                            fetchKKPhimList(filterUrl, page, MovieSource.KKPHIM)
                        }
                        else -> {
                            FreeReelsClient.getDramaList(client, gson, filterUrl, page)
                        }
                    }"""

    new_get_movie_list = """                } else if (source == MovieSource.FREEREELS) {
                    when {
                        filterUrl.startsWith("gamomephim://") -> {
                            GaMoMePhimClient.getDramaList(client, filterUrl, page)
                        }
                        filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://") -> {
                            fetchShortDramaList(filterUrl, page)
                        }
                        filterUrl.startsWith("https://phimapi.com") -> {
                            fetchKKPhimList(filterUrl, page, MovieSource.KKPHIM)
                        }
                        else -> {
                            FreeReelsClient.getDramaList(client, gson, filterUrl, page)
                        }
                    }"""

    content = content.replace(old_get_movie_list, new_get_movie_list)

    # 4. Update getMovieDetail when source == MovieSource.FREEREELS
    old_detail = """                } else if (source == MovieSource.FREEREELS) {
                    FreeReelsClient.getDramaDetail(client, gson, slug)"""

    new_detail = """                } else if (source == MovieSource.FREEREELS) {
                    if (slug.startsWith("gamomephim:")) {
                        GaMoMePhimClient.getDramaDetail(client, slug.removePrefix("gamomephim:"))
                    } else {
                        FreeReelsClient.getDramaDetail(client, gson, slug)
                    }"""

    content = content.replace(old_detail, new_detail)

    # 5. Update searchMovies
    old_search = """                // 2. Tim trong Phim Ngan FreeReels
                val freeReelsMatches = FreeReelsClient.search(client, gson, keyword)
                results.addAll(freeReelsMatches)"""

    new_search = """                // 1.5. Tim trong Ga Mo Me Phim
                val gaMoMatches = GaMoMePhimClient.search(client, keyword)
                results.addAll(gaMoMatches)

                // 2. Tim trong Phim Ngan FreeReels
                val freeReelsMatches = FreeReelsClient.search(client, gson, keyword)
                results.addAll(freeReelsMatches)"""

    content = content.replace(old_search, new_search)

    # 6. Append GaMoMePhimClient at the end if not already present
    if "object GaMoMePhimClient" not in content:
        content = content.rstrip() + "\n\n" + gamomephim_client_code.strip() + "\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Cập nhật thành công {file_path}")

update_file(r"HuyCaBuonCa_TV\app\src\main\java\com\huycabuonca\tv\api\MovieRepository.kt")
update_file(r"HuyCaBuonCa_Mobile\app\src\main\java\com\huycabuonca\mobile\api\MovieRepository.kt")
