import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Update HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/ui/PlayerActivity.kt
tv_player_path = "HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/ui/PlayerActivity.kt"
with open(tv_player_path, "r", encoding="utf-8") as f:
    tv_code = f.read()

target_tv = """        player = ExoPlayer.Builder(this)
            .setTrackSelector(trackSelector)
            .setLoadControl(loadControl)
            .build().apply {"""

replacement_tv = """        val renderersFactory = object : androidx.media3.exoplayer.DefaultRenderersFactory(this) {
            override fun buildTextRenderers(
                context: android.content.Context,
                output: androidx.media3.exoplayer.text.TextOutput,
                outputLooper: android.os.Looper,
                extensionRendererMode: Int,
                out: java.util.ArrayList<androidx.media3.exoplayer.Renderer>
            ) {
                val tr = androidx.media3.exoplayer.text.TextRenderer(output, outputLooper).apply {
                    experimentalSetLegacyDecodingEnabled(true)
                }
                out.add(tr)
            }
        }

        player = ExoPlayer.Builder(this, renderersFactory)
            .setTrackSelector(trackSelector)
            .setLoadControl(loadControl)
            .build().apply {"""

target_tv_err = """                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                    binding.playerProgress.visibility = View.GONE
                    val embedUrl = intent.getStringExtra("EXTRA_EMBED_URL")
                    if (!embedUrl.isNullOrEmpty() && binding.webViewPlayer.visibility != View.VISIBLE) {
                        initWebViewPlayer(embedUrl)
                    }
                }"""

replacement_tv_err = """                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                    binding.playerProgress.visibility = View.GONE
                    android.util.Log.e("PlayerActivity", "ExoPlayer playback error: ${error.message}", error)
                    if (!subtitleUrl.isNullOrEmpty()) {
                        android.util.Log.w("PlayerActivity", "Lỗi phát với Subtitle, tự động fallback sang video không subtitle")
                        initExoPlayer(url, null)
                        return
                    }
                    val embedUrl = intent.getStringExtra("EXTRA_EMBED_URL")
                    if (!embedUrl.isNullOrEmpty() && binding.webViewPlayer.visibility != View.VISIBLE) {
                        initWebViewPlayer(embedUrl)
                    }
                }"""

if target_tv in tv_code and target_tv_err in tv_code:
    tv_code = tv_code.replace(target_tv, replacement_tv)
    tv_code = tv_code.replace(target_tv_err, replacement_tv_err)
    with open(tv_player_path, "w", encoding="utf-8") as f:
        f.write(tv_code)
    print("✅ Đã cập nhật Subtitle & Fallback cho TV PlayerActivity.kt")
else:
    print("❌ Không tìm thấy target trong TV PlayerActivity.kt")

# 2. Update HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/PlayerActivity.kt
mb_player_path = "HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/PlayerActivity.kt"
with open(mb_player_path, "r", encoding="utf-8") as f:
    mb_player_code = f.read()

target_mb_p = """        player = ExoPlayer.Builder(this)
            .setTrackSelector(trackSelector)
            .setLoadControl(loadControl)
            .build().apply {"""

replacement_mb_p = """        val renderersFactory = object : androidx.media3.exoplayer.DefaultRenderersFactory(this) {
            override fun buildTextRenderers(
                context: android.content.Context,
                output: androidx.media3.exoplayer.text.TextOutput,
                outputLooper: android.os.Looper,
                extensionRendererMode: Int,
                out: java.util.ArrayList<androidx.media3.exoplayer.Renderer>
            ) {
                val tr = androidx.media3.exoplayer.text.TextRenderer(output, outputLooper).apply {
                    experimentalSetLegacyDecodingEnabled(true)
                }
                out.add(tr)
            }
        }

        player = ExoPlayer.Builder(this, renderersFactory)
            .setTrackSelector(trackSelector)
            .setLoadControl(loadControl)
            .build().apply {"""

target_mb_p_err = """                override fun onPlayerError(error: PlaybackException) {
                    binding.playerProgress.visibility = View.GONE
                    val embedUrl = intent.getStringExtra("EXTRA_EMBED_URL")
                    if (!embedUrl.isNullOrEmpty() && binding.webViewPlayer.visibility != View.VISIBLE) {
                        initWebViewPlayer(embedUrl)
                    }
                }"""

replacement_mb_p_err = """                override fun onPlayerError(error: PlaybackException) {
                    binding.playerProgress.visibility = View.GONE
                    android.util.Log.e("PlayerActivity", "ExoPlayer error: ${error.message}", error)
                    if (!subtitleUrl.isNullOrEmpty()) {
                        android.util.Log.w("PlayerActivity", "Lỗi phát với Subtitle, tự động fallback sang video không subtitle")
                        initExoPlayer(url, null)
                        return
                    }
                    val embedUrl = intent.getStringExtra("EXTRA_EMBED_URL")
                    if (!embedUrl.isNullOrEmpty() && binding.webViewPlayer.visibility != View.VISIBLE) {
                        initWebViewPlayer(embedUrl)
                    }
                }"""

if target_mb_p in mb_player_code and target_mb_p_err in mb_player_code:
    mb_player_code = mb_player_code.replace(target_mb_p, replacement_mb_p)
    mb_player_code = mb_player_code.replace(target_mb_p_err, replacement_mb_p_err)
    with open(mb_player_path, "w", encoding="utf-8") as f:
        f.write(mb_player_code)
    print("✅ Đã cập nhật Subtitle & Fallback cho Mobile PlayerActivity.kt")
else:
    print("❌ Không tìm thấy target trong Mobile PlayerActivity.kt")

# 3. Update HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt
mb_detail_path = "HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt"
with open(mb_detail_path, "r", encoding="utf-8") as f:
    mb_detail_code = f.read()

target_mb_d = """        player = ExoPlayer.Builder(this)
            .setTrackSelector(trackSelector)
            .setLoadControl(loadControl)
            .build().apply {"""

replacement_mb_d = """        val renderersFactory = object : androidx.media3.exoplayer.DefaultRenderersFactory(this) {
            override fun buildTextRenderers(
                context: android.content.Context,
                output: androidx.media3.exoplayer.text.TextOutput,
                outputLooper: android.os.Looper,
                extensionRendererMode: Int,
                out: java.util.ArrayList<androidx.media3.exoplayer.Renderer>
            ) {
                val tr = androidx.media3.exoplayer.text.TextRenderer(output, outputLooper).apply {
                    experimentalSetLegacyDecodingEnabled(true)
                }
                out.add(tr)
            }
        }

        player = ExoPlayer.Builder(this, renderersFactory)
            .setTrackSelector(trackSelector)
            .setLoadControl(loadControl)
            .build().apply {"""

target_mb_d_err = """                override fun onPlayerError(error: PlaybackException) {
                    binding.playerProgress.visibility = View.GONE
                    val embedUrl = currentEpisode?.linkEmbed
                    if (!embedUrl.isNullOrEmpty() && binding.webViewPlayer.visibility != View.VISIBLE) {
                        initWebViewPlayer(embedUrl)
                    }
                }"""

replacement_mb_d_err = """                override fun onPlayerError(error: PlaybackException) {
                    binding.playerProgress.visibility = View.GONE
                    android.util.Log.e("DetailActivity", "Inline ExoPlayer error: ${error.message}", error)
                    if (!subtitleUrl.isNullOrEmpty()) {
                        android.util.Log.w("DetailActivity", "Lỗi phát với Subtitle, tự động fallback sang video không subtitle")
                        initExoPlayer(url, null)
                        return
                    }
                    val embedUrl = currentEpisode?.linkEmbed
                    if (!embedUrl.isNullOrEmpty() && binding.webViewPlayer.visibility != View.VISIBLE) {
                        initWebViewPlayer(embedUrl)
                    }
                }"""

if target_mb_d in mb_detail_code and target_mb_d_err in mb_detail_code:
    mb_detail_code = mb_detail_code.replace(target_mb_d, replacement_mb_d)
    mb_detail_code = mb_detail_code.replace(target_mb_d_err, replacement_mb_d_err)
    with open(mb_detail_path, "w", encoding="utf-8") as f:
        f.write(mb_detail_code)
    print("✅ Đã cập nhật Subtitle & Fallback cho Mobile DetailActivity.kt")
else:
    print("❌ Không tìm thấy target trong Mobile DetailActivity.kt")
