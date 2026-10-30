import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = 'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

target = """        val reqHeaders = mutableMapOf<String, String>()
        if (url.contains("phimapi.com") || url.contains("phimimg.com") || url.contains("phim1280.tv")) {
            reqHeaders["Referer"] = "https://player.phimapi.com/"
            reqHeaders["Origin"] = "https://player.phimapi.com"
        }
        val dataSourceFactory = DefaultHttpDataSource.Factory()
            .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
            .setDefaultRequestProperties(reqHeaders)
            .setAllowCrossProtocolRedirects(true)

        val mediaItemBuilder = MediaItem.Builder().setUri(url)

        if (!subtitleUrl.isNullOrEmpty()) {
            val mimeType = if (subtitleUrl.contains(".vtt", ignoreCase = true)) {
                androidx.media3.common.MimeTypes.TEXT_VTT
            } else {
                androidx.media3.common.MimeTypes.APPLICATION_SUBRIP
            }
            val subConfig = MediaItem.SubtitleConfiguration.Builder(Uri.parse(subtitleUrl))
                .setMimeType(mimeType)
                .setLanguage("vi")
                .setLabel("Tiếng Việt")
                .setSelectionFlags(androidx.media3.common.C.SELECTION_FLAG_DEFAULT or androidx.media3.common.C.SELECTION_FLAG_FORCED)
                .build()
            mediaItemBuilder.setSubtitleConfigurations(listOf(subConfig))
        }

        val mediaItem = mediaItemBuilder.build()
        val mediaSourceFactory = androidx.media3.exoplayer.source.DefaultMediaSourceFactory(this)
            .setDataSourceFactory(dataSourceFactory)
        val mediaSource = mediaSourceFactory.createMediaSource(mediaItem)"""

replacement = """        val reqHeaders = mutableMapOf<String, String>()
        if (url.contains("phimapi.com") || url.contains("phimimg.com") || url.contains("phim1280.tv")) {
            reqHeaders["Referer"] = "https://player.phimapi.com/"
            reqHeaders["Origin"] = "https://player.phimapi.com"
        } else if (url.contains("huyca.pages.dev") || url.contains("nguonc_stream")) {
            reqHeaders["Referer"] = "https://huyca.pages.dev/"
            reqHeaders["Origin"] = "https://huyca.pages.dev"
        }
        val dataSourceFactory = DefaultHttpDataSource.Factory()
            .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
            .setDefaultRequestProperties(reqHeaders)
            .setAllowCrossProtocolRedirects(true)

        val isHlsStream = url.contains(".m3u8", ignoreCase = true) || 
                          url.contains("m3u8", ignoreCase = true) || 
                          url.contains("nguonc_stream", ignoreCase = true)

        val mediaItemBuilder = MediaItem.Builder().setUri(url)
        if (isHlsStream) {
            mediaItemBuilder.setMimeType(androidx.media3.common.MimeTypes.APPLICATION_M3U8)
        }

        if (!subtitleUrl.isNullOrEmpty()) {
            val mimeType = if (subtitleUrl.contains(".vtt", ignoreCase = true)) {
                androidx.media3.common.MimeTypes.TEXT_VTT
            } else {
                androidx.media3.common.MimeTypes.APPLICATION_SUBRIP
            }
            val subConfig = MediaItem.SubtitleConfiguration.Builder(Uri.parse(subtitleUrl))
                .setMimeType(mimeType)
                .setLanguage("vi")
                .setLabel("Tiếng Việt")
                .setSelectionFlags(androidx.media3.common.C.SELECTION_FLAG_DEFAULT or androidx.media3.common.C.SELECTION_FLAG_FORCED)
                .build()
            mediaItemBuilder.setSubtitleConfigurations(listOf(subConfig))
        }

        val mediaItem = mediaItemBuilder.build()
        val mediaSource = if (isHlsStream) {
            androidx.media3.exoplayer.hls.HlsMediaSource.Factory(dataSourceFactory)
                .setPlaylistParserFactory(com.huycabuonca.mobile.util.AdBlockPlaylistParserFactory())
                .createMediaSource(mediaItem)
        } else {
            androidx.media3.exoplayer.source.DefaultMediaSourceFactory(this)
                .setDataSourceFactory(dataSourceFactory)
                .createMediaSource(mediaItem)
        }"""

target_norm = target.replace('\r\n', '\n')
code_norm = code.replace('\r\n', '\n')
repl_norm = replacement.replace('\r\n', '\n')

if target_norm in code_norm:
    code_norm = code_norm.replace(target_norm, repl_norm)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code_norm)
    print("✅ Đã cập nhật thành công HuyCaBuonCa_Mobile DetailActivity.kt!")
else:
    print("❌ Không tìm thấy target block trong Mobile DetailActivity.kt!")
