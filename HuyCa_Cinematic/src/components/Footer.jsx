import React from 'react';
import { Film, ShieldCheck, Tv, Sparkles, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="mt-16 sm:mt-24 bg-[#070A0F] border-t border-white/10 text-gray-400 py-12 sm:py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          
          {/* Col 1: Brand */}
          <div className="space-y-4 md:col-span-2">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#E50914] to-[#990000] p-0.5 shadow-neon-red flex items-center justify-center">
                <img src="./logo.png" alt="Logo" className="w-full h-full object-cover rounded-[10px]" />
              </div>
              <span className="text-xl font-black text-white tracking-wider">
                HUY CÁ <span className="text-[#E50914]">CINEMA</span>
              </span>
            </div>
            <p className="text-sm text-gray-400 max-w-md leading-relaxed">
              Trải nghiệm điện ảnh đỉnh cao chuẩn Hollywood. Tốc độ truyền tải siêu tốc, âm thanh vòm sống động và kho tàng phim bom tấn 4K không giới hạn.
            </p>
            <div className="flex items-center gap-4 text-xs font-semibold text-gray-300">
              <span className="flex items-center gap-1.5"><ShieldCheck className="w-4 h-4 text-[#F5C518]" /> 100% An Toàn & Bảo Mật</span>
              <span className="flex items-center gap-1.5"><Sparkles className="w-4 h-4 text-[#E50914]" /> Chất Lượng 4K HDR</span>
            </div>
          </div>

          {/* Col 2: Danh Mục */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">Khám Phá Phim</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#movies" className="hover:text-white transition-colors">Phim Chiếu Rạp Mới Nhất</a></li>
              <li><a href="#series" className="hover:text-white transition-colors">Phim Bộ Độc Quyền VIP</a></li>
              <li><a href="#anime" className="hover:text-white transition-colors">Anime Nhật Bản & 3D Trung Quốc</a></li>
              <li><a href="#short-drama" className="hover:text-white transition-colors">Kho Tiểu Kịch Đa Nền Tảng</a></li>
            </ul>
          </div>

          {/* Col 3: Hỗ Trợ & Thiết Bị */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">Tải App Đa Nền Tảng</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="/api/download?file=mobile" download="HuyCa_Mobile_v2.8.apk" className="text-[#F5C518] hover:underline font-semibold">⬇️ Huy Cá Mobile (Android APK)</a></li>
              <li><a href="/api/download?file=tv" download="HuyCa_TV_v2.8.apk" className="text-gray-300 hover:text-white transition-colors">⬇️ Huy Cá Android TV (APK TV)</a></li>
              <li><a href="/api/download?file=windows" download="HuyCa_Windows_v2.8.zip" className="text-gray-300 hover:text-white transition-colors">⬇️ Huy Cá Windows PC (.ZIP)</a></li>
              <li><a href="/api/download?file=lg" download="HuyCa_LG_webOS_v2.8.ipk" className="text-gray-300 hover:text-white transition-colors">⬇️ Huy Cá LG Smart TV (.IPK)</a></li>
            </ul>
          </div>

        </div>

        {/* Copyright Bar */}
        <div className="pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-400 gap-4">
          <p>© 2026 Huy Cá Cinema. Tất cả quyền được bảo lưu.</p>
          <div className="flex items-center gap-1">
            <span>Thiết kế & hoàn thiện với kỹ năng</span>
            <span className="text-white font-bold">UI-UX Pro Max</span>
            <span>đậm chất điện ảnh</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
