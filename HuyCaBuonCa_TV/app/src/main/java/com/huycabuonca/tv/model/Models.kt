package com.huycabuonca.tv.model

import java.io.Serializable

enum class MovieSource(val displayName: String) {
    KKPHIM("KKPhim (HLS VIP)"),
    ANIMEHAY("AnimeHay (Hoạt Hình Anime)"),
    XEMTIVI("Xem TiVi (Truyền Hình Trực Tuyến)")
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
    val linkEmbed: String? = null
) : Serializable
