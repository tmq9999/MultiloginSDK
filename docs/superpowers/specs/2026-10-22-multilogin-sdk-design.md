# MultiloginSDK Python — đề xuất kiến trúc và lộ trình

Ngày: 2026-10-22. Trạng thái: người dùng duyệt ngày 2026-10-23; chưa triển khai.

## 1. Mục tiêu và cơ sở

Người dùng yêu cầu nghiên cứu collection Multilogin và lập kế hoạch xây SDK bằng Python. Dự án hiện là thư mục trống, chưa có Git repository. Mục tiêu đề xuất: thư viện Python tái sử dụng cho quản lý browser profile và cloud phone, có typing, giao diện sync/async, phân biệt các dịch vụ và lỗi rõ ràng.

Nguồn đã đọc bằng Postman CLI: workspace `fcb8367c-8eb4-4173-a511-2e151812fba7`, collection `46206122-78bf4173-0a22-4651-890d-b160177d47b1`. Audit đi kèm: `docs/research/2026-10-22-multilogin-api-audit.md`, gồm 125 request, mô tả, body template, tham số và cấu trúc response mẫu.

Chưa thực hiện request nghiệp vụ Multilogin, chưa xác nhận runtime, TLS Launcher, quota thực tế hay khả năng automation của tài khoản. Các lựa chọn công nghệ và API Python bên dưới là đề xuất; Python là lựa chọn người dùng đã xác nhận.

## 2. Các phương án

| Phương án | Ưu điểm | Chi phí / giới hạn |
|---|---|---|
| A. Resource client viết tay + bảng contract kiểm tra tự động (đề xuất) | Python dễ dùng, xử lý được khác biệt payload, retry và response từng operation | Cần duy trì mapping khi collection đổi |
| B. Sinh toàn bộ code từ collection | Có coverage ban đầu nhanh | Template không hợp lệ, request trùng, ví dụ mâu thuẫn khiến code sinh ra không đáng tin nếu thiếu bước chuẩn hóa |
| C. Wrapper request trả dict | Ít code, phù hợp prototype | Người gọi phải tự xử lý mọi khác biệt; thiếu typing và lifecycle |

Chọn A, dùng collection làm đầu vào kiểm tra coverage và fixture đã làm sạch. Chưa tạo thêm OpenAPI song song trong MVP vì sẽ có thêm một contract cần đồng bộ.

## 3. Phạm vi phát hành

| Nhóm collection | Requests | Đợt |
|---|---:|---|
| Launcher | 18 | MVP cho start/stop/status/version/quick v3; các operation còn lại đợt 2 |
| Profile Access Management | 15 | MVP cho token, workspace, folders; quản trị tài khoản đợt 3 |
| Profile Management | 20 | MVP cho CRUD/search/metas; tags/security/convert đợt 2–3 |
| Browser Profile Data | 1 | Đợt 2 |
| Proxy | 3 | Đợt 2 |
| Pre-made Cookies | 4 | Đợt 2 |
| Script Runner | 4 | Đợt 2 |
| Profile Import/Export | 6 | Đợt 2 |
| Object Storage | 16 | Đợt 2, chặn riêng operation mâu thuẫn |
| Bookmark Management | 3 | Đợt 2 |
| 2FA | 9 | Đợt 3 |
| Mobile Profile Management, gồm ADB | 26 | Đợt 3 |

Định nghĩa coverage: mỗi request ID phải có một trong các trạng thái implemented, alias, deferred hoặc blocked, kèm lý do và test tương ứng nếu implemented. Không gọi 125 request là 125 endpoint duy nhất: `Get QBP status` và `Get All Quick Profiles Status` cùng method/path; còn có các operation cùng path nhưng tên khác.

MVP gồm: User Sign In; User Refresh Token; User Workspaces; Workspace Automation Token; Workspace Folders; Workspace Create/Update/Remove Folders; Profile Create/Search/Update/Partial Update/Remove/Restore/Metas; Start Browser Profile v2; Start Quick Profile v3; Stop Browser Profile; Get Profile Status; Get All Profiles Status; Get Version. Các operation ngoài danh sách thuộc các đợt kế tiếp.

Không bao gồm trong SDK lõi: giao diện quản trị, scheduler, proxy marketplace, tự động thao tác bên trong Android app, hoặc tải/cài desktop Multilogin. Selenium/Playwright là phần tích hợp tùy chọn.

## 4. Kiến trúc đề xuất

Python >=3.11; httpx cho HTTP sync/async; Pydantic v2 cho request/response models. Công cụ phát triển: pytest, pytest-asyncio, Ruff, mypy, build. Các version cụ thể sẽ được pin sau khi xác minh tương thích lúc bắt đầu triển khai; chưa cài dependency trong bước nghiên cứu.

Package import: `multilogin_sdk`. Tên distribution dự kiến `multilogin-sdk`; phải kiểm tra tên trên registry trước khi phát hành.

```text
pyproject.toml
src/multilogin_sdk/
  __init__.py                 # MultiloginClient, AsyncMultiloginClient
  py.typed
  client.py                  # cấu hình, resource composition, lifecycle
  config.py                  # URL từng service, timeout, strict mode
  errors.py                  # lỗi HTTP, API envelope, transport, protocol
  _transport.py              # httpx sync/async; shared request specifications
  _operations.py             # operation metadata, routing, retry safety
  _pagination.py             # offset iterator và page iterator riêng
  models/
    common.py                # ApiResponse[T], ApiStatus, UNSET
    auth.py
    profiles.py
    launcher.py
    mobile.py                # đợt 3
  resources/
    auth.py
    workspaces.py
    folders.py
    profiles.py
    launcher.py
    proxies.py               # đợt 2
    cookies.py
    scripts.py
    transfers.py
    objects.py
    bookmarks.py
    two_factor.py            # đợt 3
    mobile.py
  integrations/              # optional extras, đợt 2
    selenium.py
    playwright.py
contracts/
  operations.json            # mapping request ID -> operation, service, status
  discrepancies.md           # mâu thuẫn và bằng chứng giải quyết
scripts/
  audit_collection.py        # đọc export local, tạo summary đã làm sạch
  check_coverage.py
examples/
tests/
  unit/
  contract/
  integration/
```

Sync và async có cùng method names, request builders và model. Async dùng httpx.AsyncClient thật; không bọc sync bằng thread và không gọi asyncio.run bên trong. Resource lớn tách thành module con khi cần, không dồn 125 method vào client.py.

### Routing và transport

Ba URL độc lập, configurable: cloud `https://api.multilogin.com`, launcher `https://launcher.mlx.yt:45001`, cookies `https://cookies.multilogin.com`. Không định tuyến theo folder: Browser Core List thuộc Launcher folder nhưng gọi Cloud; Profile Convert thuộc Profile Management nhưng gọi Launcher.

Với 8 URL `{{baseUrl}}`, cần xác minh global hoặc nguồn vendor trước khi khóa contract; không tự mặc định đã xác nhận. Credential theo service, chỉ truyền tới host được cấu hình; không forward Authorization qua redirect khác origin. TLS verification bật mặc định; hỗ trợ CA tùy chỉnh cho Launcher. Không mặc định verify=False. Launcher unavailable có exception riêng chứa hướng dẫn kiểm tra desktop/agent và URL đã cấu hình.

Defaults đề xuất: connect timeout 10 giây, read/write/pool 30 giây, start/import/export có override theo operation. Client sở hữu httpx session thì đóng bằng close/aclose hoặc context manager; session được inject do người gọi sở hữu thì không đóng ngoài ý muốn.

### Authentication và workspace

Ưu tiên `MultiloginClient(token=...)` nhận automation token từ môi trường/người gọi. Không yêu cầu lưu mật khẩu. Automation token có thời hạn theo contract: 1h, 3h, 5h, 16h, 24h, 48h, 1w, 2w, 3w, 1mo, no_exp; no_exp vẫn có thể bị vô hiệu hóa.

Sign-in tùy chọn gửi MD5 password theo yêu cầu wire protocol. Tách `sign_in(email, password)` và `sign_in_with_hash(email, password_md5)` để tránh double hashing; không coi MD5 là mã hóa bảo vệ credential. Kết quả token giữ trong bộ nhớ, không log.

MVP refresh/switch workspace là thao tác explicit, trả bộ token mới và client cho workspace mới. Không âm thầm đổi workspace của một client đang có request song song. Tự refresh với single-flight là bước sau nếu có nhu cầu; không tự retry một mutation sau 401.

### Payload và typing

Các request model riêng cho create/update/partial update/quick v2/v3; không dùng chung một model proxy nesting. `UNSET` biểu diễn trường không gửi; `None` chỉ thành null khi endpoint cho phép. Giữ false, 0, chuỗi rỗng và list rỗng khi được truyền rõ ràng. Strict mode mặc định không gửi header; chỉ gửi X-Strict-Mode theo config/override và validate các trường strict đã xác nhận.

Không đưa comment, placeholder `<integer>` hoặc danh sách lựa chọn như `false,true` trong collection vào request thật. Enum wire values giữ đúng chữ thường; unknown response fields được giữ hoặc cho phép để tránh gãy khi API thêm dữ liệu. Mobile ID là str, không ép UUID/int.

### Response và lỗi

Method trả `ApiResponse[T]` với data typed, status envelope và HTTP status thực. Operation không có data dùng ApiResponse[None]. Có khả năng truy cập response thô đã loại thông tin nhạy cảm để debug; không log body mặc định.

HTTP non-2xx luôn là lỗi, kể cả body báo 200. HTTP 2xx nhưng envelope http_code>=400 hoặc error_code khác rỗng là ApiError. Body rỗng/binary và response không có envelope phải được khai báo theo operation. Envelope thiếu trường bắt buộc hoặc kiểu bất thường là ProtocolError khi contract yêu cầu; không coi http_code=0 trong ví dụ placeholder là thành công chuẩn.

Lỗi có status_code, api_error_code, message, operation và request ID nếu server có trả; redact token/password/cookie/ADB pwd/proxy credentials. Lỗi batch cấp item được giữ trong BatchResult, không ném đi toàn bộ phần thành công. Có helper raise_for_failures tùy chọn.

### Retry, phân trang và polling

Mặc định không tự retry. Tùy chọn max_retries=2 chỉ áp dụng operation được đánh dấu read-only sau audit; hỗ trợ 429/502/503/504, Retry-After và backoff có jitter, tổng wait bị giới hạn. Không đánh dấu an toàn chỉ vì method GET: start/stop/delete/restore/automation token/get_or_create đều có side effect. POST Profile Search hoặc ADB Info chỉ được retry nếu được đánh dấu rõ là read-only.

Browser search: limit 1–100, offset 0–10000; iterator dừng khi hết trang hoặc chạm trần và thông báo giới hạn, không hứa đọc hết tập dữ liệu > giới hạn. Mobile pagination tách theo page/page_size và metadata đã kiểm chứng. Polling start/import/export có timeout tổng, khoảng chờ và cancellation; không gọi lại thao tác start mỗi lần poll.

### Lifecycle và tích hợp

Start v2 normalize data.port từ string sang int có kiểm tra phạm vi; adapter legacy v1 đọc status.message riêng khi hợp lệ. Không tự chuyển phiên bản endpoint sau lỗi. Quick v3 là mặc định; v2 explicit compatibility method.

Context manager session chỉ stop profile do chính session đó start thành công. Cleanup có timeout, giữ lỗi gốc nếu stop cũng thất bại. Không tự stop toàn bộ profile. Selenium/Playwright thuộc optional extras; Stealthfox + Playwright bị từ chối theo giới hạn tài liệu. Endpoint kết nối trả từ server được validate trước khi sử dụng.

Import/export path là đường dẫn trên máy Launcher; SDK không giả định đó là máy đang chạy Python. Cookie import nhận list/dict thuận tiện nhưng serialize thành JSON string trong trường cookies theo contract. Cookies trả về cần xác minh shape trước khi hứa một helper chuẩn hóa ổn định.

Mobile đợt 3 trả BatchResult, ADB set/info tối đa 50 IDs mỗi call; helper chunking chỉ thực hiện khi người gọi chọn. SDK quản lý cloud phone và trả thông tin ADB, không tự bật ADB hoặc chạy Appium khi chỉ gọi info. Start phone tiêu thụ plan minutes theo tài liệu dù không GUI.

## 5. Các điểm phải giải quyết trước khi cam kết coverage

1. Xác nhận `baseUrl` trong global cho 8 request, chỉ đọc biến cần thiết.
2. Cloud to Local trỏ cùng local_to_cloud: tìm contract chính xác; chưa phát hành wrapper sai chiều.
3. Mobile import validate nhắc confirm nhưng thiếu request confirm: chỉ hỗ trợ validate, chưa thêm endpoint suy đoán.
4. HTTP status trong saved examples lệch envelope: giữ fixture mismatch để test lỗi, không dùng làm mẫu thành công.
5. Quick v3 body có `canvas_noise:` sai tên và template invalid: đối chiếu mô tả/example/vendor trước khi khóa model.
6. Browser Core List GET có body và query cùng mô tả: xác minh vị trí tham số, không âm thầm bỏ body.
7. Object examples phần lớn placeholder: cần response thật đã làm sạch để khóa typed model.
8. Chưa có con số rate limit đủ tin cậy: không hard-code quota theo trí nhớ.

Mỗi điểm có trạng thái open/resolved/blocked trong discrepancies.md. Operation bị chặn không cản phát hành MVP nếu nằm ngoài phạm vi MVP; tài liệu phải ghi rõ.

## 6. Lộ trình thực hiện và tiêu chí hoàn thành

Đây là roadmap kiến trúc, chưa phải task-by-task implementation plan đã được phê duyệt.

### M0 — Chuẩn hóa contract

- Tạo operations.json đủ 125 request IDs; lưu service, method, path template, body kind, retry safety, coverage status.
- Tạo audit_collection.py tái lập báo cáo từ export local; không gửi thông tin tài khoản vào artifact.
- Giải quyết baseUrl và mâu thuẫn ảnh hưởng MVP; những điểm còn lại ghi blocked có lý do.
- Kiểm tra: script coverage đếm đúng 125 entries, phát hiện ID trùng/mất, không đánh đồng alias với operation khác phiên bản.

### M1 — Lõi HTTP và model

- Tạo pyproject, src layout, config, errors, transport, ApiResponse, UNSET và sync/async client lifecycle.
- Test bằng HTTP transport giả lập: routing 3 service, TLS config, encoding, giữ false/0/empty, timeout, đóng session đúng ownership.
- Test HTTP500+body200 phải lỗi; HTTP200+bodyerror phải lỗi; malformed JSON, missing envelope, redaction, unsafe GET không retry.
- Hoàn thành khi sync/async cùng vượt bộ contract tests; Ruff/mypy/build chạy được.

### M2 — Authentication, workspace và folders

- Viết typed resources auth/workspaces/folders cho các operation MVP.
- Test MD5 không double hash, noauth sign-in, automation expiration enum, explicit refresh/switch không thay client cũ.
- Test request params/body đúng vị trí, folder mutations không tự retry; token không xuất hiện trong repr/log.

### M3 — Browser profiles và Launcher MVP

- CRUD/search/metas, serializers riêng partial update, start v2/quick v3/stop/status/version, iterator và session helper.
- Test proxy root/parameters, ISP empty host, offset boundary, v2 string port, cleanup khi exception và Launcher offline.
- Bộ kiểm tra hợp đồng so sánh request sinh ra với mapping đã review; không copy placeholder làm payload chạy.
- Hoàn thành khi ví dụ create -> start -> lấy connection -> stop chạy được với server mô phỏng và cleanup được kiểm chứng.

### M4 — Tài liệu, CI và phát hành MVP

- README tiếng Việt, quickstarts sync/async, token setup, lỗi, strict mode, Ubuntu Launcher và giới hạn coverage.
- CI: lint/type/unit/contract/build, kiểm tra artifact wheel và sdist cài được trong môi trường sạch.
- Dùng Postman api-simulation khi thực thi luồng client chống HTTP service mô phỏng; ghi rõ kết quả mô phỏng.
- Live smoke test opt-in trên workspace thử nghiệm và profile do test sở hữu; không chạy toàn collection vì có delete, password, revoke, 2FA và start cloud phone.
- Không tuyên bố live verified nếu chỉ có fixture/mô phỏng. Chưa publish package khi mới lập kế hoạch.

### M5 — Browser nâng cao

- Proxies, tags, unlock, cookies, Script Runner, transfers, bookmarks, object storage/extensions, core management và legacy quick v2.
- Tách tests cho host cookies, cookie JSON string, task polling, Launcher-side paths, và response placeholder.
- Selenium/Playwright integration test opt-in; dependency optional không được import khi dùng core.
- Những operation có mâu thuẫn tiếp tục marked blocked cho tới có bằng chứng.

### M6 — Mobile và bảo mật tài khoản

- 26 mobile requests: phone lifecycle, group/tag, limits, geo/brand, files multipart/template validation và ADB.
- 2FA/profile-password/user-account operations trả dữ liệu tường minh, không tự thay đổi thiết lập từ tiện ích khác.
- Test batch partial failures, status 0 không bị coi false/missing, mobile str IDs, ADB max50, multipart streaming/close, cancellation và secrets redaction.
- Bản đầy đủ chỉ được tuyên bố theo coverage matrix: implemented+alias được giải thích, blocked/deferred được công bố.

## 7. Tiêu chí review trước triển khai

- Phạm vi đề xuất ưu tiên browser automation ở MVP; mobile đợt 3 là giả định để review, chưa phải yêu cầu đã xác nhận.
- Chọn sync+async từ lõi để tránh hai kiến trúc sau này; có thể chỉ phát hành sync trước nếu người dùng muốn rút gọn.
- Bằng chứng hiện tại đủ cho thiết kế và roadmap; chưa đủ để coi collection là schema chuẩn hoặc runtime chính xác.
- Sau khi review kiến trúc, viết implementation plan riêng với files, signatures, test cases, commands và checkbox cho từng task M0–M4. Chưa viết mã SDK trước khi chốt thiết kế theo workflow Superpowers.
