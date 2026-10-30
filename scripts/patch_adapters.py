import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. TV MovieAdapter
tv_adapter = "HuyCaBuonCa_TV/app/src/main/java/com/huycabuonca/tv/ui/adapter/MovieAdapter.kt"
with open(tv_adapter, "r", encoding="utf-8") as f:
    c_tv = f.read().replace("\r\n", "\n")

old_block = """            val defaultTvLogo = "file:///android_asset/logos/vtv1.png"
            val finalImgUrl = if (item.source == MovieSource.XEMTIVI && imgUrl.isEmpty()) {
                defaultTvLogo
            } else {
                imgUrl
            }

            Glide.with(binding.imgPoster.context)
                .load(finalImgUrl)
                .transition(DrawableTransitionOptions.withCrossFade())
                .placeholder(R.drawable.bg_focus_card)
                .error(if (item.source == MovieSource.XEMTIVI) R.drawable.tv_banner else R.drawable.bg_btn_secondary)
                .into(binding.imgPoster)"""

new_block = """            val defaultTvLogo = "file:///android_asset/logos/tv_default_premium.png"
            val finalImgUrl = if (item.source == MovieSource.XEMTIVI) {
                if (imgUrl.isNotEmpty()) imgUrl else defaultTvLogo
            } else {
                imgUrl
            }

            Glide.with(binding.imgPoster.context)
                .load(finalImgUrl)
                .transition(DrawableTransitionOptions.withCrossFade())
                .placeholder(R.drawable.bg_focus_card)
                .error(if (item.source == MovieSource.XEMTIVI) R.mipmap.ic_launcher else R.drawable.bg_btn_secondary)
                .into(binding.imgPoster)"""

if old_block in c_tv:
    c_tv = c_tv.replace(old_block, new_block)
    with open(tv_adapter, "w", encoding="utf-8", newline="\n") as f:
        f.write(c_tv)
    print("✔ Đã cập nhật TV MovieAdapter.kt")
else:
    print("❌ Không tìm thấy block trong TV MovieAdapter.kt")

# 2. Mobile MovieAdapter
mobile_adapter = "HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/adapter/MovieAdapter.kt"
with open(mobile_adapter, "r", encoding="utf-8") as f:
    c_mb = f.read().replace("\r\n", "\n")

if old_block in c_mb:
    c_mb = c_mb.replace(old_block, new_block)
    with open(mobile_adapter, "w", encoding="utf-8", newline="\n") as f:
        f.write(c_mb)
    print("✔ Đã cập nhật Mobile MovieAdapter.kt")
else:
    print("❌ Không tìm thấy block trong Mobile MovieAdapter.kt")

# 3. Mobile QuickChannelAdapter
quick_adapter = "HuyCaBuonCa_Mobile/app/src/main/java/com/huycabuonca/mobile/ui/adapter/QuickChannelAdapter.kt"
with open(quick_adapter, "r", encoding="utf-8") as f:
    c_qc = f.read().replace("\r\n", "\n")

qc_old = """        val defaultTvLogo = "file:///android_asset/logos/vtv1.png"
        Glide.with(holder.itemView.context)
            .load(if (!ch.logo.isNullOrEmpty()) ch.logo else defaultTvLogo)
            .placeholder(R.drawable.bg_focus_card)
            .error(R.drawable.bg_btn_secondary)
            .into(holder.imgLogo)"""

qc_new = """        val resolvedLogo = com.huycabuonca.mobile.api.MovieRepository.resolveChannelLogo(ch)
        Glide.with(holder.itemView.context)
            .load(resolvedLogo)
            .placeholder(R.drawable.bg_focus_card)
            .error(R.mipmap.ic_launcher)
            .into(holder.imgLogo)"""

if qc_old in c_qc:
    c_qc = c_qc.replace(qc_old, qc_new)
    with open(quick_adapter, "w", encoding="utf-8", newline="\n") as f:
        f.write(c_qc)
    print("✔ Đã cập nhật Mobile QuickChannelAdapter.kt")
else:
    print("❌ Không tìm thấy block trong QuickChannelAdapter.kt")

print("Hoàn tất cập nhật các Adapter!")
