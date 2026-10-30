import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Update HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/PlayerActivity.kt
mb_player_path = "HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/PlayerActivity.kt"
with open(mb_player_path, "r", encoding="utf-8") as f:
    code = f.read()

target1 = """        player = ExoPlayer.Builder(this).setTrackSelector(trackSelector).build().apply {
            setMediaSource(mediaSource)
            prepare()
            playWhenReady = true
            addListener(object : Player.Listener {
                override fun onPlaybackStateChanged(playbackState: Int) {
                    if (playbackState == Player.STATE_BUFFERING) {
                        binding.playerProgress.visibility = View.VISIBLE
                    } else {
                        binding.playerProgress.visibility = View.GONE
                        binding.btnPlayPause.setImageResource(if (isPlaying) R.drawable.ic_pause else R.drawable.ic_play)
                    }
                }

                override fun onIsPlayingChanged(isPlaying: Boolean) {
                    binding.btnPlayPause.setImageResource(if (isPlaying) R.drawable.ic_pause else R.drawable.ic_play)
                }
            })
        }"""

replacement1 = """        val renderersFactory = object : androidx.media3.exoplayer.DefaultRenderersFactory(this) {
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

        player = ExoPlayer.Builder(this, renderersFactory).setTrackSelector(trackSelector).build().apply {
            setMediaSource(mediaSource)
            prepare()
            playWhenReady = true
            addListener(object : Player.Listener {
                override fun onPlaybackStateChanged(playbackState: Int) {
                    if (playbackState == Player.STATE_BUFFERING) {
                        binding.playerProgress.visibility = View.VISIBLE
                    } else {
                        binding.playerProgress.visibility = View.GONE
                        binding.btnPlayPause.setImageResource(if (isPlaying) R.drawable.ic_pause else R.drawable.ic_play)
                    }
                }

                override fun onIsPlayingChanged(isPlaying: Boolean) {
                    binding.btnPlayPause.setImageResource(if (isPlaying) R.drawable.ic_pause else R.drawable.ic_play)
                }

                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
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
                }
            })
        }"""

if target1 in code:
    code = code.replace(target1, replacement1)
    with open(mb_player_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Đã cập nhật Subtitle & onPlayerError cho Mobile PlayerActivity.kt")
else:
    print("❌ Không tìm thấy target1 trong Mobile PlayerActivity.kt")


# 2. Update HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt
mb_detail_path = "HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt"
with open(mb_detail_path, "r", encoding="utf-8") as f:
    d_code = f.read()

target2 = """        player = ExoPlayer.Builder(this)
            .setTrackSelector(trackSelector)
            .setLoadControl(loadControl)
            .build().apply {"""

replacement2 = """        val renderersFactory = object : androidx.media3.exoplayer.DefaultRenderersFactory(this) {
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

target2_err = """                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                    binding.playerLoading.visibility = View.GONE"""

replacement2_err = """                override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
                    binding.playerLoading.visibility = View.GONE
                    android.util.Log.e("DetailActivity", "Inline ExoPlayer error: ${error.message}", error)
                    if (!subtitleUrl.isNullOrEmpty()) {
                        android.util.Log.w("DetailActivity", "Lỗi phát với Subtitle, tự động fallback sang video không subtitle")
                        initExoPlayer(url, null)
                        return
                    }"""

if target2 in d_code and target2_err in d_code:
    d_code = d_code.replace(target2, replacement2)
    d_code = d_code.replace(target2_err, replacement2_err)
    with open(mb_detail_path, "w", encoding="utf-8") as f:
        f.write(d_code)
    print("✅ Đã cập nhật Subtitle & Fallback cho Mobile DetailActivity.kt")
else:
    print("❌ Không tìm thấy target2 trong Mobile DetailActivity.kt")
