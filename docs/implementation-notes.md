# Implementation decisions — 2026-10-23

MVP plan M0–M4 đã được thực thi trên nhánh feat/python-sdk-mvp. Repository bắt đầu không có Git/mã nguồn; người dùng duyệt kiến trúc, implementation plan và yêu cầu push repo private.

Các quyết định trong ledger:

1. Dùng nhánh feature ngay trong thư mục dự án mới được chỉ định thay vì tạo thêm checkout; chưa có mã/nhánh làm việc cũ cần tách. Nếu cần isolation bổ sung sau này có thể tạo worktree.
2. Git chưa có author identity, nên commit dùng author local Codex <codex@local>, không giả danh tài khoản người dùng. Nếu muốn author khác sẽ cần chỉnh lịch sử có chủ đích.
3. MVP folder baseUrl được ánh xạ Cloud từ saved requests create/remove/revoke trong chính collection; update dùng cùng biến baseUrl. Global thiếu biến. Nếu inference sai, folder_update routing cần sửa; URL vẫn configurable và chưa live verified.
4. Exception dùng thông báo cố định thay vì raw server message/body để tránh credential bị echo. Chi phí: ít chi tiết debug từ server; vẫn có HTTP status, operation và safe API code/request ID khi xác định được.
5. Base URL cho phép static path prefix để chạy gateway/Postman simulation qua HTTP transport thật; từ chối dot segments, percent escapes, backslash, embedded credentials/query/fragment. Chi phí nếu lựa chọn sai: cần siết validation URL; tests routing vẫn kiểm tra origin.

Giới hạn lifecycle: sync cleanup timeout áp dụng từng giai đoạn I/O; async cleanup có deadline tổng. Không bảo đảm có thể stop profile nếu start timeout hoặc response bị hỏng khiến client không nhận được ID thành công. Không retry ambiguous mutation.

Các quyết định này không làm thay đổi phạm vi:21 request MVP,104 request còn lại được ghi deferred/blocked; mobile,2FA và browser adapters thuộc các giai đoạn tiếp theo.

## Final review và các quyết định sau review

Reviewer độc lập đọc toàn nhánh 9f1b80d..ac555ee, tự chạy suite tại thời điểm review:144 pass/1 skip, cùng Ruff/mypy/coverage. Không có Critical; một finding strict-remove được reviewer gán Minor. Implementer đánh giá lại là lỗi contract Important vì public strict-mode mutation bỏ qua validation đã biết. Đã thêm check ids/permanently, chứng minh test thất bại trước sửa và pass sau sửa (sync/async); suite sau sửa146 pass/1 live skip. Không có minor còn hoãn.

Những hành vi reviewer đã cân nhắc, quyết định giữ nguyên:

| Hành vi | Quyết định và lý do | Chi phí / giới hạn |
|---|---|---|
| Sync polling/cleanup không forcibly interrupt cả thread | Giữ per-I/O timeouts và deadline giữa request như docs | Có thể vượt wall-clock deadline trong một I/O kéo dài |
| Cancellation lặp lại trong cleanup | Stop đã được thử, task được cancel/join để không rò task | Không hứa server nhận stop khi cancellation tiếp diễn |
| Start thành công server nhưng response fail client | Không tự suy đoán ownership/start lại | Người gọi phải kiểm tra status để phục hồi |
| switch_workspace không trả refresh token cùng client | Giữ chữ ký đã duyệt; auth.refresh trả tokens riêng | Caller muốn tokens phải gọi API refresh tường minh |
| with_token không dùng lại injected sessions/service tokens | Client mới độc lập theo spec | Caller phải cấu hình session custom cho client mới nếu cần |
| Full update cho phép bỏ field trong mode thường | Không suy đoán server yêu cầu strict trong non-strict; payload đầy đủ vẫn biểu diễn được | Có thể bị vendor reject; chưa live verified |
| Một số response data dùng dict và giữ extra fields | Theo scope MVP, tránh khóa schema sai khi chỉ có template | Ít typing hơn cho những response này |
| Success data có thể chứa credential | Ứng dụng cần đọc token/proxy data; không log mặc định | Caller phải bảo vệ dữ liệu khi tự log/serialize |
| Metas không retry | Chọn chính sách bảo thủ | Caller xử lý transient error thủ công |
| Pagination đầy trang ở offset10000 báo giới hạn | Giữ để không hứa đọc hết dữ liệu | Caller cần filter hẹp hơn |
| Không có raw-response accessor public | Giao diện MVP giữ safe metadata, không phát hành raw accessor thiếu chính sách redaction | Debug server response hạn chế |
| Live API/TLS/vendor-runtime chưa xác minh | Không dùng token thật khi chỉ có phép nghiên cứu/triển khai | Cần live smoke opt-in trước cam kết vận hành |

Chi phí của strict-remove fix: chỉ mode strict=True bỏ field bị từ chối sớm; gửi permanently=False vẫn giữ nguyên và được phép qua HTTP. Có test chứng minh không phát network khi thiếu field.
