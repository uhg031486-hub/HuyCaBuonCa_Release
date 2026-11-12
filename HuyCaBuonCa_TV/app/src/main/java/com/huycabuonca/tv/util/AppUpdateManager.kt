package com.huycabuonca.tv.util

import android.app.Activity
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.Settings
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.FileProvider
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.TimeUnit

object AppUpdateManager {

    private val UPDATE_CONFIG_URLS = listOf(
        "https://huyca.pages.dev/version.json",
        "https://raw.githubusercontent.com/uhg031486-hub/HuyCaBuonCa_Release/main/version.json",
        "https://raw.githubusercontent.com/uhg031486-hub/HuyCaBuonCa_Release/master/version.json"
    )

    private var pendingInstallFile: File? = null
    private var activeDownloadJob: Job? = null

    data class UpdateInfo(
        val versionCode: Int,
        val versionName: String,
        val title: String,
        val changelog: String,
        val apkUrl: String
    )

    private fun getCurrentVersionCode(context: Context): Long {
        return try {
            val pInfo = context.packageManager.getPackageInfo(context.packageName, 0)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                pInfo.longVersionCode
            } else {
                @Suppress("DEPRECATION")
                pInfo.versionCode.toLong()
            }
        } catch (e: Exception) {
            11L
        }
    }

    private fun getCurrentVersionName(context: Context): String {
        return try {
            val pInfo = context.packageManager.getPackageInfo(context.packageName, 0)
            pInfo.versionName ?: "2.0"
        } catch (e: Exception) {
            "2.0"
        }
    }

    fun onActivityResume(activity: Activity) {
        val file = pendingInstallFile ?: return
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            if (activity.packageManager.canRequestPackageInstalls() && file.exists()) {
                pendingInstallFile = null
                installApk(activity, file)
            }
        }
    }

    fun checkForUpdate(activity: Activity, showToastIfLatest: Boolean = false) {
        CoroutineScope(Dispatchers.IO).launch {
            val client = OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(10, TimeUnit.SECONDS)
                .followRedirects(true)
                .followSslRedirects(true)
                .build()

            var json: JSONObject? = null
            for (baseUrl in UPDATE_CONFIG_URLS) {
                try {
                    val request = Request.Builder()
                        .url("$baseUrl?t=${System.currentTimeMillis()}")
                        .header("Cache-Control", "no-cache, no-store, must-revalidate")
                        .header("Pragma", "no-cache")
                        .build()

                    client.newCall(request).execute().use { response ->
                        if (response.isSuccessful) {
                            val body = response.body?.string()
                            if (!body.isNullOrBlank()) {
                                val parsed = JSONObject(body)
                                if (parsed.optInt("versionCode", 0) > 0) {
                                    json = parsed
                                }
                            }
                        }
                    }
                    if (json != null) break
                } catch (_: Exception) {
                }
            }

            val validJson = json
            if (validJson != null) {
                val remoteVersionCode = validJson.optInt("versionCode", 0)
                val remoteVersionName = validJson.optString("versionName", "")
                val title = validJson.optString("title", "Phiên bản mới")
                val changelog = validJson.optString("changelog", "Cải tiến hiệu năng và cập nhật tính năng mới.")
                val apkUrl = validJson.optString("tvApkUrl").ifEmpty { validJson.optString("apkUrl", "") }
                val isMaintenanceLocked = validJson.optBoolean("isMaintenanceLocked", false)
                val maintenanceMessage = validJson.optString("maintenanceMessage", "Hệ thống đang bảo trì nội bộ. Vui lòng quay lại sau!")

                val currentVersionCode = getCurrentVersionCode(activity)
                val currentVersionName = getCurrentVersionName(activity)

                withContext(Dispatchers.Main) {
                    if (!activity.isFinishing && !activity.isDestroyed) {
                        if (isMaintenanceLocked) {
                            showMaintenanceDialog(activity, maintenanceMessage)
                            return@withContext
                        }
                        if (remoteVersionCode.toLong() > currentVersionCode && apkUrl.isNotEmpty()) {
                            showUpdateDialog(
                                activity,
                                UpdateInfo(
                                    versionCode = remoteVersionCode,
                                    versionName = remoteVersionName,
                                    title = title,
                                    changelog = changelog,
                                    apkUrl = apkUrl
                                )
                            )
                        } else if (showToastIfLatest) {
                            Toast.makeText(activity, "✅ Ứng dụng đang ở phiên bản mới nhất (v$currentVersionName)", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            } else if (showToastIfLatest) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(activity, "Không thể kết nối máy chủ kiểm tra cập nhật.", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun showMaintenanceDialog(activity: Activity, message: String) {
        AlertDialog.Builder(activity)
            .setTitle("🔒 THÔNG BÁO BẢO TRÌ NỘI BỘ")
            .setMessage(message)
            .setCancelable(false)
            .setPositiveButton("Thoát Ứng Dụng") { _, _ ->
                activity.finishAffinity()
            }
            .show()
    }

    private fun showUpdateDialog(activity: Activity, info: UpdateInfo) {
        AlertDialog.Builder(activity)
            .setTitle("🚀 ${info.title} (v${info.versionName})")
            .setMessage("Nội dung cập nhật:\n\n${info.changelog}\n\nBạn có muốn cập nhật ngay bây giờ?")
            .setCancelable(false)
            .setPositiveButton("CẬP NHẬT NGAY") { _, _ ->
                downloadAndInstallApk(activity, info.apkUrl, "HuyCa_TV_v${info.versionName}.apk")
            }
            .setNeutralButton("TẢI TRÌNH DUYỆT") { _, _ ->
                openBrowserFallback(activity, info.apkUrl)
            }
            .setNegativeButton("ĐỂ SAU", null)
            .show()
    }

    fun downloadAndInstallApk(context: Context, url: String, fileName: String) {
        val activity = context as? Activity
        if (activity == null || activity.isFinishing || activity.isDestroyed) {
            openBrowserFallback(context, url)
            return
        }

        val density = activity.resources.displayMetrics.density
        val pad = (20 * density).toInt()

        val container = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
        }

        val txtStatus = TextView(activity).apply {
            text = "Đang kết nối máy chủ tải bản cập nhật TV..."
            textSize = 14f
            setTextColor(Color.WHITE)
            setTypeface(null, Typeface.BOLD)
        }

        val progressBar = ProgressBar(activity, null, android.R.attr.progressBarStyleHorizontal).apply {
            isIndeterminate = false
            max = 100
            progress = 0
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                (12 * density).toInt()
            ).apply {
                topMargin = (14 * density).toInt()
                bottomMargin = (8 * density).toInt()
            }
        }

        val txtPercent = TextView(activity).apply {
            text = "0%"
            textSize = 13f
            setTextColor(Color.parseColor("#FFD54F"))
            gravity = Gravity.END
        }

        container.addView(txtStatus)
        container.addView(progressBar)
        container.addView(txtPercent)

        val progressDialog = AlertDialog.Builder(activity)
            .setTitle("⬇️ Đang Tải Bản Cập Nhật Huy Cá TV")
            .setView(container)
            .setCancelable(false)
            .setNegativeButton("HỦY TẢI") { dialog, _ ->
                activeDownloadJob?.cancel()
                dialog.dismiss()
            }
            .setNeutralButton("MỞ TRÌNH DUYỆT") { dialog, _ ->
                activeDownloadJob?.cancel()
                dialog.dismiss()
                openBrowserFallback(activity, url)
            }
            .create()

        progressDialog.show()

        activeDownloadJob?.cancel()
        activeDownloadJob = CoroutineScope(Dispatchers.IO).launch {
            val downloadDir = activity.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS) ?: activity.cacheDir
            if (!downloadDir.exists()) downloadDir.mkdirs()

            // Dọn dẹp các file APK cũ để giải phóng bộ nhớ TV Box
            downloadDir.listFiles()?.forEach { f ->
                if (f.name.endsWith(".apk", ignoreCase = true)) {
                    try { f.delete() } catch (_: Exception) {}
                }
            }

            val targetFile = File(downloadDir, fileName)
            val candidateUrls = listOf(
                url,
                "https://huyca.pages.dev/api/download?file=tv"
            ).distinct()

            val client = OkHttpClient.Builder()
                .connectTimeout(20, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)
                .followRedirects(true)
                .followSslRedirects(true)
                .build()

            var downloadedOk = false
            var lastError = ""

            for (candidateUrl in candidateUrls) {
                try {
                    val req = Request.Builder()
                        .url(candidateUrl)
                        .header("User-Agent", "Mozilla/5.0 (Linux; Android 14; Android TV) HuyCaUpdater/3.5")
                        .header("Accept", "*/*")
                        .build()

                    client.newCall(req).execute().use { resp ->
                        if (!resp.isSuccessful) {
                            lastError = "HTTP ${resp.code}"
                            return@use
                        }
                        val body = resp.body ?: return@use
                        val totalBytes = body.contentLength()
                        val input = body.byteStream()
                        FileOutputStream(targetFile).use { output ->
                            val buffer = ByteArray(32 * 1024)
                            var bytesRead: Int
                            var downloadedBytes = 0L
                            var lastUiUpdate = 0L

                            while (input.read(buffer).also { bytesRead = it } != -1) {
                                output.write(buffer, 0, bytesRead)
                                downloadedBytes += bytesRead

                                val now = System.currentTimeMillis()
                                if (now - lastUiUpdate > 120 || downloadedBytes == totalBytes) {
                                    lastUiUpdate = now
                                    val pct = if (totalBytes > 0) ((downloadedBytes * 100) / totalBytes).toInt().coerceIn(0, 100) else -1
                                    val mbDone = String.format("%.1f", downloadedBytes / (1024f * 1024f))
                                    val mbTotal = if (totalBytes > 0) String.format("%.1f", totalBytes / (1024f * 1024f)) else "?"
                                    withContext(Dispatchers.Main) {
                                        if (progressDialog.isShowing) {
                                            if (pct >= 0) {
                                                progressBar.isIndeterminate = false
                                                progressBar.progress = pct
                                                txtStatus.text = "Đang tải: $fileName"
                                                txtPercent.text = "$pct% ($mbDone MB / $mbTotal MB)"
                                            } else {
                                                progressBar.isIndeterminate = true
                                                txtStatus.text = "Đang tải: $fileName ($mbDone MB)"
                                                txtPercent.text = "Đang tải..."
                                            }
                                        }
                                    }
                                }
                            }
                            output.flush()
                        }

                        if (targetFile.exists() && targetFile.length() > 1_000_000L) {
                            downloadedOk = true
                        } else {
                            lastError = "Tệp tải về không hợp lệ (${targetFile.length()} bytes)"
                        }
                    }
                    if (downloadedOk) break
                } catch (e: Exception) {
                    lastError = e.message ?: "Lỗi kết nối mạng"
                }
            }

            withContext(Dispatchers.Main) {
                try {
                    if (progressDialog.isShowing) progressDialog.dismiss()
                } catch (_: Exception) {}

                if (downloadedOk && targetFile.exists()) {
                    installApk(activity, targetFile)
                } else {
                    Toast.makeText(activity, "Tải trực tiếp thất bại ($lastError). Đang chuyển sang trình duyệt...", Toast.LENGTH_LONG).show()
                    openBrowserFallback(activity, url)
                }
            }
        }
    }

    private fun openBrowserFallback(context: Context, url: String) {
        try {
            val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url)).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(browserIntent)
        } catch (e: Exception) {
            Toast.makeText(context, "Không thể mở trình duyệt tải: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun installApk(context: Context, file: File) {
        if (!file.exists()) {
            Toast.makeText(context, "Không tìm thấy tệp cài đặt!", Toast.LENGTH_SHORT).show()
            return
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            if (!context.packageManager.canRequestPackageInstalls()) {
                pendingInstallFile = file
                val activity = context as? Activity
                if (activity != null && !activity.isFinishing && !activity.isDestroyed) {
                    AlertDialog.Builder(activity)
                        .setTitle("🔓 Cấp Quyền Cài Đặt Bản Cập Nhật")
                        .setMessage("Để cài đặt bản cập nhật mới trên Android TV / Điện thoại, vui lòng bật \"Cho phép cài đặt ứng dụng không rõ nguồn gốc\" cho Huy Cá, sau đó bấm nút Back (Quay lại).")
                        .setCancelable(false)
                        .setPositiveButton("MỞ CÀI ĐẶT NGAY") { _, _ ->
                            try {
                                val settingsIntent = Intent(
                                    Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                                    Uri.parse("package:${context.packageName}")
                                ).apply {
                                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                                }
                                context.startActivity(settingsIntent)
                            } catch (e: Exception) {
                                launchPackageInstallerIntent(context, file)
                            }
                        }
                        .setNegativeButton("ĐỂ SAU", null)
                        .show()
                    return
                }
            }
        }

        launchPackageInstallerIntent(context, file)
    }

    private fun launchPackageInstallerIntent(context: Context, file: File) {
        try {
            val apkUri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                file
            )

            val installIntent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(apkUri, "application/vnd.android.package-archive")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(installIntent)
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(context, "Không thể mở trình cài đặt: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }
}
