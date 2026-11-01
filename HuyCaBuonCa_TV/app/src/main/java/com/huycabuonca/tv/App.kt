package com.huycabuonca.tv

import android.app.Application
import com.bumptech.glide.Glide
import com.bumptech.glide.load.model.GlideUrl
import com.huycabuonca.tv.util.OkHttpUrlLoader
import java.io.InputStream

class App : Application() {
    override fun onCreate() {
        super.onCreate()

        // Thay thế kết nối mạng mặc định của Glide (HttpURLConnection timeout 2.5s)
        // bằng OkHttpClient cấu hình cao cấp với timeout 30s, tự động phục hồi kết nối
        // giúp tải 100% hình ảnh poster từ mọi CDN phim (phimimg.com, nguonc.com, ...)
        try {
            Glide.get(this).registry.replace(
                GlideUrl::class.java,
                InputStream::class.java,
                OkHttpUrlLoader.Factory()
            )
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
