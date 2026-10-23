# MultiloginSDK

Python SDK typed, sync và async cho Multilogin Cloud API, Launcher cục bộ và cookie service. Yêu cầu Python 3.11 trở lên.

`0.1.0` hiện triển khai **30/125** request đã audit. Các endpoint đã có contract test; profile search và 9 endpoint discovery đã được xác nhận bằng response API thật. Package chưa phát hành lên PyPI.

## Cài vào project khác

Repository là private. Máy cài cần quyền đọc repository qua GitHub credential, SSH key, GitHub CLI hoặc PAT có quyền `repo`.

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
python -m pip install "git+https://github.com/tmq9999/MultiloginSDK.git@5638ba3"
```

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
```

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
response = client.workspaces.list()
print(response.data)  # payload đã parse
print(response.status)  # status envelope Multilogin
print(response.http_status)  # HTTP status thực tế
print(response.request_id)  # x-request-id an toàn nếu server trả về
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


async def main() -> None:
    email = os.environ["MULTILOGIN_EMAIL"]
    password = os.environ.get("MULTILOGIN_PASSWORD") or getpass.getpass(
        "Multilogin password: "
    )

    async with AsyncMultiloginClient() as anonymous:
        tokens = (await anonymous.auth.sign_in(email=email, password=password)).data

    async with AsyncMultiloginClient(tokens.token.get_secret_value()) as client:
        workspaces = await client.workspaces.list()
        print(workspaces.data.total_count)


asyncio.run(main())
```

Các method auth async tương ứng là `await client.auth.refresh(...)` và `await client.auth.automation_token("1w")`. Refresh cần email, refresh token và workspace ID; tạo automation token có side effect giống bản sync.

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
    # Chỉ tạo token mới nếu ứng dụng cần automation token riêng.
    automation = client.auth.automation_token("1w").data
    os.environ["MULTILOGIN_TOKEN"] = automation.token.get_secret_value()
```

`sign_in` hash password theo wire protocol Multilogin. `automation_token(...)` tạo token mới, nên có side effect. Kỳ hạn: `1h`, `3h`, `5h`, `16h`, `24h`, `48h`, `1w`, `2w`, `3w`, `1mo`, `no_exp`.

Đổi workspace tạo client mới, không thay token của request đang chạy:

```python
next_client = client.switch_workspace(
    email="user@example.com",
    refresh_token=tokens.refresh_token.get_secret_value(),
    workspace_id="workspace-id",
)
try:
    print(next_client.workspaces.list().data)
finally:
    next_client.close()
```

Nếu đã có access token và refresh token, gọi trực tiếp `client.auth.refresh(email, refresh_token, workspace_id)` để nhận cặp token mới. Auth payload không dùng Authorization header; các request workspace/profile sau đăng nhập mới dùng bearer token.

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

Mutation nhận các Pydantic request model. Tạo profile sẽ dùng folder hiện có; `create` trả data có `ids` của profile vừa tạo.

```python
import os

from multilogin_sdk import MultiloginClient
from multilogin_sdk.models.profiles import ProfileCreateRequest
from multilogin_sdk.models.workspaces import FolderCreateRequest

with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
    folder = client.folders.create(
        FolderCreateRequest(name="sdk-test", comment="Created by my app")
    )
    folder_id = str(folder.data["id"])

    created = client.profiles.create(
        ProfileCreateRequest(name="example-profile", folder_id=folder_id)
    )
    profile_id = str(created.data["ids"][0])
```

Không xóa folder/profile của người dùng trong ví dụ khởi động. `profiles.remove(..., permanently=False)` là soft delete; đặt `permanently=True` sẽ xóa vĩnh viễn theo contract.

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

## Model, strict mode và pagination

Request model nằm trong `multilogin_sdk.models.profiles`, `.workspaces` và `.launcher`. Pydantic kiểm tra type/constraint trước khi gửi. Field không truyền bị bỏ khỏi JSON; `False`, `0`, `""` và `[]` vẫn được giữ.

`ProfileSearchRequest` luôn gửi 9 trường mà production endpoint yêu cầu, kể cả khi caller dùng default. `iter_profiles` dùng `limit` 1–100 và `offset` tối đa 10000. Nếu gặp trang đầy tại giới hạn này, SDK ném `PaginationLimitError` thay vì báo sai rằng đã đọc hết dữ liệu.

`ClientConfig(strict_mode=True)` gửi `X-Strict-Mode: true` và kiểm tra các field strict đã xác nhận trong collection.

Model create/full update đặt proxy ở `parameters.proxy`; partial update đặt proxy ở root. ISP proxy yêu cầu `host=""` và `times=1` khi tạo profile. Khi chỉ cập nhật vài field, dùng `ProfilePartialUpdateRequest`; bỏ `auto_update_core` khỏi payload có thể khiến server bật lại mặc định, vì vậy gửi `False` tường minh nếu cần giữ core hiện tại.

## Cấu hình HTTP và lỗi

```python
import httpx

from multilogin_sdk import ClientConfig, MultiloginClient

config = ClientConfig(
    timeout=httpx.Timeout(30, connect=10),
    start_timeout=120,
    max_retries=2,
    retry_budget=30,
)
client = MultiloginClient("token", config=config)
```

TLS verification bật mặc định. Connect timeout mặc định 10 giây; read/write/pool 30 giây. Retry mặc định tắt; khi bật, SDK chỉ retry operation read-only trên `429`, `502`, `503`, `504`. Start/stop profile và tạo token không tự retry.

| Exception | Ý nghĩa |
|---|---|
| `HttpError` | HTTP response không phải 2xx |
| `ApiError` | HTTP thành công nhưng envelope báo lỗi |
| `ProtocolError` | Envelope/payload không khớp contract |
| `TransportError` | Lỗi kết nối hoặc timeout |
| `LauncherUnavailable` | Không kết nối được Launcher |

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
/home/mquangprovip0503/.local/bin/postman simulation run \
  tests/fixtures/simulation/mvp.sim.yaml --port 4900 --output ndjson --no-history

# Terminal khác
MULTILOGIN_SIMULATION=1 python -m pytest tests/integration/test_simulated_workflow.py -q
```

Live smoke mặc định skip. Chỉ bật bằng `MULTILOGIN_LIVE_TEST=1` trong workspace thử nghiệm vì test tạo profile rồi soft-delete profile do chính nó tạo:

```bash
MULTILOGIN_LIVE_TEST=1 \
MULTILOGIN_TOKEN='...' \
MULTILOGIN_TEST_WORKSPACE_ID='...' \
MULTILOGIN_TEST_FOLDER_ID='...' \
python -m pytest tests/integration/test_live_smoke.py -q
```

Xem thêm [hướng dẫn kỹ thuật](docs/usage.md), [validation](docs/validation.md) và [discrepancy đã biết](contracts/discrepancies.md).
