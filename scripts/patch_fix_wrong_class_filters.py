import sys

files = [
    "HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt",
    "HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt"
]

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Chặn phim thường ngồi nhầm lớp sang Anime trong fetchKKPhimList
    target1 = """            itemsArray?.forEach { el ->
                if (el.isJsonObject) {
                    val o = el.asJsonObject
                    val thumb = o.getSafeString("thumb_url")"""

    replacement1 = """            itemsArray?.forEach { el ->
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

                    val thumb = o.getSafeString("thumb_url")"""

    assert target1 in text, f"Target 1 not found in {path}"
    text = text.replace(target1, replacement1, 1)

    # 2. Xóa bỏ hoàn toàn việc trộn phim dài tập KKPhim vào Tiểu Kịch (Phim Ngắn)
    target2 = """        // 3. Ở trang 1, trộn thêm các phim tiểu kịch từ KKPhim
        if (page == 1 && kkKeyword.isNotEmpty()) {
            try {
                val kkItems = fetchKKPhimSearch(kkKeyword)
                result.addAll(kkItems)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }"""

    if target2 in text:
        text = text.replace(target2, "        // Đã loại bỏ hoàn toàn việc trộn phim thường từ KKPhim vào mục Phim Ngắn", 1)

    # 3. Thay đổi URL mặc định của Anime thành danh-sach/hoat-hinh thay vì quoc-gia/nhat-ban hay quoc-gia/trung-quoc
    text = text.replace(
        'FilterItem("Anime Mới Cập Nhật", "https://phimapi.com/v1/api/quoc-gia/nhat-ban")',
        'FilterItem("Anime Mới Cập Nhật", "https://phimapi.com/v1/api/danh-sach/hoat-hinh")'
    )
    text = text.replace(
        'FilterItem("3D Mới Cập Nhật", "https://phimapi.com/v1/api/quoc-gia/trung-quoc")',
        'FilterItem("3D Mới Cập Nhật", "https://phimapi.com/v1/api/danh-sach/hoat-hinh")'
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"Patched {path} successfully!")
