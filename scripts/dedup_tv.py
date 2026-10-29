path = 'HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

dup_fn = '''    fun getDramaList(client: OkHttpClient, filterUrl: String, page: Int): List<MovieItem> {
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
                list.addAll(parseGaMoMeHtml(html))

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
                                val fbItems = parseGaMoMeHtml(fbHtml)
                                fbItems.forEach { item ->
                                    list.add(item.copy(originName = "Gà Mờ Mê Phim • Mới Cập Nhật"))
                                }
                            }
                        }
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }'''

count = content.count(dup_fn)
print(f"Occurrences of dup_fn in TV: {count}")
if count == 2:
    # replace first occurrence only
    content = content.replace(dup_fn, '', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Removed 1 duplicate getDramaList in TV!")
else:
    print("Count is not 2, checking exact lines...")
