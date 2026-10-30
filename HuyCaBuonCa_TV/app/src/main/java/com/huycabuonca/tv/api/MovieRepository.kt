package com.huycabuonca.tv.api

import android.content.Context
import com.google.gson.Gson
import com.google.gson.JsonArray
import com.google.gson.JsonObject
import com.google.gson.reflect.TypeToken
import com.huycabuonca.tv.model.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.OkHttpClient
import okhttp3.Request
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import com.google.gson.JsonParser
import java.net.URLEncoder
import java.security.MessageDigest
import java.util.UUID
import java.util.concurrent.TimeUnit

data class TvChannelItem(
    val id: String,
    val name: String,
    val group: String,
    val logo: String,
    val url: String
)

data class FreeReelsUnlocked(
    val streamUrl: String,
    val subtitleUrl: String?
)

object MovieRepository {

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()
    private const val KKPHIM_IMG_BASE = "https://phimimg.com/"
    private var cachedTvChannels: List<TvChannelItem>? = null

    fun initTvChannels(context: Context, forceReload: Boolean = false) {
        if (cachedTvChannels != null && !forceReload) return
        val appContext = context.applicationContext
        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
            try {
                val jsonString = appContext.assets.open("tv_channels.json").bufferedReader().use { it.readText() }
                val itemType = object : TypeToken<List<TvChannelItem>>() {}.type
                val baseList: List<TvChannelItem> = gson.fromJson(jsonString, itemType) ?: emptyList()
                val custom = getCustomChannels(appContext)
                cachedTvChannels = custom + baseList
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    fun getAllTvChannels(context: Context? = null): List<TvChannelItem> {
        if (cachedTvChannels == null && context != null) {
            try {
                val jsonString = context.applicationContext.assets.open("tv_channels.json").bufferedReader().use { it.readText() }
                val itemType = object : TypeToken<List<TvChannelItem>>() {}.type
                val baseList: List<TvChannelItem> = gson.fromJson(jsonString, itemType) ?: emptyList()
                val custom = getCustomChannels(context.applicationContext)
                cachedTvChannels = custom + baseList
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
        return cachedTvChannels ?: emptyList()
    }

    fun getCustomChannels(context: Context): List<TvChannelItem> {
        val sp = context.getSharedPreferences("custom_iptv_prefs", Context.MODE_PRIVATE)
        val json = sp.getString("custom_channels_json", null) ?: return emptyList()
        return try {
            val itemType = object : TypeToken<List<TvChannelItem>>() {}.type
            gson.fromJson(json, itemType) ?: emptyList()
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun addCustomChannel(context: Context, name: String, url: String, group: String = "Kênh Tự Thêm"): TvChannelItem {
        val current = getCustomChannels(context).toMutableList()
        val id = "custom_${System.currentTimeMillis()}"
        val defaultLogo = "https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png"
        val newChannel = TvChannelItem(id = id, name = name, group = group, logo = defaultLogo, url = url)
        current.add(0, newChannel)
        val sp = context.getSharedPreferences("custom_iptv_prefs", Context.MODE_PRIVATE)
        sp.edit().putString("custom_channels_json", gson.toJson(current)).apply()
        
        initTvChannels(context, forceReload = true)
        return newChannel
    }

    fun getChannelsInSameGroup(channelIdOrUrl: String, context: Context? = null): List<TvChannelItem> {
        val all = getAllTvChannels(context)
        val cur = all.find { it.id == channelIdOrUrl || it.url == channelIdOrUrl }
        return if (cur != null) {
            val same = all.filter { it.group.equals(cur.group, ignoreCase = true) }
            if (same.isNotEmpty()) same else all
        } else all
    }

    fun isChannelFavorite(context: Context, channelId: String): Boolean {
        val sp = context.getSharedPreferences("favorite_channels_prefs", Context.MODE_PRIVATE)
        val favSet = sp.getStringSet("fav_ids", emptySet()) ?: emptySet()
        return favSet.contains(channelId)
    }

    fun toggleChannelFavorite(context: Context, channelId: String): Boolean {
        val sp = context.getSharedPreferences("favorite_channels_prefs", Context.MODE_PRIVATE)
        val favSet = (sp.getStringSet("fav_ids", emptySet()) ?: emptySet()).toMutableSet()
        val isFav = if (favSet.contains(channelId)) {
            favSet.remove(channelId)
            false
        } else {
            favSet.add(channelId)
            true
        }
        sp.edit().putStringSet("fav_ids", favSet).apply()
        return isFav
    }

    fun getFavoriteChannelIds(context: Context): Set<String> {
        val sp = context.getSharedPreferences("favorite_channels_prefs", Context.MODE_PRIVATE)
        return sp.getStringSet("fav_ids", emptySet()) ?: emptySet()
    }

    fun getLastWatchedChannelId(context: Context): String? {
        val sp = context.getSharedPreferences("tv_history_prefs", Context.MODE_PRIVATE)
        return sp.getString("last_watched_channel_id", null)
    }

    fun setLastWatchedChannelId(context: Context, channelId: String) {
        val sp = context.getSharedPreferences("tv_history_prefs", Context.MODE_PRIVATE)
        sp.edit().putString("last_watched_channel_id", channelId).apply()
    }

    fun importM3uPlaylist(context: Context, m3uContent: String): Int {
        val lines = m3uContent.lines()
        val imported = mutableListOf<TvChannelItem>()
        var currentName = ""
        var currentGroup = "M3U Tự Thêm"
        var currentLogo = "https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png"
        
        for (line in lines) {
            val trimmed = line.trim()
            if (trimmed.startsWith("#EXTINF")) {
                val groupMatch = "group-title=\"([^\"]+)\"".toRegex().find(trimmed)
                if (groupMatch != null) currentGroup = groupMatch.groupValues[1]
                val logoMatch = "tvg-logo=\"([^\"]+)\"".toRegex().find(trimmed)
                if (logoMatch != null) currentLogo = logoMatch.groupValues[1]
                val nameParts = trimmed.split(",")
                if (nameParts.size > 1) currentName = nameParts.last().trim()
            } else if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
                if (currentName.isNotEmpty()) {
                    val id = "custom_${System.currentTimeMillis()}_${imported.size}"
                    imported.add(TvChannelItem(id = id, name = currentName, group = currentGroup, logo = currentLogo, url = trimmed))
                    currentName = ""
                }
            }
        }
        if (imported.isNotEmpty()) {
            val current = getCustomChannels(context).toMutableList()
            current.addAll(0, imported)
            val sp = context.getSharedPreferences("custom_iptv_prefs", Context.MODE_PRIVATE)
            sp.edit().putString("custom_channels_json", gson.toJson(current)).apply()
            
            initTvChannels(context, forceReload = true)
        }
        return imported.size
    }

        private var cachedMatches: List<FootballMatch>? = null
    private var lastMatchFetchTime: Long = 0L
    private const val MATCH_CACHE_DURATION = 10 * 60 * 1000L // 10 phút

    private fun formatEspnDate(isoDate: String): String {
        if (isoDate.isEmpty()) return "Hôm nay"
        val patterns = arrayOf(
            "yyyy-MM-dd'T'HH:mm'Z'",
            "yyyy-MM-dd'T'HH:mm:ss'Z'",
            "yyyy-MM-dd'T'HH:mmZ",
            "yyyy-MM-dd'T'HH:mm:ssZ"
        )
        for (p in patterns) {
            try {
                val sdf = SimpleDateFormat(p, Locale.US).apply {
                    timeZone = TimeZone.getTimeZone("UTC")
                }
                val date = sdf.parse(isoDate)
                if (date != null) {
                    val outSdf = SimpleDateFormat("HH:mm • dd/MM", Locale.getDefault()).apply {
                        timeZone = TimeZone.getTimeZone("GMT+7")
                    }
                    return outSdf.format(date)
                }
            } catch (_: Exception) {}
        }
        return isoDate
    }

    suspend fun fetchRealtimeLiveMatches(): List<FootballMatch> {
        val now = System.currentTimeMillis()
        if (cachedMatches != null && (now - lastMatchFetchTime) < MATCH_CACHE_DURATION) {
            return cachedMatches!!
        }

        return withContext(Dispatchers.IO) {
            val leagues = listOf(
                Triple("eng.1", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh", "True Premier Football 1 HD" to "sports_sat_true_premier_1"),
                Triple("uefa.champions", "🏆 Cúp C1 Châu Âu", "True Premier Football 2 HD" to "sports_sat_true_premier_2"),
                Triple("esp.1", "🇪🇸 La Liga", "Astro SuperSport 1 HD" to "sports_sat_astro_supersport_1"),
                Triple("ita.1", "🇮🇹 Serie A", "Astro SuperSport 2 HD" to "sports_sat_astro_supersport_2")
            )

            val results = mutableListOf<FootballMatch>()

            for ((leagueCode, leagueName, channelPair) in leagues) {
                val (chName, chSlug) = channelPair
                try {
                    val url = "https://site.api.espn.com/apis/site/v2/sports/soccer/$leagueCode/scoreboard"
                    val request = Request.Builder()
                        .url(url)
                        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
                        .build()

                    val response = client.newCall(request).execute()
                    if (response.isSuccessful) {
                        val body = response.body?.string() ?: ""
                        if (body.isNotEmpty()) {
                            val jsonRoot = JsonParser.parseString(body).asJsonObject
                            val events = jsonRoot.getAsJsonArray("events")
                            if (events != null) {
                                for (evElement in events) {
                                    val ev = evElement.asJsonObject
                                    val mId = if (ev.has("id")) ev.get("id").asString else ""
                                    val dateIso = if (ev.has("date")) ev.get("date").asString else ""
                                    val formattedTime = formatEspnDate(dateIso)

                                    val statusObj = if (ev.has("status") && ev.get("status").isJsonObject) ev.getAsJsonObject("status") else null
                                    val typeObj = if (statusObj != null && statusObj.has("type") && statusObj.get("type").isJsonObject) statusObj.getAsJsonObject("type") else null
                                    val state = if (typeObj != null && typeObj.has("state")) typeObj.get("state").asString else "pre"
                                    val detail = if (typeObj != null && typeObj.has("detail")) typeObj.get("detail").asString else ""

                                    val competitions = if (ev.has("competitions") && ev.get("competitions").isJsonArray) ev.getAsJsonArray("competitions") else null
                                    val firstComp = if (competitions != null && competitions.size() > 0 && competitions.get(0).isJsonObject) competitions.get(0).asJsonObject else null
                                    val competitors = if (firstComp != null && firstComp.has("competitors") && firstComp.get("competitors").isJsonArray) firstComp.getAsJsonArray("competitors") else null

                                    var teamHome = ""
                                    var teamAway = ""
                                    var logoHome = ""
                                    var logoAway = ""
                                    var scoreHome = ""
                                    var scoreAway = ""

                                    if (competitors != null) {
                                        for (compElement in competitors) {
                                            if (!compElement.isJsonObject) continue
                                            val comp = compElement.asJsonObject
                                            val isHome = comp.has("homeAway") && comp.get("homeAway").asString == "home"
                                            val teamObj = if (comp.has("team") && comp.get("team").isJsonObject) comp.getAsJsonObject("team") else null
                                            val tName = if (teamObj != null && teamObj.has("displayName")) teamObj.get("displayName").asString else ""
                                            val tLogo = if (teamObj != null && teamObj.has("logo")) teamObj.get("logo").asString else ""
                                            val sc = if (comp.has("score")) comp.get("score").asString else ""

                                            if (isHome) {
                                                teamHome = tName
                                                logoHome = tLogo
                                                scoreHome = sc
                                            } else {
                                                teamAway = tName
                                                logoAway = tLogo
                                                scoreAway = sc
                                            }
                                        }
                                    }

                                    val isLiveMatch = (state == "in")
                                    val (matchTime, matchScore) = when {
                                        state == "in" -> {
                                            val liveStatus = if (detail.isNotEmpty()) "🔴 $detail" else "🔴 LIVE"
                                            val sc = if (scoreHome.isNotEmpty() && scoreAway.isNotEmpty()) "$scoreHome - $scoreAway" else "LIVE"
                                            liveStatus to sc
                                        }
                                        state == "post" -> {
                                            val sc = if (scoreHome.isNotEmpty() && scoreAway.isNotEmpty()) "$scoreHome - $scoreAway" else "FT"
                                            "🏁 Hết Giờ" to sc
                                        }
                                        else -> {
                                            formattedTime to "VS"
                                        }
                                    }

                                    results.add(
                                        FootballMatch(
                                            id = "espn_$mId",
                                            time = matchTime,
                                            tournament = leagueName,
                                            teamA = if (teamHome.isNotEmpty()) teamHome else "Đội Nhà",
                                            teamB = if (teamAway.isNotEmpty()) teamAway else "Đội Khách",
                                            channelName = chName,
                                            channelSlug = chSlug,
                                            score = matchScore,
                                            logoA = logoHome,
                                            logoB = logoAway,
                                            isLive = isLiveMatch
                                        )
                                    )
                                }
                            }
                        }
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }

            val sorted = results.sortedWith(
                compareBy(
                    { match ->
                        when {
                            match.isLive -> 0
                            match.time.contains("🔴") -> 0
                            match.score == "VS" -> 1
                            else -> 2
                        }
                    }
                )
            )

            if (sorted.isNotEmpty()) {
                cachedMatches = sorted
                lastMatchFetchTime = System.currentTimeMillis()
                sorted
            } else {
                cachedMatches ?: emptyList()
            }
        }
    }

    fun getLiveMatches(): List<FootballMatch> {
        return cachedMatches ?: emptyList()
    }

    fun setMatchAlarm(context: Context, match: FootballMatch, enable: Boolean) {
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as? android.app.AlarmManager ?: return
        try {
            val intent = android.content.Intent().apply {
                setClassName(context.packageName, "${context.packageName}.receiver.MatchReminderReceiver")
                putExtra("extra_match_id", match.id)
                putExtra("extra_team_a", match.teamA)
                putExtra("extra_team_b", match.teamB)
                putExtra("extra_time_str", match.time)
            }
            val requestCode = match.id.hashCode()
            val flag = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.M) {
                android.app.PendingIntent.FLAG_UPDATE_CURRENT or android.app.PendingIntent.FLAG_IMMUTABLE
            } else {
                android.app.PendingIntent.FLAG_UPDATE_CURRENT
            }
            val pendingIntent = android.app.PendingIntent.getBroadcast(context, requestCode, intent, flag)

            if (enable) {
                // Nhắc trước giờ đá (mặc định thử nghiệm sau 15 giây hoặc đúng giờ đá)
                val triggerTime = System.currentTimeMillis() + (15 * 1000)
                if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.M) {
                    alarmManager.setExactAndAllowWhileIdle(android.app.AlarmManager.RTC_WAKEUP, triggerTime, pendingIntent)
                } else {
                    alarmManager.setExact(android.app.AlarmManager.RTC_WAKEUP, triggerTime, pendingIntent)
                }
            } else {
                alarmManager.cancel(pendingIntent)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun exportBackupData(context: Context): String {
        val spCustom = context.getSharedPreferences("custom_iptv_prefs", Context.MODE_PRIVATE)
        val spVbook = context.getSharedPreferences("vbook_playback_prefs", Context.MODE_PRIVATE)
        val customChannels = spCustom.getString("custom_channels_json", "[]")
        
        val backupObj = JsonObject().apply {
            addProperty("app", "HuyCaBuonCa")
            addProperty("version", "1.8")
            addProperty("export_date", System.currentTimeMillis())
            add("custom_channels", gson.fromJson(customChannels, com.google.gson.JsonArray::class.java))
            addProperty("sub_font_size", spVbook.getFloat("sub_font_size", 18f))
            addProperty("sub_font_color", spVbook.getString("sub_font_color", "#FFD700"))
            addProperty("data_saver", spVbook.getBoolean("data_saver", false))
            addProperty("volume_boost", spVbook.getInt("volume_boost_gain", 0))
        }
        return gson.toJson(backupObj)
    }

    fun restoreBackupData(context: Context, jsonString: String): Boolean {
        return try {
            val root = gson.fromJson(jsonString, JsonObject::class.java) ?: return false
            if (!root.has("app")) return false
            
            if (root.has("custom_channels")) {
                val customArr = root.getAsJsonArray("custom_channels")
                val spCustom = context.getSharedPreferences("custom_iptv_prefs", Context.MODE_PRIVATE)
                spCustom.edit().putString("custom_channels_json", gson.toJson(customArr)).apply()
                initTvChannels(context, forceReload = true)
            }
            val spVbook = context.getSharedPreferences("vbook_playback_prefs", Context.MODE_PRIVATE)
            val editor = spVbook.edit()
            if (root.has("sub_font_size")) editor.putFloat("sub_font_size", root.get("sub_font_size").asFloat)
            if (root.has("sub_font_color")) editor.putString("sub_font_color", root.get("sub_font_color").asString)
            if (root.has("data_saver")) editor.putBoolean("data_saver", root.get("data_saver").asBoolean)
            if (root.has("volume_boost")) editor.putInt("volume_boost_gain", root.get("volume_boost").asInt)
            editor.apply()
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    fun TvChannelItem.toMovieItem(): MovieItem {
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

    fun getAnimeSubSources(): List<FilterItem> {
        return listOf(
            FilterItem("⛩️ Anime Vietsub", "anime_sub://vietsub"),
            FilterItem("🐉 Hoạt Hình 3D Trung Quốc", "anime_sub://hh3d"),
            FilterItem("🏰 Hoạt Hình Chiếu Rạp", "anime_sub://movies"),
            FilterItem("🎙️ Anime Thuyết Minh (Tổng Hợp)", "anime_sub://dubbed")
        )
    }

    fun getAnimeFilters(subSourceUrl: String): List<FilterItem> {
        return when (subSourceUrl) {
            "anime_sub://hh3d" -> listOf(
                FilterItem("3D Mới Cập Nhật", "https://phimapi.com/v1/api/danh-sach/hoat-hinh"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Hoạt Hình Yêu Thích", "app://favorites"),
                FilterItem("Tu Tiên & Huyền Huyễn", "https://phimapi.com/v1/api/the-loai/than-thoai"),
                FilterItem("Kiếm Hiệp & Võ Thuật", "https://phimapi.com/v1/api/the-loai/kiem-hiep"),
                FilterItem("Hành Động 3D", "https://phimapi.com/v1/api/the-loai/hanh-dong"),
                FilterItem("Cổ Trang 3D", "https://phimapi.com/v1/api/the-loai/co-trang")
            )
            "anime_sub://movies" -> listOf(
                FilterItem("Hoạt Hình Chiếu Rạp", "https://phimapi.com/v1/api/danh-sach/hoat-hinh"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites"),
                FilterItem("Ghibli & Cổ Điển", "https://phimapi.com/v1/api/the-loai/gia-dinh"),
                FilterItem("Phiêu Lưu", "https://phimapi.com/v1/api/the-loai/phieu-luu"),
                FilterItem("Hài Hước", "https://phimapi.com/v1/api/the-loai/hai-huoc")
            )
            "anime_sub://dubbed" -> listOf(
                FilterItem("🎙️ Tất Cả Anime Thuyết Minh", "anime_dubbed://all"),
                FilterItem("⛩️ Anime Nhật Lồng Tiếng", "anime_dubbed://japan"),
                FilterItem("🐉 Hoạt Hình 3D Trung Quốc", "anime_dubbed://china"),
                FilterItem("🏰 Hoạt Hình Chiếu Rạp", "anime_dubbed://cinema"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            else -> listOf(
                FilterItem("Anime Mới Cập Nhật", "https://phimapi.com/v1/api/danh-sach/hoat-hinh"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Anime Yêu Thích", "app://favorites"),
                FilterItem("Hành Động", "https://phimapi.com/v1/api/the-loai/hanh-dong"),
                FilterItem("Thần Thoại", "https://phimapi.com/v1/api/the-loai/than-thoai"),
                FilterItem("Học Đường", "https://phimapi.com/v1/api/the-loai/hoc-duong"),
                FilterItem("Viễn Tưởng", "https://phimapi.com/v1/api/the-loai/vien-tuong")
            )
        }
    }

    fun getMovieSubSources(): List<FilterItem> {
        return listOf(
            FilterItem("⚡ KKPhim VIP (HLS 1080p)", "movie_sub://kkphim"),
            FilterItem("🔥 NguonC Cinema (Phim Rạp & Mới)", "movie_sub://nguonc"),
            FilterItem("🎙️ Thuyết Minh & Lồng Tiếng", "movie_sub://dubbed"),
            FilterItem("🍿 Phim Chiếu Rạp Bom Tấn", "movie_sub://cinema")
        )
    }

    fun getMovieFilters(subSourceUrl: String): List<FilterItem> {
        return when (subSourceUrl) {
            "movie_sub://nguonc" -> listOf(
                FilterItem("🔥 Mới Cập Nhật", "https://phim.nguonc.com/api/films/phim-moi-cap-nhat"),
                FilterItem("🎬 Phim Bộ Mới", "https://phim.nguonc.com/api/films/danh-sach/phim-bo"),
                FilterItem("🍿 Phim Lẻ / Chiếu Rạp", "https://phim.nguonc.com/api/films/danh-sach/phim-le"),
                FilterItem("📺 TV Shows", "https://phim.nguonc.com/api/films/danh-sach/tv-shows"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Phim Yêu Thích", "app://favorites")
            )
            "movie_sub://dubbed" -> listOf(
                FilterItem("🎙️ Thuyết Minh Chuẩn", "https://phimapi.com/v1/api/danh-sach/phim-thuyet-minh"),
                FilterItem("🗣️ Lồng Tiếng", "https://phimapi.com/v1/api/danh-sach/phim-long-tieng"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Phim Yêu Thích", "app://favorites")
            )
            "movie_sub://cinema" -> listOf(
                FilterItem("🍿 Chiếu Rạp Mới Nhất", "https://phimapi.com/v1/api/danh-sach/phim-le"),
                FilterItem("🇺🇸 Bom Tấn Âu Mỹ", "https://phimapi.com/v1/api/quoc-gia/au-my"),
                FilterItem("🇰🇷 Chiếu Rạp Hàn Quốc", "https://phimapi.com/v1/api/quoc-gia/han-quoc"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Phim Yêu Thích", "app://favorites")
            )
            else -> listOf(
                FilterItem("Mới Cập Nhật", "https://phimapi.com/danh-sach/phim-moi-cap-nhat"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Phim Yêu Thích", "app://favorites"),
                FilterItem("Phim Bộ", "https://phimapi.com/v1/api/danh-sach/phim-bo"),
                FilterItem("Phim Lẻ", "https://phimapi.com/v1/api/danh-sach/phim-le"),
                FilterItem("TV Shows", "https://phimapi.com/v1/api/danh-sach/tv-shows"),
                FilterItem("Hành Động", "https://phimapi.com/v1/api/the-loai/hanh-dong"),
                FilterItem("Cổ Trang", "https://phimapi.com/v1/api/the-loai/co-trang"),
                FilterItem("Tình Cảm", "https://phimapi.com/v1/api/the-loai/tinh-cam"),
                FilterItem("Kinh Dị", "https://phimapi.com/v1/api/the-loai/kinh-di"),
                FilterItem("Hàn Quốc", "https://phimapi.com/v1/api/quoc-gia/han-quoc"),
                FilterItem("Trung Quốc", "https://phimapi.com/v1/api/quoc-gia/trung-quoc"),
                FilterItem("Âu Mỹ", "https://phimapi.com/v1/api/quoc-gia/au-my")
            )
        }
    }

    fun getShortDramaSubSources(): List<FilterItem> {
        return listOf(
            FilterItem("🐺 Nguồn ReelShort (Âu Mỹ)", "short_src://reelshort"),
            FilterItem("📱 Nguồn DramaBox (Top Thế Giới)", "short_src://dramabox"),
            FilterItem("⚡ Nguồn ShortMax (Thịnh Hành)", "short_src://shortmax"),
            FilterItem("💎 Nguồn FreeReels Gốc (9:16)", "short_src://freereels"),
            FilterItem("🎙️ Nguồn Gà Mờ Mê Phim (Thuyết Minh)", "short_src://gamomephim"),
            FilterItem("🤖 Nguồn AI Cinema (Phim AI & Sora)", "short_src://aicinema"),
            FilterItem("🎭 Nguồn GoodShort & Sereal+", "short_src://goodshort")
        )
    }

    fun getShortDramaFilters(subSourceUrl: String): List<FilterItem> {
        return when (subSourceUrl) {
            "short_src://reelshort" -> listOf(
                FilterItem("🔥 Thịnh Hành ReelShort", "short_kw://reelshort_hot"),
                FilterItem("🐺 Người Sói & Alpha (Werewolf)", "short_kw://werewolf"),
                FilterItem("🧛 Ma Cà Rồng (Vampire)", "short_kw://vampire"),
                FilterItem("💎 Tỷ Phú Âu Mỹ (Billionaire)", "short_kw://billionaire"),
                FilterItem("🔫 Mafia & Boss Ngầm", "short_kw://mafia"),
                FilterItem("💔 Hôn Nhân Hợp Đồng & Ngược Tâm", "short_kw://rejected"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            "short_src://dramabox" -> listOf(
                FilterItem("🔥 Top Thịnh Hành DramaBox", "short_kw://dramabox_hot"),
                FilterItem("👑 Tổng Tài Bá Đạo", "short_kw://tong_tai"),
                FilterItem("🐉 Trọng Sinh & Báo Thù", "short_kw://trong_sinh"),
                FilterItem("⚔️ Chiến Thần & Long Vương", "short_kw://chien_than"),
                FilterItem("🏰 Cổ Trang & Cung Đấu", "short_kw://co_trang"),
                FilterItem("💖 Hào Môn Thế Gia", "short_kw://hao_mon"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            "short_src://shortmax" -> listOf(
                FilterItem("⚡ Thịnh Hành ShortMax", "short_kw://shortmax_hot"),
                FilterItem("🚀 Nghịch Tập Đổi Đời", "short_kw://nghich_tap"),
                FilterItem("🩺 Thần Y & Cao Thủ", "short_kw://than_y"),
                FilterItem("🧟 Sinh Tồn & Mạt Thế", "short_kw://mat_the"),
                FilterItem("💍 Cô Dâu Thế Thân & Ngược Tâm", "short_kw://nguoc_tam"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            "short_src://gamomephim" -> listOf(
                FilterItem("🔥 Phim Mới Cập Nhật", "gamomephim://phim-moi"),
                FilterItem("🏆 Bảng Xếp Hạng Thịnh Hành", "gamomephim://ban-xep-hang"),
                FilterItem("👑 Cưới Trước Yêu Sau & Tổng Tài", "gamomephim://the-loai/cuoi-truoc-yeu-sau"),
                FilterItem("🪞 Gương Vỡ Lại Lành & Ngược Tâm", "gamomephim://the-loai/guong-vo-lai-lanh"),
                FilterItem("💘 Yêu Thầm & Ngọt Sủng", "gamomephim://the-loai/yeu-tham"),
                FilterItem("🌆 Tiểu Kịch Hiện Đại", "gamomephim://the-loai/hien-dai"),
                FilterItem("🐉 Trọng Sinh & Báo Thù", "gamomephim://the-loai/trong-sinh"),
                FilterItem("⏳ Xuyên Không Trùng Sinh", "gamomephim://the-loai/xuyen-khong"),
                FilterItem("🏰 Cổ Trang & Cung Đấu", "gamomephim://the-loai/co-trang"),
                FilterItem("🤣 Hài Hước & Hóm Hỉnh", "gamomephim://the-loai/hai-huoc"),
                FilterItem("🍵 Trà Xanh Nam & Ngược Tâm", "gamomephim://the-loai/tra-xanh-nam"),
                FilterItem("✨ Chữa Lành & Thanh Xuân", "gamomephim://the-loai/chua-lanh"),
                FilterItem("🎒 Thanh Xuân Vườn Trường", "gamomephim://the-loai/thanh-xuan"),
                FilterItem("🕰️ Dân Quốc & Niên Đại", "gamomephim://the-loai/dan-quoc"),
                FilterItem("🌾 Niên Đại Thập Niên", "gamomephim://the-loai/nien-dai"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            "short_src://aicinema" -> listOf(
                FilterItem("🤖 Tất Cả Phim AI & Sora", "short_kw://ai_all"),
                FilterItem("🦾 Thế Giới Robot & Cyborg", "short_kw://ai_robot"),
                FilterItem("🌌 Khoa Học Viễn Tưởng (Sci-Fi)", "short_kw://ai_scifi"),
                FilterItem("⏳ Du Hành Tương Lai", "short_kw://ai_future"),
                FilterItem("🧬 Thực Tế Ảo & Huyền Huyễn AI", "short_kw://ai_fantasy"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            "short_src://goodshort" -> listOf(
                FilterItem("🌟 Tuyển Chọn GoodShort", "short_kw://goodshort_hot"),
                FilterItem("🎬 Sereal+ Quốc Tế", "short_kw://sereal"),
                FilterItem("🍿 MoboReels & Mini Drama", "short_kw://moboreels"),
                FilterItem("💕 Ngôn Tình Ngọt Sủng", "short_kw://ngot_sung"),
                FilterItem("👶 Bảo Bối Thiên Tài", "short_kw://bao_boi"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            else -> listOf(
                FilterItem("🔥 Đề Xuất Thịnh Hành", "freereels://foryou"),
                FilterItem("🎙️ Phim Lồng Tiếng Việt", "freereels://dubbed_vi"),
                FilterItem("⚡ Mới Lên Sóng", "freereels://tab_505"),
                FilterItem("🎀 Tuyển Tập Phim Nữ", "freereels://tab_504"),
                FilterItem("👑 Tuyển Tập Phim Nam", "freereels://tab_506"),
                FilterItem("🎭 Hoạt Hình Ngắn 3D", "freereels://tab_547"),
                FilterItem("👑 Trọn Bộ Hoàn Tất", "short_kw://tron_bo"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
        }
    }

    fun getFiltersForSource(source: MovieSource): List<FilterItem> {
        return when (source) {
            MovieSource.KKPHIM -> listOf(
                FilterItem("Mới Cập Nhật", "https://phimapi.com/danh-sach/phim-moi-cap-nhat"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Phim Yêu Thích", "app://favorites"),
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
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Anime Yêu Thích", "app://favorites"),
                FilterItem("Anime Hành Động", "https://phimapi.com/v1/api/the-loai/hanh-dong"),
                FilterItem("Anime Thần Thoại", "https://phimapi.com/v1/api/the-loai/than-thoai"),
                FilterItem("Anime Học Đường", "https://phimapi.com/v1/api/the-loai/hoc-duong"),
                FilterItem("Anime Viễn Tưởng", "https://phimapi.com/v1/api/the-loai/vien-tuong")
            )
            MovieSource.XEMTIVI -> listOf(
                FilterItem("Tất Cả Kênh", "tv://all"),
                FilterItem("⚽ Lịch Thi Đấu & Bóng Đá", "tv://schedule"),
                FilterItem("🕒 Kênh Vừa Xem", "app://history"),
                FilterItem("⭐ Kênh Yêu Thích", "tv://favorites"),
                FilterItem("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh (EPL)", "tv://epl"),
                FilterItem("📡 Kênh Vệ Tinh Quốc Tế", "tv://satellite"),
                FilterItem("⚽ Bóng Đá & Thể Thao VN", "tv://football"),
                FilterItem("🏆 Cúp C1 & Thể Thao ESPN", "tv://sports_intl"),
                FilterItem("🏎️ Đua Xe & Võ Thuật", "tv://racing_combat"),
                FilterItem("VTV Quốc Gia", "tv://vtv"),
                FilterItem("VTVcab", "tv://vtvcab"),
                FilterItem("SCTV", "tv://sctv"),
                FilterItem("Rạp Phim", "tv://movies"),
                FilterItem("Sự Kiện TV360", "tv://live"),
                FilterItem("Kênh Quốc Tế", "tv://intl"),
                FilterItem("Đài Địa Phương", "tv://local"),
                FilterItem("Radio Trực Tuyến", "tv://radio"),
                FilterItem("➕ Thêm Kênh IPTV", "tv://custom")
            )
            MovieSource.FREEREELS -> getShortDramaFilters("short_src://reelshort")
        }
    }

    suspend fun getMovies(source: MovieSource, filterUrl: String, page: Int = 1, context: Context? = null): List<MovieItem> {
        return withContext(Dispatchers.IO) {
            try {
                if (filterUrl == "app://favorites") {
                    val favs = if (context != null) com.huycabuonca.tv.util.FavoriteMovieManager.getFavorites(context) else emptyList()
                    return@withContext favs.filter { it.source == source }
                }
                if (filterUrl == "app://history") {
                    val history = if (context != null) com.huycabuonca.tv.util.WatchHistoryManager.getHistory(context) else emptyList()
                    return@withContext history.filter { it.movie.source == source }.map { it.movie }
                }

                if (source == MovieSource.XEMTIVI) {
                    val channels = cachedTvChannels ?: emptyList()
                    val filtered = when (filterUrl) {
                        "tv://favorites" -> {
                            val favIds = if (context != null) getFavoriteChannelIds(context) else emptySet()
                            channels.filter { it.id in favIds }
                        }
                        "tv://custom" -> channels.filter {
                            it.id.startsWith("custom_") ||
                            it.group.contains("Tự Thêm", ignoreCase = true) ||
                            it.group.contains("Cá Nhân", ignoreCase = true) ||
                            it.group.contains("M3U", ignoreCase = true)
                        }
                        "tv://vtv" -> channels.filter { it.group.equals("VTV", ignoreCase = true) || it.name.startsWith("VTV", ignoreCase = true) }
                        "tv://epl" -> channels.filter {
                            it.group.contains("Vệ Tinh", ignoreCase = true) ||
                            it.name.contains("True Premier", ignoreCase = true) ||
                            it.name.contains("Astro", ignoreCase = true) ||
                            it.name.contains("Sky Sports", ignoreCase = true) ||
                            it.name.contains("TNT Sports", ignoreCase = true) ||
                            it.name.contains("beIN", ignoreCase = true)
                        }
                        "tv://satellite" -> channels.filter {
                            it.group.contains("Vệ Tinh", ignoreCase = true) ||
                            it.name.contains("True Premier", ignoreCase = true) ||
                            it.name.contains("Astro", ignoreCase = true) ||
                            it.name.contains("Sky Sports", ignoreCase = true) ||
                            it.name.contains("TNT Sports", ignoreCase = true) ||
                            it.name.contains("beIN", ignoreCase = true) ||
                            it.name.contains("NBC Sports", ignoreCase = true)
                        }
                        "tv://schedule" -> channels.filter {
                            it.group.contains("Bóng Đá", ignoreCase = true) ||
                            it.group.contains("Vệ Tinh", ignoreCase = true) ||
                            it.name.contains("True Premier", ignoreCase = true) ||
                            it.name.contains("Astro", ignoreCase = true) ||
                            it.name.contains("VTV6", ignoreCase = true)
                        }
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
                            it.group.contains("TVB", ignoreCase = true) ||
                            it.group.contains("Vệ Tinh", ignoreCase = true) ||
                            it.name.contains("NHK", ignoreCase = true) ||
                            it.name.contains("Al Jazeera", ignoreCase = true) ||
                            it.name.contains("DW ", ignoreCase = true) ||
                            it.name.contains("France 24", ignoreCase = true) ||
                            it.name.contains("ABC News", ignoreCase = true) ||
                            it.name.contains("CBS News", ignoreCase = true) ||
                            it.name.contains("NBC News", ignoreCase = true) ||
                            it.name.contains("Bloomberg", ignoreCase = true) ||
                            it.name.contains("CNA", ignoreCase = true) ||
                            it.name.contains("Euronews", ignoreCase = true) ||
                            it.name.contains("Arirang", ignoreCase = true) ||
                            it.name.contains("Red Bull", ignoreCase = true) ||
                            it.name.contains("Reuters", ignoreCase = true) ||
                            it.name.contains("CNBC", ignoreCase = true)
                        }
                        "tv://local" -> channels.filter { 
                            it.group.contains("Địa phương", ignoreCase = true) || 
                            it.group.contains("HTV", ignoreCase = true) ||
                            it.name.startsWith("HTV", ignoreCase = true) ||
                            it.name.startsWith("THVL", ignoreCase = true)
                        }
                        "tv://radio" -> channels.filter { it.group.contains("Radio", ignoreCase = true) }
                        else -> channels
                    }
                    if (page == 1) {
                        filtered.map { it.toMovieItem() }
                    } else emptyList()

                } else if (source == MovieSource.FREEREELS) {
                    when {
                        filterUrl.startsWith("gamomephim://") -> {
                            GaMoMePhimClient.getDramaList(client, filterUrl, page)
                        }
                        filterUrl.startsWith("short_kw://") || filterUrl.startsWith("multi_short://") || filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://") -> {
                            fetchShortDramaList(filterUrl, page)
                        }
                        filterUrl.startsWith("https://phimapi.com") -> {
                            fetchKKPhimList(filterUrl, page, MovieSource.KKPHIM)
                        }
                        else -> {
                            FreeReelsClient.getDramaList(client, gson, filterUrl, page)
                        }
                    }
                } else if (filterUrl.startsWith("anime_dubbed://")) {
                    fetchPureAnimeDubbedList(filterUrl, page, source)
                } else {
                    if (filterUrl.startsWith("https://phim.nguonc.com") || filterUrl.startsWith("nguonc://")) {
                    NguonCClient.getFilmList(client, gson, filterUrl, page)
                } else {
                    fetchKKPhimList(filterUrl, page, source)
                }
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
                if (slug.startsWith("nguonc:")) {
                    val realSlug = slug.removePrefix("nguonc:")
                    NguonCClient.getFilmDetail(client, gson, realSlug)
                } else if (source == MovieSource.FREEREELS || slug.startsWith("freereels:") || slug.startsWith("gamomephim:")) {
                    if (slug.startsWith("gamomephim:")) {
                        GaMoMePhimClient.getDramaDetail(client, slug.removePrefix("gamomephim:"))
                    } else {
                        val cleanId = slug.removePrefix("freereels:")
                        FreeReelsClient.getDramaDetail(client, gson, cleanId)
                    }
                } else if (source == MovieSource.XEMTIVI) {
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

    suspend fun unlockFreeReelsEpisode(seriesId: String, episodeId: String): FreeReelsUnlocked? {
        return withContext(Dispatchers.IO) {
            FreeReelsClient.unlockEpisode(client, gson, seriesId, episodeId)
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

                // 1.5. Tim trong Ga Mo Me Phim
                val gaMoMatches = GaMoMePhimClient.search(client, keyword)
                results.addAll(gaMoMatches)

                // 2. Tim trong Phim Ngan FreeReels
                val freeReelsMatches = FreeReelsClient.search(client, gson, keyword)
                results.addAll(freeReelsMatches)

                // 3. Tim trong phim KKPhim
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
    private fun fetchPureAnimeDubbedList(filterUrl: String, page: Int, source: MovieSource): List<MovieItem> {
        val filterType = filterUrl.removePrefix("anime_dubbed://")
        val p1 = (page - 1) * 2 + 1
        val p2 = page * 2
        val items = mutableListOf<MovieItem>()

        for (p in listOf(p1, p2)) {
            val apiEndpoints = listOf(
                "https://phimapi.com/v1/api/danh-sach/phim-thuyet-minh?page=$p",
                "https://phimapi.com/v1/api/danh-sach/phim-long-tieng?page=$p",
                "https://phimapi.com/v1/api/the-loai/hoat-hinh?page=$p"
            )
            for (endpoint in apiEndpoints) {
                try {
                    val req = Request.Builder().url(endpoint).header("User-Agent", "Mozilla/5.0").build()
                    client.newCall(req).execute().use { resp ->
                        if (!resp.isSuccessful) return@use
                        val body = resp.body?.string() ?: return@use
                        val root = gson.fromJson(body, JsonObject::class.java)
                        val itemsArray = if (root.has("items") && !root.get("items").isJsonNull) {
                            root.getAsJsonArray("items")
                        } else if (root.has("data") && !root.get("data").isJsonNull && root.getAsJsonObject("data").has("items")) {
                            root.getAsJsonObject("data").getAsJsonArray("items")
                        } else null

                        itemsArray?.forEach { el ->
                            if (el.isJsonObject) {
                                val o = el.asJsonObject
                                val type = o.getSafeString("type")
                                val lang = o.getSafeString("lang").lowercase()
                                val categoryArray = o.getAsJsonArray("category")
                                val isCategoryAnim = categoryArray?.any { catEl ->
                                    val catSlug = catEl.asJsonObject.getSafeString("slug")
                                    catSlug == "hoat-hinh" || catSlug.contains("hoat-hinh")
                                } ?: false

                                val isAnimation = (type == "hoathinh" || isCategoryAnim)
                                val isDubbed = (lang.contains("thuyết minh") || lang.contains("lồng tiếng") || lang.contains("tm") || lang.contains("lt"))

                                if (isAnimation && isDubbed) {
                                    val countryArray = o.getAsJsonArray("country")
                                    val countrySlugs = mutableListOf<String>()
                                    countryArray?.forEach { cEl ->
                                        if (cEl.isJsonObject) countrySlugs.add(cEl.asJsonObject.getSafeString("slug"))
                                    }

                                    var matched = true
                                    if (filterType == "japan" && !countrySlugs.contains("nhat-ban")) matched = false
                                    if (filterType == "china" && !countrySlugs.contains("trung-quoc")) matched = false
                                    if (filterType == "cinema" && !countrySlugs.any { it in listOf("au-my", "my", "phap", "anh", "canada", "uc", "duc") }) matched = false

                                    if (matched) {
                                        val thumb = o.getSafeString("thumb_url")
                                        val poster = o.getSafeString("poster_url").ifEmpty { thumb }
                                        val fullThumb = if (thumb.startsWith("http")) thumb else if (thumb.isNotEmpty()) KKPHIM_IMG_BASE + thumb.removePrefix("/") else ""
                                        val fullPoster = if (poster.startsWith("http")) poster else if (poster.isNotEmpty()) KKPHIM_IMG_BASE + poster.removePrefix("/") else fullThumb

                                        items.add(
                                            MovieItem(
                                                id = o.getSafeString("_id"),
                                                name = o.getSafeString("name"),
                                                slug = o.getSafeString("slug"),
                                                originName = o.getSafeString("origin_name"),
                                                thumbUrl = fullThumb,
                                                posterUrl = fullPoster,
                                                year = o.getSafeString("year"),
                                                quality = o.getSafeString("quality", "FHD"),
                                                episodeCurrent = o.getSafeString("episode_current"),
                                                source = source
                                            )
                                        )
                                    }
                                }
                            }
                        }
                    }
                } catch (e: Exception) {
                }
            }
        }
        return items.distinctBy { it.name.trim().lowercase() }
    }


    private fun fetchShortDramaList(filterUrl: String, page: Int): List<MovieItem> {
        val frKeyword: String
        val altKeywords: List<String>
        val gmGenre: String
        val kkKeyword: String

        val kwType = filterUrl.removePrefix("short_kw://").removePrefix("multi_short://").removePrefix("short_filter://").removePrefix("short_dramabox://")
        when (kwType) {
            "reelshort", "reelshort_hot" -> {
                frKeyword = "người sói"; altKeywords = listOf("tỷ phú", "ma cà rồng", "mafia", "hợp đồng"); gmGenre = "phim-moi"; kkKeyword = "người sói"
            }
            "werewolf" -> {
                frKeyword = "người sói"; altKeywords = listOf("vua sói", "nữ hoàng alpha", "werewolf"); gmGenre = "the-loai/hien-dai"; kkKeyword = "người sói"
            }
            "vampire" -> {
                frKeyword = "ma cà rồng"; altKeywords = listOf("chúa tể bóng đêm", "khát máu", "vampire"); gmGenre = "the-loai/hien-dai"; kkKeyword = "ma cà rồng"
            }
            "billionaire" -> {
                frKeyword = "tỷ phú"; altKeywords = listOf("thừa kế", "ông trùm", "đại gia"); gmGenre = "the-loai/cuoi-truoc-yeu-sau"; kkKeyword = "tỷ phú"
            }
            "mafia" -> {
                frKeyword = "mafia"; altKeywords = listOf("ông trùm", "băng đảng", "sát thủ"); gmGenre = "the-loai/hien-dai"; kkKeyword = "mafia"
            }
            "rejected" -> {
                frKeyword = "hợp đồng"; altKeywords = listOf("ly hôn", "vợ cũ", "thế thân"); gmGenre = "the-loai/guong-vo-lai-lanh"; kkKeyword = "ly hôn"
            }
            "dramabox", "dramabox_hot" -> {
                frKeyword = "tổng tài"; altKeywords = listOf("báo thù", "trọng sinh", "hào môn"); gmGenre = "the-loai/cuoi-truoc-yeu-sau"; kkKeyword = "tổng tài"
            }
            "tong_tai", "tong-tai" -> {
                frKeyword = "tổng tài"; altKeywords = listOf("bá đạo", "chủ tịch", "phu nhân"); gmGenre = "the-loai/cuoi-truoc-yeu-sau"; kkKeyword = "tổng tài"
            }
            "trong_sinh", "trong-sinh" -> {
                frKeyword = "trọng sinh"; altKeywords = listOf("trùng sinh", "báo thù"); gmGenre = "the-loai/trong-sinh"; kkKeyword = "trọng sinh"
            }
            "chien_than", "chien-than", "chienthan" -> {
                frKeyword = "chiến thần"; altKeywords = listOf("tu tiên", "long vương"); gmGenre = "the-loai/co-trang"; kkKeyword = "chiến thần"
            }
            "co_trang", "co-trang", "cotrang" -> {
                frKeyword = "cổ trang"; altKeywords = listOf("cung đấu", "hoàng phi"); gmGenre = "the-loai/co-trang"; kkKeyword = "cổ trang"
            }
            "hao_mon", "hao-mon" -> {
                frKeyword = "hào môn"; altKeywords = listOf("thế gia", "thiên kim"); gmGenre = "the-loai/cuoi-truoc-yeu-sau"; kkKeyword = "hào môn"
            }
            "shortmax", "shortmax_hot" -> {
                frKeyword = "cao thủ"; altKeywords = listOf("thần y", "vua cờ bạc", "nghịch tập"); gmGenre = "the-loai/hien-dai"; kkKeyword = "cao thủ"
            }
            "nghich_tap" -> {
                frKeyword = "nghịch tập"; altKeywords = listOf("đổi đời", "ở rể", "ẩn danh"); gmGenre = "the-loai/hien-dai"; kkKeyword = "nghịch tập"
            }
            "than_y" -> {
                frKeyword = "thần y"; altKeywords = listOf("cao thủ", "y thuật", "xuống núi"); gmGenre = "the-loai/hien-dai"; kkKeyword = "thần y"
            }
            "mat_the" -> {
                frKeyword = "mạt thế"; altKeywords = listOf("sinh tồn", "không gian", "tận thế"); gmGenre = "the-loai/hien-dai"; kkKeyword = "mạt thế"
            }
            "nguoc_tam" -> {
                frKeyword = "thế thân"; altKeywords = listOf("ngược tâm", "ly hôn", "hối hận"); gmGenre = "the-loai/tra-xanh-nam"; kkKeyword = "ngược tâm"
            }
            "ai_all", "ai-cinema" -> {
                frKeyword = "người máy"; altKeywords = listOf("hệ thống", "khoa học", "thực tế ảo"); gmGenre = "the-loai/hien-dai"; kkKeyword = "người máy"
            }
            "ai_robot" -> {
                frKeyword = "người máy"; altKeywords = listOf("trí tuệ nhân tạo", "công nghệ"); gmGenre = "the-loai/hien-dai"; kkKeyword = "người máy"
            }
            "ai_scifi" -> {
                frKeyword = "khoa học"; altKeywords = listOf("vũ trụ", "siêu năng lực"); gmGenre = "the-loai/hien-dai"; kkKeyword = "khoa học"
            }
            "ai_future" -> {
                frKeyword = "đếm ngược"; altKeywords = listOf("thời gian", "tương lai", "tái sinh"); gmGenre = "the-loai/hien-dai"; kkKeyword = "tương lai"
            }
            "ai_fantasy" -> {
                frKeyword = "hệ thống"; altKeywords = listOf("thực tế ảo", "siêu năng lực", "dị năng"); gmGenre = "the-loai/hien-dai"; kkKeyword = "hệ thống"
            }
            "goodshort", "goodshort_hot" -> {
                frKeyword = "cưng chiều"; altKeywords = listOf("tình yêu", "ngọt sủng", "hôn nhân"); gmGenre = "the-loai/yeu-tham"; kkKeyword = "ngọt sủng"
            }
            "sereal" -> {
                frKeyword = "định mệnh"; altKeywords = listOf("bí mật", "tình yêu", "người yêu"); gmGenre = "the-loai/cuoi-truoc-yeu-sau"; kkKeyword = "định mệnh"
            }
            "moboreels" -> {
                frKeyword = "cô dâu"; altKeywords = listOf("trọn bộ", "hiện đại", "đô thị"); gmGenre = "the-loai/hien-dai"; kkKeyword = "cô dâu"
            }
            "ngot_sung" -> {
                frKeyword = "ngọt sủng"; altKeywords = listOf("cưng chiều", "yêu thầm", "thanh xuân"); gmGenre = "the-loai/yeu-tham"; kkKeyword = "ngọt sủng"
            }
            "bao_boi" -> {
                frKeyword = "bảo bối"; altKeywords = listOf("thiên tài", "mẹ đơn thân", "sinh đôi"); gmGenre = "the-loai/cuoi-truoc-yeu-sau"; kkKeyword = "bảo bối"
            }
            "tron_bo" -> {
                frKeyword = "lồng tiếng"; altKeywords = listOf("tổng tài", "trọng sinh", "cưng chiều"); gmGenre = "phim-moi"; kkKeyword = "lồng tiếng"
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

        // Đã loại bỏ hoàn toàn việc trộn phim thường từ KKPhim vào mục Phim Ngắn

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

                    // Chặn triệt để phim thường (live-action) ngồi nhầm lớp sang Anime/Hoạt hình
                    if (source == MovieSource.ANIMEHAY) {
                        val type = o.getSafeString("type")
                        val catArr = o.getAsJsonArray("category")
                        val isCatAnim = catArr?.any {
                            val catSlug = it.asJsonObject.getSafeString("slug")
                            catSlug == "hoat-hinh" || catSlug.contains("hoat-hinh")
                        } ?: false
                        val nameLower = o.getSafeString("name").lowercase()
                        val isAnim = type == "hoathinh" || isCatAnim || nameLower.contains("anime") || nameLower.contains("hoạt hình")
                        if (!isAnim) {
                            return@forEach // Bỏ qua phim thường trong danh mục Anime
                        }
                    }

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


object NguonCClient {
    private const val API_BASE = "https://phim.nguonc.com/api"

    private fun JsonObject.getSafeString(key: String, default: String = ""): String {
        if (!has(key)) return default
        val el = get(key)
        if (el == null || el.isJsonNull) return default
        return try { el.asString } catch (e: Exception) { default }
    }

    fun getFilmList(client: OkHttpClient, gson: Gson, filterUrl: String, page: Int): List<MovieItem> {
        val sep = if (filterUrl.contains("?")) "&" else "?"
        val url = "$filterUrl${sep}page=$page"
        val req = Request.Builder().url(url).header("User-Agent", "Mozilla/5.0").build()
        return try {
            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return emptyList()
                val body = resp.body?.string() ?: return emptyList()
                val root = gson.fromJson(body, JsonObject::class.java)
                val items = root.getAsJsonArray("items") ?: return emptyList()
                val list = mutableListOf<MovieItem>()
                items.forEach { el ->
                    if (el.isJsonObject) {
                        val o = el.asJsonObject
                        val slug = o.getSafeString("slug")
                        val thumb = o.getSafeString("thumb_url")
                        val poster = o.getSafeString("poster_url").ifEmpty { thumb }
                        val epCurrent = o.getSafeString("current_episode")
                        val quality = o.getSafeString("quality", "HD")
                        val lang = o.getSafeString("language", "Vietsub")
                        val badge = if (lang.isNotEmpty()) "$quality $lang" else quality

                        list.add(
                            MovieItem(
                                id = "nguonc:$slug",
                                name = o.getSafeString("name"),
                                slug = "nguonc:$slug",
                                originName = o.getSafeString("original_name"),
                                thumbUrl = thumb,
                                posterUrl = poster,
                                year = o.getSafeString("year", "2026"),
                                quality = badge,
                                episodeCurrent = epCurrent,
                                source = MovieSource.KKPHIM
                            )
                        )
                    }
                }
                list
            }
        } catch (e: Exception) {
            emptyList()
        }
    }

    fun getFilmDetail(client: OkHttpClient, gson: Gson, realSlug: String): MovieDetail? {
        val url = "$API_BASE/film/$realSlug"
        val req = Request.Builder().url(url).header("User-Agent", "Mozilla/5.0").build()
        return try {
            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return null
                val body = resp.body?.string() ?: return null
                val root = gson.fromJson(body, JsonObject::class.java)
                val movie = root.getAsJsonObject("movie") ?: return null

                val title = movie.getSafeString("name")
                val thumb = movie.getSafeString("thumb_url")
                val poster = movie.getSafeString("poster_url").ifEmpty { thumb }
                val desc = movie.getSafeString("description")
                val epArray = movie.getAsJsonArray("episodes")

                val serverGroups = mutableListOf<ServerGroup>()
                epArray?.forEach { sEl ->
                    if (sEl.isJsonObject) {
                        val sObj = sEl.asJsonObject
                        val sName = sObj.getSafeString("server_name", "NguonC VIP")
                        val itemsArr = sObj.getAsJsonArray("items")
                        val epList = mutableListOf<EpisodeItem>()

                        itemsArr?.forEach { epEl ->
                            if (epEl.isJsonObject) {
                                val epObj = epEl.asJsonObject
                                val epName = epObj.getSafeString("name")
                                val epSlug = epObj.getSafeString("slug")
                                val embed = epObj.getSafeString("embed")
                                val m3u8 = epObj.getSafeString("m3u8")

                                val dispName = if (epName.all { it.isDigit() }) "Tập $epName" else epName
                                epList.add(
                                    EpisodeItem(
                                        name = dispName,
                                        slug = epSlug,
                                        filename = dispName,
                                        linkM3u8 = if (m3u8.isNotEmpty()) m3u8 else null,
                                        linkEmbed = if (embed.isNotEmpty()) embed else null
                                    )
                                )
                            }
                        }
                        if (epList.isNotEmpty()) {
                            serverGroups.add(ServerGroup(serverName = sName, episodes = epList))
                        }
                    }
                }

                MovieDetail(
                    id = "nguonc:$realSlug",
                    name = title,
                    slug = "nguonc:$realSlug",
                    originName = movie.getSafeString("original_name"),
                    content = desc,
                    thumbUrl = thumb,
                    posterUrl = poster,
                    year = movie.getSafeString("year", "2026"),
                    time = movie.getSafeString("time"),
                    quality = movie.getSafeString("quality", "HD"),
                    lang = movie.getSafeString("language", "Vietsub"),
                    source = MovieSource.KKPHIM,
                    servers = serverGroups
                )
            }
        } catch (e: Exception) {
            null
        }
    }
}

object FreeReelsClient {
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

                if (rawId.isNotEmpty() && !rawId.equals("null", ignoreCase = true) && title.isNotEmpty() && !title.equals("TOP", ignoreCase = true) && !title.startsWith("TOP ")) {
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

                        val rawStream = epObj.getSafeString("external_audio_h264_m3u8").ifEmpty {
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
}

object GaMoMePhimClient {
    private const val BASE_URL = "https://gamomephim.com"

    fun parseGaMoMeHtml(html: String): List<MovieItem> {
        val list = mutableListOf<MovieItem>()
        val seen = mutableSetOf<String>()
        val aPattern = java.util.regex.Pattern.compile("""<a[^>]+href="/phim/([^"/]+)"[^>]*>(.*?)</a>""", java.util.regex.Pattern.DOTALL)
        val matcher = aPattern.matcher(html)
        while (matcher.find()) {
            val slug = matcher.group(1)?.trim() ?: ""
            val body = matcher.group(2) ?: ""
            if (slug.isEmpty() || seen.contains(slug)) continue

            var title = ""
            val titleM = java.util.regex.Pattern.compile("""title="([^"]+)"""").matcher(matcher.group())
            if (titleM.find()) {
                title = titleM.group(1)?.trim() ?: ""
            }
            if (title.isEmpty()) {
                val hM = java.util.regex.Pattern.compile("""<h[34][^>]*>(.*?)</h[34]>""", java.util.regex.Pattern.DOTALL).matcher(body)
                if (hM.find()) {
                    title = hM.group(1)?.replace(Regex("<[^>]+>"), "")?.trim() ?: ""
                }
            }
            if (title.isEmpty()) {
                val altM = java.util.regex.Pattern.compile("""<img[^>]+alt="([^"]+)"""").matcher(body)
                if (altM.find()) {
                    title = altM.group(1)?.replace("Poster phim ", "")?.replace("Poster ", "")?.trim() ?: ""
                }
            }

            var thumb = ""
            val imgM = java.util.regex.Pattern.compile("""<img[^>]+src="([^"]+)"""").matcher(body)
            if (imgM.find()) {
                thumb = imgM.group(1)?.trim() ?: ""
            }

            if (slug.isNotEmpty() && title.isNotEmpty()) {
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
        return list
    }



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
    }

    fun getDramaDetail(client: OkHttpClient, cleanSlug: String): MovieDetail? {
        return try {
            val realSlug = cleanSlug.removePrefix("gamomephim:").removePrefix("/phim/").removePrefix("phim/").removePrefix("/")
            var targetUrl = "$BASE_URL/$realSlug"
            val req = Request.Builder()
                .url(targetUrl)
                .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                .build()

            var html = ""
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
            if (html.isEmpty()) return null

                // Title
                var title = ""
                val titleMatcher = java.util.regex.Pattern.compile("""<h1[^>]*>([^<]+)</h1>""").matcher(html)
                if (titleMatcher.find()) {
                    title = titleMatcher.group(1)?.trim() ?: ""
                }
                if (title.isEmpty()) {
                    title = cleanSlug.replace("-", " ")
                }

                // Description
                var desc = "Phim ngắn tiểu kịch lồng tiếng/thuyết minh tiếng Việt trọn bộ cực hay."
                val descMatcher = java.util.regex.Pattern.compile("""description\\":\\"([^\\"]+)\\"""").matcher(html)
                if (descMatcher.find()) {
                    desc = descMatcher.group(1)?.replace("\\n", "\n") ?: desc
                }

                // Thumb / Poster
                var thumb = ""
                val thumbMatcher = java.util.regex.Pattern.compile("""https://r2\.gamomephim\.com/thumbnails/[^"'\s<>]+""").matcher(html)
                if (thumbMatcher.find()) {
                    thumb = thumbMatcher.group()
                }

                // Video Streams (MP4)
                val streamMatcher = java.util.regex.Pattern.compile("""https://r2\.gamomephim\.com/videos/[^\s"'<>]+\.mp4""").matcher(html)
                val streamUrls = mutableListOf<String>()
                while (streamMatcher.find()) {
                    val sUrl = streamMatcher.group().replace("\\", "")
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
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }
}
