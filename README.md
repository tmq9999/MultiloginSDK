# MultiloginSDK

Python SDK typed, sync và async cho Multilogin Cloud API, Launcher cục bộ và cookie service. Yêu cầu Python 3.11 trở lên.

Dependencies runtime: `httpx>=0.28,<1` và `pydantic>=2,<3`. Selenium, Playwright và Puppeteer không phải dependency của SDK; Launcher trả connection port để ứng dụng nối bằng thư viện automation riêng.

`0.1.0` hiện triển khai **30/125** request đã audit. Các endpoint đã có contract test; profile search và 9 endpoint discovery đã được xác nhận bằng response API thật. Package chưa phát hành lên PyPI.

## Cài vào project khác

Repository là private. Máy cài cần quyền đọc repository qua GitHub credential, SSH key, GitHub CLI hoặc PAT có quyền `repo`.

Chạy lệnh cài trong virtual environment của project nhận dependency:

```bash
cd /path/to/your-project
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
```

Nếu dùng HTTPS và GitHub CLI đã đăng nhập, cấu hình Git lấy credential qua CLI một lần:

```bash
gh auth login
gh auth setup-git
```

Nếu dùng SSH, kiểm tra quyền truy cập trước khi cài:

```bash
ssh -T git@github.com
```

Không đặt PAT trực tiếp trong URL cài đặt vì URL có thể lưu vào shell history và log pip.

```bash
# Cài branch hiện tại
python -m pip install "git+https://github.com/tmq9999/MultiloginSDK.git@feat/python-sdk-mvp"

# Cài qua SSH nếu đã cấu hình GitHub SSH key
python -m pip install "git+ssh://git@github.com/tmq9999/MultiloginSDK.git@feat/python-sdk-mvp"
```

Để ghim bản đã kiểm tra, dùng commit SHA:

```bash
python -m pip install "git+https://github.com/tmq9999/MultiloginSDK.git@c5fb8e9"
```

Để cài cùng các dependency khác từ file requirements, thêm một dòng VCS:

```text
multilogin-sdk @ git+https://github.com/tmq9999/MultiloginSDK.git@feat/python-sdk-mvp
```

Trong `pyproject.toml` của project dùng SDK, khai báo cùng chuỗi PEP 508 dưới `project.dependencies`.

Lệnh `git+https` dùng Git để clone repository, nên credential helper phải đăng nhập được tài khoản có quyền đọc repo. Trong CI, cấu hình Git credential bằng secret store của CI; không đặt PAT trong URL.

Phát triển từ checkout local:

```bash
git clone git@github.com:tmq9999/MultiloginSDK.git
cd MultiloginSDK
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -c "from multilogin_sdk import MultiloginClient; print('MultiloginSDK ready')"
```

Trên Windows PowerShell, tạo và bật virtual environment như sau:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install "git+https://github.com/tmq9999/MultiloginSDK.git@feat/python-sdk-mvp"
```

## Xác thực và cấu hình

SDK không tự đọc `.env`, không truy cập credential của Multilogin desktop và không tự đăng nhập. Ứng dụng truyền token tường minh. Dùng automation token của đúng workspace và không commit token vào Git.

```bash
export MULTILOGIN_TOKEN='...'
export MULTILOGIN_FOLDER_ID='...'
export MULTILOGIN_PROFILE_ID='...'
export MULTILOGIN_EMAIL='user@example.com'  # chỉ cần cho sign-in/refresh
```

Đăng nhập bằng email/password dùng thêm `MULTILOGIN_EMAIL`; ví dụ bên dưới hỏi password ẩn bằng `getpass` nếu chưa đặt `MULTILOGIN_PASSWORD`.

| Service | URL mặc định |
|---|---|
| Cloud | `https://api.multilogin.com` |
| Launcher | `https://launcher.mlx.yt:45001` |
| Cookies | `https://cookies.multilogin.com` |

Multilogin desktop/agent phải chạy để gọi Launcher. Cloud resource không cần Launcher.

## Bắt đầu nhanh: sync

```python
import os

from multilogin_sdk import MultiloginClient
from multilogin_sdk.models.profiles import ProfileSearchRequest

with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
    # Workspace rỗng có thể trả profiles: null; SDK chuẩn hóa thành []
    page = client.profiles.search(ProfileSearchRequest(limit=10, offset=0))
    for profile in page.data.profiles:
        print(profile.id, profile.name, profile.browser_type)

    print(client.workspaces.statistics().data)
    print(client.mobile.limit().data)
    print(client.cookies.websites().data)
```

Mọi method trả `ApiResponse[T]`:

```python
import os

from multilogin_sdk import MultiloginClient

with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
    response = client.workspaces.list()
    print(response.data)  # payload đã parse
    print(response.status)  # status envelope Multilogin
    print(response.http_status)  # HTTP status thực tế
    print(response.request_id)  # x-request-id nếu có
```

## Client async

Sync và async có cùng resource/method. Với async, dùng `async with` và `await`.

```python
import asyncio
import os

from multilogin_sdk import AsyncMultiloginClient


async def main() -> None:
    async with AsyncMultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
        workspaces = await client.workspaces.list()
        proxy_account = await client.proxies.user()
        print(workspaces.data.total_count)
        print(proxy_account.data)


asyncio.run(main())
```

`AsyncMultiloginClient` cũng có đầy đủ auth methods. Đăng nhập bất đồng bộ như sau:

```python
import asyncio
import getpass
import os

from multilogin_sdk import AsyncMultiloginClient

email = os.environ["MULTILOGIN_EMAIL"]
password = os.environ.get("MULTILOGIN_PASSWORD") or getpass.getpass(
    "Multilogin password: "
)

async def main() -> None:
    async with AsyncMultiloginClient() as anonymous:
        tokens = (await anonymous.auth.sign_in(email=email, password=password)).data

    async with AsyncMultiloginClient(tokens.token.get_secret_value()) as client:
        workspaces = await client.workspaces.list()
        print(workspaces.data.total_count)


asyncio.run(main())
```

Async có đủ bốn method auth, tương ứng trực tiếp với bản sync:

| Sync | Async |
|---|---|
| `client.auth.sign_in(email, password)` | `await client.auth.sign_in(email, password)` |
| `client.auth.sign_in_with_hash(email, password_md5)` | `await client.auth.sign_in_with_hash(email, password_md5)` |
| `client.auth.refresh(email, refresh_token, workspace_id)` | `await client.auth.refresh(email, refresh_token, workspace_id)` |
| `client.auth.automation_token("1w")` | `await client.auth.automation_token("1w")` |

Refresh cần email, refresh token và workspace ID. Tạo automation token có side effect giống bản sync.

Đổi workspace bất đồng bộ trả về client mới; đóng client mới sau khi dùng:

```python
import asyncio
import os

from multilogin_sdk import AsyncMultiloginClient


async def switch_workspace() -> None:
    async with AsyncMultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as current:
        next_client = await current.switch_workspace(
            email=os.environ["MULTILOGIN_EMAIL"],
            refresh_token=os.environ["MULTILOGIN_REFRESH_TOKEN"],
            workspace_id=os.environ["MULTILOGIN_WORKSPACE_ID"],
        )
        try:
            print((await next_client.workspaces.list()).data)
        finally:
            await next_client.aclose()


asyncio.run(switch_workspace())
```

## Đăng nhập, refresh token và workspace

Khi có email/mật khẩu, SDK có thể gọi luồng Cloud API. Lấy password từ secret manager hoặc environment, không ghi vào source code.

```python
import getpass
import os

from multilogin_sdk import MultiloginClient

email = os.environ["MULTILOGIN_EMAIL"]
password = os.environ.get("MULTILOGIN_PASSWORD") or getpass.getpass("Multilogin password: ")

with MultiloginClient() as anonymous:
    tokens = anonymous.auth.sign_in(email=email, password=password).data
    access_token = tokens.token.get_secret_value()
    refresh_token = tokens.refresh_token.get_secret_value()

with MultiloginClient(access_token) as client:
    print(client.workspaces.list().data)

    # Chỉ tạo automation token mới nếu tác vụ cần token riêng:
    # automation_token = client.auth.automation_token("1w").data.token
```

`sign_in` hash password theo wire protocol Multilogin. `automation_token(...)` tạo token mới, nên có side effect. Kỳ hạn: `1h`, `3h`, `5h`, `16h`, `24h`, `48h`, `1w`, `2w`, `3w`, `1mo`, `no_exp`.

Đổi workspace tạo client mới, không thay token của request đang chạy:

```python
import os

from multilogin_sdk import MultiloginClient

with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as current_client:
    next_client = current_client.switch_workspace(
        email=os.environ["MULTILOGIN_EMAIL"],
        refresh_token=os.environ["MULTILOGIN_REFRESH_TOKEN"],
        workspace_id=os.environ["MULTILOGIN_WORKSPACE_ID"],
    )
    try:
        print(next_client.workspaces.list().data)
    finally:
        next_client.close()
```

Nếu chỉ cần refresh token, không đổi client hoặc workspace:

```python
import os

from multilogin_sdk import MultiloginClient

with MultiloginClient() as client_without_token:
    refreshed = client_without_token.auth.refresh(
        email=os.environ["MULTILOGIN_EMAIL"],
        refresh_token=os.environ["MULTILOGIN_REFRESH_TOKEN"],
        workspace_id=os.environ["MULTILOGIN_WORKSPACE_ID"],
    ).data

with MultiloginClient(refreshed.token.get_secret_value()) as client:
    print(client.workspaces.list().data)
```

Auth payload không dùng Authorization header; các request workspace/profile sau đăng nhập mới dùng bearer token.

## Khởi chạy browser

```python
import os

from multilogin_sdk import MultiloginClient
from multilogin_sdk.models.launcher import LauncherStartRequest

with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
    request = LauncherStartRequest(
        folder_id=os.environ["MULTILOGIN_FOLDER_ID"],
        profile_id=os.environ["MULTILOGIN_PROFILE_ID"],
        automation_type="selenium",  # selenium | puppeteer | playwright
        headless_mode=False,
    )
    with client.launcher.session(request) as connection:
        print(connection.port)
        # Kết nối Selenium / Playwright / Puppeteer vào port này.
```

`launcher.session(...)` chỉ stop profile mà chính session start, kể cả khi code bên trong lỗi. Nếu start timeout hoặc response lỗi, SDK không tự replay start/stop; hãy kiểm tra trạng thái Launcher trước khi thao tác lại.

Stealthfox chỉ hỗ trợ Selenium theo collection. Mimic hỗ trợ Selenium, Puppeteer và Playwright. Khi truyền automation, hãy mở URL bằng automation client thay vì dựa vào `custom_start_urls`.

Async dùng cùng quy tắc sở hữu session:

```python
import asyncio
import os

from multilogin_sdk import AsyncMultiloginClient
from multilogin_sdk.models.launcher import LauncherStartRequest


async def launch() -> None:
    request = LauncherStartRequest(
        folder_id=os.environ["MULTILOGIN_FOLDER_ID"],
        profile_id=os.environ["MULTILOGIN_PROFILE_ID"],
        automation_type="playwright",
    )
    async with AsyncMultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
        async with client.launcher.session(request) as connection:
            print(connection.port)


asyncio.run(launch())
```

## Tạo folder và profile

Mutation nhận Pydantic request model và thay đổi tài khoản thật. Ví dụ dưới đây tạo folder/profile có tên thử nghiệm rồi dọn chúng ở `finally`; chỉ chạy khi bạn muốn tạo các tài nguyên đó.

```python
import os
import uuid

from multilogin_sdk import MultiloginClient
from multilogin_sdk.models.profiles import ProfileCreateRequest, ProfileRemoveRequest
from multilogin_sdk.models.workspaces import FolderCreateRequest, FoldersRemoveRequest

with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
    suffix = uuid.uuid4().hex[:10]
    folder_id = None
    profile_id = None
    try:
        folder = client.folders.create(
            FolderCreateRequest(name=f"sdk-test-{suffix}", comment="SDK example")
        )
        folder_id = str(folder.data["id"])

        created = client.profiles.create(
            ProfileCreateRequest(name=f"sdk-profile-{suffix}", folder_id=folder_id)
        )
        profile_id = str(created.data["ids"][0])
        print("Created profile:", profile_id)
    finally:
        try:
            if profile_id:
                client.profiles.remove(
                    ProfileRemoveRequest(ids=[profile_id], permanently=True)
                )
        finally:
            if folder_id:
                client.folders.remove(FoldersRemoveRequest(ids=[folder_id]))
```

Ví dụ cleanup dùng `permanently=True` chỉ cho profile thử nghiệm vừa tạo; thao tác này xóa profile vĩnh viễn. Với profile của người dùng, `permanently=False` là soft delete. Luôn giữ ID những object do ứng dụng tạo nếu cần dọn dẹp sau đó.

## Resource đã hỗ trợ

| Resource | Methods |
|---|---|
| `auth` | `sign_in`, `sign_in_with_hash`, `refresh`, `automation_token` |
| `workspaces` | `list`, `statistics` |
| `folders` | `list`, `create`, `update`, `remove` |
| `profiles` | `create`, `search`, `iter_profiles`, `update`, `partial_update`, `remove`, `restore`, `metas` |
| `launcher` | `start`, `start_quick`, `stop`, `status`, `statuses`, `version`, `wait_ready`, `session` |
| `proxies` | `user`, `isp_proxies` |
| `objects` | `types`, `statistics` |
| `mobile` | `limit`, `list` |
| `fingerprints` | `resolutions` |
| `cookies` | `websites` |

Danh sách đủ 125 request, trạng thái triển khai và contract mơ hồ: [contracts/operations.json](contracts/operations.json). Chi tiết collection: [audit](docs/research/2026-10-22-multilogin-api-audit.md).

Mỗi method resource có bản sync và async: ví dụ `client.profiles.search(...)` và `await async_client.profiles.search(...)`. Ngoại lệ là iterator/context manager: sync dùng `for`/`with`, async dùng `async for`/`async with`. Các response của folder/profile mutation hiện có `dict[str, object]` ở những payload thay đổi theo server; workspaces, folder list, profile search và launcher connection có model response cụ thể.

## Model, strict mode và pagination

Request model nằm trong `multilogin_sdk.models.profiles`, `.workspaces` và `.launcher`. Pydantic kiểm tra type/constraint trước khi gửi. Field không truyền bị bỏ khỏi JSON; `False`, `0`, `""` và `[]` vẫn được giữ.

`ProfileSearchRequest` luôn gửi 9 trường mà production endpoint yêu cầu, kể cả khi caller dùng default. `iter_profiles` dùng `limit` 1–100 và `offset` tối đa 10000. Nếu gặp trang đầy tại giới hạn này, SDK ném `PaginationLimitError` thay vì báo sai rằng đã đọc hết dữ liệu.

Profile model hỗ trợ browser `mimic`/`stealthfox`, OS `linux`/`macos`/`windows`/`android`; `times` từ 1 đến 10, tối đa 10 tags và 5 custom start URLs. Android chỉ dùng Mimic; ISP proxy yêu cầu `times=1`.

`ClientConfig(strict_mode=True)` gửi `X-Strict-Mode: true` và kiểm tra các field strict đã xác nhận trong collection.

Model create/full update đặt proxy ở `parameters.proxy`; partial update đặt proxy ở root. ISP proxy yêu cầu `host=""` và `times=1` khi tạo profile. Khi chỉ cập nhật vài field, dùng `ProfilePartialUpdateRequest`; bỏ `auto_update_core` khỏi payload có thể khiến server bật lại mặc định, vì vậy gửi `False` tường minh nếu cần giữ core hiện tại.

Ví dụ partial update gửi đúng field cần đổi và giữ lại `False` tường minh:

```python
import os

from multilogin_sdk import MultiloginClient
from multilogin_sdk.models.profiles import ProfilePartialUpdateRequest

request = ProfilePartialUpdateRequest(
    profile_id=os.environ["MULTILOGIN_PROFILE_ID"],
    name="renamed-profile",
    auto_update_core=False,
)
with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
    client.profiles.partial_update(request)
```

## Cấu hình HTTP và lỗi

```python
import httpx
import os

from multilogin_sdk import ClientConfig, MultiloginClient

config = ClientConfig(
    timeout=httpx.Timeout(30, connect=10),
    start_timeout=120,
    max_retries=2,
    retry_budget=30,
)
with MultiloginClient(os.environ["MULTILOGIN_TOKEN"], config=config) as client:
    print(client.workspaces.list().data)
```

TLS verification bật mặc định. Connect timeout mặc định 10 giây; read/write/pool 30 giây. Retry mặc định tắt; khi bật, SDK chỉ retry operation read-only trên `429`, `502`, `503`, `504`. Start/stop profile và tạo token không tự retry.

Nếu chỉ truyền `token`, SDK gửi cùng token tới cả Cloud, Launcher và Cookies service. Có thể đặt token riêng theo service bằng `service_tokens`; chỉ trỏ URL service tùy chỉnh tới host bạn tin cậy vì token bearer được gửi tới origin đó. Session `httpx` tự tạo dùng `trust_env=False`; nếu cần proxy hoặc transport tùy chỉnh, tạo `httpx.Client`/`httpx.AsyncClient` rồi truyền qua `sessions=`. Session do caller truyền vào thì caller tự đóng.

Ví dụ truyền token riêng và URL gateway cho từng service:

```python
from multilogin_sdk import ClientConfig, MultiloginClient

config = ClientConfig(
    cloud_url="https://cloud.example.internal",
    launcher_url="https://launcher.example.internal",
    cookies_url="https://cookies.example.internal",
)
with MultiloginClient(
    config=config,
    service_tokens={
        "cloud": "cloud-token",
        "launcher": "launcher-token",
        "cookies": "cookies-token",
    },
) as client:
    print(client.workspaces.list().data)
```

| Exception | Ý nghĩa |
|---|---|
| `HttpError` | HTTP response không phải 2xx |
| `ApiError` | HTTP thành công nhưng envelope báo lỗi |
| `ProtocolError` | Envelope/payload không khớp contract |
| `TransportError` | Lỗi kết nối hoặc timeout |
| `LauncherUnavailable` | Không kết nối được Launcher |
| `PollingTimeout` | Profile không đạt trạng thái sẵn sàng trước deadline |
| `PaginationLimitError` | Phân trang chạm offset tối đa trong khi trang vẫn đầy |

Xử lý lỗi ở ranh giới tác vụ, ghi operation/status code, và không log token hoặc body:

```python
import os

from multilogin_sdk import MultiloginClient
from multilogin_sdk.errors import ApiError, HttpError, TransportError
from multilogin_sdk.models.profiles import ProfileSearchRequest

try:
    with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
        page = client.profiles.search(ProfileSearchRequest(limit=10, offset=0))
except ApiError as exc:
    print("Multilogin từ chối request:", exc.operation, exc.api_error_code)
except HttpError as exc:
    print("HTTP lỗi:", exc.operation, exc.status_code)
except TransportError as exc:
    print("Không gọi được API:", exc.operation)
```

SDK không đưa raw response body hoặc raw server message vào exception để tránh rò rỉ credential. Token và refresh token dùng `SecretStr`; chỉ gọi `.get_secret_value()` khi thực sự cần.

## Phát triển và kiểm thử

```bash
python -m pip install -r requirements-dev.lock
python -m pip install -e .
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy src/multilogin_sdk
python scripts/check_coverage.py
python -m build
```

Postman simulation kiểm tra HTTP workflow cục bộ, không chứng minh API Multilogin thật hoạt động:

```bash
postman simulation run \
  tests/fixtures/simulation/mvp.sim.yaml --port 4900 --output ndjson --no-history

# Terminal khác
MULTILOGIN_SIMULATION=1 python -m pytest tests/integration/test_simulated_workflow.py -q
```

Máy phát triển cần cài Postman CLI và đặt lệnh `postman` trong `PATH` để chạy simulation.

Live smoke mặc định skip. Chỉ bật bằng `MULTILOGIN_LIVE_TEST=1` trong workspace thử nghiệm vì test tạo profile rồi soft-delete profile do chính nó tạo:

```bash
MULTILOGIN_LIVE_TEST=1 \
MULTILOGIN_TOKEN='...' \
MULTILOGIN_TEST_WORKSPACE_ID='...' \
MULTILOGIN_TEST_FOLDER_ID='...' \
python -m pytest tests/integration/test_live_smoke.py -q
```

Xem thêm [hướng dẫn kỹ thuật](docs/usage.md), [validation](docs/validation.md) và [discrepancy đã biết](contracts/discrepancies.md).
