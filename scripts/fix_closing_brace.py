import sys

sys.stdout.reconfigure(encoding='utf-8')

for path in ["HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/api/MovieRepository.kt", "HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/api/MovieRepository.kt"]:
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    target = """                    servers = servers
                )
            }
        } catch (e: Exception) {"""

    replacement = """                    servers = servers
                )
        } catch (e: Exception) {"""

    if target in code:
        code = code.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"✅ Đã fix thừa dấu ngoặc trong {path}")
    else:
        print(f"❌ Không tìm thấy target trong {path}")
