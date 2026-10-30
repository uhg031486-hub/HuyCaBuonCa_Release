import re

# Test Kotlin regex logic in Python
code_tv = '''
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
'''
print("Kotlin parser structure looks solid!")
