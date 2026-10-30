import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

RESOLVE_FUNCTION = """    fun resolveChannelLogo(channel: TvChannelItem): String {
        val raw = channel.logo.trim()
        val name = channel.name.trim().lowercase()

        // 1. Ánh xạ ưu tiên về asset nội bộ cực nét, 0ms latency, 100% không phụ thuộc mạng
        when {
            name.contains("vtv10") || name.contains("cần thơ") -> return "file:///android_asset/logos/vtv_cantho.png"
            name.contains("vtv1") -> return "file:///android_asset/logos/vtv1.png"
            name.contains("vtv2") -> return "file:///android_asset/logos/vtv2.png"
            name.contains("vtv3") -> return "file:///android_asset/logos/vtv3.png"
            name.contains("vtv4") -> return "file:///android_asset/logos/vtv4.png"
            name.contains("vtv5") -> return "file:///android_asset/logos/vtv5.png"
            name.contains("vtv6") -> return "file:///android_asset/logos/vtv6.png"
            name.contains("vtv7") -> return "file:///android_asset/logos/vtv7.png"
            name.contains("vtv8") -> return "file:///android_asset/logos/vtv8.png"
            name.contains("vtv9") -> return "file:///android_asset/logos/vtv9.png"
            name.contains("vietnam today") -> return "https://raw.githubusercontent.com/vuminhthanh12/vuminhthanh12/refs/heads/main/VietnamToday.jpg"
            name.contains("htv thể thao") || name.contains("htvc thể thao") -> return "file:///android_asset/logos/htv_thethao.png"
            name.contains("htv1") -> return "file:///android_asset/logos/htv1.png"
            name.contains("htv2") -> return "file:///android_asset/logos/htv2.png"
            name.contains("htv3") -> return "file:///android_asset/logos/htv3.png"
            name.contains("htv7") -> return "file:///android_asset/logos/htv7.webp"
            name.contains("htv9") -> return "file:///android_asset/logos/htv9.webp"
            name.contains("thvl1") -> return "file:///android_asset/logos/thvl1.png"
            name.contains("thvl2") -> return "file:///android_asset/logos/thvl2.png"
            name.contains("thvl3") -> return "file:///android_asset/logos/thvl3.png"
            name.contains("thvl4") -> return "file:///android_asset/logos/thvl4.png"
            name.contains("on cine") -> return "file:///android_asset/logos/on_cine.png"
            name.contains("on phim") -> return "file:///android_asset/logos/on_phimviet.png"
            name.contains("on vie drama") -> return "file:///android_asset/logos/on_viedramas.png"
            name.contains("on movies") -> return "file:///android_asset/logos/on_movies.png"
            name.contains("on music") -> return "file:///android_asset/logos/on_music.png"
            name.contains("on bibi") -> return "file:///android_asset/logos/on_bibi.png"
            name.contains("on e-") || name.contains("one channel") -> return "file:///android_asset/logos/on_echannel.png"
            name.contains("on style") -> return "file:///android_asset/logos/on_style.png"
            name.contains("vtvcab") -> return "file:///android_asset/logos/vtvcab_on.png"
            name.contains("true premier 1") || name.contains("true premier football 1") -> return "file:///android_asset/logos/true_premier_1.png"
            name.contains("true premier 2") || name.contains("true premier football 2") -> return "file:///android_asset/logos/true_premier_2.png"
            name.contains("astro supersport 1") -> return "file:///android_asset/logos/astro_supersport_1.png"
            name.contains("astro supersport 2") -> return "file:///android_asset/logos/astro_supersport_2.png"
            name.contains("sky sports") -> return "file:///android_asset/logos/sky_sports_pl.png"
            name.contains("tnt sports") -> return "file:///android_asset/logos/tnt_sports_1.png"
            name.contains("bein") -> return "file:///android_asset/logos/bein_sports_1.png"
            name.contains("bbc earth") -> return "file:///android_asset/logos/bbc_earth.png"
            name.contains("cnn") -> return "file:///android_asset/logos/cnn.png"
            name.contains("bloomberg") -> return "file:///android_asset/logos/bloomberg.png"
            name.contains("warnertv") || name.contains("warner tv") -> return "file:///android_asset/logos/warnertv.png"
            name.contains("nhk world") -> return "file:///android_asset/logos/nhkworld.png"
            name.contains("cbs news") -> return "file:///android_asset/logos/cbs_news.png"
            name.contains("france 24") -> return "file:///android_asset/logos/france24.png"
            name.contains("dw ") || name.contains("dw english") -> return "file:///android_asset/logos/dw.png"
            name.contains("al jazeera") -> return "file:///android_asset/logos/aljazeera.png"
            name.contains("cartoonito") -> return "file:///android_asset/logos/cartoonito.png"
            name.contains("arirang") -> return "file:///android_asset/logos/arirang.png"
            name.contains("mbc") -> return "file:///android_asset/logos/mbc.png"
        }

        // 2. Chuyển đổi đường dẫn tương đối (data/logos/ hoặc logos/) sang asset Android
        if (raw.startsWith("data/logos/")) {
            val fn = raw.removePrefix("data/logos/").replace(".svg", ".png")
            return "file:///android_asset/logos/$fn"
        }
        if (raw.startsWith("logos/")) {
            val fn = raw.removePrefix("logos/").replace(".svg", ".png")
            return "file:///android_asset/logos/$fn"
        }

        // 3. Nếu là URL online hợp lệ
        if (raw.startsWith("http://") || raw.startsWith("https://")) {
            return raw
        }

        return "file:///android_asset/logos/tv_default_premium.png"
    }

    fun TvChannelItem.toMovieItem(): MovieItem {
        val finalLogo = resolveChannelLogo(this)
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
    }"""

files = [
    "HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt",
    "HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt"
]

target_old = """    fun TvChannelItem.toMovieItem(): MovieItem {
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
    }"""

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize line endings for replacement
    content_norm = content.replace("\r\n", "\n")
    target_norm = target_old.replace("\r\n", "\n")
    resolve_norm = RESOLVE_FUNCTION.replace("\r\n", "\n")

    if target_norm in content_norm:
        content_norm = content_norm.replace(target_norm, resolve_norm)
        
        # Also update getMovieDetail
        detail_old = """                    val channel = cachedTvChannels?.find { it.id == slug }
                    if (channel != null) {
                        val defaultTvLogo = "https://raw.githubusercontent.com/Chanhnh/vbook-ext/main/tivi/icon.png"
                        val finalLogo = if (channel.logo.isNotEmpty()) channel.logo else defaultTvLogo"""
        detail_new = """                    val channel = cachedTvChannels?.find { it.id == slug }
                    if (channel != null) {
                        val finalLogo = resolveChannelLogo(channel)"""
        content_norm = content_norm.replace(detail_old.replace("\r\n", "\n"), detail_new.replace("\r\n", "\n"))

        with open(fpath, "w", encoding="utf-8", newline="\n") as f:
            f.write(content_norm)
        print(f"✔ Đã cập nhật thành công: {fpath}")
    else:
        print(f"❌ Không tìm thấy target trong: {fpath}")

print("Done patching MovieRepository.kt!")
