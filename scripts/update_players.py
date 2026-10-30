# scripts/update_players.py
import re

# 1. Update TV PlayerActivity.kt
tv_player_path = 'HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/ui/PlayerActivity.kt'
with open(tv_player_path, 'r', encoding='utf-8') as f:
    tv_player = f.read()

old_tv_init = '''        if (streamUrl.contains("streamc.xyz") || streamUrl.contains("embed.php")) {
            val cleanM3u8 = "https://huyca.pages.dev/api/nguonc_stream?url=${java.net.URLEncoder.encode(streamUrl, "UTF-8")}"
            initExoPlayer(cleanM3u8, subtitleUrl)
        } else if (isM3u8) {
            initExoPlayer(streamUrl, subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }'''

new_tv_init = '''        if (streamUrl.startsWith("freereels_unlock:")) {
            val tokens = streamUrl.split(":")
            if (tokens.size >= 3) {
                val sId = tokens[1].removePrefix("freereels:")
                val epId = tokens[2]
                binding.playerProgress.visibility = View.VISIBLE
                lifecycleScope.launch {
                    val res = MovieRepository.unlockFreeReelsEpisode(sId, epId)
                    binding.playerProgress.visibility = View.GONE
                    if (res != null && res.streamUrl.isNotEmpty()) {
                        initExoPlayer(res.streamUrl, res.subtitleUrl ?: subtitleUrl)
                    } else {
                        Toast.makeText(this@PlayerActivity, "Không thể tải tập phim ngắn này", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        } else if (streamUrl.contains("streamc.xyz") || streamUrl.contains("embed.php")) {
            val cleanM3u8 = "https://huyca.pages.dev/api/nguonc_stream?url=${java.net.URLEncoder.encode(streamUrl, "UTF-8")}"
            initExoPlayer(cleanM3u8, subtitleUrl)
        } else if (isM3u8 || streamUrl.contains(".m3u8") || streamUrl.contains(".mp4") || streamUrl.contains("gamomephim")) {
            initExoPlayer(streamUrl, subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }'''

if old_tv_init in tv_player:
    tv_player = tv_player.replace(old_tv_init, new_tv_init)
    print('Updated TV PlayerActivity onCreate streamUrl handler')
else:
    print('Warning: old_tv_init not found in TV PlayerActivity')

old_tokens = 'val res = MovieRepository.unlockFreeReelsEpisode(tokens[1], tokens[2])'
new_tokens = 'val res = MovieRepository.unlockFreeReelsEpisode(tokens[1].removePrefix("freereels:"), tokens[2])'
tv_player = tv_player.replace(old_tokens, new_tokens)

old_check = 'if (episode.linkM3u8 != null || streamUrl.contains(".m3u8")) {'
new_check = 'if (episode.linkM3u8 != null || streamUrl.contains(".m3u8") || streamUrl.contains(".mp4") || streamUrl.contains("gamomephim")) {'
tv_player = tv_player.replace(old_check, new_check)

with open(tv_player_path, 'w', encoding='utf-8') as f:
    f.write(tv_player)
print('Saved TV PlayerActivity')

# 2. Update Mobile PlayerActivity.kt
mobile_player_path = 'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/PlayerActivity.kt'
with open(mobile_player_path, 'r', encoding='utf-8') as f:
    mobile_player = f.read()

if 'import androidx.lifecycle.lifecycleScope' not in mobile_player:
    mobile_player = mobile_player.replace('import androidx.appcompat.app.AppCompatActivity', 'import androidx.appcompat.app.AppCompatActivity\nimport androidx.lifecycle.lifecycleScope\nimport kotlinx.coroutines.launch')

old_mobile_setup = '''    private fun setupMovieMode(streamUrl: String, isM3u8: Boolean, title: String, episode: String, subtitleUrl: String? = null) {
        binding.btnOpenChannelList.visibility = View.GONE
        binding.btnPrevChannel.visibility = View.GONE
        binding.btnNextChannel.visibility = View.GONE

        binding.txtPlayerTitle.text = if (episode.isNotEmpty()) "$title - $episode" else title

        if (isM3u8) {
            initExoPlayer(streamUrl, subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }
    }'''

new_mobile_setup = '''    private fun setupMovieMode(streamUrl: String, isM3u8: Boolean, title: String, episode: String, subtitleUrl: String? = null) {
        binding.btnOpenChannelList.visibility = View.GONE
        binding.btnPrevChannel.visibility = View.GONE
        binding.btnNextChannel.visibility = View.GONE

        binding.txtPlayerTitle.text = if (episode.isNotEmpty()) "$title - $episode" else title

        if (streamUrl.startsWith("freereels_unlock:")) {
            val tokens = streamUrl.split(":")
            if (tokens.size >= 3) {
                val sId = tokens[1].removePrefix("freereels:")
                val epId = tokens[2]
                binding.playerProgress.visibility = View.VISIBLE
                lifecycleScope.launch {
                    val res = MovieRepository.unlockFreeReelsEpisode(sId, epId)
                    binding.playerProgress.visibility = View.GONE
                    if (res != null && res.streamUrl.isNotEmpty()) {
                        initExoPlayer(res.streamUrl, res.subtitleUrl ?: subtitleUrl)
                    } else {
                        Toast.makeText(this@PlayerActivity, "Không thể tải tập phim ngắn này", Toast.LENGTH_SHORT).show()
                    }
                }
                return
            }
        }

        if (streamUrl.contains("streamc.xyz") || streamUrl.contains("embed.php")) {
            val cleanM3u8 = "https://huyca.pages.dev/api/nguonc_stream?url=${java.net.URLEncoder.encode(streamUrl, "UTF-8")}"
            initExoPlayer(cleanM3u8, subtitleUrl)
            return
        }

        val isExo = isM3u8 || streamUrl.contains(".m3u8", ignoreCase = true) || streamUrl.contains(".mp4", ignoreCase = true) || streamUrl.contains("gamomephim")
        if (isExo) {
            initExoPlayer(streamUrl, subtitleUrl)
        } else {
            initWebViewPlayer(streamUrl)
        }
    }'''

if old_mobile_setup in mobile_player:
    mobile_player = mobile_player.replace(old_mobile_setup, new_mobile_setup)
    print('Updated Mobile PlayerActivity setupMovieMode')
else:
    print('Warning: old_mobile_setup not found in Mobile PlayerActivity')

with open(mobile_player_path, 'w', encoding='utf-8') as f:
    f.write(mobile_player)
print('Saved Mobile PlayerActivity')

# 3. Update DetailActivity in both TV and Mobile
for d_path in ['HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/ui/DetailActivity.kt', 'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt']:
    with open(d_path, 'r', encoding='utf-8') as f:
        dt = f.read()
    dt = dt.replace('tokens[1], tokens[2]', 'tokens[1].removePrefix("freereels:"), tokens[2]')
    dt = dt.replace('val sId = tokens[1]', 'val sId = tokens[1].removePrefix("freereels:")')
    with open(d_path, 'w', encoding='utf-8') as f:
        f.write(dt)
    print(f'Updated {d_path}')
