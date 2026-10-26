def fix_comma(path):
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    # Sửa "                FilterItem(\"❤️ Yêu Thích\", \"app://favorites\")\n            ),"
    # thành "                FilterItem(\"❤️ Yêu Thích\", \"app://favorites\")\n            )"
    old_str = 'FilterItem("❤️ Yêu Thích", "app://favorites")\n            ),'
    new_str = 'FilterItem("❤️ Yêu Thích", "app://favorites")\n            )'
    txt = txt.replace(old_str, new_str)
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    print("Fixed comma in", path)

fix_comma(r"HuyCaBuonCa_TV\app\src\main\java\com\huycabuonca\tv\api\MovieRepository.kt")
fix_comma(r"HuyCaBuonCa_Mobile\app\src\main\java\com\huycabuonca\mobile\api\MovieRepository.kt")
