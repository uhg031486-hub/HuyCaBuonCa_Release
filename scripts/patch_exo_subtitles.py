import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Update TV PlayerActivity.kt
tv_player_path = 'HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/ui/PlayerActivity.kt'
with open(tv_player_path, 'r', encoding='utf-8') as f:
    text_tv = f.read()

old_tv_ms = '''        val mediaItem = mediaItemBuilder.build()
        val mediaSource = if (isHlsStream) {
            androidx.media3.exoplayer.hls.HlsMediaSource.Factory(dataSourceFactory)
                .setPlaylistParserFactory(com.huycabuonca.tv.util.AdBlockPlaylistParserFactory())
                .createMediaSource(mediaItem)
        } else {
            androidx.media3.exoplayer.source.DefaultMediaSourceFactory(this)
                .setDataSourceFactory(dataSourceFactory)
                .createMediaSource(mediaItem)
        }'''

new_tv_ms = '''        val mediaItem = mediaItemBuilder.build()
        val baseMediaSource = if (isHlsStream) {
            androidx.media3.exoplayer.hls.HlsMediaSource.Factory(dataSourceFactory)
                .setPlaylistParserFactory(com.huycabuonca.tv.util.AdBlockPlaylistParserFactory())
                .createMediaSource(mediaItem)
        } else {
            androidx.media3.exoplayer.source.ProgressiveMediaSource.Factory(dataSourceFactory)
                .createMediaSource(mediaItem)
        }

        val mediaSource = if (!subtitleUrl.isNullOrEmpty()) {
            val mimeType = if (subtitleUrl.contains(".vtt", ignoreCase = true)) {
                androidx.media3.common.MimeTypes.TEXT_VTT
            } else {
                androidx.media3.common.MimeTypes.APPLICATION_SUBRIP
            }
            val subConfig = MediaItem.SubtitleConfiguration.Builder(android.net.Uri.parse(subtitleUrl))
                .setMimeType(mimeType)
                .setLanguage("vi")
                .setLabel("Tiếng Việt")
                .setSelectionFlags(androidx.media3.common.C.SELECTION_FLAG_DEFAULT or androidx.media3.common.C.SELECTION_FLAG_FORCED)
                .build()
            val subSource = androidx.media3.exoplayer.source.SingleSampleMediaSource.Factory(dataSourceFactory)
                .createMediaSource(subConfig, androidx.media3.common.C.TIME_UNSET)
            androidx.media3.exoplayer.source.MergingMediaSource(baseMediaSource, subSource)
        } else {
            baseMediaSource
        }'''

if old_tv_ms in text_tv:
    text_tv = text_tv.replace(old_tv_ms, new_tv_ms)
    with open(tv_player_path, 'w', encoding='utf-8') as f:
        f.write(text_tv)
    print('Updated TV PlayerActivity.kt successfully!')
else:
    print('Warning: old_tv_ms not found in TV PlayerActivity.kt')

# 2. Update Mobile PlayerActivity.kt
mobile_player_path = 'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/PlayerActivity.kt'
with open(mobile_player_path, 'r', encoding='utf-8') as f:
    text_mp = f.read()

old_mp_ms = '''        val mediaItem = mediaItemBuilder.build()
        val mediaSource = if (isHlsStream) {
            HlsMediaSource.Factory(dataSourceFactory)
                .setPlaylistParserFactory(com.huycabuonca.mobile.util.AdBlockPlaylistParserFactory())
                .createMediaSource(mediaItem)
        } else {
            androidx.media3.exoplayer.source.DefaultMediaSourceFactory(this)
                .setDataSourceFactory(dataSourceFactory)
                .createMediaSource(mediaItem)
        }'''

new_mp_ms = '''        val mediaItem = mediaItemBuilder.build()
        val baseMediaSource = if (isHlsStream) {
            HlsMediaSource.Factory(dataSourceFactory)
                .setPlaylistParserFactory(com.huycabuonca.mobile.util.AdBlockPlaylistParserFactory())
                .createMediaSource(mediaItem)
        } else {
            androidx.media3.exoplayer.source.ProgressiveMediaSource.Factory(dataSourceFactory)
                .createMediaSource(mediaItem)
        }

        val mediaSource = if (!subtitleUrl.isNullOrEmpty()) {
            val mimeType = if (subtitleUrl.contains(".vtt", ignoreCase = true)) {
                androidx.media3.common.MimeTypes.TEXT_VTT
            } else {
                androidx.media3.common.MimeTypes.APPLICATION_SUBRIP
            }
            val subConfig = MediaItem.SubtitleConfiguration.Builder(android.net.Uri.parse(subtitleUrl))
                .setMimeType(mimeType)
                .setLanguage("vi")
                .setLabel("Tiếng Việt")
                .setSelectionFlags(androidx.media3.common.C.SELECTION_FLAG_DEFAULT or androidx.media3.common.C.SELECTION_FLAG_FORCED)
                .build()
            val subSource = androidx.media3.exoplayer.source.SingleSampleMediaSource.Factory(dataSourceFactory)
                .createMediaSource(subConfig, androidx.media3.common.C.TIME_UNSET)
            androidx.media3.exoplayer.source.MergingMediaSource(baseMediaSource, subSource)
        } else {
            baseMediaSource
        }'''

if old_mp_ms in text_mp:
    text_mp = text_mp.replace(old_mp_ms, new_mp_ms)
    with open(mobile_player_path, 'w', encoding='utf-8') as f:
        f.write(text_mp)
    print('Updated Mobile PlayerActivity.kt successfully!')
else:
    print('Warning: old_mp_ms not found in Mobile PlayerActivity.kt')

# 3. Update Mobile DetailActivity.kt
mobile_detail_path = 'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt'
with open(mobile_detail_path, 'r', encoding='utf-8') as f:
    text_md = f.read()

old_md_ms = '''        val mediaItem = mediaItemBuilder.build()
        val mediaSource = if (isHlsStream) {
            androidx.media3.exoplayer.hls.HlsMediaSource.Factory(dataSourceFactory)
                .setPlaylistParserFactory(com.huycabuonca.mobile.util.AdBlockPlaylistParserFactory())
                .createMediaSource(mediaItem)
        } else {
            androidx.media3.exoplayer.source.DefaultMediaSourceFactory(this)
                .setDataSourceFactory(dataSourceFactory)
                .createMediaSource(mediaItem)
        }'''

new_md_ms = '''        val mediaItem = mediaItemBuilder.build()
        val baseMediaSource = if (isHlsStream) {
            androidx.media3.exoplayer.hls.HlsMediaSource.Factory(dataSourceFactory)
                .setPlaylistParserFactory(com.huycabuonca.mobile.util.AdBlockPlaylistParserFactory())
                .createMediaSource(mediaItem)
        } else {
            androidx.media3.exoplayer.source.ProgressiveMediaSource.Factory(dataSourceFactory)
                .createMediaSource(mediaItem)
        }

        val mediaSource = if (!subtitleUrl.isNullOrEmpty()) {
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
            val subSource = androidx.media3.exoplayer.source.SingleSampleMediaSource.Factory(dataSourceFactory)
                .createMediaSource(subConfig, androidx.media3.common.C.TIME_UNSET)
            androidx.media3.exoplayer.source.MergingMediaSource(baseMediaSource, subSource)
        } else {
            baseMediaSource
        }'''

if old_md_ms in text_md:
    text_md = text_md.replace(old_md_ms, new_md_ms)
    with open(mobile_detail_path, 'w', encoding='utf-8') as f:
        f.write(text_md)
    print('Updated Mobile DetailActivity.kt successfully!')
else:
    print('Warning: old_md_ms not found in Mobile DetailActivity.kt')
