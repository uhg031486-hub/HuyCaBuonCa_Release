import json
import hashlib
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load original channels
with open('HuyCaBuonCa_Mobile/app/src/main/assets/tv_channels.json', 'r', encoding='utf-8') as f:
    orig_channels = json.load(f)

print(f"Original channels count: {len(orig_channels)}")

# Filter out broken sports channels and dummy movie VODs in sports
bad_domains = ['watchtivo-8k.com', 'ciao-ott.net']
bad_groups = ['LIVE EVENTS 🔴', 'ASEAN HUYNDAI CUP 2026', 'THỂ THAO QUỐC TẾ', '⚽| Thể thao quốc tế']

cleaned_channels = []
for c in orig_channels:
    if c['group'] in bad_groups:
        continue
    if any(bd in c['url'] for bd in bad_domains):
        continue
    if 'id' not in c or not c['id']:
        c['id'] = 'tv_' + hashlib.md5(c['url'].encode('utf-8')).hexdigest()[:10]
    cleaned_channels.append(c)

print(f"Channels after removing old sports: {len(cleaned_channels)}")

# Curated High Quality Verified Sports Channels with explicit 'id'
sports_channels = [
    # --- BÓNG ĐÁ VIỆT NAM & ĐTQG ---
    {
        "id": "sports_vn_vtv6",
        "name": "VTV6 Thể Thao HD (FPT)",
        "group": "⚽ Bóng Đá & Thể Thao VN",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/VTV6_2013.svg/200px-VTV6_2013.svg.png",
        "url": "https://vips-livecdn.fptplay.net/live/media/vtv6/live247-hls-avc/index.m3u8"
    },
    {
        "id": "sports_vn_htvc_thethao",
        "name": "HTVC Thể Thao HD (FPT)",
        "group": "⚽ Bóng Đá & Thể Thao VN",
        "logo": "https://i.imgur.com/8QZ9q2P.png",
        "url": "https://vips-livecdn.fptplay.net/live/media/htvthethao/live247-hls-avc/index.m3u8"
    },
    {
        "id": "sports_vn_htv_thethao",
        "name": "HTV Thể Thao",
        "group": "⚽ Bóng Đá & Thể Thao VN",
        "logo": "https://i.imgur.com/8QZ9q2P.png",
        "url": "https://dethich.pw/htvthethao/index.m3u8"
    },
    {
        "id": "sports_vn_dongnai2",
        "name": "Đồng Nai 2 (Thể Thao & Giải Trí)",
        "group": "⚽ Bóng Đá & Thể Thao VN",
        "logo": "https://i.imgur.com/2sXv4cW.png",
        "url": "https://vtvgolive-ott3.vtvdigital.vn/live/dongnai2tv/chunklist_2.m3u8"
    },
    {
        "id": "sports_vn_thvl4",
        "name": "Vĩnh Long 4 Thể Thao",
        "group": "⚽ Bóng Đá & Thể Thao VN",
        "logo": "https://i.imgur.com/8QZ9q2P.png",
        "url": "https://dethich.pw/thvl4/index.m3u8"
    },

    # --- BÓNG ĐÁ QUỐC TẾ & CÚP C1 / UEFA ---
    {
        "id": "sports_intl_cbs_golazo",
        "name": "CBS Sports Golazo (Cúp C1 / Serie A)",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "https://dai.google.com/linear/hls/event/7f3Wv6f7QEKfQna22jHqLQ/master.m3u8"
    },
    {
        "id": "sports_intl_bein_xtra",
        "name": "beIN SPORTS XTRA HD",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "https://bein-xtra-bein.amagi.tv/playlist.m3u8"
    },
    {
        "id": "sports_intl_fifa_plus_live",
        "name": "FIFA+ Live HD (Trực Tiếp & World Cup)",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/h5TzG6a.png",
        "url": "https://d2w9q46ikgrcwx.cloudfront.net/v1/master/3722c60a815c199d9c0ef36c5b73da68a62b09d1/cc-of5cbk3sav3w5/v1/sysdata_s_p_a_fifa_7/samsungheadend_us/latest/main/hls/playlist.m3u8"
    },
    {
        "id": "sports_intl_fifa_plus_global",
        "name": "FIFA+ Global HD",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/h5TzG6a.png",
        "url": "https://jmp2.uk/plu-660c29b5aec9680008f5b4a4.m3u8"
    },
    {
        "id": "sports_intl_eurosport_live",
        "name": "Eurosport Live HD",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/yS7Jj4e.png",
        "url": "https://drk6xq0vhn.gpcdn.net/live/euro_sports_hd_abr/index.m3u8"
    },
    {
        "id": "sports_intl_eurosport_1",
        "name": "Eurosport 1 HD (1080p)",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/yS7Jj4e.png",
        "url": "http://57.128.210.196:8080/264/index.m3u8"
    },
    {
        "id": "sports_intl_eurosport_2",
        "name": "Eurosport 2 HD (1080p)",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/yS7Jj4e.png",
        "url": "http://57.128.210.196:8080/263/index.m3u8"
    },
    {
        "id": "sports_intl_cctv_football",
        "name": "CCTV-Storm Football (Bóng Đá 24/7)",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "http://38.75.136.137:98/gslb/dsdqpub/fyzq.m3u8?auth=testpub"
    },
    {
        "id": "sports_intl_tyc_sports",
        "name": "TyC Sports HD (Bóng Đá Nam Mỹ)",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "https://amg26268-amg26268c14-freelivesports-emea-10267.playouts.now.amagi.tv/ts-us-e2-n2/playlist/amg26268-sportsstudio-tycsports-freelivesportsemea/playlist.m3u8"
    },
    {
        "id": "sports_intl_lequipe",
        "name": "L'Equipe Live 1080p (Pháp)",
        "group": "⚽ Bóng Đá Quốc Tế & C1",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "https://dq37unyetkpcz.cloudfront.net/v1/master/3722c60a815c199d9c0ef36c5b73da68a62b09d1/cc-m04j89j7k5gtp/LEquipe_FR.m3u8"
    },

    # --- KÊNH THỂ THAO ESPN & FOX ---
    {
        "id": "sports_espn_usa",
        "name": "ESPN HD (United States)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "http://85.237.89.160:9590/usa-s/ESPN-HD/index.m3u8"
    },
    {
        "id": "sports_espn_2_usa",
        "name": "ESPN 2 HD (United States)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "http://85.237.89.160:9590/usa-s/ESPN-2-HD/index.m3u8"
    },
    {
        "id": "sports_espn_u",
        "name": "ESPNU HD",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "http://85.237.89.160:9590/usa-s/ESPN-U-HD/index.m3u8"
    },
    {
        "id": "sports_espn_latam_1",
        "name": "ESPN Latin America (1080p)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "https://barinaslive1.boldmss.com/ESPN/ESPN.isml/ESPN.m3u8"
    },
    {
        "id": "sports_espn_latam_2",
        "name": "ESPN 2 Latin America (1080p)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "https://barinaslive1.boldmss.com/ESPN_2/ESPN_2.isml/ESPN_2.m3u8"
    },
    {
        "id": "sports_espn_latam_3",
        "name": "ESPN 3 Latin America (1080p)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "https://barinaslive1.boldmss.com/ESPN_3/ESPN_3.isml/ESPN_3.m3u8"
    },
    {
        "id": "sports_espn_latam_4",
        "name": "ESPN 4 Latin America (1080p)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "https://barinaslive1.boldmss.com/ESPN_4/ESPN_4.isml/ESPN_4.m3u8"
    },
    {
        "id": "sports_espn_latam_5",
        "name": "ESPN 5 Latin America (1080p)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "https://barinaslive1.boldmss.com/ESPN_5/ESPN_5.isml/ESPN_5.m3u8"
    },
    {
        "id": "sports_espn_latam_6",
        "name": "ESPN 6 Latin America (1080p)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "https://barinaslive1.boldmss.com/ESPN_6/ESPN_6.isml/ESPN_6.m3u8"
    },
    {
        "id": "sports_espn_latam_7",
        "name": "ESPN 7 Latin America (1080p)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/t3cWJ3F.png",
        "url": "https://barinaslive1.boldmss.com/ESPN_7/ESPN_7.isml/ESPN_7.m3u8"
    },
    {
        "id": "sports_fox_sports_1",
        "name": "Fox Sports 1 (720p)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "http://85.237.89.160:9590/usa-s/FOX-SPORTS-1/index.m3u8"
    },
    {
        "id": "sports_fox_sports_news",
        "name": "Fox Sports News (1080p Akamai)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "https://skynewsau-live-premium.akamaized.net/hls/live/2105307/foxsportsnews/live_1080p.m3u8"
    },
    {
        "id": "sports_fubo_sports",
        "name": "Fubo Sports Network (1080p)",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "https://dnf08l6u6uxnz.cloudfront.net/master.m3u8"
    },
    {
        "id": "sports_eleven_1",
        "name": "Eleven Sports 1 HD",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "http://92.114.85.87:8002/play/a00e/index.m3u8"
    },
    {
        "id": "sports_eleven_2",
        "name": "Eleven Sports 2 HD",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "http://92.114.85.87:8002/play/a00f/index.m3u8"
    },
    {
        "id": "sports_eleven_3",
        "name": "Eleven Sports 3 HD",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "http://92.114.85.87:8002/play/a00g/index.m3u8"
    },
    {
        "id": "sports_eleven_4",
        "name": "Eleven Sports 4 HD",
        "group": "🏆 Kênh Thể Thao ESPN & FOX",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "http://92.114.85.87:8002/play/a00h/index.m3u8"
    },

    # --- ĐUA XE & MẠO HIỂM ---
    {
        "id": "sports_redbull_tv",
        "name": "Red Bull TV HD (Akamai)",
        "group": "🏎️ Đua Xe & Mạo Hiểm",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "https://rbmn-live.akamaized.net/hls/live/590964/BoRB-AT/master.m3u8"
    },
    {
        "id": "sports_rally_tv",
        "name": "Rally TV 1080p (WRC Trực Tiếp)",
        "group": "🏎️ Đua Xe & Mạo Hiểm",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "https://rally-tv-live.akamaized.net/hls/live/2117704/RallyTV-Pri/master.m3u8"
    },
    {
        "id": "sports_racer_select",
        "name": "RACER Select HD",
        "group": "🏎️ Đua Xe & Mạo Hiểm",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "https://amg00378-amg00378c4-freelivesports-emea-5637.playouts.now.amagi.tv/playlist.m3u8"
    },
    {
        "id": "sports_nhra_tv",
        "name": "NHRA TV HD (Đua Xe Tốc Độ)",
        "group": "🏎️ Đua Xe & Mạo Hiểm",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "https://d265y4sk8257lt.cloudfront.net/nh.m3u8"
    },

    # --- VÕ THUẬT & ĐỐI KHÁNG ---
    {
        "id": "sports_swerve_combat",
        "name": "Swerve Combat HD (MMA & Boxing)",
        "group": "🥊 Võ Thuật & Đối Kháng",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "https://linear-253.frequency.stream/mt/roku/253/hls/master/playlist.m3u8"
    },
    {
        "id": "sports_persiana_fight",
        "name": "Persiana Fight HD",
        "group": "🥊 Võ Thuật & Đối Kháng",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "https://fighthls.persiana.live/hls/stream.m3u8"
    },
    {
        "id": "sports_polsat_sport_fight",
        "name": "Polsat Sport Fight (1080p)",
        "group": "🥊 Võ Thuật & Đối Kháng",
        "logo": "https://i.imgur.com/4gW5V0G.png",
        "url": "http://57.128.210.196:8080/194/index.m3u8"
    },

    # --- BÓNG RỔ, QUẦN VỢT & KHÁC ---
    {
        "id": "sports_nba_tv",
        "name": "NBA TV HD (Bóng Rổ)",
        "group": "🏀 Bóng Rổ & Quần Vợt",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "http://23.237.104.106:8080/USA_NBA/index.m3u8"
    },
    {
        "id": "sports_nfl_network",
        "name": "NFL Network HD (Bóng Bầu Dục)",
        "group": "🏀 Bóng Rổ & Quần Vợt",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "http://198.58.104.90:8989/nfl/index.m3u8"
    },
    {
        "id": "sports_tennis_channel_2",
        "name": "Tennis Channel 2 HD",
        "group": "🏀 Bóng Rổ & Quần Vợt",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "https://mumbai-edge.smartplaytv.in/Tennis2/index.m3u8"
    },
    {
        "id": "sports_pga_tour",
        "name": "PGA Tour HD (Golf)",
        "group": "🏀 Bóng Rổ & Quần Vợt",
        "logo": "https://i.imgur.com/6E2hS6F.png",
        "url": "https://d11k1mnrgfposz.cloudfront.net/playlist.m3u8"
    }
]

# Put Sports channels right near the top after VTV
vtv_channels = [c for c in cleaned_channels if c['group'] == 'VTV']
other_channels = [c for c in cleaned_channels if c['group'] != 'VTV']

final_channels = vtv_channels + sports_channels + other_channels

print(f"Final total channels: {len(final_channels)}")
# Verify all channels have id
for c in final_channels:
    assert 'id' in c and c['id'], f"Missing id in channel: {c['name']}"

# Save to Mobile assets
with open('HuyCaBuonCa_Mobile/app/src/main/assets/tv_channels.json', 'w', encoding='utf-8') as f:
    json.dump(final_channels, f, ensure_ascii=False, indent=2)

# Save to TV assets
with open('HuyCaBuonCa_TV/app/src/main/assets/tv_channels.json', 'w', encoding='utf-8') as f:
    json.dump(final_channels, f, ensure_ascii=False, indent=2)

print("Successfully written to Mobile and TV assets with valid 'id' for every channel!")
