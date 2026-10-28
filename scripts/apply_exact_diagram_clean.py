def update_file(path):
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. getShortDramaSubSources
    old_sub = """    fun getShortDramaSubSources(): List<FilterItem> {
        return listOf(
            FilterItem("🎙️ Gà Mờ Mê Phim (Thuyết Minh & Vietsub)", "freereels_sub://gamomephim"),
            FilterItem("📱 FreeReels Dọc (Phụ Đề & Lồng Tiếng)", "freereels_sub://freereels"),
            FilterItem("🇻🇳 Tiểu Kịch Vietsub (KKPhim HD)", "freereels_sub://kkphim"),
            FilterItem("💎 DramaBox Hot (Tuyển Chọn Hay Nhất)", "freereels_sub://dramabox")
        )
    }"""

    new_sub = """    fun getShortDramaSubSources(): List<FilterItem> {
        return listOf(
            FilterItem("🔥 Kho Tiểu Kịch Đa Nền Tảng (Full Vietsub/Lồng Tiếng)", "freereels_sub://multiplatform"),
            FilterItem("🎙️ Kho Thuyết Minh Đặc Tuyển (Gà Mờ Mê Phim / Voice AI)", "freereels_sub://gamomephim"),
            FilterItem("📱 Kho FreeReels Gốc (Xem Dọc 9:16 Full Mở Khóa)", "freereels_sub://freereels")
        )
    }"""

    c = c.replace(old_sub, new_sub)

    # 2. getShortDramaFilters
    old_filters = """    fun getShortDramaFilters(subSourceUrl: String): List<FilterItem> {
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
            )
            "freereels_sub://kkphim" -> listOf(
                FilterItem("🔥 Tất Cả Tiểu Kịch Vietsub", "https://phimapi.com/v1/api/the-loai/phim-ngan"),
                FilterItem("👑 Tổng Tài & Bá Đạo", "short_filter://tong-tai"),
                FilterItem("🐉 Trọng Sinh & Nghịch Tập", "short_filter://trong-sinh"),
                FilterItem("💖 Ngôn Tình & Hôn Nhân", "short_filter://ngon-tinh"),
                FilterItem("🎭 Hài Hước & Đời Sống", "short_filter://hai-huoc"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            "freereels_sub://dramabox" -> listOf(
                FilterItem("🌟 Tuyển Chọn Phim Ngắn Hot", "short_dramabox://hot"),
                FilterItem("⚔️ Chiến Thần & Tu Tiên", "short_dramabox://chienthan"),
                FilterItem("👑 Thiếu Gia Ẩn Danh", "short_dramabox://thieugia"),
                FilterItem("🏰 Cung Đấu & Cổ Trang", "short_dramabox://cotrang"),
                FilterItem("🕒 Lịch Sử Xem", "app://history"),
                FilterItem("❤️ Yêu Thích", "app://favorites")
            )
            else -> listOf("""

    new_filters = """    fun getShortDramaFilters(subSourceUrl: String): List<FilterItem> {
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
            else -> listOf("""

    c = c.replace(old_filters, new_filters)

    # 3. getMovieList condition
    old_cond = """                        filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://") -> {"""
    new_cond = """                        filterUrl.startsWith("multi_short://") || filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://") -> {"""
    c = c.replace(old_cond, new_cond)

    # 4. fetchShortDramaList mapping
    old_mapping = """        val keyword = when (filterUrl) {
            "short_filter://tong-tai" -> "tổng tài"
            "short_filter://trong-sinh" -> "trọng sinh"
            "short_filter://ngon-tinh" -> "hôn nhân"
            "short_filter://hai-huoc" -> "hài hước"
            "short_dramabox://chienthan" -> "chiến thần"
            "short_dramabox://thieugia" -> "thiếu gia"
            "short_dramabox://cotrang" -> "cung đấu"
            else -> ""
        }"""

    new_mapping = """        val keyword = when (filterUrl) {
            "multi_short://tong-tai" -> "tổng tài"
            "multi_short://trong-sinh" -> "trọng sinh"
            "multi_short://chien-than" -> "chiến thần"
            "multi_short://thieu-gia" -> "thiếu gia"
            "multi_short://co-trang" -> "cung đấu"
            "multi_short://hao-mon" -> "hào môn"
            "short_filter://tong-tai" -> "tổng tài"
            "short_filter://trong-sinh" -> "trọng sinh"
            "short_filter://ngon-tinh" -> "hôn nhân"
            "short_filter://hai-huoc" -> "hài hước"
            "short_dramabox://chienthan" -> "chiến thần"
            "short_dramabox://thieugia" -> "thiếu gia"
            "short_dramabox://cotrang" -> "cung đấu"
            else -> "tổng tài"
        }"""

    c = c.replace(old_mapping, new_mapping)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("Updated", path)

update_file(r"HuyCaBuonCa_TV\app\src\main\java\com\huycabuonca\tv\api\MovieRepository.kt")
update_file(r"HuyCaBuonCa_Mobile\app\src\main\java\com\huycabuonca\mobile\api\MovieRepository.kt")
