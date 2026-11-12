import os
import json
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_UPDATER = os.path.join(
    ROOT_DIR, "HuyCaBuonCa_Mobile", "app", "src", "main", "java", "com", "huycabuonca", "mobile", "util", "AppUpdateManager.kt"
)
TV_UPDATER = os.path.join(
    ROOT_DIR, "HuyCaBuonCa_TV", "app", "src", "main", "java", "com", "huycabuonca", "tv", "util", "AppUpdateManager.kt"
)
WEB_WORKER = os.path.join(ROOT_DIR, "HuyCa_Web", "_worker.js")
WEB_VERSION = os.path.join(ROOT_DIR, "HuyCa_Web", "version.json")
ROOT_VERSION = os.path.join(ROOT_DIR, "version.json")


class TestAndroidUpdaterTDD(unittest.TestCase):

    def test_01_mobile_and_tv_updater_do_not_use_broken_receiver_not_exported(self):
        """Android 13/14+ blocks DownloadManager broadcasts when registered with RECEIVER_NOT_EXPORTED."""
        for path in [MOBILE_UPDATER, TV_UPDATER]:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.assertNotIn(
                "Context.RECEIVER_NOT_EXPORTED",
                code,
                f"{os.path.basename(path)} must NOT use RECEIVER_NOT_EXPORTED for system broadcasts!"
            )

    def test_02_direct_okhttp_streaming_progress_downloader(self):
        """Both Mobile and TV AppUpdateManager must stream APK directly via OkHttp with live progress UI (0-100%)."""
        for path in [MOBILE_UPDATER, TV_UPDATER]:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.assertIn("ProgressBar", code, f"{path} should display a live ProgressBar during APK download")
            self.assertIn("FileOutputStream", code, f"{path} should write APK stream directly via FileOutputStream")
            self.assertIn("https://huyca.pages.dev/version.json", code, f"{path} should include Cloudflare Pages mirror for version.json")

    def test_03_unknown_app_sources_permission_handling(self):
        """Both Mobile and TV AppUpdateManager must check canRequestPackageInstalls() on Android 8.0+ (API 26+) and remember pending APK."""
        for path in [MOBILE_UPDATER, TV_UPDATER]:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.assertIn("canRequestPackageInstalls", code, f"{path} must check packageManager.canRequestPackageInstalls()")
            self.assertIn("ACTION_MANAGE_UNKNOWN_APP_SOURCES", code, f"{path} must guide user to Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES if needed")
            self.assertIn("onActivityResume", code, f"{path} must expose onActivityResume to auto-resume pending APK install after permission grant")

    def test_04_web_version_json_and_worker_redirect(self):
        """HuyCa_Web/version.json must exist and match root version.json, and _worker.js /api/download must redirect reliably."""
        self.assertTrue(os.path.exists(WEB_VERSION), "HuyCa_Web/version.json must exist as a fast CDN mirror")
        with open(WEB_VERSION, "r", encoding="utf-8") as f:
            web_ver = json.load(f)
        with open(ROOT_VERSION, "r", encoding="utf-8") as f:
            root_ver = json.load(f)
        self.assertEqual(web_ver["versionCode"], root_ver["versionCode"])
        self.assertEqual(web_ver["versionName"], root_ver["versionName"])
        self.assertGreaterEqual(root_ver["versionCode"], 36, "Version code should be bumped to >= 36 (v3.4.2)")


if __name__ == "__main__":
    unittest.main()
