import os
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_APP_JS = os.path.join(ROOT_DIR, "HuyCa_Web", "js", "app.js")
MOBILE_REPO = os.path.join(
    ROOT_DIR,
    "HuyCaBuonCa_Mobile",
    "app",
    "src",
    "main",
    "java",
    "com",
    "huycabuonca",
    "mobile",
    "api",
    "MovieRepository.kt",
)
TV_REPO = os.path.join(
    ROOT_DIR,
    "HuyCaBuonCa_TV",
    "app",
    "src",
    "main",
    "java",
    "com",
    "huycabuonca",
    "tv",
    "api",
    "MovieRepository.kt",
)
TV_PLAYER = os.path.join(
    ROOT_DIR,
    "HuyCaBuonCa_TV",
    "app",
    "src",
    "main",
    "java",
    "com",
    "huycabuonca",
    "tv",
    "ui",
    "PlayerActivity.kt",
)
MOBILE_PLAYER = os.path.join(
    ROOT_DIR,
    "HuyCaBuonCa_Mobile",
    "app",
    "src",
    "main",
    "java",
    "com",
    "huycabuonca",
    "mobile",
    "ui",
    "PlayerActivity.kt",
)
MOBILE_GRADLE = os.path.join(ROOT_DIR, "HuyCaBuonCa_Mobile", "app", "build.gradle.kts")
TV_GRADLE = os.path.join(ROOT_DIR, "HuyCaBuonCa_TV", "app", "build.gradle.kts")
WEBOS_APPINFO = os.path.join(ROOT_DIR, "HuyCaBuonCa_LG_webOS", "appinfo.json")


class TestYouTubeAIMoviesTDD(unittest.TestCase):
    def test_01_web_has_youtube_ai_client_and_categories(self):
        with open(WEB_APP_JS, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("const YouTubeAIClient", js, "Web app.js must define YouTubeAIClient")
        self.assertIn("ytInitialData", js, "YouTubeAIClient must parse ytInitialData")
        self.assertIn("sp=EgIYAg%3D%3D", js, "YouTubeAIClient must use >20m long video filter")
        self.assertIn("yt_ai://ai_all", js, "SUB_SOURCES must include yt_ai://ai_all")
        self.assertIn("yt_ai://ai_tutien", js, "SUB_SOURCES must include yt_ai://ai_tutien")
        self.assertIn("yt_ai://ai_manhwa", js, "SUB_SOURCES must include yt_ai://ai_manhwa")
        self.assertIn("yt_ai://ai_scifi", js, "SUB_SOURCES must include yt_ai://ai_scifi")
        self.assertIn("yt_ai://short_full", js, "SUB_SOURCES must include yt_ai://short_full")
        self.assertIn("currentFilter.startsWith('yt_ai://')", js, "loadMovies must handle yt_ai:// filters")
        self.assertIn("movie.slug.startsWith('yt_ai:')", js, "openMovieDetail must handle yt_ai: movies")
        self.assertIn("youtube-nocookie.com/embed/", js, "YouTubeAIClient must use youtube-nocookie embed URL")

    def test_02_web_player_shows_embed_helper_bar_for_all_embeds(self):
        with open(WEB_APP_JS, "r", encoding="utf-8") as f:
            js = f.read()

        # Verify embedHelperBar is shown for all embeds (not hidden when !isNguonCEmbed)
        self.assertIn("const showHelperBar = isEmbed;", js, "playVideo must display embedHelperBar for all embed streams")

    def test_03_mobile_and_tv_have_youtube_ai_client(self):
        for label, path in [("Mobile", MOBILE_REPO), ("TV", TV_REPO)]:
            with open(path, "r", encoding="utf-8") as f:
                kt = f.read()
            self.assertIn("object YouTubeAIClient", kt, f"{label} MovieRepository.kt must define object YouTubeAIClient")
            self.assertIn("ytInitialData", kt, f"{label} YouTubeAIClient must parse ytInitialData")
            self.assertIn("yt_ai:", kt, f"{label} MovieRepository.kt must support yt_ai: prefix")
            self.assertIn("youtube-nocookie.com/embed/", kt, f"{label} YouTubeAIClient must build youtube-nocookie.com embed URL")

    def test_04_tv_and_mobile_player_support_youtube_embed(self):
        for label, path in [("Mobile", MOBILE_PLAYER), ("TV", TV_PLAYER)]:
            with open(path, "r", encoding="utf-8") as f:
                kt = f.read()
            self.assertIn("youtube", kt, f"{label} PlayerActivity.kt must allow youtube/youtube-nocookie in WebView")
            self.assertIn("Referer", kt, f"{label} PlayerActivity.kt must send Referer header for embed playback")

    def test_05_version_bumped_to_3_4_1(self):
        for label, path in [("Mobile", MOBILE_GRADLE), ("TV", TV_GRADLE)]:
            with open(path, "r", encoding="utf-8") as f:
                gradle = f.read()
            self.assertIn("versionCode = 35", gradle, f"{label} build.gradle.kts must have versionCode = 35")
            self.assertIn('versionName = "3.4.1"', gradle, f'{label} build.gradle.kts must have versionName = "3.4.1"')

        with open(WEBOS_APPINFO, "r", encoding="utf-8") as f:
            appinfo = f.read()
        self.assertIn('"3.4.1"', appinfo, "LG webOS appinfo.json must have version 3.4.1")


if __name__ == "__main__":
    unittest.main()
