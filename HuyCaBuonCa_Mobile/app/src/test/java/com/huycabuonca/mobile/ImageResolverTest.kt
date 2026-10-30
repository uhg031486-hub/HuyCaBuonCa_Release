package com.huycabuonca.mobile

import com.huycabuonca.mobile.util.ImageResolver
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ImageResolverTest {

    @Test
    fun testRelativeKkphimUrlResolution() {
        val relative = "uploads/movies/20261010/film.webp"
        val resolved = ImageResolver.cleanAndResolve(relative)
        assertEquals("https://phimimg.com/uploads/movies/20261010/film.webp", resolved)
    }

    @Test
    fun testSlashPrefixRelativeUrl() {
        val slashPrefix = "/upload/vod/20260415-1/abc.jpg"
        val resolved = ImageResolver.cleanAndResolve(slashPrefix)
        assertEquals("https://phimimg.com/upload/vod/20260415-1/abc.jpg", resolved)
    }

    @Test
    fun testHttpToHttpsUpgrade() {
        val httpUrl = "http://phimimg.com/uploads/movies/test.webp"
        val resolved = ImageResolver.cleanAndResolve(httpUrl)
        assertEquals("https://phimimg.com/uploads/movies/test.webp", resolved)
    }

    @Test
    fun testJunkDomainOnlyUrlFallback() {
        // Lỗi phổ biến: KKPHIM_IMG_BASE + "" dẫn đến "https://phimimg.com/"
        val junkUrl = "https://phimimg.com/"
        val fallback = "https://phimimg.com/uploads/movies/fallback.webp"
        val resolved = ImageResolver.cleanAndResolve(junkUrl, fallback)
        assertEquals(fallback, resolved)
    }

    @Test
    fun testNullOrEmptyWithFallback() {
        val fallback = "https://phimimg.com/uploads/movies/valid.webp"
        assertEquals(fallback, ImageResolver.cleanAndResolve(null, fallback))
        assertEquals(fallback, ImageResolver.cleanAndResolve("", fallback))
        assertEquals(fallback, ImageResolver.cleanAndResolve("   ", fallback))
        assertEquals(fallback, ImageResolver.cleanAndResolve("null", fallback))
    }

    @Test
    fun testNguonCRelativeUrlResolution() {
        val relative = "/images/img-fa400c1b.png"
        val resolved = ImageResolver.cleanAndResolve(relative, defaultBase = ImageResolver.NGUONC_IMG_BASE)
        assertEquals("https://img.nguonc.com/images/img-fa400c1b.png", resolved)
    }

    @Test
    fun testAssetUrlPreservation() {
        val assetUrl = "file:///android_asset/logos/tv_default_premium.png"
        val resolved = ImageResolver.cleanAndResolve(assetUrl)
        assertEquals(assetUrl, resolved)
    }

    @Test
    fun testIsValidImageUrl() {
        assertTrue(ImageResolver.isValidImageUrl("https://phimimg.com/upload/vod/1.jpg"))
        assertFalse(ImageResolver.isValidImageUrl(""))
        assertFalse(ImageResolver.isValidImageUrl("null"))
        assertFalse(ImageResolver.isValidImageUrl("https://phimimg.com"))
        assertFalse(ImageResolver.isValidImageUrl("https://phimimg.com/"))
    }
}
