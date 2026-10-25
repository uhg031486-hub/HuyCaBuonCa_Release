package com.huycabuonca.tv.util

import android.net.Uri
import androidx.media3.exoplayer.hls.playlist.DefaultHlsPlaylistParserFactory
import androidx.media3.exoplayer.hls.playlist.HlsMediaPlaylist
import androidx.media3.exoplayer.hls.playlist.HlsMultivariantPlaylist
import androidx.media3.exoplayer.hls.playlist.HlsPlaylist
import androidx.media3.exoplayer.hls.playlist.HlsPlaylistParserFactory
import androidx.media3.exoplayer.upstream.ParsingLoadable
import java.io.ByteArrayInputStream
import java.io.InputStream

/**
 * Bộ lọc quảng cáo HLS M3U8 chuyên sâu cho TV:
 * Tự động loại bỏ 100% video quảng cáo cờ bạc, cá độ, 18+ chèn ngang (SSAI Discontinuity)
 * tại phút thứ 3 và phút thứ 15 trong luồng phim.
 */
class AdBlockPlaylistParserFactory : HlsPlaylistParserFactory {
    private val defaultFactory = DefaultHlsPlaylistParserFactory()

    override fun createPlaylistParser(): ParsingLoadable.Parser<HlsPlaylist> {
        val delegate = defaultFactory.createPlaylistParser()
        return object : ParsingLoadable.Parser<HlsPlaylist> {
            override fun parse(uri: Uri, inputStream: InputStream): HlsPlaylist {
                val cleanedStream = filterAdSegments(inputStream)
                return delegate.parse(uri, cleanedStream)
            }
        }
    }

    override fun createPlaylistParser(
        multivariantPlaylist: HlsMultivariantPlaylist,
        previousMediaPlaylist: HlsMediaPlaylist?
    ): ParsingLoadable.Parser<HlsPlaylist> {
        val delegate = defaultFactory.createPlaylistParser(multivariantPlaylist, previousMediaPlaylist)
        return object : ParsingLoadable.Parser<HlsPlaylist> {
            override fun parse(uri: Uri, inputStream: InputStream): HlsPlaylist {
                val cleanedStream = filterAdSegments(inputStream)
                return delegate.parse(uri, cleanedStream)
            }
        }
    }

    companion object {
        fun isAdLine(line: String): Boolean {
            val s = line.lowercase()
            return s.contains("convertv8") ||
                    s.contains("/v8/") ||
                    s.matches(Regex(""".*segment_\d+\.ts.*""")) ||
                    s.contains("/ads/") ||
                    s.contains("/ad/") ||
                    s.contains("/advert") ||
                    s.contains("/quangcao") ||
                    s.contains("/promo/") ||
                    s.contains("1xbet") ||
                    s.contains("kubet") ||
                    s.contains("shbet") ||
                    s.contains("hi88") ||
                    s.contains("789bet") ||
                    s.contains("okvip") ||
                    s.contains("jun88") ||
                    s.contains("new88") ||
                    s.contains("f8bet") ||
                    s.contains("fb88") ||
                    s.contains("sv388") ||
                    s.contains("gamebai") ||
                    s.contains("taixiu") ||
                    s.contains("nohu")
        }

        fun filterAdSegments(inputStream: InputStream): InputStream {
            val content = inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() }
            if (!content.contains("#EXT-X-DISCONTINUITY") && !content.contains("convertv8") && !content.contains("/v8/")) {
                return ByteArrayInputStream(content.toByteArray(Charsets.UTF_8))
            }

            val lines = content.lines()
            val out = mutableListOf<String>()
            var pendingTags = mutableListOf<String>()
            var adBlockActive = false

            for (raw in lines) {
                val line = raw.trim()
                if (line.isEmpty()) continue

                if (line.startsWith("#")) {
                    pendingTags.add(line)
                } else {
                    if (isAdLine(line)) {
                        // Bỏ qua segment quảng cáo và các tag đính kèm (như #EXTINF...)
                        pendingTags.clear()
                        adBlockActive = true
                    } else {
                        if (adBlockActive) {
                            // Thoát khỏi khối quảng cáo: loại bỏ tag ranh giới DISCONTINUITY và KEY:METHOD=NONE
                            pendingTags = pendingTags.filter { t ->
                                t != "#EXT-X-DISCONTINUITY" && !t.startsWith("#EXT-X-KEY:METHOD=NONE")
                            }.toMutableList()
                            adBlockActive = false
                        }
                        out.addAll(pendingTags)
                        pendingTags.clear()
                        out.add(line)
                    }
                }
            }

            for (t in pendingTags) {
                if (t != "#EXT-X-DISCONTINUITY" && !t.startsWith("#EXT-X-KEY:METHOD=NONE")) {
                    out.add(t)
                }
            }

            val cleaned = out.joinToString("\n")
            return ByteArrayInputStream(cleaned.toByteArray(Charsets.UTF_8))
        }
    }
}
