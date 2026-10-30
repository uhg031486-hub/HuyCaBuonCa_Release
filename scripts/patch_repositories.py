import sys

sys.stdout.reconfigure(encoding='utf-8')

def patch_repo(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    target = """                        "tv://vtv" -> channels.filter { it.group.equals("VTV", ignoreCase = true) }
                        "tv://epl" -> channels.filter {
                            it.group.contains("Vệ Tinh", ignoreCase = true) ||
                            it.name.contains("True Premier", ignoreCase = true) ||
                            it.name.contains("Astro", ignoreCase = true) ||
                            it.name.contains("Sky Sports", ignoreCase = true) ||
                            it.name.contains("TNT Sports", ignoreCase = true) ||
                            it.name.contains("beIN", ignoreCase = true)
                        }
                        "tv://satellite" -> channels.filter {
                            it.group.contains("Vệ Tinh", ignoreCase = true) ||
                            it.name.contains("True Premier", ignoreCase = true) ||
                            it.name.contains("Astro", ignoreCase = true) ||
                            it.name.contains("Sky Sports", ignoreCase = true) ||
                            it.name.contains("TNT Sports", ignoreCase = true)
                        }"""

    replacement = """                        "tv://vtv" -> channels.filter { it.group.equals("VTV", ignoreCase = true) || it.name.startsWith("VTV", ignoreCase = true) }
                        "tv://epl" -> channels.filter {
                            it.group.contains("Vệ Tinh", ignoreCase = true) ||
                            it.name.contains("True Premier", ignoreCase = true) ||
                            it.name.contains("Astro", ignoreCase = true) ||
                            it.name.contains("Sky Sports", ignoreCase = true) ||
                            it.name.contains("TNT Sports", ignoreCase = true) ||
                            it.name.contains("beIN", ignoreCase = true)
                        }
                        "tv://satellite" -> channels.filter {
                            it.group.contains("Vệ Tinh", ignoreCase = true) ||
                            it.name.contains("True Premier", ignoreCase = true) ||
                            it.name.contains("Astro", ignoreCase = true) ||
                            it.name.contains("Sky Sports", ignoreCase = true) ||
                            it.name.contains("TNT Sports", ignoreCase = true) ||
                            it.name.contains("beIN", ignoreCase = true) ||
                            it.name.contains("NBC Sports", ignoreCase = true)
                        }"""

    target2 = """                        "tv://intl" -> channels.filter {
                            it.group.contains("Quốc Tế", ignoreCase = true) ||
                            it.group.contains("Hàn Quốc", ignoreCase = true) ||
                            it.group.contains("Trung Quốc", ignoreCase = true) ||
                            it.group.contains("Israel", ignoreCase = true) ||
                            it.group.contains("TVB", ignoreCase = true)
                        }
                        "tv://local" -> channels.filter { it.group.contains("Địa phương", ignoreCase = true) || it.group.contains("HTV", ignoreCase = true) }"""

    replacement2 = """                        "tv://intl" -> channels.filter {
                            it.group.contains("Quốc Tế", ignoreCase = true) ||
                            it.group.contains("Hàn Quốc", ignoreCase = true) ||
                            it.group.contains("Trung Quốc", ignoreCase = true) ||
                            it.group.contains("Israel", ignoreCase = true) ||
                            it.group.contains("TVB", ignoreCase = true) ||
                            it.group.contains("Vệ Tinh", ignoreCase = true) ||
                            it.name.contains("NHK", ignoreCase = true) ||
                            it.name.contains("Al Jazeera", ignoreCase = true) ||
                            it.name.contains("DW ", ignoreCase = true) ||
                            it.name.contains("France 24", ignoreCase = true) ||
                            it.name.contains("ABC News", ignoreCase = true) ||
                            it.name.contains("CBS News", ignoreCase = true) ||
                            it.name.contains("NBC News", ignoreCase = true) ||
                            it.name.contains("Bloomberg", ignoreCase = true) ||
                            it.name.contains("CNA", ignoreCase = true) ||
                            it.name.contains("Euronews", ignoreCase = true) ||
                            it.name.contains("Arirang", ignoreCase = true) ||
                            it.name.contains("Red Bull", ignoreCase = true) ||
                            it.name.contains("Reuters", ignoreCase = true) ||
                            it.name.contains("CNBC", ignoreCase = true)
                        }
                        "tv://local" -> channels.filter { 
                            it.group.contains("Địa phương", ignoreCase = true) || 
                            it.group.contains("HTV", ignoreCase = true) ||
                            it.name.startsWith("HTV", ignoreCase = true) ||
                            it.name.startsWith("THVL", ignoreCase = true)
                        }"""

    code_norm = code.replace('\r\n', '\n')
    t_norm = target.replace('\r\n', '\n')
    r_norm = replacement.replace('\r\n', '\n')
    t2_norm = target2.replace('\r\n', '\n')
    r2_norm = replacement2.replace('\r\n', '\n')

    if t_norm in code_norm:
        code_norm = code_norm.replace(t_norm, r_norm)
    if t2_norm in code_norm:
        code_norm = code_norm.replace(t2_norm, r2_norm)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code_norm)
    print(f"✅ Patched {file_path}")

patch_repo('HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt')
patch_repo('HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt')
