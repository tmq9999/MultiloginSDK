# MultiloginSDK Python MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây Python SDK sync/async cho 21 request MVP quản lý authentication, workspace, folders, browser profiles và Launcher.

**Architecture:** Resource client viết tay dùng chung operation metadata, serializers và typed response parser. HTTP sync/async chạy bằng httpx riêng, routing theo service của operation; contract coverage theo request ID.

**Tech Stack:** Python >=3.11, httpx, Pydantic v2, pytest, pytest-asyncio, Ruff, mypy, build.

**Spec:** `docs/superpowers/specs/2026-10-22-multilogin-sdk-design.md` — duyệt 2026-10-23.

## Global Constraints

- Package import: `multilogin_sdk`; tên distribution dự kiến `multilogin-sdk`, chưa publish.
- Python >=3.11; httpx cho HTTP sync/async; Pydantic v2 cho request/response models.
- Cloud `https://api.multilogin.com`, Launcher `https://launcher.mlx.yt:45001`, cookies `https://cookies.multilogin.com` là ba service configurable độc lập.
- TLS verification bật mặc định; hỗ trợ CA tùy chỉnh cho Launcher. Không mặc định verify=False.
- Connect timeout 10 giây, read/write/pool 30 giây; cho phép override theo operation.
- Mặc định không tự retry. Tùy chọn max_retries=2 chỉ áp dụng operation được đánh dấu read-only sau audit.
- Không tự refresh token, đổi workspace hoặc fallback phiên bản endpoint sau lỗi.
- HTTP non-2xx luôn là lỗi, kể cả body báo 200.
- Browser search: limit 1–100, offset 0–10000. `UNSET` không gửi; null chỉ hợp lệ khi contract cho phép.
- Không log credential, cookie, proxy password, ADB pwd hoặc response body mặc định.
- Chưa triển khai mobile, 2FA, objects, cookies, transfers, Selenium/Playwright adapters ở MVP; giữ coverage deferred/blocked rõ ràng.
- Chỉ sửa tài liệu trong bước lập kế hoạch. Phê duyệt spec không thay cho review implementation plan.

## Review Focus

1. GET có side effect: start/stop/automation token không được retry (Task 3).
2. false/0/empty khác omitted/null; partial update không làm sai proxy nesting (Tasks 2, 6).
3. HTTP status lệch envelope, HTTP200 lỗi API, hoặc body malformed phải phân loại đúng (Task 3).
4. Async cancellation trong session vẫn thử cleanup có thời hạn, giữ exception gốc (Task 8).
5. Secret nằm trong server message hoặc redirect khác origin không được lộ qua exception/Authorization (Task 3).

## Phạm vi, dependencies và file map

Tasks 1–9 tương ứng M0–M4. Tasks 1 → 2 → 3 → 4 tạo nền tảng; Tasks 5–7 dùng nền tảng; Task 8 dùng 6–7; Task 9 tích hợp toàn bộ. M5–M6 lập plan riêng khi bắt đầu, theo spec đã duyệt.

- `contracts/operations.json`, `contracts/discrepancies.md`: toàn bộ 125 request IDs, evidence và coverage.
- `scripts/audit_collection.py`, `scripts/check_coverage.py`: tái lập audit và kiểm tra mapping.
- `src/multilogin_sdk/{config,errors,_operations,_transport,_response,_retry,_pagination,client}.py`: mỗi file một trách nhiệm đúng tên.
- `src/multilogin_sdk/models/{common,auth,workspaces,profiles,launcher}.py`: wire models; `models/__init__.py` exports.
- `src/multilogin_sdk/resources/{auth,workspaces,folders,profiles,launcher}.py`: mỗi module gồm resource sync/async, dùng chung request builder.
- `src/multilogin_sdk/_session.py`: owned profile lifecycle.
- `tests/{unit,contract,integration}/`: transport/model, wire parity và mô phỏng/live opt-in.
- `README.md`, `docs/usage.md`, `examples/{sync_profiles,async_profiles}.py`, `.github/workflows/ci.yml`: onboarding, ví dụ và validation.

Git hiện chưa được khởi tạo. Khi thực thi, kiểm tra lại repository/AGENTS.md; dùng skill using-git-worktrees trước khi quyết định isolation. Nếu vẫn là thư mục trống thì khởi tạo Git ngay trong dự án và commit tài liệu đã duyệt trước Task 1. Mỗi task commit đúng các file của task, không stage thay đổi ngoài phạm vi.

## Task 1: Contract registry đủ 125 request IDs — M0

**Files:** Create `scripts/audit_collection.py`, `scripts/check_coverage.py`, `contracts/operations.json`, `contracts/discrepancies.md`, `tests/contract/test_registry.py`, `tests/fixtures/collection_minimal.json`.

**Interfaces:**
- `audit_collection(source: Path) -> list[dict[str, object]]`: recursive V3 items, giữ request IDs, không headers/credential values.
- `check_coverage(registry: Path) -> list[str]`: empty list là hợp lệ; CLI `python scripts/check_coverage.py` exit0 khi hợp lệ, exit1 khi lỗi.
- Registry entry: `request_id`, `name`, `group`, `operation`, `service`, `method`, `path`, `body_kind`, `read_only`, `status`, `reason`, `test_ids`, `alias_of`. service thuộc cloud/launcher/cookies/unresolved; status implemented/alias/deferred/blocked.

- [ ] Viết `test_recursive_registry`: fixture có nested ADB và alias, assert mỗi ID xuất hiện đúng một lần; `test_missing_duplicate_and_wrong_alias`: missing/duplicate ID, alias khác method/path phải báo lỗi; `test_sanitized_export`: token/header không xuất hiện trong registry. Tạo minimal dev setup pytest trong pyproject nếu chưa có để chạy test.
- [ ] Chạy `python -m pytest tests/contract/test_registry.py -q`; kỳ vọng FAIL do scripts chưa có.
- [ ] Viết scripts; tải collection bằng CLI đã có: `/home/mquangprovip0503/.local/bin/postman collection get 46206122-78bf4173-0a22-4651-890d-b160177d47b1 --json` vào file private tạm, không commit raw export. Tra CLI help để đọc chỉ biến baseUrl thuộc global `00f51822-8551-4be0-804b-53a692f93dee`; không dump toàn bộ global. Nếu thiếu baseUrl, đối chiếu vendor hoặc giữ blocked; không đoán.
- [ ] Đọc lại audit và ghi 8 discrepancy trong spec vào discrepancies.md; mỗi mục có evidence, trạng thái và operation bị ảnh hưởng. Quick v3 canvas_noise phải xác nhận từ nguồn cụ thể trước khi khóa serializer; không sửa template hàng loạt theo suy đoán.
- [ ] Chạy lại test và coverage CLI: 125 IDs duy nhất; 21 request MVP được chọn đích danh như spec, hiện deferred với reason planned; chỉ chuyển implemented khi task tương ứng qua tests. Alias chưa triển khai không được tính implemented.
- [ ] Commit: `chore: establish sanitized Multilogin contract registry`.

## Task 2: Typed models và request representation — M1

**Files:** Create/complete `pyproject.toml`, `src/multilogin_sdk/{__init__,config,errors,_operations}.py`, `src/multilogin_sdk/py.typed`, `src/multilogin_sdk/models/{__init__,common}.py`, `tests/unit/test_models.py`, `tests/unit/test_config.py`.

**Interfaces:**
- `Service = Literal['cloud', 'launcher', 'cookies']`.
- Frozen `ClientConfig`: three base URLs above, `strict_mode: bool | None = None`, timeout httpx.Timeout(30, connect=10), `max_retries: int = 0`, `retry_budget: float = 30`, `launcher_ca: ssl.SSLContext | None = None`.
- Frozen `Operation`: `name: str`, `service: Service`, `method: str`, `path: str`, `read_only: bool`, `auth_required: bool`, `response_kind: Literal['envelope','empty','binary']`, `read_timeout: float | None`.
- `RequestSpec`: operation, path_params, query, json_body; mappings are copied on construction.
- `RequestModel.to_wire() -> dict[str, object]`: only explicitly set fields; reject null for non-nullable fields; `UNSET` is an exported singleton excluded before Pydantic serialization.
- `ApiStatus(http_code: int, error_code: str, message: str)`; `ApiResponse[T](data: T, status: ApiStatus, http_status: int, request_id: str | None)`, response models extra='allow'.
- `MultiloginError`, `HttpError`, `ApiError`, `ProtocolError`, `TransportError`, `LauncherUnavailable`, `PaginationLimitError`, `PollingTimeout`; common attributes operation/status_code/api_error_code/request_id, redacted message only.

- [ ] Test `test_omitted_vs_falsy`: assert to_wire preserves False, 0, '', []; excludes UNSET/unset fields; explicit None rejected unless field annotated nullable. `test_extra_response_preserved` retains unknown response fields. `test_invalid_config` rejects negative retries/timeouts and base URLs containing embedded credentials/query/fragment.
- [ ] Run `python -m pytest tests/unit/test_models.py tests/unit/test_config.py -q`; expected FAIL before implementation.
- [ ] Implement interfaces and package metadata, typed marker, runtime dependency major bounds httpx<1 and Pydantic>=2,<3. At execution verify current official compatibility, resolve exact dev versions into `requirements-dev.lock`; installation network is not needed during planning.
- [ ] Run same tests; expected PASS. Build `python -m build`; expect wheel/sdist with py.typed.
- [ ] Commit: `feat: add typed SDK configuration and wire models`.

## Task 3: Transport, response parser, retry và redaction — M1

**Files:** Create `_transport.py`, `_response.py`, `_retry.py`, `_redaction.py` under `src/multilogin_sdk/`; tests `tests/unit/test_transport.py`, `test_response.py`, `test_retry.py`, `test_redaction.py`.

**Interfaces:**
- `SyncTransport(config: ClientConfig, *, tokens: Mapping[Service, str], sessions: Mapping[Service, httpx.Client] | None = None)`; async counterpart uses AsyncClient.
- `send(spec: RequestSpec, data_type: type[T]) -> ApiResponse[T]`; async counterpart `async send(...)`.
- `close() -> None` / `async aclose() -> None`; injected session ownership retained by caller.
- `parse_response(response: httpx.Response, operation: Operation, data_type: type[T]) -> ApiResponse[T]`.
- `redact(value: object, secrets: Collection[str]) -> object`: recursively hide sensitive key values and replace known secrets inside messages before formatting errors.
- Retry policy consumes operation.read_only, max_retries, attempt and Retry-After; injectable clock/sleeper/random for deterministic tests. Cap total sleep to retry_budget=30s, numeric or HTTP-date Retry-After; invalid values use jittered exponential backoff base0.5s cap8s. Unsafe operations never retry, including network ambiguity.

- [ ] Parametrize sync/async `test_service_routing`, `test_url_encoding`, `test_no_cross_origin_redirect`, `test_session_ownership`, `test_timeout_mapping`: exact service host; quoted path values cannot add slash/query; redirects disabled; owned sessions closed, injected sessions retained; SSL config uses verified defaults/custom Launcher CA.
- [ ] Add `test_http500_envelope200`, `test_http200_api_error`, `test_bad_json`, `test_missing_status`, `test_zero_envelope_code`: first is HttpError, next ApiError, remainder ProtocolError for envelope operation. Explicit empty/binary operation bypasses envelope parser only as declared.
- [ ] Add retry tests: default attempts=1; max_retries=2 allows at most3 attempts on read-only429/502/503/504; start/stop/token GET attempts=1; 401/403 no retry; Retry-After date/numeric/corrupt and budget tested with fake clock. Add `test_error_message_secret_redaction`: HTTP body echoes token, password, cookie and proxy credentials; repr/str contain none of provided sentinel strings.
- [ ] Run `python -m pytest tests/unit/test_transport.py tests/unit/test_response.py tests/unit/test_retry.py tests/unit/test_redaction.py -q`; expected FAIL.
- [ ] Implement transport and parsers using Task2 interfaces. Separate per-service session ensures Launcher CA does not alter Cloud trust. RequestSpec cannot supply arbitrary absolute URL. Map Launcher connect errors separately, cancellation propagates; redact raw diagnostics. Reject http_code outside200–299 for a success envelope, unless >=400 classified ApiError.
- [ ] Run same test command; expected PASS sync/async. `python -m mypy src/multilogin_sdk` expected success.
- [ ] Commit: `feat: implement safe sync and async HTTP transport`.

## Task 4: Public clients và resource composition — M1

**Files:** Create `src/multilogin_sdk/client.py`; modify package exports; create `tests/unit/test_client.py`.

**Interfaces:**
- `MultiloginClient(token: str | None = None, *, config: ClientConfig | None = None, service_tokens: Mapping[Service,str] | None = None, sessions: Mapping[Service,httpx.Client] | None = None)`; async counterpart with AsyncClient.
- Explicit token populates configured known services unless overridden by service_tokens; no environment loading or login implicitly. token=None allows only noauth operations until a token is provided.
- `with_token(token: str) -> MultiloginClient` / async equivalent creates independent owned sessions/config; does not mutate or close old client.
- Properties auth/workspaces/folders/profiles/launcher become concrete typed resources in Tasks5–7; no public generic arbitrary URL requester.
- `__enter__/__exit__/close`, `__aenter__/__aexit__/aclose`: repeat close allowed, request after close raises RuntimeError.

- [ ] Write `test_client_lifecycle`, `test_with_token_isolation`, `test_unauthenticated_operation_rejected`, `test_repr_hides_token`: assert ownership and secret behavior above for both clients.
- [ ] Run `python -m pytest tests/unit/test_client.py -q`; expect FAIL.
- [ ] Implement public constructors/lifecycle and no implicit token acquisition; connect resource properties as subsequent tasks add classes.
- [ ] Run client tests and prior unit tests; expect PASS. Core import does not import Selenium/Playwright.
- [ ] Commit: `feat: expose sync and async Multilogin clients`.

## Task 5: Authentication, workspaces và folders — M2

**Files:** Create `models/auth.py`, `models/workspaces.py`, `resources/{__init__,auth,workspaces,folders}.py` under package; tests `tests/contract/test_access.py`, `tests/unit/test_auth.py`; modify client composition and registry.

**Interfaces:** Sync methods below; async counterparts same signature with awaitable results.
- `auth.sign_in(email: str, password: str) -> ApiResponse[Tokens]`; `sign_in_with_hash(email: str, password_md5: str) -> ApiResponse[Tokens]`; Tokens fields token/refresh_token use SecretStr.
- `auth.refresh(email: str, refresh_token: str, workspace_id: str) -> ApiResponse[Tokens]`; `client.switch_workspace(*, email: str, refresh_token: str, workspace_id: str) -> MultiloginClient`: refresh explicit, return new client through with_token; current client unchanged.
- `auth.automation_token(expiration_period: ExpirationPeriod) -> ApiResponse[AutomationToken]`; Literal values exactly those listed in spec.
- `workspaces.list() -> ApiResponse[WorkspacesData]`; `folders.list() -> ApiResponse[FoldersData]`.
- `folders.create(request: FolderCreateRequest)`, `folders.update(request: FolderUpdateRequest)`, `folders.remove(request: FoldersRemoveRequest)` return ApiResponse[dict[str,object] | None], according to reviewed response data presence. Model fields mirror audit body; define explicit fields after Task1 confirms templates, never reuse disabled query values as runtime defaults.
- All resources have shared builders `build_<operation>(request) -> RequestSpec`; contract fixtures in `tests/fixtures/access/` are hand-cleaned valid JSON.

- [ ] Test `test_password_hash_once`: password='password' sends `5f4dcc3b5aa765d61d8327deb882cf99`; hash method sends supplied32-hex unchanged and rejects invalid input. Test noauth sign-in has no Authorization header.
- [ ] Test `test_access_wire_contract` for all8 access MVP request IDs: assert method/path/query/body/header against reviewed fixture, folder body fields never in query; token expiry sent as one enum value. Test `test_workspace_switch_isolation` concurrently reading old client still uses old token. Test response model SecretStr repr hides tokens.
- [ ] Run `python -m pytest tests/unit/test_auth.py tests/contract/test_access.py -q`; expect FAIL.
- [ ] Implement models/builders/resources, explicit refresh, client switch helper; consume contract review decisions from Task1. Do not auto-replay requests after401.
- [ ] Run same tests for sync/async, update8 registry entries implemented with real test_ids; `python scripts/check_coverage.py` passes.
- [ ] Commit: `feat: add authentication workspace and folder resources`.

## Task 6: Browser profile CRUD và offset iterator — M3

**Files:** Create `models/profiles.py`, `resources/profiles.py`, `_pagination.py`; tests `tests/contract/test_profiles.py`, `tests/unit/test_profile_models.py`, `test_pagination.py`; modify client/registry.

**Interfaces:**
- Models: ProfileCreateRequest, ProfileUpdateRequest, ProfilePartialUpdateRequest, ProfileSearchRequest, ProfileRemoveRequest, ProfileRestoreRequest, ProfileMetasRequest, ProfileSummary, ProfileSearchData(profiles: list[ProfileSummary]); remaining data types from reviewed fixture keyed to each operation, preserve extra fields.
- `profiles.create/update/partial_update/remove/restore/metas(request: corresponding RequestModel) -> ApiResponse[dict[str,object] | None]`; `search(request: ProfileSearchRequest) -> ApiResponse[ProfileSearchData]`.
- `profiles.iter_profiles(request: ProfileSearchRequest) -> Iterator[ProfileSummary]`; async returns AsyncIterator. Treat request.offset as first offset; request.limit determines page size.
- Mutable dict/list defaults use factories; payload model names and JSON types match operation-specific body, not guessed common schema. Create proxy `parameters.proxy`; partial update root `proxy`; empty host retained.

- [ ] Test `test_profile_wire_contract` for7 profile IDs. `test_isp_payload` asserts create host='' retained, times other than1 rejected when isp_ip_id set; partial proxy root and flags nested. `test_partial_preserves_explicit_false` sends auto_update_core=False and excludes omitted auto_update_core; docs explain server default if omitted.
- [ ] Pagination tests: reject limit0/101 and offset-1/10001; pages at offsets0,100 then short page stop; starting offset10000 with full page raises PaginationLimitError before next request, with short page completes; empty page stops; cancellation makes no further async requests. Iterator must never silently claim complete after ceiling.
- [ ] Run `python -m pytest tests/contract/test_profiles.py tests/unit/test_profile_models.py tests/unit/test_pagination.py -q`; expect FAIL.
- [ ] Implement builders/resources/models/iterators. Define nullable fields only from reviewed evidence; unknown request fields rejected. No inferred patch merging or hidden get-before-update.
- [ ] Same test command passes sync/async; update7 registry entries implemented/test_ids, run coverage CLI.
- [ ] Commit: `feat: add browser profile resources and pagination`.

## Task 7: Launcher MVP và typed connection — M3

**Files:** Create `models/launcher.py`, `resources/launcher.py`; tests `tests/contract/test_launcher.py`, `tests/unit/test_launcher_models.py`; modify client/registry.

**Interfaces:**
- `LauncherStartRequest(folder_id: str, profile_id: str, automation_type: Literal['selenium','puppeteer','playwright']='selenium', headless_mode: bool=False)`.
- `QuickProfileV3Request` fields from reviewed v3 contract; proxy inside parameters. No quick v2 fallback.
- `BrowserConnection`: id: str, port: int (1..65535), browser_type: str, core_version: int | None, is_quick: bool; preserve response additions.
- `launcher.start(request: LauncherStartRequest) -> ApiResponse[BrowserConnection]`; `quick(request: QuickProfileV3Request) -> ApiResponse[BrowserConnection]` after reviewed quick response supports this shape, otherwise separate QuickProfileConnection model with documented normalization.
- `stop(profile_id: str) -> ApiResponse[None]`; `status(profile_id: str) -> ApiResponse[dict[str,object]]`; `statuses() -> ApiResponse[dict[str,object]]`; `version() -> ApiResponse[dict[str,object]]`. Preserve unknown status values; browser_running is the ready value for Task8.
- `read_timeout=120` for start/quick, configurable. HTTP deadlines are separate from polling deadline.

- [ ] Write `test_launcher_wire_contract` for6 request IDs: v2 start path, bool query 'true'/'false', quick v3 path, stop/status/version. Assert default strict mode header absent; explicit strict mode validates confirmed required fields and emits true/false literally.
- [ ] Test string port '55513' normalizes55513; invalid/out-of-range port raises ProtocolError; unknown added fields accepted; start never parses message as port when data.port absent. v1 legacy remains deferred. Test Launcher offline raises LauncherUnavailable with URL and desktop hint, no token.
- [ ] Run `python -m pytest tests/contract/test_launcher.py tests/unit/test_launcher_models.py -q`; expected FAIL.
- [ ] Implement builders and typed results; Quick model blocked if Task1 lacks shape evidence, do not mark6 entries complete until resolved. automation compatibility validated when browser_type known (quick); for regular start do not invent browser_type that request does not carry. Document Mimic custom_start_urls limitation.
- [ ] Same tests pass sync/async, update6 registry IDs/test_ids and run coverage CLI. Total MVP implemented=21.
- [ ] Commit: `feat: add Launcher v2 start and quick v3 resources`.

## Task 8: Owned browser session và bounded polling — M3

**Files:** Create `_session.py`; modify `resources/launcher.py`; tests `tests/unit/test_session.py`.

**Interfaces:**
- `launcher.session(request: LauncherStartRequest, *, wait_timeout: float=120, poll_interval: float=1, cleanup_timeout: float=10) -> ContextManager[BrowserConnection]`; async counterpart AsyncContextManager.
- `launcher.wait_ready(profile_id: str, *, timeout: float=120, poll_interval: float=1) -> ApiResponse[dict[str,object]]`; use monotonic deadline, ready browser_running, explicit error status names from audit terminate early; unknown status polls until deadline.
- session start once → ownership recorded after successful start → status poll → yield → stop only returned profile id. Host/port for automation derives configured Launcher host and validated returned port; no executable adapters in MVP.

- [ ] Tests: `test_session_starts_once_and_stops_owned_profile`; `test_failed_start_does_not_stop`; `test_wait_failure_after_start_cleans_up`; `test_body_and_cleanup_failure_preserves_original` asserts original exception propagated and cleanup note is redacted; `test_cleanup_failure_without_original_raises` surfaces stop failure.
- [ ] `test_async_cancellation_cleanup_bounded` cancels body and fake stop hangs: cleanup attempted under shield+10s deadline, cancellation propagates and no leaked task remains. Fake clock/sleeper tests polling120s ceiling without wall-clock wait and no repeated start. Validate positive timeouts/intervals.
- [ ] Run `python -m pytest tests/unit/test_session.py -q`; expected FAIL.
- [ ] Implement lifecycle and polling; use asyncio timeout/shield with explicit task cleanup for async. Stop timeout scoped to cleanup request, not global config mutation.
- [ ] Same tests pass sync/async, plus existing launcher tests.
- [ ] Commit: `feat: manage owned browser sessions with bounded cleanup`.

## Task 9: End-to-end simulation, docs và distributable MVP — M4

**Files:** Create `README.md`, `docs/usage.md`, `examples/sync_profiles.py`, `examples/async_profiles.py`, `tests/integration/test_simulated_workflow.py`, `tests/integration/test_live_smoke.py`, `tests/contract/test_public_api_parity.py`, `.github/workflows/ci.yml`, `.gitignore`, `MANIFEST.in` if backend requires; update pyproject and registry evidence.

**Interfaces:**
- Live marker disabled unless `MULTILOGIN_LIVE_TEST=1`; require test workspace/folder explicitly and token provided privately. Only delete/stop resources created by the test; fail before network if identifiers absent.
- Simulation uses configured local service URLs for all3 routes; token sentinel only. Consume client public methods, no direct bypass of transport.
- CI uses Python3.11 and latest stable compatible Python verified at execution; run lint/type/tests/build, then install wheel and sdist separately into clean venvs. No live secrets in default CI.

- [ ] Write `test_create_start_status_stop_workflow` on Postman simulation: assert create ID flows into start/status/stop, cleanup after application error; inject429 on safe search with retries enabled,503 on start must produce only one start, timeout on status cleans up. Write `test_public_api_parity` comparing public sync/async methods/parameters and builder wire output.
- [ ] Run `python -m pytest tests/integration/test_simulated_workflow.py tests/contract/test_public_api_parity.py -q`; expect FAIL before fixtures/simulation configuration. Load api-simulation skill at execution and follow installed CLI help for scenario setup; keep reusable simulation input in `tests/fixtures/simulation/`. Do not claim local unit stubs are Postman simulation evidence.
- [ ] Finish simulation, examples and Vietnamese documentation: token setup; sync/async examples; UNSET/null; explicit refresh/workspace switch; owned lifecycle; config/TLS; safe retries; pagination ceiling; 21 implemented IDs and blocked/deferred list. Explicitly state mobile and browser integrations remain later phases.
- [ ] Add opt-in live smoke; default run must SKIP it. When explicitly enabled, report live outcome separately from simulation and make cleanup evidence visible without exposing secrets.
- [ ] Run `python -m ruff check .`, `python -m ruff format --check .`, `python -m mypy src/multilogin_sdk`, `python -m pytest tests/unit tests/contract -q`, simulation test command, `python scripts/check_coverage.py`, `python -m build`. Expected: all pass;21 MVP request IDs implemented with existing test IDs,125 total IDs accounted for. Install built wheel and sdist in separate temporary venvs and verify package import/py.typed and both examples' imports; do not publish.
- [ ] Commit: `docs: ship validated Python SDK MVP with simulation evidence`.

## Self-review và handoff

Coverage M0→Task1; M1→Tasks2–4; M2→Task5; M3→Tasks6–8; M4→Task9. Review Focus1/3/5 covered Task3,2 covered Tasks2/6,4 covered Task8. M5/M6 explicitly deferred; no speculative endpoint bodies promoted to implementation.

Implementation remains blocked only per operation by unresolved contract evidence; research/other tasks can proceed. MVP cannot be declared complete if one of its21 requests remains blocked. Resolve and record evidence or return a concrete scope change for review.

Plan review pending. Recommended execution: Native — shared transport/models make tasks strongly sequential and this avoids a fresh implementer context for each boundary. Subagent-driven remains an option if the user prefers separate task review. Final whole-branch review follows chosen skill and actual available reviewer tooling; do not invent tool/model support.
