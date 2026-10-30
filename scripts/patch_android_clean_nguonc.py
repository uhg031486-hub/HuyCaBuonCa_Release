import sys

sys.stdout.reconfigure(encoding='utf-8')

# Patch Mobile DetailActivity.kt
mobile_file = 'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt'
with open(mobile_file, 'r', encoding='utf-8') as f:
    m_content = f.read()

m_target = """        val isM3u8 = episode.linkM3u8 != null || streamUrl.contains(".m3u8")
        if (isM3u8) {
            initExoPlayer(streamUrl, episode.subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }"""

m_replace = """        // TỰ ĐỘNG GIẢI MÃ NGUỒN C SANG LUỒNG M3U8 SẠCH (ZERO ADS) QUA API HUY CÁ
        if (streamUrl.contains("streamc.xyz") || streamUrl.contains("embed.php")) {
            val cleanM3u8 = "https://huyca.pages.dev/api/nguonc_stream?url=${java.net.URLEncoder.encode(streamUrl, "UTF-8")}"
            initExoPlayer(cleanM3u8, episode.subtitleUrl)
            return
        }

        val isM3u8 = episode.linkM3u8 != null || streamUrl.contains(".m3u8")
        if (isM3u8) {
            initExoPlayer(streamUrl, episode.subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }"""

assert m_target in m_content, "m_target not found in DetailActivity.kt"
m_content = m_content.replace(m_target, m_replace, 1)

with open(mobile_file, 'w', encoding='utf-8') as f:
    f.write(m_content)
print("Đã cập nhật Mobile DetailActivity.kt!")

# Patch TV PlayerActivity.kt
tv_file = 'HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/ui/PlayerActivity.kt'
with open(tv_file, 'r', encoding='utf-8') as f:
    tv_content = f.read()

tv_target1 = """        if (isM3u8) {
            initExoPlayer(streamUrl, subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }"""

tv_replace1 = """        if (streamUrl.contains("streamc.xyz") || streamUrl.contains("embed.php")) {
            val cleanM3u8 = "https://huyca.pages.dev/api/nguonc_stream?url=${java.net.URLEncoder.encode(streamUrl, "UTF-8")}"
            initExoPlayer(cleanM3u8, subtitleUrl)
        } else if (isM3u8) {
            initExoPlayer(streamUrl, subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }"""

assert tv_target1 in tv_content, "tv_target1 not found in TV PlayerActivity.kt"
tv_content = tv_content.replace(tv_target1, tv_replace1, 1)

tv_target2 = """        if (episode.linkM3u8 != null || streamUrl.contains(".m3u8")) {
            initExoPlayer(streamUrl, episode.subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }"""

tv_replace2 = """        if (streamUrl.contains("streamc.xyz") || streamUrl.contains("embed.php")) {
            val cleanM3u8 = "https://huyca.pages.dev/api/nguonc_stream?url=${java.net.URLEncoder.encode(streamUrl, "UTF-8")}"
            initExoPlayer(cleanM3u8, episode.subtitleUrl)
            return
        }

        if (episode.linkM3u8 != null || streamUrl.contains(".m3u8")) {
            initExoPlayer(streamUrl, episode.subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }"""

assert tv_target2 in tv_content, "tv_target2 not found in TV PlayerActivity.kt"
tv_content = tv_content.replace(tv_target2, tv_replace2, 1)

with open(tv_file, 'w', encoding='utf-8') as f:
    f.write(tv_content)
print("Đã cập nhật TV PlayerActivity.kt!")
