import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

test_channels = [
    ("HTVC Thể Thao", "https://vips-livecdn.fptplay.net/live/media/htvthethao/live247-hls-avc/index.m3u8"),
    ("VTV6 Thể Thao (FPT)", "https://vips-livecdn.fptplay.net/live/media/vtv6/live247-hls-avc/index.m3u8"),
    ("Canal+ Sport SK (Ngoại Hạng Anh)", "http://rpprod.hbbtv.cdn.cra.cz:8080/hbbTV/cme-sk-canal-plus-sport/live_fullhd?offsetSeconds=0"),
    ("Canal+ Sport 2 SK", "http://rpprod.hbbtv.cdn.cra.cz:8080/hbbTV/cme-sk-canal-plus-sport2/live_fullhd?offsetSeconds=0"),
    ("beIN SPORTS XTRA", "https://bein-xtra-bein.amagi.tv/playlist.m3u8"),
    ("CBS Sports Golazo (Cúp C1 / Serie A)", "https://dai.google.com/linear/hls/event/7f3Wv6f7QEKfQna22jHqLQ/master.m3u8"),
    ("FIFA+ Live", "https://d2w9q46ikgrcwx.cloudfront.net/v1/master/3722c60a815c199d9c0ef36c5b73da68a62b09d1/cc-of5cbk3sav3w5/v1/sysdata_s_p_a_fifa_7/samsungheadend_us/latest/main/hls/playlist.m3u8"),
    ("Eurosport Live", "https://drk6xq0vhn.gpcdn.net/live/euro_sports_hd_abr/index.m3u8"),
    ("ESPN 2 Latin America", "https://barinaslive1.boldmss.com/ESPN_2/ESPN_2.isml/ESPN_2.m3u8"),
    ("Futbol TV 1080p", "http://stream3.cinerama.uz/1010/tracks-v1a1/mono.m3u8"),
    ("Fubo Sports Network", "https://dnf08l6u6uxnz.cloudfront.net/master.m3u8"),
    ("Red Bull TV HD", "https://rbmn-live.akamaized.net/hls/live/590964/BoRB-AT/master.m3u8"),
    ("Rally TV 1080p", "https://rally-tv-live.akamaized.net/hls/live/2117704/RallyTV-Pri/master.m3u8")
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for name, url in test_channels:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = resp.read(600).decode('utf-8', errors='ignore')
            lines = [l.strip() for l in data.splitlines() if l.strip()]
            print(f"=== {name} ===")
            print(f"URL: {url}")
            print(f"Status: {resp.status}, Content-Type: {resp.headers.get('Content-Type')}")
            for l in lines[:5]:
                print(f"  {l}")
            print()
    except Exception as e:
        print(f"=== {name} === ERROR: {e}\n")
