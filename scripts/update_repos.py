import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def update_repo(path, pkg_name):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Update getShortDramaSubSources
    old_sub_start = text.find('fun getShortDramaSubSources(): List<FilterItem> {')
    old_sub_end = text.find('fun getShortDramaFilters', old_sub_start)

    new_sub = '''fun getShortDramaSubSources(): List<FilterItem> {
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

    '''

    # 2. Update getShortDramaFilters
    old_filters_end = text.find('fun getFiltersForSource', old_sub_end)

    new_filters = '''fun getShortDramaFilters(subSourceUrl: String): List<FilterItem> {
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
                FilterItem("🔥 Tiểu Kịch Hiện Đại Mới", "gamomephim://the-loai/hien-dai"),
                FilterItem("👑 Cưới Trước Yêu Sau & Tổng Tài", "gamomephim://the-loai/cuoi-truoc-yeu-sau"),
                FilterItem("🐉 Trọng Sinh & Báo Thù", "gamomephim://the-loai/trong-sinh"),
                FilterItem("🏰 Cổ Trang & Xuyên Không", "gamomephim://the-loai/co-trang"),
                FilterItem("🍵 Trà Xanh Nam & Ngược Tâm", "gamomephim://the-loai/tra-xanh-nam"),
                FilterItem("✨ Chữa Lành & Thanh Xuân", "gamomephim://the-loai/chua-lanh"),
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

    '''

    text = text[:old_sub_start] + new_sub + new_filters + text[old_filters_end:]

    # 3. Update XEMTIVI in getFiltersForSource
    p_xemtivi = text.find('MovieSource.XEMTIVI -> listOf(')
    p_xemtivi_end = text.find('MovieSource.FREEREELS ->', p_xemtivi)

    new_xemtivi = '''MovieSource.XEMTIVI -> listOf(
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
            '''

    text = text[:p_xemtivi] + new_xemtivi + text[p_xemtivi_end:]

    # 4. Update fetchShortDramaList
    p_fetch_start = text.find('fun fetchShortDramaList(filterUrl: String, page: Int): List<MovieItem> {')
    p_fetch_end = text.find('suspend fun getAnimeDetail', p_fetch_start)
    if p_fetch_end == -1:
        p_fetch_end = text.find('private val cleanYourTvApi', p_fetch_start)

    new_fetch = '''fun fetchShortDramaList(filterUrl: String, page: Int): List<MovieItem> {
        val kwType = filterUrl.removePrefix("short_kw://").removePrefix("multi_short://").removePrefix("short_filter://").removePrefix("short_dramabox://")
        val (frKeyword, altKeywords, gmGenre) = when (kwType) {
            "reelshort", "reelshort_hot" -> Triple("người sói", listOf("tỷ phú", "ma cà rồng", "mafia", "hợp đồng"), "the-loai/hien-dai")
            "werewolf" -> Triple("người sói", listOf("vua sói", "nữ hoàng alpha", "werewolf", "bạn đời"), "the-loai/hien-dai")
            "vampire" -> Triple("ma cà rồng", listOf("chúa tể bóng đêm", "khát máu", "vampire", "thợ săn"), "the-loai/hien-dai")
            "billionaire" -> Triple("tỷ phú", listOf("thừa kế", "ông trùm", "đại gia", "chồng tỷ phú"), "the-loai/cuoi-truoc-yeu-sau")
            "mafia" -> Triple("mafia", listOf("ông trùm", "băng đảng", "sát thủ", "vệ sĩ"), "the-loai/hien-dai")
            "rejected" -> Triple("hợp đồng", listOf("ly hôn", "vợ cũ", "bị từ chối", "thế thân"), "the-loai/cuoi-truoc-yeu-sau")
            "dramabox", "dramabox_hot" -> Triple("tổng tài", listOf("báo thù", "trọng sinh", "hào môn"), "the-loai/cuoi-truoc-yeu-sau")
            "tong_tai", "tong-tai" -> Triple("tổng tài", listOf("chủ tịch", "bá đạo", "phu nhân", "thư ký"), "the-loai/cuoi-truoc-yeu-sau")
            "trong_sinh", "trong-sinh" -> Triple("trọng sinh", listOf("trùng sinh", "báo thù", "kiếp trước"), "the-loai/trong-sinh")
            "chien_than", "chien-than", "chienthan" -> Triple("chiến thần", listOf("long vương", "tu tiên", "võ thần"), "the-loai/co-trang")
            "co_trang", "co-trang", "cotrang" -> Triple("cổ trang", listOf("hoàng hậu", "cung đấu", "vương gia", "xuyên không"), "the-loai/co-trang")
            "hao_mon", "hao-mon" -> Triple("hào môn", listOf("thế gia", "thiên kim", "thiếu gia", "thừa kế"), "the-loai/cuoi-truoc-yeu-sau")
            "shortmax", "shortmax_hot" -> Triple("cao thủ", listOf("thần y", "vua cờ bạc", "nghịch tập"), "the-loai/hien-dai")
            "nghich_tap" -> Triple("nghịch tập", listOf("đổi đời", "ở rể", "ẩn danh", "phế vật"), "the-loai/hien-dai")
            "than_y" -> Triple("thần y", listOf("cao thủ", "y thuật", "xuống núi", "kỳ tài"), "the-loai/hien-dai")
            "mat_the" -> Triple("mạt thế", listOf("sinh tồn", "không gian", "tận thế", "zombie"), "the-loai/hien-dai")
            "nguoc_tam" -> Triple("thế thân", listOf("ngược tâm", "ly hôn", "hối hận", "bỏ rơi"), "the-loai/tra-xanh-nam")
            "ai_all", "ai-cinema" -> Triple("người máy", listOf("hệ thống", "khoa học", "thực tế ảo"), "the-loai/hien-dai")
            "ai_robot" -> Triple("người máy", listOf("trí tuệ nhân tạo", "công nghệ", "kỳ tài"), "the-loai/hien-dai")
            "ai_scifi" -> Triple("khoa học", listOf("vũ trụ", "siêu năng lực", "không gian"), "the-loai/hien-dai")
            "ai_future" -> Triple("đếm ngược", listOf("thời gian", "tương lai", "tái sinh"), "the-loai/hien-dai")
            "ai_fantasy" -> Triple("hệ thống", listOf("thực tế ảo", "siêu năng lực", "dị năng"), "the-loai/hien-dai")
            "goodshort", "goodshort_hot" -> Triple("cưng chiều", listOf("tình yêu", "ngọt sủng", "hôn nhân"), "the-loai/cuoi-truoc-yeu-sau")
            "sereal" -> Triple("định mệnh", listOf("bí mật", "tình yêu", "người yêu"), "the-loai/cuoi-truoc-yeu-sau")
            "moboreels" -> Triple("cô dâu", listOf("trọn bộ", "hiện đại", "đô thị"), "the-loai/cuoi-truoc-yeu-sau")
            "ngot_sung" -> Triple("ngọt sủng", listOf("cưng chiều", "yêu thầm", "thanh xuân"), "the-loai/chua-lanh")
            "bao_boi" -> Triple("bảo bối", listOf("thiên tài", "mẹ đơn thân", "sinh đôi"), "the-loai/cuoi-truoc-yeu-sau")
            "tron_bo" -> Triple("lồng tiếng", listOf("tổng tài", "trọng sinh", "cưng chiều"), "the-loai/cuoi-truoc-yeu-sau")
            else -> Triple("tổng tài", listOf("bá đạo", "trọng sinh"), "the-loai/cuoi-truoc-yeu-sau")
        }

        val result = mutableListOf<MovieItem>()
        try {
            val frItems = FreeReelsClient.search(client, gson, frKeyword, page)
            result.addAll(frItems)

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

        if (result.size < 6 && gmGenre.isNotEmpty()) {
            try {
                val gmItems = GaMoMePhimClient.getDramaList(client, "gamomephim://$gmGenre", page)
                result.addAll(gmItems)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }

        if (result.isEmpty()) {
            try {
                val fallbackList = FreeReelsClient.getDramaList(client, gson, "freereels://foryou", page)
                result.addAll(fallbackList)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }

        return result.distinctBy { it.id }
    }

    '''

    text = text[:p_fetch_start] + new_fetch + text[p_fetch_end:]

    # 5. Update subtitle fallback in FreeReelsClient
    p_fr_sub = text.find('var viSubUrl: String? = null')
    if p_fr_sub != -1:
        p_fr_sub_end = text.find('epList.add(', p_fr_sub)
        new_vi_block = '''var viSubUrl: String? = null
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

                        '''
        text = text[:p_fr_sub] + new_vi_block + text[p_fr_sub_end:]

    # Update second occurrence (in unlockEpisode)
    p_fr_unl = text.find('var viSubUrl: String? = null', text.find('fun unlockEpisode'))
    if p_fr_unl != -1:
        p_fr_unl_end = text.find('FreeReelsUnlocked(streamUrl = stream', p_fr_unl)
        new_vi_block2 = '''var viSubUrl: String? = null
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

                '''
        text = text[:p_fr_unl] + new_vi_block2 + text[p_fr_unl_end:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'Updated {path} successfully!')

update_repo('HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt', 'tv')
update_repo('HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt', 'mobile')
