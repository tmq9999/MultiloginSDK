# Sử dụng SDK

## Clients và cấu hình

`MultiloginClient` dùng `with`; `AsyncMultiloginClient` dùng `async with`. Mỗi resource có cùng method và request model; async methods dùng await. `session` và `iter_profiles` trả async context manager/iterator ở client async.

`ClientConfig` có cloud_url, launcher_url, cookies_url, timeout, start_timeout, strict_mode, max_retries, retry_budget, launcher_ca. URL mặc định là Cloud https://api.multilogin.com, Launcher https://launcher.mlx.yt:45001, cookies https://cookies.multilogin.com. URL custom có thể có static path prefix để dùng gateway/simulation, không có credential/query/fragment. Token mặc định gửi tới cả ba service đã cấu hình; dùng service_tokens để override riêng. Chỉ cấu hình URL mà bạn tin tưởng nhận token.

Mặc định TLS verification bật. Với Launcher dùng CA riêng, truyền SSLContext đã load CA, giữ CERT_REQUIRED và check_hostname=True. Không tắt verification để né lỗi chứng chỉ. Trust_env=False ở session do SDK tạo; nếu cần proxy môi trường hãy inject httpx sessions đã cấu hình. Sessions do người gọi inject vẫn thuộc người gọi và cần tự đóng; SDK không dùng headers/cookies/auth mặc định của injected session để tránh credential bị gửi sai service.

Timeout: connect10s, read/write/pool30s. Start/quick read timeout120s, đổi bằng start_timeout. Polling có deadline riêng120s, interval1s. Async cleanup có timeout tổng10s; sync cleanup áp dụng10s mỗi giai đoạn I/O của httpx. Sync I/O không có cơ chế forcibly interrupt Python thread, nên deadline được kiểm tra giữa các request và dùng giới hạn I/O còn lại.

## Xác thực

Truyền token vào constructor, SDK không tự đọc env hoặc đăng nhập. Từ client không token có thể gọi `auth.sign_in(email,password)` hoặc `sign_in_with_hash(email,password_md5)`. Password được MD5 theo yêu cầu wire protocol; hash method không hash lần hai. Token và refresh_token trong response dùng SecretStr; truy cập bằng `.get_secret_value()`. Không print credential hoặc response thô.

`auth.automation_token('1w')` tạo token mới và có side effect. Thời hạn hợp lệ: 1h,3h,5h,16h,24h,48h,1w,2w,3w,1mo,no_exp. no_exp vẫn có thể bị revoke. Không có auto-renew.

`auth.refresh(email,refresh_token,workspace_id)` trả tokens mới. `client.switch_workspace(email=...,refresh_token=...,workspace_id=...)` gọi refresh rồi trả client mới độc lập; phải đóng cả client cũ và mới. Không đổi token của các request đang chạy. `with_token(token)` cũng tạo client mới với cùng config và sessions do client mới sở hữu.

## Payload

Models import từ `multilogin_sdk.models.profiles`, `.workspaces`, `.launcher`. Trường không truyền bị bỏ khỏi JSON. `UNSET` có thể dùng để loại bỏ một field khi truyền dictionary; False,0,'',[] vẫn gửi nguyên. Null bị từ chối nếu endpoint/model không khai báo nullable. Không dùng `model_construct`/`model_copy(update=...)` với input không tin cậy: chúng bỏ qua Pydantic validation.

Create/full update dùng parameters.proxy; partial update dùng proxy top-level. ISP proxy cần có host='' dù server bỏ qua giá trị, và create times=1. Nếu đang tắt proxy, cần parameters.flags.proxy_masking='custom' để bật. Không chuyển nested object giữa các model bằng suy đoán.

Partial update bỏ auto_update_core có thể làm server bật lại giá trị này. Gửi auto_update_core=False rõ ràng nếu muốn giữ core cũ; SDK không tự đọc/merge profile trước khi update.

Strict mode mặc định không gửi header. strict_mode=True gửi X-Strict-Mode:true và kiểm tra những trường strict đã xác nhận trong contract; không tự điền fingerprint custom. Trường hợp vendor yêu cầu thêm field chưa có trong collection vẫn có thể bị server từ chối.

## Kết quả và lỗi

Method trả ApiResponse với data typed, status envelope và http_status. Unknown response fields được giữ. HTTP non-2xx là HttpError dù body báo thành công. HTTP2xx + API error là ApiError. Envelope/payload sai là ProtocolError. Lỗi kết nối là TransportError; LauncherUnavailable nhắc kiểm tra desktop/agent.

Exception không chứa raw server message/body vì server có thể echo credential. Không log request/response body mặc định. Khi debug, xem operation và status_code; credential-bearing data chỉ được ứng dụng xử lý tường minh.

Retry mặc định tắt. Khi max_retries=2 chỉ read-only operations (search/list/status/version) được retry429/502/503/504 tối đa3 attempts, tuân Retry-After trong retry_budget30s. GET start/stop/tạo token không được retry. 401/403 và ambiguous network failure không retry. Polling tự quản deadline và không lồng retry.

## Browser và phiên bản

Launcher.start dùng /api/v2/profile/.../start; quick dùng /api/v3/profile/quick. data.port được kiểm tra và đổi từ chuỗi thập phân thành int1..65535. Không fallback sang v1 hoặc parse status.message làm port. Quick proxy nằm trong parameters.

Stealthfox chỉ hỗ trợ selenium theo collection. Regular start request không chứa browser_type nên caller cần biết loại profile; quick kiểm tra khi model biết loại browser. Mimic custom_start_urls có hạn chế khi truyền automation; nên mở URL bằng automation client sau khi kết nối. SDK MVP chỉ trả connection, không tự cài Selenium/Playwright.

`iter_profiles` theo limit1–100, offset0–10000. Trang rỗng/ngắn dừng iterator. Trang đầy ở trần offset ném PaginationLimitError; cần thu hẹp filter, không coi iterator đã đọc hết mọi profile.

Owned session không delete profile, chỉ stop ID trả về từ start thành công. Khi stop thất bại cùng lỗi ứng dụng, lỗi ứng dụng được giữ và có note cleanup cố định. Khi chỉ cleanup lỗi, lỗi cleanup được trả cho caller. Nếu start thành công trên server nhưng timeout/response malformed ở client, cần kiểm tra trạng thái tường minh.
