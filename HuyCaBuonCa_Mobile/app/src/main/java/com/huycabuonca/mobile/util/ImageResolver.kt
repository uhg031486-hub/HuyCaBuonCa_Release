package com.huycabuonca.mobile.util

import com.bumptech.glide.load.model.GlideUrl
import com.bumptech.glide.load.model.LazyHeaders

object ImageResolver {

    const val KKPHIM_IMG_BASE = "https://phimimg.com/"
    const val NGUONC_IMG_BASE = "https://img.nguonc.com/"
    const val GAMOME_IMG_BASE = "https://r2.gamomephim.com/"

    private const val BROWSER_UA =
        "Mozilla/5.0 (Linux; Android 10; SM-A536E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"

    /**
     * Kiểm tra xem một chuỗi URL có phải là URL ảnh hợp lệ hay không.
     * Loại bỏ các URL rác như: null, rỗng, "null", domain trần không có path ảnh ("https://phimimg.com/").
     */
    fun isValidImageUrl(url: String?): Boolean {
        if (url.isNullOrBlank()) return false
        val trimmed = url.trim()
        if (trimmed.equals("null", ignoreCase = true) || trimmed.equals("undefined", ignoreCase = true)) return false

        // Chấp nhận các URI cục bộ
        if (trimmed.startsWith("file://") || trimmed.startsWith("android.resource://") || trimmed.startsWith("content://") || trimmed.startsWith("data:image/")) {
            return true
        }

        if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
            val withoutProtocol = trimmed.substringAfter("://")
            val path = withoutProtocol.substringAfter("/", "")
            // Nếu không có path sau domain hoặc chỉ là "/" thì coi như domain trần -> URL rác
            return path.isNotEmpty() && path != "/"
        }

        // Relative path hợp lệ nếu không rỗng và không chỉ là dấu gạch chéo
        val cleanPath = trimmed.removePrefix("/")
        return cleanPath.isNotEmpty()
    }

    /**
     * Chuẩn hóa URL ảnh:
     * 1. Nâng cấp http -> https
     * 2. Bù domain gốc nếu là relative path
     * 3. Loại bỏ domain trần không có path
     * 4. Tự động fallback sang fallbackUrl nếu rawUrl không hợp lệ
     */
    fun cleanAndResolve(
        rawUrl: String?,
        fallbackUrl: String? = null,
        defaultBase: String = KKPHIM_IMG_BASE
    ): String {
        val primary = cleanSingle(rawUrl, defaultBase)
        if (primary.isNotEmpty()) return primary

        val secondary = cleanSingle(fallbackUrl, defaultBase)
        return secondary
    }

    private fun cleanSingle(url: String?, defaultBase: String): String {
        if (url.isNullOrBlank()) return ""
        val trimmed = url.trim()
        if (trimmed.equals("null", ignoreCase = true) || trimmed.equals("undefined", ignoreCase = true)) return ""

        // Local asset / data URI
        if (trimmed.startsWith("file://") || trimmed.startsWith("android.resource://") || trimmed.startsWith("content://") || trimmed.startsWith("data:image/")) {
            return trimmed
        }

        // Full URL
        if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
            val withoutProtocol = trimmed.substringAfter("://")
            val path = withoutProtocol.substringAfter("/", "")
            if (path.isEmpty() || path == "/") {
                return "" // Domain trần rác
            }
            return if (trimmed.startsWith("http://")) {
                trimmed.replaceFirst("http://", "https://")
            } else {
                trimmed
            }
        }

        // Relative path
        val cleanPath = trimmed.removePrefix("/")
        if (cleanPath.isEmpty()) return ""

        val base = if (defaultBase.endsWith("/")) defaultBase else "$defaultBase/"
        return base + cleanPath
    }

    /**
     * Tạo GlideUrl có kèm Headers User-Agent và Referer chuẩn trình duyệt
     * để vượt qua các lớp chặn Hotlink / Cloudflare WAF của các CDN ảnh phim.
     */
    fun buildGlideUrl(url: String): Any {
        if (url.isBlank()) return ""
        if (url.startsWith("file://") || url.startsWith("android.resource://") || url.startsWith("content://") || url.startsWith("data:image/")) {
            return url
        }

        val secureUrl = if (url.startsWith("http://")) url.replaceFirst("http://", "https://") else url
        val referer = when {
            secureUrl.contains("nguonc.com") -> "https://phim.nguonc.com/"
            secureUrl.contains("gamomephim.com") -> "https://gamomephim.com/"
            secureUrl.contains("free-reels.com") || secureUrl.contains("bytegecko") -> "https://www.free-reels.com/"
            else -> "https://phimimg.com/"
        }

        return GlideUrl(
            secureUrl,
            LazyHeaders.Builder()
                .addHeader("User-Agent", BROWSER_UA)
                .addHeader("Referer", referer)
                .addHeader("Accept", "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8")
                .build()
        )
    }
}
