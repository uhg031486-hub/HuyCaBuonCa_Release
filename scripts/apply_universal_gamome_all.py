import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("1. Updating HuyCa_Web/js/app.js ...")
with open('HuyCa_Web/js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Add getAppProxyUrl at top if not present
if 'function getAppProxyUrl(' not in app_js:
    helper = '''  function getAppProxyUrl(target) {
    if (!target) return '';
    if (target.includes('/api/proxy?url=')) return target;
    const isCloudflare = window.location.hostname && (window.location.hostname.endsWith('pages.dev') || window.location.hostname.includes('huyca.'));
    const base = isCloudflare ? '/api/proxy?url=' : 'https://huyca.pages.dev/api/proxy?url=';
    return base + encodeURIComponent(target);
  }
'''
    app_js = app_js.replace("'use strict';", "'use strict';\n\n" + helper)

# Update GaMoMePhimClient getProxyUrl
app_js = re.sub(
    r'getProxyUrl\(target\) \{.*?return \S+;?\s*\},',
    'getProxyUrl(target) {\n      return getAppProxyUrl(target);\n    },',
    app_js,
    count=1
)

# Update FreeReelsClient getProxyUrl
app_js = re.sub(
    r'(const FreeReelsClient = window\.FreeReelsClient = \{[\s\S]*?getProxyUrl\(target\) \{)[\s\S]*?(\n    \},)',
    r'\1\n      return getAppProxyUrl(target);\2',
    app_js,
    count=1
)

with open('HuyCa_Web/js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("  app.js updated successfully!")

print("2. Updating HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt ...")
tv_path = 'HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt'
with open(tv_path, 'r', encoding='utf-8') as f:
    tv_code = f.read()

tv_replacement = '''object GaMoMePhimClient {
    private const val BASE_URL = "https://gamomephim.com"

    fun parseGaMoMeHtml(html: String): List<MovieItem> {
        val list = mutableListOf<MovieItem>()
        val seen = mutableSetOf<String>()
        val aPattern = java.util.regex.Pattern.compile("""<a[^>]+href="/phim/([^"/]+)"[^>]*>(.*?)</a>""", java.util.regex.Pattern.DOTALL)
        val matcher = aPattern.matcher(html)
        while (matcher.find()) {
            val slug = matcher.group(1)?.trim() ?: ""
            val body = matcher.group(2) ?: ""
            if (slug.isEmpty() || seen.contains(slug)) continue

            var title = ""
            val titleM = java.util.regex.Pattern.compile("""title="([^"]+)"""").matcher(matcher.group())
            if (titleM.find()) {
                title = titleM.group(1)?.trim() ?: ""
            }
            if (title.isEmpty()) {
                val hM = java.util.regex.Pattern.compile("""<h[34][^>]*>(.*?)</h[34]>""", java.util.regex.Pattern.DOTALL).matcher(body)
                if (hM.find()) {
                    title = hM.group(1)?.replace(Regex("<[^>]+>"), "")?.trim() ?: ""
                }
            }
            if (title.isEmpty()) {
                val altM = java.util.regex.Pattern.compile("""<img[^>]+alt="([^"]+)"""").matcher(body)
                if (altM.find()) {
                    title = altM.group(1)?.replace("Poster phim ", "")?.replace("Poster ", "")?.trim() ?: ""
                }
            }

            var thumb = ""
            val imgM = java.util.regex.Pattern.compile("""<img[^>]+src="([^"]+)"""").matcher(body)
            if (imgM.find()) {
                thumb = imgM.group(1)?.trim() ?: ""
            }

            if (slug.isNotEmpty() && title.isNotEmpty()) {
                seen.add(slug)
                list.add(
                    MovieItem(
                        id = "gamomephim:$slug",
                        name = title,
                        slug = "gamomephim:$slug",
                        originName = "Gà Mờ Mê Phim • Thuyết Minh",
                        thumbUrl = thumb,
                        posterUrl = thumb,
                        year = "2026",
                        quality = "🎙️ Thuyết Minh & Vietsub",
                        episodeCurrent = "Full Bộ HD",
                        source = MovieSource.FREEREELS
                    )
                )
            }
        }
        return list
    }

    fun getDramaList(client: OkHttpClient, filterUrl: String, page: Int): List<MovieItem> {
        val list = mutableListOf<MovieItem>()
        try {
            val genrePath = filterUrl.removePrefix("gamomephim://")
            val targetUrl = if (page <= 1) {
                "$BASE_URL/$genrePath"
            } else {
                "$BASE_URL/$genrePath?page=$page"
            }

            val req = Request.Builder()
                .url(targetUrl)
                .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                .build()

            client.newCall(req).execute().use { resp ->
                if (!resp.isSuccessful) return emptyList()
                val html = resp.body?.string() ?: return emptyList()
                list.addAll(parseGaMoMeHtml(html))

                // Tự động nạp thêm từ Phim Mới nếu thể loại này hết phim ở page > 1 (chống lỗi kéo thêm không ra phim)
                if (list.isEmpty() && page > 1 && genrePath != "phim-moi") {
                    try {
                        val fbUrl = "$BASE_URL/phim-moi?page=$page"
                        val fbReq = Request.Builder()
                            .url(fbUrl)
                            .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                            .build()
                        client.newCall(fbReq).execute().use { fbResp ->
                            if (fbResp.isSuccessful) {
                                val fbHtml = fbResp.body?.string() ?: ""
                                val fbItems = parseGaMoMeHtml(fbHtml)
                                fbItems.forEach { item ->
                                    list.add(item.copy(originName = "Gà Mờ Mê Phim • Mới Cập Nhật"))
                                }
                            }
                        }
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return list
    }'''

tv_code = re.sub(
    r'object GaMoMePhimClient \{[\s\S]*?return list\s*\}',
    tv_replacement,
    tv_code
)
with open(tv_path, 'w', encoding='utf-8') as f:
    f.write(tv_code)
print("  TV MovieRepository.kt updated successfully!")

print("3. Updating HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/data/repository/MovieRepository.kt ...")
mobile_path = 'HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt'
with open(mobile_path, 'r', encoding='utf-8') as f:
    mobile_code = f.read()

mobile_code = re.sub(
    r'object GaMoMePhimClient \{[\s\S]*?return list\s*\}',
    tv_replacement,
    mobile_code
)
with open(mobile_path, 'w', encoding='utf-8') as f:
    f.write(mobile_code)
print("  Mobile MovieRepository.kt updated successfully!")
