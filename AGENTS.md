# Quy Tắc Ngôn Ngữ (Language Rule)

- **Ngôn ngữ phản hồi mặc định**: Luôn luôn giao tiếp, trao đổi, trả lời và giải thích bằng **Tiếng Việt**.
- Giữ nguyên thuật ngữ chuyên ngành công nghệ thông tin, cú pháp code, tên biến, hàm, lớp, API và thư viện chuẩn bằng tiếng Anh để đảm bảo tính chính xác kỹ thuật.
- Khi tạo tài liệu hoặc chú thích theo yêu cầu của dự án, ưu tiên tiếng Việt trừ khi có yêu cầu cụ thể khác từ người dùng.

# Quy Tắc Phiên Bản & Rollback (Versioning & Rollback Rule)

- **Quy tắc đặt tên phiên bản**:
  - Mỗi khi nâng cấp tính năng hoặc sửa lỗi cho phiên bản mới, bắt buộc phải tăng số phiên bản: ví dụ `v1.0` -> `v1.1` -> `v1.2`...
  - Cập nhật đồng bộ `versionCode` (tăng +1) và `versionName` trong file `build.gradle.kts` của cả hai app (Mobile và TV).
  - Tên file xuất ra bắt buộc phải theo chuẩn thương hiệu duy nhất Huy Cá: `HuyCa_TV_v{X.Y}.apk`, `HuyCa_Mobile_v{X.Y}.apk`, `HuyCa_LG_webOS_v{X.Y}.ipk` và `HuyCa_Windows_v{X.Y}.zip`.
- **Lưu trữ mã nguồn & Khả năng Rollback**:
  - Không bao giờ xóa hoặc làm mất mã nguồn phiên bản cũ.
  - Sử dụng Git: Mỗi phiên bản mới được đóng gói bắt buộc phải được `git commit` kèm mô tả chi tiết và đánh dấu bằng Git Tag (`git tag -a v{X.Y}`).
  - Khi cần rollback, có thể kiểm tra danh sách tag bằng `git tag -l` và quay về ngay lập tức bằng `git checkout v{X.Y}`.
  - Giữ nguyên các file APK của các phiên bản trước đó để người dùng có thể cài đặt và đối chiếu bất kỳ lúc nào.
