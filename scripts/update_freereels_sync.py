# update_freereels_sync.py
import re

freereels_client_code = '''object FreeReelsClient {
    private const val API_BASE = "https://apiv2.free-reels.com/frv2-api"
    private const val APP_SECRET = "8IAcbWyCsVhYv82S2eofRqK1DF3nNDAv"
    private const val APP_NAME = "com.freereels.app"
    private const val APP_VERSION = "2.2.81"

    private var deviceId: String = ""
    private var sessionId: String = ""
    private var oauthToken: String = ""
    private var oauthSecret: String = ""

    private fun md5(s: String): String {
        val md = java.security.MessageDigest.getInstance("MD5")
        val bytes = md.digest(s.toByteArray(Charsets.UTF_8))
        return bytes.joinToString("") { "%02x".format(it) }
    }

    private fun ensureLogin(client: OkHttpClient, gson: Gson): Boolean {
        if (oauthToken.isNotEmpty() && oauthSecret.isNotEmpty()) return true
        return try {
            if (deviceId.isEmpty()) deviceId = java.util.UUID.randomUUID().toString()
            if (sessionId.isEmpty()) sessionId = java.util.UUID.randomUUID().toString()
            val sign = md5(APP_SECRET + deviceId)

            val loginJson = JsonObject().apply {
                addProperty("device_id", deviceId)
                addProperty("device_name", "samsung SM-A536E")
                addProperty("sign", sign)
            }

            val mediaType = "application/json; charset=utf-8".toMediaType()
            val body = loginJson.toString().toRequestBody(mediaType)

            val req = Request.Builder()
                .url("$API_BASE/anonymous/login")
                .post(body)
                .header("Accept", "application/json")
                .header("Content-Type", "application/json")
                .header("app-name", APP_NAME)
                .header("app-version", APP_VERSION)
                .header("device", "android")
                .header("device-version", "33")
                .header("device-id", deviceId)
                .header("session-id", sessionId)
                .header("language", "vi-VN")
                .header("country", "VN")
                .build()

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return false
                val respStr = resp.body?.string() ?: return false
                val root = gson.fromJson(respStr, JsonObject::class.java)
                val data = root.getAsJsonObject("data") ?: return false
                oauthToken = data.get("auth_key")?.asString ?: ""
                oauthSecret = data.get("auth_secret")?.asString ?: ""
                oauthToken.isNotEmpty() && oauthSecret.isNotEmpty()
            }
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    private fun buildAuthorizedRequest(client: OkHttpClient, gson: Gson, url: String, method: String = "GET", jsonBody: String? = null): Request? {
        if (!ensureLogin(client, gson)) return null
        val ts = System.currentTimeMillis().toString()
        val sig = md5("$APP_SECRET&$oauthSecret")
        val authHeader = "oauth_signature=$sig,oauth_token=$oauthToken,ts=$ts"

        val builder = Request.Builder()
            .url(url)
            .header("Accept", "application/json")
            .header("Content-Type", "application/json")
            .header("User-Agent", "Mozilla/5.0")
            .header("app-name", APP_NAME)
            .header("app-version", APP_VERSION)
            .header("device", "android")
            .header("device-version", "33")
            .header("device-id", deviceId)
            .header("session-id", sessionId)
            .header("language", "vi-VN")
            .header("country", "VN")
            .header("Authorization", authHeader)

        val mediaType = "application/json; charset=utf-8".toMediaType()
        if (method == "POST") {
            val body = (jsonBody ?: "{}").toRequestBody(mediaType)
            builder.post(body)
        } else {
            builder.get()
        }
        return builder.build()
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

    private fun parseDramaItems(itemsArray: com.google.gson.JsonArray?, outList: MutableList<MovieItem>) {
        if (itemsArray == null) return
        itemsArray.forEach { el ->
            if (el.isJsonObject) {
                val obj = el.asJsonObject
                val series = if (obj.has("series") && obj.get("series").isJsonObject) {
                    obj.getAsJsonObject("series")
                } else if (obj.has("info") && obj.get("info").isJsonObject) {
                    obj.getAsJsonObject("info")
                } else obj

                val rawId = series.getSafeString("id").ifEmpty {
                    series.getSafeString("key").ifEmpty {
                        series.getSafeString("series_id")
                    }
                }
                val title = series.getSafeString("title").ifEmpty {
                    series.getSafeString("name")
                }
                val cover = series.getSafeString("cover").ifEmpty {
                    series.getSafeString("poster")
                }
                val epCount = series.getSafeString("episode_count")

                if (rawId.isNotEmpty() && title.isNotEmpty() && !title.equals("TOP", ignoreCase = true)) {
                    val isDubbed = title.contains("lồng tiếng", ignoreCase = true) || title.contains("thuyết minh", ignoreCase = true)
                    val qualityBadge = if (isDubbed) "🎙️ Lồng Tiếng" else "🇻🇳 Phụ Đề"
                    outList.add(
                        MovieItem(
                            id = "freereels:$rawId",
                            name = title,
                            slug = "freereels:$rawId",
                            originName = if (isDubbed) "$epCount tập • Lồng Tiếng Việt" else "$epCount tập • Phụ Đề Tiếng Việt",
                            thumbUrl = cover,
                            posterUrl = cover,
                            year = "2026",
                            quality = qualityBadge,
                            episodeCurrent = if (epCount.isNotEmpty()) "$epCount tập" else "Trọn bộ",
                            source = MovieSource.FREEREELS
                        )
                    )
                }
            }
        }
    }

    data class TabMeta(val moduleKey: String, val pos: Int, val simpleNext: Boolean)

    private val TAB_META = mapOf(
        "503" to TabMeta("1036", 10000, true),
        "505" to TabMeta("1040", 10001, false),
        "504" to TabMeta("1039", 10003, false),
        "506" to TabMeta("1041", 10004, false),
        "547" to TabMeta("2204", 10005, true)
    )

    fun fetchTabFeedOffset(client: OkHttpClient, gson: Gson, tabKey: String = "503", offset: Int = 0): List<MovieItem> {
        val list = mutableListOf<MovieItem>()
        try {
            if (tabKey == "foryou") {
                val nextParam = if (offset > 0) "offset=$offset" else ""
                val req = buildAuthorizedRequest(client, gson, "$API_BASE/foryou/feed?next=${java.net.URLEncoder.encode(nextParam, "UTF-8")}", "GET")
                    ?: return emptyList()
                client.newCall(req).execute().use { resp ->
                    if (!resp.isSuccessful) return emptyList()
                    val respStr = resp.body?.string() ?: return emptyList()
                    val root = gson.fromJson(respStr, JsonObject::class.java)
                    val data = root.getAsJsonObject("data") ?: return emptyList()
                    val items = if (data.has("items") && !data.get("items").isJsonNull) data.getAsJsonArray("items")
                                else if (data.has("list") && !data.get("list").isJsonNull) data.getAsJsonArray("list")
                                else null
                    parseDramaItems(items, list)
                }
                return list
            }

            val meta = TAB_META[tabKey] ?: TAB_META["503"]!!
            val nextStr = if (meta.simpleNext) {
                "offset=$offset&position_index=${meta.pos}"
            } else {
                "last_quality=0&offset=$offset&position_index=${meta.pos}&timestamp="
            }

            val bodyJson = JsonObject().apply {
                addProperty("tab_key", tabKey)
                addProperty("module_key", meta.moduleKey)
                addProperty("next", nextStr)
            }.toString()

            val req = buildAuthorizedRequest(client, gson, "$API_BASE/homepage/v2/tab/feed", "POST", bodyJson)
                ?: return emptyList()

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return emptyList()
                val respStr = resp.body?.string() ?: return emptyList()
                val root = gson.fromJson(respStr, JsonObject::class.java)
                val data = root.getAsJsonObject("data") ?: return emptyList()
                val items = if (data.has("items") && !data.get("items").isJsonNull) data.getAsJsonArray("items")
                            else if (data.has("list") && !data.get("list").isJsonNull) data.getAsJsonArray("list")
                            else null
                parseDramaItems(items, list)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }

    fun getDramaList(client: OkHttpClient, gson: Gson, filterUrl: String, page: Int): List<MovieItem> {
        val baseOffset = (page - 1) * 20
        return when {
            filterUrl == "freereels://foryou" || filterUrl.startsWith("freereels://foryou") -> {
                val a = fetchTabFeedOffset(client, gson, "503", baseOffset + 10)
                val b = fetchTabFeedOffset(client, gson, "504", baseOffset + 20)
                (a + b).distinctBy { it.id }
            }
            filterUrl == "freereels://dubbed_vi" -> {
                val a = fetchTabFeedOffset(client, gson, "503", baseOffset)
                val b = fetchTabFeedOffset(client, gson, "504", baseOffset)
                val c = fetchTabFeedOffset(client, gson, "506", baseOffset)
                val combined = (a + b + c).distinctBy { it.id }
                val dubbed = combined.filter { it.name.contains("lồng tiếng", ignoreCase = true) || it.name.contains("thuyết minh", ignoreCase = true) }
                if (dubbed.isNotEmpty()) dubbed else combined
            }
            filterUrl.startsWith("freereels://tab_") -> {
                val tabKey = filterUrl.removePrefix("freereels://tab_")
                val a = fetchTabFeedOffset(client, gson, tabKey, baseOffset)
                val b = fetchTabFeedOffset(client, gson, tabKey, baseOffset + 10)
                (a + b).distinctBy { it.id }
            }
            else -> {
                val a = fetchTabFeedOffset(client, gson, "503", baseOffset)
                val b = fetchTabFeedOffset(client, gson, "foryou", baseOffset)
                (a + b).distinctBy { it.id }
            }
        }
    }

    private val FALLBACK_FEED_MAP = mapOf(
        "người sói" to listOf("505", "0", "foryou", "10"),
        "vua sói" to listOf("505", "20", "foryou", "0"),
        "ma cà rồng" to listOf("505", "20", "foryou", "30"),
        "tỷ phú" to listOf("505", "10", "foryou", "20"),
        "mafia" to listOf("505", "30", "foryou", "40"),
        "hợp đồng" to listOf("505", "40", "foryou", "50"),
        "tổng tài" to listOf("504", "0", "503", "10"),
        "báo thù" to listOf("503", "20", "504", "20"),
        "trọng sinh" to listOf("503", "30", "504", "30"),
        "chiến thần" to listOf("503", "10", "506", "30"),
        "cổ trang" to listOf("504", "10", "506", "20"),
        "hào môn" to listOf("504", "40", "503", "20"),
        "nghịch tập" to listOf("506", "10", "503", "40"),
        "cao thủ" to listOf("506", "30", "503", "10"),
        "thần y" to listOf("506", "20", "506", "30"),
        "mạt thế" to listOf("506", "40", "547", "20"),
        "thế thân" to listOf("504", "20", "505", "20"),
        "người máy" to listOf("547", "10", "547", "0"),
        "trí tuệ nhân tạo" to listOf("547", "20", "506", "20"),
        "khoa học" to listOf("547", "20", "547", "30"),
        "đếm ngược" to listOf("547", "30", "506", "10"),
        "hệ thống" to listOf("547", "0", "503", "20"),
        "cưng chiều" to listOf("foryou", "0", "504", "20"),
        "tình yêu" to listOf("foryou", "10", "504", "30"),
        "định mệnh" to listOf("foryou", "20", "505", "10"),
        "cô dâu" to listOf("foryou", "10", "504", "10"),
        "ngọt sủng" to listOf("foryou", "30", "504", "0"),
        "bảo bối" to listOf("504", "30", "foryou", "40"),
        "lồng tiếng" to listOf("503", "0", "506", "0")
    )

    fun search(client: OkHttpClient, gson: Gson, keyword: String, page: Int = 1): List<MovieItem> {
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
            }.toString()

            val req = buildAuthorizedRequest(client, gson, "$API_BASE/search/drama", "POST", jsonBody)
            if (req != null) {
                client.newCall(req).execute().use { resp ->
                    if (resp.isSuccessful) {
                        val respStr = resp.body?.string() ?: ""
                        val root = gson.fromJson(respStr, JsonObject::class.java)
                        val data = root.getAsJsonObject("data")
                        if (data != null) {
                            val itemsArray = if (data.has("items") && !data.get("items").isJsonNull) {
                                data.getAsJsonArray("items")
                            } else if (data.has("list") && !data.get("list").isJsonNull) {
                                data.getAsJsonArray("list")
                            } else null

                            parseDramaItems(itemsArray, list)
                        }
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        if (list.size < 4) {
            val kwLower = keyword.lowercase().trim()
            val cfg = FALLBACK_FEED_MAP[kwLower] ?: listOf("503", ((kwLower.length % 5) * 10).toString(), "foryou", (((kwLower.length + 2) % 5) * 10).toString())
            val pOffset = (cfg[1].toIntOrNull() ?: 0) + (page - 1) * 20
            val sOffset = (cfg[3].toIntOrNull() ?: 0) + (page - 1) * 20
            val batch1 = fetchTabFeedOffset(client, gson, cfg[0], pOffset)
            val batch2 = fetchTabFeedOffset(client, gson, cfg[2], sOffset)
            val combined = (batch1 + batch2).distinctBy { it.id }
            if (combined.isNotEmpty()) {
                list.addAll(combined)
            }
        }

        return list.distinctBy { it.id }
    }

    fun getDramaDetail(client: OkHttpClient, gson: Gson, seriesId: String): MovieDetail? {
        return try {
            val cleanSeriesId = seriesId.removePrefix("freereels:")
            val req = buildAuthorizedRequest(client, gson, "$API_BASE/drama/info_v2?series_id=$cleanSeriesId&scene=search", "GET")
                ?: return null

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return null
                val respStr = resp.body?.string() ?: return null
                val root = gson.fromJson(respStr, JsonObject::class.java)
                val data = root.getAsJsonObject("data") ?: return null
                val info = if (data.has("info") && data.get("info").isJsonObject) {
                    data.getAsJsonObject("info")
                } else data

                val title = info.getSafeString("name").ifEmpty { info.getSafeString("title") }
                val cover = info.getSafeString("cover").ifEmpty { info.getSafeString("poster") }
                val desc = info.getSafeString("desc").ifEmpty { "Phim ngắn màn hình dọc FreeReels chất lượng cao (9:16) kèm phụ đề/thuyết minh Tiếng Việt." }
                val epCount = info.getSafeString("episode_count", "Nhiều")

                val epList = mutableListOf<EpisodeItem>()
                val epArray = if (info.has("episode_list") && !info.get("episode_list").isJsonNull) {
                    info.getAsJsonArray("episode_list")
                } else null

                epArray?.forEachIndexed { idx, el ->
                    if (el.isJsonObject) {
                        val epObj = el.asJsonObject
                        val epId = epObj.getSafeString("id").ifEmpty { epObj.getSafeString("key") }
                        val rawName = epObj.getSafeString("name").trim()
                        val epName = if (rawName.isEmpty() || rawName.equals(title, ignoreCase = true) || rawName.length > 20) {
                            "Tập ${idx + 1}"
                        } else if (rawName.all { it.isDigit() }) {
                            "Tập $rawName"
                        } else {
                            rawName
                        }

                        var viSubUrl: String? = null
                        if (epObj.has("subtitle_list") && epObj.get("subtitle_list").isJsonArray) {
                            val subs = epObj.getAsJsonArray("subtitle_list")
                            subs.forEach { sEl ->
                                if (sEl.isJsonObject) {
                                    val sObj = sEl.asJsonObject
                                    val lang = sObj.getSafeString("language").lowercase()
                                    val disp = sObj.getSafeString("display_name").lowercase()
                                    if (lang.contains("vi") || disp.contains("việt") || disp.contains("viet")) {
                                        val vtt = sObj.getSafeString("vtt")
                                        val srt = sObj.getSafeString("subtitle")
                                        viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                                    }
                                }
                            }
                            if (viSubUrl == null && subs.size() > 0) {
                                for (sEl in subs) {
                                    if (sEl.isJsonObject) {
                                        val sObj = sEl.asJsonObject
                                        val lang = sObj.getSafeString("language").lowercase()
                                        if (lang.contains("en")) {
                                            val vtt = sObj.getSafeString("vtt")
                                            val srt = sObj.getSafeString("subtitle")
                                            viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                                            break
                                        }
                                    }
                                }
                                if (viSubUrl == null) {
                                    val sObj = subs[0].asJsonObject
                                    val vtt = sObj.getSafeString("vtt")
                                    val srt = sObj.getSafeString("subtitle")
                                    viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                                }
                            }
                        }

                        epList.add(
                            EpisodeItem(
                                name = epName,
                                slug = epId,
                                filename = epName,
                                linkM3u8 = "freereels_unlock:$cleanSeriesId:$epId",
                                linkEmbed = null,
                                subtitleUrl = viSubUrl
                            )
                        )
                    }
                }

                // Tự động mở khóa trước link tập 1 để phát mượt ngay tức thì
                if (epList.isNotEmpty()) {
                    val firstEp = epList[0]
                    val unlockRes = unlockEpisode(client, gson, cleanSeriesId, firstEp.slug)
                    if (unlockRes != null) {
                        epList[0] = firstEp.copy(
                            linkM3u8 = unlockRes.streamUrl,
                            subtitleUrl = unlockRes.subtitleUrl ?: firstEp.subtitleUrl
                        )
                    }
                }

                MovieDetail(
                    id = "freereels:$cleanSeriesId",
                    name = title,
                    slug = "freereels:$cleanSeriesId",
                    originName = "$epCount tập • FreeReels Dọc (9:16)",
                    content = desc,
                    thumbUrl = cover,
                    posterUrl = cover,
                    year = "2026",
                    time = "$epCount tập",
                    quality = "9:16 Dọc HD",
                    lang = "Vietsub / Thuyết Minh Tiếng Việt",
                    source = MovieSource.FREEREELS,
                    servers = listOf(
                        ServerGroup(
                            serverName = "FreeReels VIP (Phụ Đề / Lồng Tiếng Việt)",
                            episodes = epList
                        )
                    )
                )
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    fun unlockEpisode(client: OkHttpClient, gson: Gson, seriesId: String, episodeId: String): FreeReelsUnlocked? {
        return try {
            val cleanSeriesId = seriesId.removePrefix("freereels:")
            val jsonBody = JsonObject().apply {
                addProperty("series_id", cleanSeriesId)
                addProperty("episode_id", episodeId)
                addProperty("lang", "vi")
            }.toString()

            val req = buildAuthorizedRequest(client, gson, "$API_BASE/drama/unlock_episode", "POST", jsonBody)
                ?: return null

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return null
                val respStr = resp.body?.string() ?: return null
                val root = gson.fromJson(respStr, JsonObject::class.java)
                val data = root.getAsJsonObject("data") ?: return null

                val m3u8H264 = data.getSafeString("external_audio_h264_m3u8")
                val m3u8Url = data.getSafeString("m3u8_url")
                val videoUrl = data.getSafeString("video_url")
                val stream = when {
                    m3u8H264.isNotEmpty() -> m3u8H264
                    m3u8Url.isNotEmpty() -> m3u8Url
                    videoUrl.isNotEmpty() -> videoUrl
                    else -> null
                } ?: return null

                var viSubUrl: String? = null
                if (data.has("subtitle_list") && data.get("subtitle_list").isJsonArray) {
                    val subs = data.getAsJsonArray("subtitle_list")
                    subs.forEach { sEl ->
                        if (sEl.isJsonObject) {
                            val sObj = sEl.asJsonObject
                            val lang = sObj.getSafeString("language").lowercase()
                            val disp = sObj.getSafeString("display_name").lowercase()
                            if (lang.contains("vi") || disp.contains("việt") || disp.contains("viet")) {
                                val vtt = sObj.getSafeString("vtt")
                                val srt = sObj.getSafeString("subtitle")
                                viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                            }
                        }
                    }
                    if (viSubUrl == null && subs.size() > 0) {
                        for (sEl in subs) {
                            if (sEl.isJsonObject) {
                                val sObj = sEl.asJsonObject
                                val lang = sObj.getSafeString("language").lowercase()
                                if (lang.contains("en")) {
                                    val vtt = sObj.getSafeString("vtt")
                                    val srt = sObj.getSafeString("subtitle")
                                    viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                                    break
                                }
                            }
                        }
                        if (viSubUrl == null) {
                            val sObj = subs[0].asJsonObject
                            val vtt = sObj.getSafeString("vtt")
                            val srt = sObj.getSafeString("subtitle")
                            viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                        }
                    }
                }

                FreeReelsUnlocked(streamUrl = stream, subtitleUrl = viSubUrl)
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}'''

targets = [
    'HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt',
    'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt'
]

for file_path in targets:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Thay the object FreeReelsClient
    obj_pattern = r'object FreeReelsClient\s*\{[\s\S]*?\n\}\n\nobject GaMoMePhimClient'
    if not re.search(obj_pattern, content):
        print(f'Cannot find FreeReelsClient in {file_path}')
        continue
    content = re.sub(obj_pattern, freereels_client_code + '\n\nobject GaMoMePhimClient', content)

    # 2. Dam bao getMovieDetail xu ly linh hoat slug freereels: hoac gamomephim:
    old_detail_check = '''} else if (source == MovieSource.FREEREELS) {
                    if (slug.startsWith("gamomephim:")) {
                        GaMoMePhimClient.getDramaDetail(client, slug.removePrefix("gamomephim:"))
                    } else {
                        FreeReelsClient.getDramaDetail(client, gson, slug)
                    }'''

    new_detail_check = '''} else if (source == MovieSource.FREEREELS || slug.startsWith("freereels:") || slug.startsWith("gamomephim:")) {
                    if (slug.startsWith("gamomephim:")) {
                        GaMoMePhimClient.getDramaDetail(client, slug.removePrefix("gamomephim:"))
                    } else {
                        val cleanId = slug.removePrefix("freereels:")
                        FreeReelsClient.getDramaDetail(client, gson, cleanId)
                    }'''

    if old_detail_check in content:
        content = content.replace(old_detail_check, new_detail_check)
        print(f'Updated getMovieDetail in {file_path}')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Successfully updated {file_path}')
