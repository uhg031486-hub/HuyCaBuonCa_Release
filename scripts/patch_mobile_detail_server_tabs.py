with open('HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt', 'r', encoding='utf-8') as f:
    text = f.read()

target = """                setBackgroundResource(R.drawable.bg_btn_selector)
                text = server.serverName"""

replacement = """                setBackgroundResource(R.drawable.bg_btn_selector)
                val rawName = server.serverName
                val isVietsub = rawName.contains("vietsub", ignoreCase = true) ||
                                rawName.contains("phụ đề", ignoreCase = true) ||
                                rawName.contains("sub", ignoreCase = true)
                val isThuyetMinh = rawName.contains("thuyết minh", ignoreCase = true) ||
                                   rawName.contains("tm", ignoreCase = true)
                val isLongTieng = rawName.contains("lồng tiếng", ignoreCase = true) ||
                                  rawName.contains("lt", ignoreCase = true)
                val cleanTitle = when {
                    isVietsub -> "🇻🇳 [Phụ Đề] $rawName"
                    isThuyetMinh -> "🎙️ [Thuyết Minh] $rawName"
                    isLongTieng -> "🗣️ [Lồng Tiếng] $rawName"
                    else -> "📺 $rawName"
                }
                text = cleanTitle"""

assert target in text, "Target not found in Mobile DetailActivity.kt"
new_text = text.replace(target, replacement, 1)

with open('HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/DetailActivity.kt', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Mobile DetailActivity.kt updated successfully!")
