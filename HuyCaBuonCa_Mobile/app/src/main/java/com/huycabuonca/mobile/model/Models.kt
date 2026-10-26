package com.huycabuonca.mobile.model

import java.io.Serializable

enum class MovieSource(val displayName: String) {
    KKPHIM("KKPhim (HLS VIP)"),
    ANIMEHAY("Anime (Hoạt Hình Đa Nguồn)"),
    XEMTIVI("Xem TiVi (Truyền Hình Trực Tuyến)"),
    FREEREELS("FreeReels (Phim Ngắn Dọc)")
}

data class FilterItem(
    val title: String,
    val endpointUrl: String
) : Serializable

data class MovieItem(
    val id: String = "",
    val name: String,
    val slug: String,
    val originName: String = "",
    val thumbUrl: String = "",
    val posterUrl: String = "",
    val year: String = "",
    val quality: String = "HD",
    val episodeCurrent: String = "",
    val source: MovieSource = MovieSource.KKPHIM
) : Serializable

data class MovieDetail(
    val id: String = "",
    val name: String,
    val slug: String,
    val originName: String = "",
    val content: String = "",
    val thumbUrl: String = "",
    val posterUrl: String = "",
    val year: String = "",
    val time: String = "",
    val quality: String = "HD",
    val lang: String = "Vietsub",
    val source: MovieSource = MovieSource.KKPHIM,
    val servers: List<ServerGroup> = emptyList()
) : Serializable

data class ServerGroup(
    val serverName: String,
    val episodes: List<EpisodeItem>
) : Serializable

data class EpisodeItem(
    val name: String,
    val slug: String,
    val filename: String = "",
    val linkM3u8: String? = null,
    val linkEmbed: String? = null,
    val subtitleUrl: String? = null
) : Serializable

data class FootballMatch(
    val id: String,
    val time: String,
    val tournament: String,
    val teamA: String,
    val teamB: String,
    val channelName: String,
    val channelSlug: String,
    val score: String = "VS",
    val logoA: String = "",
    val logoB: String = "",
    val isLive: Boolean = false
) : Serializable
