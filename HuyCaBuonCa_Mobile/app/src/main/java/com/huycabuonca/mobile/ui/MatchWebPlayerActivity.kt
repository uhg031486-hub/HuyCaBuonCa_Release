package com.huycabuonca.mobile.ui

import android.annotation.SuppressLint
import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.view.WindowManager
import android.webkit.*
import android.widget.ImageButton
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.huycabuonca.mobile.R

class MatchWebPlayerActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    private lateinit var txtTitle: TextView
    private lateinit var txtServer: TextView
    private lateinit var btnBack: ImageButton
    private lateinit var btnSwitchServer: ImageButton
    private var currentServer = 1
    private var teamA = ""
    private var teamB = ""

    companion object {
        const val EXTRA_MATCH_TITLE = "extra_match_title"
        const val EXTRA_SERVER_NUM = "extra_server_num"
        const val EXTRA_TEAM_A = "extra_team_a"
        const val EXTRA_TEAM_B = "extra_team_b"
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        hideSystemUI()
        setContentView(R.layout.activity_match_web_player)

        teamA = intent.getStringExtra(EXTRA_TEAM_A) ?: "Đội nhà"
        teamB = intent.getStringExtra(EXTRA_TEAM_B) ?: "Đội khách"
        currentServer = intent.getIntExtra(EXTRA_SERVER_NUM, 1)

        webView = findViewById(R.id.matchWebView)
        progressBar = findViewById(R.id.matchWebProgress)
        txtTitle = findViewById(R.id.txtWebMatchTitle)
        txtServer = findViewById(R.id.txtWebMatchServer)
        btnBack = findViewById(R.id.btnBackWebMatch)
        btnSwitchServer = findViewById(R.id.btnSwitchServerWeb)

        txtTitle.text = "⚽ $teamA vs $teamB"
        btnBack.setOnClickListener { finish() }

        btnSwitchServer.setOnClickListener {
            showSwitchServerDialog()
        }

        setupWebView()
        loadServerUrl(currentServer)
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.mediaPlaybackRequiresUserGesture = false
        settings.allowFileAccess = false
        settings.userAgentString = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: ""
                // Chặn toàn bộ pop-up nhảy sang tab cá cược hoặc trang ngoài
                if (url.contains("bet") || url.contains("88") || url.contains("game") || url.contains("ad.") || url.contains("tracker")) {
                    return true
                }
                return false
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility = View.GONE
                // Tiêm mã CSS/JS để xóa sạch 100% banner quảng cáo cá cược, chỉ giữ lại khung video toàn màn hình
                injectAdBlockerAndFullscreen()
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                if (newProgress < 100) {
                    progressBar.visibility = View.VISIBLE
                    progressBar.progress = newProgress
                } else {
                    progressBar.visibility = View.GONE
                }
            }
        }
    }

    private fun injectAdBlockerAndFullscreen() {
        val js = """
            javascript:(function() {
                var style = document.createElement('style');
                style.innerHTML = '
                    .banner, .banner-ads, .popup-ads, .ad-box, #chat-box, .advertisement, [class*="bet"], [class*="banner"] { display: none !important; }
                    header, footer, nav, .sidebar { display: none !important; }
                    body, html { background: #000 !important; margin: 0 !important; padding: 0 !important; overflow: hidden !important; }
                    video, iframe, #player { width: 100vw !important; height: 100vh !important; max-height: 100vh !important; }
                ';
                document.head.appendChild(style);
                var ads = document.querySelectorAll('.banner, .banner-ads, .popup-ads, .ad-box, #chat-box, [class*="bet"]');
                ads.forEach(function(el) { el.remove(); });
            })()
        """.trimIndent()
        webView.evaluateJavascript(js, null)
    }

    private fun loadServerUrl(serverNum: Int) {
        currentServer = serverNum
        val (url, name) = when (serverNum) {
            1 -> Pair("https://thapcamtv.to/", "Server 1: Thập Cẩm HD (BLV Tiếng Việt)")
            2 -> Pair("https://xoilac-tv.college/", "Server 2: Xôi Lạc HD (BLV Tiếng Việt)")
            else -> Pair("https://vebotv.live/", "Server 3: Về Bờ HD (BLV Tiếng Việt)")
        }
        txtServer.text = name
        progressBar.visibility = View.VISIBLE
        webView.loadUrl(url)
    }

    private fun showSwitchServerDialog() {
        val servers = arrayOf(
            "🟢 Server 1: Thập Cẩm HD (BLV Tiếng Việt)",
            "🔵 Server 2: Xôi Lạc HD (BLV Tiếng Việt)",
            "🟣 Server 3: Về Bờ HD (BLV Tiếng Việt)"
        )
        AlertDialog.Builder(this)
            .setTitle("Chọn Server Dự Phòng")
            .setItems(servers) { _, which ->
                loadServerUrl(which + 1)
            }
            .setNegativeButton("Hủy", null)
            .show()
    }

    private fun hideSystemUI() {
        supportRequestWindowFeature(android.view.Window.FEATURE_NO_TITLE)
        window.setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            window.insetsController?.let {
                it.hide(WindowInsets.Type.statusBars() or WindowInsets.Type.navigationBars())
                it.systemBarsBehavior = WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            }
        }
    }

    override fun onDestroy() {
        webView.loadUrl("about:blank")
        webView.destroy()
        super.onDestroy()
    }
}
