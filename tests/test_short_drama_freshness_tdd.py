import os
import re
import sys
import unittest

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_APP_JS = os.path.join(ROOT_DIR, "HuyCa_Web", "js", "app.js")
MOBILE_REPO_KT = os.path.join(ROOT_DIR, "HuyCaBuonCa_Mobile", "app", "src", "main", "java", "com", "huycabuonca", "mobile", "api", "MovieRepository.kt")
TV_REPO_KT = os.path.join(ROOT_DIR, "HuyCaBuonCa_TV", "app", "src", "main", "java", "com", "huycabuonca", "tv", "api", "MovieRepository.kt")
MOBILE_GRADLE = os.path.join(ROOT_DIR, "HuyCaBuonCa_Mobile", "app", "build.gradle.kts")
TV_GRADLE = os.path.join(ROOT_DIR, "HuyCaBuonCa_TV", "app", "build.gradle.kts")


class TestShortDramaFreshnessTDD(unittest.TestCase):
    def setUp(self):
        with open(WEB_APP_JS, "r", encoding="utf-8") as f:
            self.web_js = f.read()
        with open(MOBILE_REPO_KT, "r", encoding="utf-8") as f:
            self.mobile_kt = f.read()
        with open(TV_REPO_KT, "r", encoding="utf-8") as f:
            self.tv_kt = f.read()
        with open(MOBILE_GRADLE, "r", encoding="utf-8") as f:
            self.mobile_gradle = f.read()
        with open(TV_GRADLE, "r", encoding="utf-8") as f:
            self.tv_gradle = f.read()

    def test_1_web_dynamic_rotation_seed_exists(self):
        """Web FreeReelsClient must implement getRotationSeed() to rotate offsets and keywords dynamically."""
        self.assertIn("getRotationSeed(", self.web_js, "Missing getRotationSeed() in HuyCa_Web/js/app.js")

    def test_2_web_foryou_prioritizes_new_releases_tab_505_and_foryou_feed(self):
        """freereels://foryou must fetch from tab 505 (New Releases) and foryou feed with rotated offset."""
        m = re.search(r"if\s*\(filterUrl\s*===\s*'freereels://foryou'.*?return\s*\[.*?\];", self.web_js, re.DOTALL)
        self.assertIsNotNone(m, "Could not find freereels://foryou handler in app.js")
        block = m.group(0)
        self.assertIn("'505'", block, "freereels://foryou must include Tab '505' (Mới Lên Sóng)")
        self.assertIn("'foryou'", block, "freereels://foryou must include dynamic 'foryou' feed")

    def test_3_web_gamomephim_has_resilient_freereels_fallback(self):
        """GaMoMePhimClient.getDramaList must fallback to FreeReelsClient when gamomephim.com is down (HTTP 530)."""
        m = re.search(r"async getDramaList\(filterUrl,\s*page\s*=\s*1\)\s*\{.*?\n\s*\},\s*\n\s*async getDramaDetail", self.web_js, re.DOTALL)
        self.assertIsNotNone(m, "Could not find GaMoMePhimClient.getDramaList in app.js")
        block = m.group(0)
        self.assertIn("fallbackGenreToFreeReels", block, "GaMoMePhimClient.getDramaList must fallback to FreeReels when gamomephim.com is unreachable")

    def test_4_kotlin_mobile_and_tv_dynamic_rotation_and_gamome_fallback(self):
        """Both Mobile and TV MovieRepository.kt must have dynamic short drama rotation and GaMoMePhim fallback."""
        for label, kt_code in [("Mobile", self.mobile_kt), ("TV", self.tv_kt)]:
            self.assertIn("getRotationSeed(", kt_code, f"{label} MovieRepository.kt missing getRotationSeed()")
            self.assertIn("fallbackGenreToFreeReels(", kt_code, f"{label} GaMoMePhimClient missing fallbackGenreToFreeReels() when gamomephim.com is down")

    def test_5_version_bumped_to_3_4_0(self):
        """Version must be >= v3.4.0 (versionCode >= 34) across Mobile and TV."""
        m_code = int(re.search(r"versionCode\s*=\s*(\d+)", self.mobile_gradle).group(1))
        t_code = int(re.search(r"versionCode\s*=\s*(\d+)", self.tv_gradle).group(1))
        self.assertGreaterEqual(m_code, 34)
        self.assertGreaterEqual(t_code, 34)


if __name__ == "__main__":
    unittest.main()
