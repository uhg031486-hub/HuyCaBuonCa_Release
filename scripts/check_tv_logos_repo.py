import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

test_channels = [
    ("united-states", "abc-news-live"),
    ("united-states", "cbs-news"),
    ("united-states", "nbc-news-now"),
    ("united-states", "bloomberg-tv"),
    ("united-states", "cnbc"),
    ("united-states", "cartoonito"),
    ("united-states", "warner-tv"),
    ("united-kingdom", "al-jazeera-english"),
    ("united-kingdom", "bbc-news"),
    ("united-kingdom", "sky-sports-premier-league"),
    ("united-kingdom", "sky-sports-main-event"),
    ("united-kingdom", "tnt-sports-1"),
    ("france", "france-24-en"),
    ("france", "euronews-en"),
    ("germany", "dw-english"),
    ("japan", "nhk-world-japan"),
    ("singapore", "cna"),
    ("south-korea", "arirang-tv"),
    ("south-korea", "mbc"),
    ("south-korea", "tv-chosun"),
    ("south-korea", "tvn"),
    ("china", "cctv-2"),
    ("qatar", "bein-sports-1-en"),
    ("thailand", "true-premier-football-1"),
    ("vietnam", "htv-the-thao"),
    ("vietnam", "htv-7"),
    ("vietnam", "htv-9")
]

print("Checking tv-logo/tv-logos GitHub repository...")
for country, slug in test_channels:
    url = f"https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/{country}/{slug}.png"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=3) as res:
            print(f"  ✔ {country}/{slug}.png -> {res.status}")
    except Exception as e:
        print(f"  ❌ {country}/{slug}.png -> {e}")
