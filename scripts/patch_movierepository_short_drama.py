import sys

sys.stdout.reconfigure(encoding='utf-8')

def patch_repo(repo_path):
    with open(repo_path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Update FreeReels rawStream & finalStreamUrl
    target_fr = """                        epList.add(
                            EpisodeItem(
                                name = epName,
                                slug = epId,
                                filename = epName,
                                linkM3u8 = "freereels_unlock:$cleanSeriesId:$epId",
                                linkEmbed = null,
                                subtitleUrl = viSubUrl
                            )
                        )"""

    replacement_fr = """                        val rawStream = epObj.getSafeString("external_audio_h264_m3u8").ifEmpty {
                            epObj.getSafeString("m3u8_url").ifEmpty {
                                epObj.getSafeString("video_url").ifEmpty {
                                    epObj.getSafeString("external_audio_h265_m3u8")
                                }
                            }
                        }
                        val finalStream = if (rawStream.startsWith("http")) rawStream else "freereels_unlock:$cleanSeriesId:$epId"

                        epList.add(
                            EpisodeItem(
                                name = epName,
                                slug = epId,
                                filename = epName,
                                linkM3u8 = finalStream,
                                linkEmbed = null,
                                subtitleUrl = viSubUrl
                            )
                        )"""

    if target_fr in code:
        code = code.replace(target_fr, replacement_fr)
        print(f" -> Patch rawStream OK cho {repo_path}")
    else:
        print(f" ⚠️ Không tìm thấy target_fr trong {repo_path}")

    # 2. Update GaMoMePhim realSlug & fallback targetUrl
    target_gm = """    fun getDramaDetail(client: OkHttpClient, cleanSlug: String): MovieDetail? {
        return try {
            val targetUrl = "$BASE_URL/$cleanSlug"
            val req = Request.Builder()"""

    replacement_gm = """    fun getDramaDetail(client: OkHttpClient, cleanSlug: String): MovieDetail? {
        return try {
            val realSlug = cleanSlug.removePrefix("gamomephim:").removePrefix("/phim/").removePrefix("phim/").removePrefix("/")
            var targetUrl = "$BASE_URL/$realSlug"
            val req = Request.Builder()"""

    if target_gm in code:
        code = code.replace(target_gm, replacement_gm)
        print(f" -> Patch realSlug OK cho {repo_path}")
    else:
        print(f" ⚠️ Không tìm thấy target_gm trong {repo_path}")

    # 3. Thêm fallback nạp $BASE_URL/phim/$realSlug nếu $BASE_URL/$realSlug không có stream
    target_gm_fetch = """            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return null
                val html = resp.body?.string() ?: return null"""

    replacement_gm_fetch = """            var html = ""
            client.newCall(req).execute().use { resp ->
                if (resp.isSuccessful) {
                    html = resp.body?.string() ?: ""
                }
            }
            if (!html.contains(".mp4") && !html.contains("r2.gamomephim.com/videos")) {
                try {
                    val fbReq = Request.Builder().url("$BASE_URL/phim/$realSlug").header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36").build()
                    client.newCall(fbReq).execute().use { fbResp ->
                        if (fbResp.isSuccessful) {
                            val fbHtml = fbResp.body?.string() ?: ""
                            if (fbHtml.contains(".mp4") || fbHtml.contains("r2.gamomephim.com/videos")) {
                                html = fbHtml
                            }
                        }
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
            if (html.isEmpty()) return null"""

    if target_gm_fetch in code:
        code = code.replace(target_gm_fetch, replacement_gm_fetch)
        print(f" -> Patch gm_fetch OK cho {repo_path}")
    else:
        print(f" ⚠️ Không tìm thấy target_gm_fetch trong {repo_path}")

    # 4. Filter bỏ item TOP hoặc ID rỗng trong parseDramaItems
    target_parse = """                if (rawId.isNotEmpty() && title.isNotEmpty() && !title.equals("TOP", ignoreCase = true)) {"""
    replacement_parse = """                if (rawId.isNotEmpty() && !rawId.equals("null", ignoreCase = true) && title.isNotEmpty() && !title.equals("TOP", ignoreCase = true) && !title.startsWith("TOP ")) {"""

    if target_parse in code:
        code = code.replace(target_parse, replacement_parse)
        print(f" -> Patch parseDramaItems OK cho {repo_path}")
    else:
        print(f" ⚠️ Không tìm thấy target_parse trong {repo_path}")

    with open(repo_path, "w", encoding="utf-8") as f:
        f.write(code)

patch_repo("HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt")
patch_repo("HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt")
print("✅ HOÀN TẤT CẬP NHẬT CẢ 2 MOVIEREPOSITORY.KT!")
