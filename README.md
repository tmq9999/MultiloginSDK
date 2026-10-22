# MultiloginSDK

Python SDK có typing, sync và async cho Multilogin Cloud API và browser Launcher.

**MVP 0.1.0:** 21 request đã triển khai trong collection 125 request. Các thao tác mobile, 2FA, cookies, object storage, import/export và tích hợp Selenium/Playwright thuộc giai đoạn sau. Thư viện chưa được publish lên PyPI.

## Cài đặt

Python >=3.11. Từ checkout:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Token truyền tường minh; nên dùng automation token được tạo trong đúng workspace. Multilogin desktop/agent phải đang chạy để dùng Launcher.

```python
import os
from multilogin_sdk import MultiloginClient
from multilogin_sdk.models.profiles import ProfileSearchRequest

with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
    page = client.profiles.search(ProfileSearchRequest(limit=10, offset=0))
    for profile in page.data.profiles:
        print(profile.id, profile.name)
```

```python
import os
from multilogin_sdk import AsyncMultiloginClient
from multilogin_sdk.models.launcher import LauncherStartRequest


async def run():
    async with AsyncMultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
        async with client.launcher.session(
            LauncherStartRequest(
                folder_id=os.environ["MULTILOGIN_FOLDER_ID"],
                profile_id=os.environ["MULTILOGIN_PROFILE_ID"],
                automation_type="selenium",
            )
        ) as connection:
            print(connection.port)
```

Session start một lần, chờ browser_running và stop profile vừa start khi thoát, kể cả lỗi ứng dụng. Không tự stop profile khác. Nếu start timeout hoặc response lỗi, SDK không biết chắc profile đã chạy hay chưa và không tự gửi start/stop lại; kiểm tra trạng thái phía Launcher.

## Phạm vi đã hỗ trợ

| Resource | Methods | Request IDs |
|---|---|---:|
| auth | sign_in, refresh, automation_token; sign_in_with_hash là helper | 3 |
| workspaces | list | 1 |
| folders | list, create, update, remove | 4 |
| profiles | create, search, update, partial_update, remove, restore, metas | 7 |
| launcher | start v2, quick v3, stop, status, statuses, version | 6 |

Helpers: with_token, switch_workspace, iter_profiles, wait_ready, session. Xem [hướng dẫn](docs/usage.md), [registry](contracts/operations.json), [mâu thuẫn contract](contracts/discrepancies.md) và [bằng chứng kiểm thử](docs/validation.md).

## Phát triển và kiểm thử

```bash
python -m pip install -r requirements-dev.lock
python -m pip install -e .
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src/multilogin_sdk
python scripts/check_coverage.py
python -m build
```

Lock ghi nhận môi trường phát triển; dependencies runtime trong pyproject dùng khoảng version. CI kiểm tra Python 3.11 và 3.14.

Postman simulation chạy local, không publish hay deploy:

```bash
postman simulation run tests/fixtures/simulation/mvp.sim.yaml --port 4900 --output ndjson --no-history
# Terminal khác:
MULTILOGIN_SIMULATION=1 python -m pytest tests/integration/test_simulated_workflow.py -q
```

Nếu `postman` không trên PATH tại máy hiện tại, dùng `/home/mquangprovip0503/.local/bin/postman`. Simulation dùng các mocks từ contract, vì workspace được cung cấp không có owner mock. Nó kiểm tra luồng HTTP và lỗi SDK, không chứng minh API Multilogin thật hoạt động. Các route không mô phỏng trả 501.

Live smoke mặc định bị skip. Chỉ bật trên workspace thử nghiệm với token, workspace ID và folder ID riêng; test tạo profile rồi soft-delete profile nó sở hữu. Không chạy toàn bộ collection như một test suite.
