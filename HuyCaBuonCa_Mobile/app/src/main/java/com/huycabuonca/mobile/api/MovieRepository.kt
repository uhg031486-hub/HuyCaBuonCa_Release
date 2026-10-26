package com.huycabuonca.mobile.api

import android.content.Context
import com.google.gson.Gson
import com.google.gson.JsonObject
import com.google.gson.reflect.TypeToken
import com.huycabuonca.mobile.model.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.OkHttpClient
import okhttp3.Request
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

    fun getLiveMatches(): List<FootballMatch> {
        return listOf(
            FootballMatch(
                id = "fpl_epl_1",
                time = "18:30 • Thứ 7 (24/10)",
                tournament = "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh • Vòng 8",
                teamA = "Aston Villa",
                teamB = "Manchester City",
                channelName = "True Premier Football 1 HD",
                channelSlug = "sports_sat_true_premier_1",
                score = "18:30"
            ),
            FootballMatch(
                id = "fpl_epl_2",
                time = "21:00 • Thứ 7 (24/10)",
                tournament = "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh • Vòng 8",
                teamA = "Arsenal",
                teamB = "Everton",
                channelName = "True Premier Football 2 HD",
                channelSlug = "sports_sat_true_premier_2",
                score = "21:00"
            ),
            FootballMatch(
                id = "fpl_epl_3",
                time = "23:30 • Thứ 7 (24/10)",
                tournament = "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh • Vòng 8",
                teamA = "Chelsea",
                teamB = "Tottenham Hotspur",
                channelName = "Astro SuperSport 1 HD",
                channelSlug = "sports_sat_astro_supersport_1",
                score = "23:30"
            ),
            FootballMatch(
                id = "fpl_epl_4",
                time = "22:30 • Chủ Nhật (25/10)",
                tournament = "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Ngoại Hạng Anh • Vòng 8",
                teamA = "Liverpool",
                teamB = "Manchester United",
                channelName = "Sky Sports Premier League",
                channelSlug = "sports_sat_sky_sports_epl",
                score = "22:30"
            ),
            FootballMatch(
                id = "fpl_laliga_1",
                time = "02:00 • Thứ 2 (26/10)",
                tournament = "🇪🇸 Siêu Kinh Điển (El Clasico)",
                teamA = "Real Madrid",
                teamB = "Barcelona",
                channelName = "beIN SPORTS 1 HD",
                channelSlug = "sports_sat_bein_sports_1",
                score = "02:00"
            )
        )
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
                FilterItem("3D Mới Cập Nhật", "https://phimapi.com/v1/api/quoc-gia/trung-quoc"),
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
                FilterItem("Anime Mới Cập Nhật", "https://phimapi.com/v1/api/quoc-gia/nhat-ban"),
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
            FilterItem("🔥 Kho Tiểu Kịch Đa Nền Tảng (Full Vietsub/Lồng Tiếng)", "freereels_sub://multiplatform"),
            FilterItem("🎙️ Kho Thuyết Minh Đặc Tuyển (Gà Mờ Mê Phim / Voice AI)", "freereels_sub://gamomephim"),
            FilterItem("📱 Kho FreeReels Gốc (Xem Dọc 9:16 Full Mở Khóa)", "freereels_sub://freereels")
        )
    }

    fun getShortDramaFilters(subSourceUrl: String): List<FilterItem> {
        return when (subSourceUrl) {
            "freereels_sub://multiplatform" -> listOf(
                FilterItem("👑 Tổng Tài & Bá Đạo (DramaBox/ShortMax)", "multi_short://tong-tai"),
                FilterItem("🐉 Trọng Sinh & Báo Thù Nghịch Tập", "multi_short://trong-sinh"),
                FilterItem("⚔️ Chiến Thần & Tu Tiên Đô Thị", "multi_short://chien-than"),
                FilterItem("💎 Thiếu Gia & Đại Gia Ẩn Danh", "multi_short://thieu-gia"),
                FilterItem("🏰 Cổ Trang & Cung Đấu Ngược Tâm", "multi_short://co-trang"),
                FilterItem("💖 Hào Môn Thế Gia & Hôn Nhân", "multi_short://hao-mon"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            "freereels_sub://gamomephim" -> listOf(
                FilterItem("🔥 Toàn Bộ Tiểu Kịch Mới", "gamomephim://the-loai/hien-dai"),
                FilterItem("👑 Cưới Trước Yêu Sau & Tổng Tài", "gamomephim://the-loai/cuoi-truoc-yeu-sau"),
                FilterItem("🐉 Trọng Sinh & Báo Thù", "gamomephim://the-loai/trong-sinh"),
                FilterItem("🏰 Cổ Trang & Xuyên Không", "gamomephim://the-loai/co-trang"),
                FilterItem("🍵 Trà Xanh Nam & Ngược Tâm", "gamomephim://the-loai/tra-xanh-nam"),
                FilterItem("✨ Chữa Lành & Thanh Xuân", "gamomephim://the-loai/chua-lanh"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            else -> listOf(
                FilterItem("🔥 Thịnh Hành", "freereels://foryou"),
                FilterItem("🎙️ Phim Lồng Tiếng Việt", "freereels://dubbed_vi"),
                FilterItem("⚡ Mới Nhất", "freereels://tab_505"),
                FilterItem("🎀 Dành Cho Nữ", "freereels://tab_504"),
                FilterItem("👑 Dành Cho Nam", "freereels://tab_506"),
                FilterItem("🎭 Hoạt Hình Ngắn", "freereels://tab_547"),
                FilterItem("⏰ Sắp Chiếu", "freereels://coming"),
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
            MovieSource.FREEREELS -> listOf(
                FilterItem("🔥 Thịnh Hành (For You)", "freereels://foryou"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Phim Ngắn Yêu Thích", "app://favorites"),
                FilterItem("✨ Mới Nhất", "freereels://tab_505"),
                FilterItem("🎀 Dành Cho Nữ", "freereels://tab_504"),
                FilterItem("👑 Dành Cho Nam", "freereels://tab_506"),
                FilterItem("🎭 Hoạt Hình Ngắn", "freereels://tab_547"),
                FilterItem("⏰ Sắp Chiếu", "freereels://coming")
            )
        }
    }

    suspend fun getMovies(source: MovieSource, filterUrl: String, page: Int = 1, context: Context? = null): List<MovieItem> {
        return withContext(Dispatchers.IO) {
            try {
                if (filterUrl == "app://favorites") {
                    val favs = if (context != null) com.huycabuonca.mobile.util.FavoriteMovieManager.getFavorites(context) else emptyList()
                    return@withContext favs.filter { it.source == source }
                }
                if (filterUrl == "app://history") {
                    val history = if (context != null) com.huycabuonca.mobile.util.WatchHistoryManager.getHistory(context) else emptyList()
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
                        "tv://vtv" -> channels.filter { it.group.equals("VTV", ignoreCase = true) }
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
                            it.name.contains("TNT Sports", ignoreCase = true)
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
                            it.group.contains("TVB", ignoreCase = true)
                        }
                        "tv://local" -> channels.filter { it.group.contains("Địa phương", ignoreCase = true) || it.group.contains("HTV", ignoreCase = true) }
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
                        filterUrl.startsWith("multi_short://") || filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://") -> {
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
                } else if (source == MovieSource.FREEREELS) {
                    if (slug.startsWith("gamomephim:")) {
                        GaMoMePhimClient.getDramaDetail(client, slug.removePrefix("gamomephim:"))
                    } else {
                        FreeReelsClient.getDramaDetail(client, gson, slug)
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

    fun getDramaList(client: OkHttpClient, gson: Gson, filterUrl: String, page: Int): List<MovieItem> {
        val list = mutableListOf<MovieItem>()
        try {
            val req = when {
                filterUrl.startsWith("freereels://tab_") -> {
                    val tabKey = filterUrl.removePrefix("freereels://tab_")
                    if (page <= 1) {
                        buildAuthorizedRequest(client, gson, "$API_BASE/homepage/v2/tab/index?tab_key=$tabKey&position_index=10000&rec_trigger=0", "GET")
                    } else {
                        val cursor = "offset=${(page - 1) * 10}"
                        buildAuthorizedRequest(client, gson, "$API_BASE/foryou/feed?next=$cursor", "GET")
                    }
                }
                filterUrl == "freereels://coming" -> {
                    if (page <= 1) {
                        buildAuthorizedRequest(client, gson, "$API_BASE/homepage/v2/tab/index?tab_key=622&position_index=10000&rec_trigger=0", "GET")
                    } else {
                        val cursor = "offset=${(page - 1) * 10}"
                        buildAuthorizedRequest(client, gson, "$API_BASE/foryou/feed?next=$cursor", "GET")
                    }
                }
                else -> {
                    val cursor = if (page <= 1) "" else "offset=${(page - 1) * 10}"
                    buildAuthorizedRequest(client, gson, "$API_BASE/foryou/feed?next=$cursor", "GET")
                }
            } ?: return emptyList()

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return emptyList()
                val respStr = resp.body?.string() ?: return emptyList()
                val root = gson.fromJson(respStr, JsonObject::class.java)
                val data = root.getAsJsonObject("data") ?: return emptyList()

                val itemsArray = if (data.has("items") && !data.get("items").isJsonNull) {
                    val itArr = data.getAsJsonArray("items")
                    if (itArr.size() > 0 && itArr[0].isJsonObject && itArr[0].asJsonObject.has("items")) {
                        itArr[0].asJsonObject.getAsJsonArray("items")
                    } else {
                        itArr
                    }
                } else if (data.has("list") && !data.get("list").isJsonNull) {
                    data.getAsJsonArray("list")
                } else null

                itemsArray?.forEach { el ->
                    if (el.isJsonObject) {
                        val obj = el.asJsonObject
                        val series = if (obj.has("series") && obj.get("series").isJsonObject) {
                            obj.getAsJsonObject("series")
                        } else if (obj.has("info") && obj.get("info").isJsonObject) {
                            obj.getAsJsonObject("info")
                        } else obj

                        val id = series.getSafeString("id").ifEmpty {
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

                        if (id.isNotEmpty() && title.isNotEmpty()) {
                            val isDubbed = title.contains("lồng tiếng", ignoreCase = true) || title.contains("thuyết minh", ignoreCase = true)
                            val qualityBadge = if (isDubbed) "🎙️ Lồng Tiếng" else "🇻🇳 Phụ Đề"
                            list.add(
                                MovieItem(
                                    id = id,
                                    name = title,
                                    slug = id,
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
        } catch (e: Exception) {
            e.printStackTrace()
        }
        if (filterUrl == "freereels://dubbed_vi") {
            val dubbedList = list.filter { it.name.contains("lồng tiếng", ignoreCase = true) || it.name.contains("thuyết minh", ignoreCase = true) }
            if (dubbedList.isNotEmpty()) return dubbedList
        }
        return list
    }

    fun getDramaDetail(client: OkHttpClient, gson: Gson, seriesId: String): MovieDetail? {
        return try {
            val req = buildAuthorizedRequest(client, gson, "$API_BASE/drama/info_v2?series_id=$seriesId&scene=search", "GET")
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
                                    if (lang.contains("vi") || disp.contains("việt")) {
                                        val vtt = sObj.getSafeString("vtt")
                                        val srt = sObj.getSafeString("subtitle")
                                        viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                                    }
                                }
                            }
                        }

                        epList.add(
                            EpisodeItem(
                                name = epName,
                                slug = epId,
                                filename = epName,
                                linkM3u8 = "freereels_unlock:$seriesId:$epId",
                                linkEmbed = null,
                                subtitleUrl = viSubUrl
                            )
                        )
                    }
                }

                // Tự động mở khóa trước link tập 1 để phát mượt ngay tức thì
                if (epList.isNotEmpty()) {
                    val firstEp = epList[0]
                    val unlockRes = unlockEpisode(client, gson, seriesId, firstEp.slug)
                    if (unlockRes != null) {
                        epList[0] = firstEp.copy(
                            linkM3u8 = unlockRes.streamUrl,
                            subtitleUrl = unlockRes.subtitleUrl ?: firstEp.subtitleUrl
                        )
                    }
                }

                MovieDetail(
                    id = seriesId,
                    name = title,
                    slug = seriesId,
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
            val jsonBody = JsonObject().apply {
                addProperty("series_id", seriesId)
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
                            if (lang.contains("vi") || disp.contains("việt")) {
                                val vtt = sObj.getSafeString("vtt")
                                val srt = sObj.getSafeString("subtitle")
                                viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                            }
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
                ?: return emptyList()

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return emptyList()
                val respStr = resp.body?.string() ?: return emptyList()
                val root = gson.fromJson(respStr, JsonObject::class.java)
                val data = root.getAsJsonObject("data") ?: return emptyList()

                val itemsArray = if (data.has("list") && !data.get("list").isJsonNull) {
                    data.getAsJsonArray("list")
                } else if (data.has("items") && !data.get("items").isJsonNull) {
                    data.getAsJsonArray("items")
                } else null

                itemsArray?.forEach { el ->
                    if (el.isJsonObject) {
                        val obj = el.asJsonObject
                        val series = if (obj.has("series") && obj.get("series").isJsonObject) {
                            obj.getAsJsonObject("series")
                        } else obj

                        val id = series.getSafeString("id").ifEmpty { series.getSafeString("key") }
                        val title = series.getSafeString("title").ifEmpty { series.getSafeString("name") }
                        val cover = series.getSafeString("cover").ifEmpty { series.getSafeString("poster") }
                        val epCount = series.getSafeString("episode_count")

                        if (id.isNotEmpty() && title.isNotEmpty()) {
                            val isDubbed = title.contains("lồng tiếng", ignoreCase = true) || title.contains("thuyết minh", ignoreCase = true)
                            val qualityBadge = if (isDubbed) "🎙️ Lồng Tiếng" else "🇻🇳 Phụ Đề"
                            list.add(
                                MovieItem(
                                    id = id,
                                    name = title,
                                    slug = id,
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
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }
}

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
