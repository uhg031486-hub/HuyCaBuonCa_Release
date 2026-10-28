import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def update_kotlin_file(path):
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Update getShortDramaSubSources
    old_sub = re.search(r'fun getShortDramaSubSources\(\): List<FilterItem> \{.*?^\s*\}', code, re.DOTALL | re.MULTILINE)
    new_sub = """fun getShortDramaSubSources(): List<FilterItem> {
        return listOf(
            FilterItem("🔥 Kho Tiểu Kịch Đa Nền Tảng (Full Vietsub/Lồng Tiếng)", "freereels_sub://multiplatform"),
            FilterItem("🎙️ Kho Thuyết Minh Đặc Tuyển (Gà Mờ Mê Phim / Voice AI)", "freereels_sub://gamomephim"),
            FilterItem("📱 Kho FreeReels Gốc (Xem Dọc 9:16 Full Mở Khóa)", "freereels_sub://freereels")
        )
    }"""
    if old_sub:
        code = code.replace(old_sub.group(0), new_sub)

    # 2. Update getShortDramaFilters
    old_filters = re.search(r'fun getShortDramaFilters\(subSourceUrl: String\): List<FilterItem> \{.*?^\s*\}', code, re.DOTALL | re.MULTILINE)
    new_filters = """fun getShortDramaFilters(subSourceUrl: String): List<FilterItem> {
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
    }"""
    if old_filters:
        code = code.replace(old_filters.group(0), new_filters)

    # 3. Update getMovieList when source == MovieSource.FREEREELS
    old_movie_list = """filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://") -> {
                            fetchShortDramaList(filterUrl, page)
                        }"""
    new_movie_list = """filterUrl.startsWith("multi_short://") || filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://") -> {
                            fetchShortDramaList(filterUrl, page)
                        }"""
    code = code.replace(old_movie_list, new_movie_list)

    # 4. Update fetchShortDramaList keyword mapping
    old_fetch_short = re.search(r'private fun fetchShortDramaList\(filterUrl: String, page: Int\): List<MovieItem> \{.*?val keyword = when \(filterUrl\) \{.*?^\s*\}', code, re.DOTALL | re.MULTILINE)
    new_fetch_kw = """private fun fetchShortDramaList(filterUrl: String, page: Int): List<MovieItem> {
        val keyword = when (filterUrl) {
            "multi_short://tong-tai" -> "tổng tài"
            "multi_short://trong-sinh" -> "trọng sinh"
            "multi_short://chien-than" -> "chiến thần"
            "multi_short://thieu-gia" -> "thiếu gia"
            "multi_short://co-trang" -> "cổ trang"
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
    if old_fetch_short:
        code = code.replace(old_fetch_short.group(0), new_fetch_kw)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Updated Kotlin file:", path)

update_kotlin_file(r"HuyCaBuonCa_TV\app\src\main\java\com\huycabuonca\tv\api\MovieRepository.kt")
update_kotlin_file(r"HuyCaBuonCa_Mobile\app\src\main\java\com\huycabuonca\mobile\api\MovieRepository.kt")

# 5. Cập nhật cho webOS và Windows app.js
def update_js_file(path):
    with open(path, "r", encoding="utf-8") as f:
        js = f.read()

    # Sub sources
    old_sub_js = re.search(r'FREEREELS:\s*\[.*?^\s*\],', js, re.DOTALL | re.MULTILINE)
    new_sub_js = """FREEREELS: [
      { name: "🔥 Kho Tiểu Kịch Đa Nền Tảng (Full Vietsub/Lồng Tiếng)", key: "freereels_sub://multiplatform" },
      { name: "🎙️ Kho Thuyết Minh Đặc Tuyển (Gà Mờ Mê Phim / Voice AI)", key: "freereels_sub://gamomephim" },
      { name: "📱 Kho FreeReels Gốc (Xem Dọc 9:16 Full Mở Khóa)", key: "freereels_sub://freereels" }
    ],"""
    if old_sub_js:
        js = js.replace(old_sub_js.group(0), new_sub_js)

    # Sub filters
    new_multi_filter = """    'freereels_sub://multiplatform': [
      { name: "👑 Tổng Tài & Bá Đạo (DramaBox/ShortMax)", url: "multi_short://tong-tai" },
      { name: "🐉 Trọng Sinh & Báo Thù Nghịch Tập", url: "multi_short://trong-sinh" },
      { name: "⚔️ Chiến Thần & Tu Tiên Đô Thị", url: "multi_short://chien-than" },
      { name: "💎 Thiếu Gia & Đại Gia Ẩn Danh", url: "multi_short://thieu-gia" },
      { name: "🏰 Cổ Trang & Cung Đấu Ngược Tâm", url: "multi_short://co-trang" },
      { name: "💖 Hào Môn Thế Gia & Hôn Nhân", url: "multi_short://hao-mon" },
      { name: "🕒 Lịch Sử Xem", url: "app://history" },
      { name: "❤️ Yêu Thích", url: "app://favorites" }
    ],
    'freereels_sub://gamomephim': ["""

    if "'freereels_sub://multiplatform'" not in js:
        js = js.replace("    'freereels_sub://gamomephim': [", new_multi_filter)

    # Handle multi_short in loadMovies
    old_load = """      // Xử lý Phim Ngắn GaMoMePhim Thuyết Minh"""
    new_load = """      // Xử lý Kho Tiểu Kịch Đa Nền Tảng (KKPhim/NguonC Short)
      if (currentFilter.startsWith('multi_short://')) {
        const kwMap = {
          'multi_short://tong-tai': 'tổng tài',
          'multi_short://trong-sinh': 'trọng sinh',
          'multi_short://chien-than': 'chiến thần',
          'multi_short://thieu-gia': 'thiếu gia',
          'multi_short://co-trang': 'cổ trang',
          'multi_short://hao-mon': 'hào môn'
        };
        const searchKw = kwMap[currentFilter] || 'tổng tài';
        let searchResults = await searchKKPhim(searchKw);
        currentMoviesList = searchResults;
        renderMovieGrid(currentMoviesList, false);
        if (paginationInfo) paginationInfo.textContent = `Đang hiển thị ${currentMoviesList.length} phim ngắn theo chủ đề (Trang ${currentPage})`;
        hideLoading();
        return;
      }

      // Xử lý Phim Ngắn GaMoMePhim Thuyết Minh"""
    if "currentFilter.startsWith('multi_short://')" not in js:
        js = js.replace(old_load, new_load)

    with open(path, "w", encoding="utf-8") as f:
        f.write(js)
    print("Updated JS file:", path)

update_js_file(r"HuyCaBuonCa_LG_webOS\js\app.js")
update_js_file(r"HuyCa_Windows\www\js\app.js")
