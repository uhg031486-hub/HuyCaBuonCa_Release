import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def patch_movie_repository(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. getShortDramaSubSources
    old_sub_start = text.find('fun getShortDramaSubSources(): List<FilterItem> {')
    old_sub_end = text.find('fun getShortDramaFilters(subSourceUrl: String): List<FilterItem> {', old_sub_start)

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

    # 2. getShortDramaFilters
    old_filters_end = text.find('fun getFiltersForSource(source: MovieSource): List<FilterItem> {', old_sub_end)

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

    '''

    text = text[:old_sub_start] + new_sub + new_filters + text[old_filters_end:]

    # 3. getFiltersForSource XEMTIVI & FREEREELS
    p_xem = text.find('MovieSource.XEMTIVI -> listOf(')
    p_xem_end = text.find('}\n    }', p_xem)

    new_xem_and_free = '''MovieSource.XEMTIVI -> listOf(
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
        '''

    text = text[:p_xem] + new_xem_and_free + text[p_xem_end:]

    # 4. getMovies FREEREELS branch: add short_kw://
    old_free_branch = 'filterUrl.startsWith("multi_short://") || filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://")'
    new_free_branch = 'filterUrl.startsWith("short_kw://") || filterUrl.startsWith("multi_short://") || filterUrl.startsWith("short_filter://") || filterUrl.startsWith("short_dramabox://")'
    text = text.replace(old_free_branch, new_free_branch)

    # 5. fetchShortDramaList: support all SHORT_KW_MAP
    p_kw_when = text.find('when (filterUrl) {', text.find('fun fetchShortDramaList'))
    p_kw_when_end = text.find('val result = mutableListOf<MovieItem>()', p_kw_when)

    new_kw_when = '''val kwType = filterUrl.removePrefix("short_kw://").removePrefix("multi_short://").removePrefix("short_filter://").removePrefix("short_dramabox://")
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

        '''

    text = text[:p_kw_when] + new_kw_when + text[p_kw_when_end:]

    # 6. GaMoMePhimClient.getDramaList infinite fallback
    p_gm_end = text.find('return list\n    }', text.find('object GaMoMePhimClient'))
    old_gm_return = 'return list\n    }'
    new_gm_return = '''// Tự động nạp thêm từ Phim Mới nếu thể loại này hết phim ở page > 1 (chống lỗi kéo thêm không ra phim)
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
                                val fbMatcher = pattern.matcher(fbHtml)
                                while (fbMatcher.find()) {
                                    val title = fbMatcher.group(1)?.trim() ?: ""
                                    val slug = fbMatcher.group(2)?.trim() ?: ""
                                    val thumb = fbMatcher.group(3)?.trim() ?: ""
                                    if (slug.isNotEmpty() && !seen.contains(slug)) {
                                        seen.add(slug)
                                        list.add(
                                            MovieItem(
                                                id = "gamomephim:$slug",
                                                name = title,
                                                slug = "gamomephim:$slug",
                                                originName = "Gà Mờ Mê Phim • Mới Cập Nhật",
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
                        }
                    } catch (err: Exception) {
                        err.printStackTrace()
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }'''

    text = text[:p_gm_end] + new_gm_return + text[p_gm_end + len(old_gm_return):]

    # 7. Subtitle fallback in FreeReelsClient
    # In getDramaDetail
    old_sub_find = '''if (lang.contains("vi") || disp.contains("việt")) {
                                        val vtt = sObj.getSafeString("vtt")
                                        val srt = sObj.getSafeString("subtitle")
                                        viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                                    }
                                }
                            }
                        }'''

    new_sub_find = '''if (lang.contains("vi") || disp.contains("việt") || disp.contains("viet")) {
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
                        }'''

    text = text.replace(old_sub_find, new_sub_find, 1)

    # In unlockEpisode
    old_unl_sub = '''if (lang.contains("vi") || disp.contains("việt")) {
                                val vtt = sObj.getSafeString("vtt")
                                val srt = sObj.getSafeString("subtitle")
                                viSubUrl = if (vtt.isNotEmpty()) vtt else srt
                            }
                        }
                    }
                }'''

    new_unl_sub = '''if (lang.contains("vi") || disp.contains("việt") || disp.contains("viet")) {
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
                }'''

    text = text.replace(old_unl_sub, new_unl_sub, 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'Successfully patched {path}!')

patch_movie_repository('HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt')
patch_movie_repository('HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt')
