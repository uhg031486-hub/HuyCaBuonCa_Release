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

# Quy Chuẩn Kiểm Thử & Chặn Rác Bắt Buộc (Mandatory Quality Gate & Anti-Write-and-Dump Rule)

## 1. Nghiêm cấm tuyệt đối hành vi "Write-and-Dump":
- Agent KHÔNG ĐƯỢC PHÉP chỉnh sửa hoặc thêm mã nguồn rồi kết thúc phiên mà không qua kiểm thử thực tế.
- Tuyệt đối KHÔNG ĐƯỢC báo cáo "Đã xong", "Đã hoàn thành", "Đã sửa xong" nếu không đính kèm bằng chứng thực thi lệnh test/build thành công (Exit code = 0) từ terminal.
- Không được suy đoán kết quả (No hallucinated pass); mọi khẳng định hoàn thành phải có output log thực tế chứng minh.

## 2. Giao thức 5 bước thực thi tự động (Automated 5-Step Verification Protocol):
Mỗi khi người dùng yêu cầu tạo tính năng mới, sửa lỗi, hoặc refactor code, Agent bắt buộc phải tự động tuân thủ chu trình sau mà không cần người dùng phải nhắc lại:
1. **Viết Test trước (Test-First / TDD)**: Phân tích yêu cầu và viết bộ test case (Unit Test, Integration Test hoặc E2E Test) bao quát cả luồng xử lý chính lẫn các trường hợp biên (Edge Cases, chuỗi rỗng, dữ liệu sai định dạng, lỗi ngoại lệ).
2. **Xác nhận thất bại (Red Gate)**: Chạy lệnh kiểm thử trong terminal để xác nhận bài test đang thất bại do chưa có mã xử lý.
3. **Triển khai mã nguồn (Implementation)**: Viết mã nguồn vừa đủ, sạch và đúng chuẩn để đáp ứng các bài test.
4. **Vòng lặp tự sửa lỗi (Green Feedback Loop)**: Chạy lại lệnh test. Nếu xuất hiện lỗi hoặc test thất bại, tự động đọc log lỗi, phân tích nguyên nhân và sửa lại cho đến khi 100% test case chuyển sang màu xanh (`PASS`).
5. **Kích hoạt `verification-loop` toàn diện**: Chạy thử lệnh build/compile thực tế của dự án (`npm run build`, `./gradlew build`, `tsc --noEmit`, `pytest`). Chỉ khi build thành công và không còn lỗi kiểu dữ liệu (type error) thì mới được bàn giao cho người dùng kèm log kết quả.
