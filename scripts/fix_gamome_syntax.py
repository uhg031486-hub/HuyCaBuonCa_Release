import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for path in ['HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt', 'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt']:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    p_gm_start = text.find('object GaMoMePhimClient {')
    p_gm_detail = text.find('fun getDramaDetail(client: OkHttpClient, cleanSlug: String): MovieDetail? {', p_gm_start)

    correct_get_drama_list = '''object GaMoMePhimClient {
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
                    """<a[^>]+title="([^"]+)"[^>]+href="/phim/([^"]+)".*?<img[^>]+src="([^"]+)"""",
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

                // Tự động nạp thêm từ Phim Mới nếu thể loại này hết phim ở page > 1 (chống lỗi kéo thêm không ra phim)
                if (list.isEmpty() && page > 1 && genrePath != "phim-moi") {
                    try {
                        val fbUrl = "$BASE_URL/phim-moi?page=$page"
                        val fbReq = Request.Builder()
                            .url(fbUrl)
                            .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                            .build()
                        client.newCall(fbReq).execute().use { fbResp ->
                            if (fbResp.isSuccessful) {
                                val fbHtml = fbResp.body?.string() ?: ""
                                val fbMatcher = pattern.matcher(fbHtml)
                                while (fbMatcher.find()) {
                                    val title = fbMatcher.group(1)?.trim() ?: ""
                                    val slug = fbMatcher.group(2)?.trim() ?: ""
                                    val thumb = fbMatcher.group(3)?.trim() ?: ""
                                    if (slug.isNotEmpty() && !seen.contains(slug)) {
                                        seen.add(slug)
                                        list.add(
                                            MovieItem(
                                                id = "gamomephim:$slug",
                                                name = title,
                                                slug = "gamomephim:$slug",
                                                originName = "Gà Mờ Mê Phim • Mới Cập Nhật",
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
                        }
                    } catch (err: Exception) {
                        err.printStackTrace()
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }

    '''

    text = text[:p_gm_start] + correct_get_drama_list + text[p_gm_detail:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'Fixed GaMoMePhimClient syntax in {path}')
