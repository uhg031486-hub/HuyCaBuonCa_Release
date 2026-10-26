// Dữ liệu phim và truyền hình chất lượng điện ảnh cho Huy Cá Cinema
export const FEATURED_MOVIES = [
  {
    id: "dune-2",
    title: "Dune: Hành Tinh Cát - Phần 2",
    originalTitle: "Dune: Part Two",
    backdrop: "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1920&q=80",
    poster: "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=600&q=80",
    imdb: "8.6",
    year: "2024",
    duration: "2h 46m",
    quality: "4K ULTRA HD",
    audio: "Thuyết Minh VIP",
    category: "Khoa Học Viễn Tưởng",
    tags: ["Chiếu Rạp", "Bom Tấn", "IMDb Cao"],
    overview: "Paul Atreides hợp lực cùng Chani và tộc người Fremen để thực hiện cuộc báo thù đẫm máu nhằm vào những kẻ đã hủy hoại gia tộc anh, đồng thời đối mặt với lựa chọn giữa tình yêu của đời mình và số phận của toàn vũ trụ.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    director: "Denis Villeneuve",
    cast: ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson", "Javier Bardem"],
    episodes: [
      { id: 1, name: "Bản Chiếu Rạp 4K", url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" }
    ]
  },
  {
    id: "oppenheimer",
    title: "Oppenheimer: Cha Đẻ Bom Nguyên Tử",
    originalTitle: "Oppenheimer",
    backdrop: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=1920&q=80",
    poster: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80",
    imdb: "8.9",
    year: "2023",
    duration: "3h 00m",
    quality: "4K ULTRA HD",
    audio: "Vietsub & Lồng Tiếng",
    category: "Lịch Sử / Tâm Lý",
    tags: ["Đoạt Giải Oscar", "Kinh Điển"],
    overview: "Câu chuyện lịch sử đầy kịch tính về cuộc đời của nhà vật lý lý thuyết J. Robert Oppenheimer, người lãnh đạo Dự án Manhattan phát triển vũ khí hạt nhân đầu tiên trong Thế chiến thứ hai, thay đổi vĩnh viễn vận mệnh nhân loại.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    director: "Christopher Nolan",
    cast: ["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr."],
    episodes: [
      { id: 1, name: "Bản Hoàn Chỉnh 4K", url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4" }
    ]
  },
  {
    id: "interstellar",
    title: "Hố Đen Tử Thần",
    originalTitle: "Interstellar",
    backdrop: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1920&q=80",
    poster: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
    imdb: "8.7",
    year: "2014",
    duration: "2h 49m",
    quality: "4K ULTRA HD",
    audio: "Thuyết Minh Cực Chuẩn",
    category: "Phiêu Lưu Không Gian",
    tags: ["Kiệt Tác", "Top 100 IMDb"],
    overview: "Khi Trái Đất dần cạn kiệt tài nguyên sống, một nhóm nhà thám hiểm dũng cảm sử dụng lỗ sâu mới được phát hiện trong không gian để vượt qua các giới hạn du hành vũ trụ của loài người, tìm kiếm một mái nhà mới giữa những vì sao.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
    director: "Christopher Nolan",
    cast: ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine"],
    episodes: [
      { id: 1, name: "Bản Phim Đầy Đủ", url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4" }
    ]
  }
];

export const CATEGORIES = [
  "Tất Cả",
  "Phim Chiếu Rạp",
  "Phim Bộ Hot",
  "Hành Động",
  "Khoa Học Viễn Tưởng",
  "Kinh Dị & Giật Gân",
  "Anime Đỉnh Cao",
  "Tiểu Kịch ReelShort",
  "Truyền Hình Thể Thao"
];

export const TRENDING_MOVIES = [
  {
    id: "avatar-3",
    title: "Avatar: Dòng Chảy Của Nước",
    originalTitle: "Avatar: The Way of Water",
    poster: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1920&q=80",
    imdb: "7.8",
    year: "2024",
    quality: "4K HDR",
    audio: "Thuyết Minh",
    category: "Viễn Tưởng",
    overview: "Jake Sully cùng Neytiri phải rời khỏi tổ ấm rừng xanh để tìm nơi ẩn náu tại vùng biển của tộc người Metkayina, chuẩn bị cho cuộc chiến sinh tử chống lại sự trở lại của loài người.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
  },
  {
    id: "cyberpunk-2099",
    title: "Cyberpunk: Thành Phố Đêm",
    originalTitle: "Cyberpunk: Edgerunners",
    poster: "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1920&q=80",
    imdb: "8.3",
    year: "2024",
    quality: "4K",
    audio: "Vietsub",
    category: "Anime Đỉnh Cao",
    overview: "Giữa thành phố tương lai bị ám ảnh bởi công nghệ và biến đổi cơ thể, một cậu thiếu niên đường phố tìm cách sống sót bằng cách trở thành một edgerunner - một lính đánh thuê ngoài vòng pháp luật.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"
  },
  {
    id: "john-wick-4",
    title: "Sát Thủ John Wick: Chương 4",
    originalTitle: "John Wick: Chapter 4",
    poster: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=1920&q=80",
    imdb: "7.7",
    year: "2023",
    quality: "Full HD",
    audio: "Thuyết Minh",
    category: "Hành Động",
    overview: "John Wick phát hiện ra con đường đánh bại Hội Đồng Tối Cao. Nhưng trước khi có thể giành lại tự do, anh phải đối đầu với một kẻ thù mới đầy quyền lực và những liên minh toàn cầu.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
  },
  {
    id: "blade-runner-2049",
    title: "Tội Phạm Nhân Bản 2049",
    originalTitle: "Blade Runner 2049",
    poster: "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?auto=format&fit=crop&w=1920&q=80",
    imdb: "8.0",
    year: "2024",
    quality: "4K HDR",
    audio: "Thuyết Minh",
    category: "Khoa Học Viễn Tưởng",
    overview: "Sĩ quan cảnh sát K của Los Angeles phát hiện một bí mật chôn giấu từ lâu có nguy cơ đẩy xã hội loài người vào sự hỗn loạn tột cùng.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4"
  },
  {
    id: "batman-dark-knight",
    title: "Kỵ Sĩ Bóng Đêm",
    originalTitle: "The Dark Knight",
    poster: "https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1509281373149-e957c6296406?auto=format&fit=crop&w=1920&q=80",
    imdb: "9.0",
    year: "2023",
    quality: "4K",
    audio: "Lồng Tiếng",
    category: "Hành Động",
    overview: "Khi mối đe dọa Joker tàn phá thành phố Gotham, Batman phải chấp nhận những thử thách tâm lý và thể chất lớn nhất đời mình để đối đầu với cái ác.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4"
  },
  {
    id: "spiderman-spiderverse",
    title: "Người Nhện: Du Hành Vũ Trụ Nhện",
    originalTitle: "Across the Spider-Verse",
    poster: "https://images.unsplash.com/photo-1635805737707-575885ab0820?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1635805737707-575885ab0820?auto=format&fit=crop&w=1920&q=80",
    imdb: "8.7",
    year: "2024",
    quality: "4K",
    audio: "Thuyết Minh VIP",
    category: "Anime & Hoạt Hình",
    overview: "Miles Morales được đẩy qua Đa vũ trụ, nơi cậu gặp gỡ một đội ngũ Người Nhện có nhiệm vụ bảo vệ sự tồn vong của thực tại.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4"
  }
];

export const LATEST_SERIES = [
  {
    id: "house-of-dragon",
    title: "Gia Tộc Rồng - Mùa 2",
    originalTitle: "House of the Dragon Season 2",
    poster: "https://images.unsplash.com/photo-1514539079130-25950c84af65?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1514539079130-25950c84af65?auto=format&fit=crop&w=1920&q=80",
    imdb: "8.5",
    year: "2024",
    quality: "4K ULTRA HD",
    audio: "Tập 8/8 Thuyết Minh",
    category: "Phim Bộ Hot",
    overview: "Cuộc nội chiến đẫm máu Vũ Điệu Của Bầy Rồng bùng nổ giữa phe Đen của Nữ vương Rhaenyra Targaryen và phe Xanh của Vua Aegon II.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
  },
  {
    id: "shogun-2024",
    title: "Shōgun: Tướng Quân",
    originalTitle: "Shōgun FX",
    poster: "https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=1920&q=80",
    imdb: "8.8",
    year: "2024",
    quality: "4K ULTRA HD",
    audio: "Trọn Bộ 10 Tập",
    category: "Phim Bộ Hot",
    overview: "Tại Nhật Bản năm 1600, Lãnh chúa Yoshii Toranaga chiến đấu giành quyền sinh tồn khi các kẻ thù trong Hội đồng Nhiếp chính hợp lực chống lại ông.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
  },
  {
    id: "fallout-series",
    title: "Fallout: Tận Thế Hạt Nhân",
    originalTitle: "Fallout",
    poster: "https://images.unsplash.com/photo-1563089145-599997674d42?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1563089145-599997674d42?auto=format&fit=crop&w=1920&q=80",
    imdb: "8.4",
    year: "2024",
    quality: "4K",
    audio: "Vietsub & Thuyết Minh",
    category: "Phim Bộ Hot",
    overview: "200 năm sau thảm họa hạt nhân, một cư dân hiền lành của Hầm Trú Ẩn buộc phải rời khỏi sự an toàn bên dưới lòng đất để khám phá vùng đất hoang Los Angeles.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
  },
  {
    id: "stranger-things-5",
    title: "Cậu Bé Mất Tích - Mùa Cuối",
    originalTitle: "Stranger Things Season 5",
    poster: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80",
    backdrop: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=1920&q=80",
    imdb: "8.7",
    year: "2024",
    quality: "4K",
    audio: "Lồng Tiếng",
    category: "Phim Bộ Hot",
    overview: "Các cô cậu thiếu niên thị trấn Hawkins bước vào trận chiến định đoạt cuối cùng chống lại thế lực tà ác Vecna và Thế Giới Ngược.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
  }
];

export const SHORT_DRAMAS = [
  {
    id: "reelshort-alpha-wolf",
    title: "Định Mệnh Của Alpha: Tình Yêu Cấm Đoán",
    platform: "ReelShort Âu Mỹ",
    poster: "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=600&q=80",
    quality: "HD 60fps",
    audio: "Vietsub AI Siêu Chuẩn",
    episodesCount: "82 Tập",
    overview: "Nữ chính bị gia đình chối bỏ bất ngờ phát hiện định mệnh hôn phối của mình là vị Thủ lĩnh Alpha quyền năng và lạnh lùng nhất lục địa.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
  },
  {
    id: "dramabox-billionaire",
    title: "Tổng Tài Ẩn Danh: Cuộc Báo Thù Hoàn Hảo",
    platform: "DramaBox",
    poster: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80",
    quality: "Full HD",
    audio: "Lồng Tiếng VIP",
    episodesCount: "95 Tập",
    overview: "Ẩn mình làm một tài xế quèn suốt 3 năm để tìm lại danh tính và đòi lại đế chế nghìn tỷ bị chính anh trai hãm hại cướp đoạt.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"
  },
  {
    id: "ai-cinema-cyber-romance",
    title: "AI Cinema: Tình Yêu Trong Chiều Không Gian Ảo",
    platform: "AI Cinema Châu Âu",
    poster: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80",
    quality: "4K AI Generated",
    audio: "Thuyết Minh Đa Ngôn Ngữ",
    episodesCount: "50 Tập",
    overview: "Bộ phim ngắn do trí tuệ nhân tạo thế hệ mới diễn xuất và đạo diễn hoàn toàn, lấy bối cảnh London năm 2150 khi robot và con người hòa quyện cảm xúc.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4"
  },
  {
    id: "shortmax-reborn-queen",
    title: "Trọng Sinh Thành Nữ Vương Bất Bại",
    platform: "ShortMax",
    poster: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80",
    quality: "Full HD",
    audio: "Vietsub Siêu Nhanh",
    episodesCount: "68 Tập",
    overview: "Tỉnh lại sau cái chết tức tưởi ở kiếp trước, cô quyết định tự tay xoay chuyển định mệnh và vạch trần bộ mặt giả nhân giả nghĩa của gia đình hào môn.",
    videoUrl: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4"
  }
];

export const TV_CHANNELS = [
  {
    id: "true-premier-1",
    name: "True Premier Football HD 1",
    group: "Ngoại Hạng Anh 4K",
    logo: "./logos/true_premier_1.svg",
    quality: "FHD 50FPS",
    status: "ĐANG TRỰC TIẾP",
    currentShow: "Trực Tiếp: Giải Ngoại Hạng Anh EPL",
    streamUrl: "https://amg00378-amg00378c4-freelivesports-emea-5637.playouts.now.amagi.tv/playlist.m3u8",
    isLiveTv: true
  },
  {
    id: "true-premier-2",
    name: "True Premier Football HD 2",
    group: "Ngoại Hạng Anh 4K",
    logo: "./logos/true_premier_2.svg",
    quality: "FHD 50FPS",
    status: "ĐANG TRỰC TIẾP",
    currentShow: "Trực Tiếp: Tâm Điểm Bóng Đá Châu Âu",
    streamUrl: "https://amg26268-amg26268c14-freelivesports-emea-10267.playouts.now.amagi.tv/playlist.m3u8",
    isLiveTv: true
  },
  {
    id: "bein-sports-1",
    name: "beIN SPORTS 1 HD",
    group: "Thể Thao Quốc Tế",
    logo: "./logos/bein_sports_1.svg",
    quality: "FHD 60FPS",
    status: "ĐANG PHÁT",
    currentShow: "Champions League & La Liga Đỉnh Cao",
    streamUrl: "https://bein-xtra-bein.amagi.tv/playlist.m3u8",
    isLiveTv: true
  },
  {
    id: "sky-sports-pl",
    name: "Sky Sports Premier League",
    group: "Thể Thao Quốc Tế",
    logo: "./logos/sky_sports_pl.svg",
    quality: "1080p Crystal",
    status: "LIVE STUDIO",
    currentShow: "Super Sunday Matchday Studio",
    streamUrl: "https://skynewsau-live-premium.akamaized.net/hls/live/2105307/foxsportsnews/master.m3u8",
    isLiveTv: true
  },
  {
    id: "vtv1-hd",
    name: "VTV1 HD Thời Sự",
    group: "Truyền Hình Việt Nam",
    logo: "./logos/vtv1.png",
    quality: "Full HD",
    status: "TRỰC TIẾP",
    currentShow: "Thời Sự & Chính Luận VTV1",
    streamUrl: "https://vtvgolivepre-vtv02.vtvdigital.vn/hls/vtv/live/vtv1__vtv1080p-h264/index.m3u8",
    isLiveTv: true
  },
  {
    id: "vtv3-hd",
    name: "VTV3 HD Giải Trí",
    group: "Truyền Hình Việt Nam",
    logo: "./logos/vtv3.png",
    quality: "Full HD",
    status: "TRỰC TIẾP",
    currentShow: "Giải Trí, Gameshow & Điện Ảnh",
    streamUrl: "https://vtvgolivepre-vtv02.vtvdigital.vn/hls/vtv/live/vtv3__vtv1080p-h264/index.m3u8",
    isLiveTv: true
  }
];
