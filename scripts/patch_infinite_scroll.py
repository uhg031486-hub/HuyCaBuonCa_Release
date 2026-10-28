import sys

sys.stdout.reconfigure(encoding='utf-8')

for path in [
    'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt',
    'HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt'
]:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update filter "gamomephim://the-loai/hien-dai" to "gamomephim://phim-moi"
    content = content.replace(
        'FilterItem("✨ Toàn Bộ Tiểu Kịch Mới", "gamomephim://the-loai/hien-dai")',
        'FilterItem("✨ Toàn Bộ Tiểu Kịch Mới", "gamomephim://phim-moi")'
    )

    # 2. Update FreeReelsClient.search to support pagination
    old_search = '''fun search(client: OkHttpClient, gson: Gson, keyword: String): List<MovieItem> {
        val list = mutableListOf<MovieItem>()
        try {
            val ts = System.currentTimeMillis().toString()
            val jsonBody = JsonObject().apply {
                addProperty("keyword", keyword)
                addProperty("next", "")
                addProperty("timestamp", ts)
            }.toString()'''

    new_search = '''fun search(client: OkHttpClient, gson: Gson, keyword: String, page: Int = 1): List<MovieItem> {
        val list = mutableListOf<MovieItem>()
        try {
            val ts = System.currentTimeMillis().toString()
            val offset = (page - 1) * 20
            val nextCursor = if (page > 1) "offset=$offset&page_size=20" else ""
            val jsonBody = JsonObject().apply {
                addProperty("keyword", keyword)
                addProperty("page_size", 20)
                addProperty("next", nextCursor)
                addProperty("timestamp", ts)
            }.toString()'''

    assert old_search in content, f"Could not find old_search in {path}"
    content = content.replace(old_search, new_search)

    # 3. Replace fetchShortDramaList with infinite scroll multi-source implementation
    start_str = "private fun fetchShortDramaList(filterUrl: String, page: Int): List<MovieItem> {"
    end_str = "private fun fetchKKPhimList(baseFilterUrl: String, page: Int, source: MovieSource): List<MovieItem> {"

    start_idx = content.find(start_str)
    end_idx = content.find(end_str, start_idx)
    assert start_idx != -1 and end_idx != -1, f"Could not find fetchShortDramaList range in {path}"

    new_fetch_code = '''private fun fetchShortDramaList(filterUrl: String, page: Int): List<MovieItem> {
        val frKeyword: String
        val altKeywords: List<String>
        val gmGenre: String
        val kkKeyword: String

        when (filterUrl) {
            "multi_short://tong-tai", "short_filter://tong-tai" -> {
                frKeyword = "tổng tài"; altKeywords = listOf("bá đạo", "boss"); gmGenre = "the-loai/cuoi-truoc-yeu-sau"; kkKeyword = "tổng tài"
            }
            "multi_short://trong-sinh", "short_filter://trong-sinh" -> {
                frKeyword = "trọng sinh"; altKeywords = listOf("trùng sinh", "báo thù"); gmGenre = "the-loai/trong-sinh"; kkKeyword = "trọng sinh"
            }
            "multi_short://chien-than", "short_dramabox://chienthan" -> {
                frKeyword = "chiến thần"; altKeywords = listOf("tu tiên", "cao thủ"); gmGenre = "the-loai/co-trang"; kkKeyword = "chiến thần"
            }
            "multi_short://thieu-gia", "short_dramabox://thieugia" -> {
                frKeyword = "thiếu gia"; altKeywords = listOf("đại gia", "tỷ phú"); gmGenre = "the-loai/hien-dai"; kkKeyword = "thiếu gia"
            }
            "multi_short://co-trang", "short_dramabox://cotrang" -> {
                frKeyword = "cổ trang"; altKeywords = listOf("cung đấu", "hoàng phi"); gmGenre = "the-loai/co-trang"; kkKeyword = "cung đấu"
            }
            "multi_short://hao-mon", "short_filter://ngon-tinh" -> {
                frKeyword = "hào môn"; altKeywords = listOf("hôn nhân", "kết hôn"); gmGenre = "the-loai/cuoi-truoc-yeu-sau"; kkKeyword = "hào môn"
            }
            else -> {
                frKeyword = "tổng tài"; altKeywords = listOf("bá đạo"); gmGenre = "the-loai/cuoi-truoc-yeu-sau"; kkKeyword = "tổng tài"
            }
        }

        val result = mutableListOf<MovieItem>()

        // 1. Luôn truy vấn FreeReels theo page (mỗi page 20 phim vô cực chuẩn dọc 9:16)
        try {
            val frItems = FreeReelsClient.search(client, gson, frKeyword, page)
            result.addAll(frItems)

            // Nếu trang này FreeReels có ít hơn 10 phim, bổ sung thêm từ khóa phụ
            if (frItems.size < 10) {
                for (alt in altKeywords) {
                    val altItems = FreeReelsClient.search(client, gson, alt, page)
                    result.addAll(altItems)
                    if (result.size >= 15) break
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        // 2. Ở các trang đầu (page 1, 2), trộn thêm kho Gà Mờ Mê Phim thuyết minh
        if (page <= 2 && gmGenre.isNotEmpty()) {
            try {
                val gmItems = GaMoMePhimClient.getDramaList(client, "gamomephim://$gmGenre", page)
                result.addAll(gmItems)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }

        // 3. Ở trang 1, trộn thêm các phim tiểu kịch từ KKPhim
        if (page == 1 && kkKeyword.isNotEmpty()) {
            try {
                val kkItems = fetchKKPhimSearch(kkKeyword)
                result.addAll(kkItems)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }

        return result.distinctBy { it.name.trim().lowercase() }
    }

    private fun fetchKKPhimSearch(keyword: String): List<MovieItem> {
        return try {
            val url = "https://phimapi.com/v1/api/tim-kiem?keyword=${java.net.URLEncoder.encode(keyword, "UTF-8")}&page=1"
            val req = Request.Builder().url(url).header("User-Agent", "Mozilla/5.0").build()
            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return emptyList()
                val body = resp.body?.string() ?: return emptyList()
                val root = gson.fromJson(body, JsonObject::class.java)
                val data = root.getAsJsonObject("data") ?: return emptyList()
                val items = data.getAsJsonArray("items") ?: return emptyList()
                val result = mutableListOf<MovieItem>()
                items.forEach { el ->
                    if (el.isJsonObject) {
                        val o = el.asJsonObject
                        val thumb = o.getSafeString("thumb_url")
                        val poster = o.getSafeString("poster_url").ifEmpty { thumb }
                        val fullThumb = if (thumb.startsWith("http")) thumb else if (thumb.isNotEmpty()) KKPHIM_IMG_BASE + thumb.removePrefix("/") else ""
                        val fullPoster = if (poster.startsWith("http")) poster else if (poster.isNotEmpty()) KKPHIM_IMG_BASE + poster.removePrefix("/") else fullThumb

                        result.add(
                            MovieItem(
                                id = o.getSafeString("_id"),
                                name = o.getSafeString("name"),
                                slug = o.getSafeString("slug"),
                                originName = o.getSafeString("origin_name"),
                                thumbUrl = fullThumb,
                                posterUrl = fullPoster,
                                year = o.getSafeString("year", "2026"),
                                quality = "1080p Vietsub",
                                episodeCurrent = o.getSafeString("episode_current"),
                                source = MovieSource.KKPHIM
                            )
                        )
                    }
                }
                result
            }
        } catch (e: Exception) {
            emptyList()
        }
    }

    '''

    content = content[:start_idx] + new_fetch_code + content[end_idx:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Successfully updated {path}")
