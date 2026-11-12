import json
import re
import urllib.parse
import urllib.request

CATEGORIES = {
    "ai_all": "phim AI trọn bộ thuyết minh",
    "ai_tutien": "phim hoạt hình AI tu tiên trọn bộ thuyết minh",
    "ai_manhwa": "phim AI xuyên không hệ thống trọn bộ thuyết minh",
    "ai_scifi": "phim khoa học viễn tưởng AI thuyết minh full",
    "short_full": "phim ngắn trọn bộ thuyết minh mới nhất",
}


def parse_minutes(dur_str: str) -> int:
    parts = [int(p) for p in dur_str.split(":") if p.isdigit()]
    if len(parts) == 3:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 2:
        return parts[0]
    return 0


def test_live_youtube_ai():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    }
    for cat, query in CATEGORIES.items():
        encoded = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded}&sp=EgIYAg%3D%3D&hl=vi&gl=VN"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
        assert m, f"Missing ytInitialData for category {cat}"
        data = json.loads(m.group(1))
        sections = (
            data.get("contents", {})
            .get("twoColumnSearchResultsRenderer", {})
            .get("primaryContents", {})
            .get("sectionListRenderer", {})
            .get("contents", [])
        )
        found = []
        for sec in sections:
            for item in sec.get("itemSectionRenderer", {}).get("contents", []):
                v = item.get("videoRenderer")
                if not v or "videoId" not in v:
                    continue
                vid = v["videoId"]
                title = v.get("title", {}).get("runs", [{}])[0].get("text", "")
                dur = v.get("lengthText", {}).get("simpleText", "")
                if not title or not dur:
                    continue
                mins = parse_minutes(dur)
                if mins >= 15:
                    found.append((vid, dur, title))
        assert len(found) >= 5, f"Expected >=5 long AI movies for {cat}, got {len(found)}"
        print(f"[PASS] Category {cat}: {len(found)} long movies found. Sample: {found[0][1]} | {found[0][2][:60]}")


if __name__ == "__main__":
    test_live_youtube_ai()
