# MVP validation — 2026-10-23

Nguồn contract: collection `46206122-78bf4173-0a22-4651-890d-b160177d47b1`, Postman CLI 1.76.0.

## Bằng chứng đã chạy

- Local Python 3.14.4: 146 tests pass khi bật simulation, 1 live smoke skip; mặc định 141 pass và 6 integration/live tests skip.
- Registry: 125 request IDs duy nhất khớp audit; 21 implemented có test function thật; các operation còn lại deferred/blocked có lý do.
- Lint (Ruff), format và mypy strict kiểm tra package.
- Build wheel và sdist; cài riêng trong hai venv sạch, kiểm tra import sync/async client, py.typed và example imports.
- Simulation log ngoài Git có listening và request events theo routeKey cloud/launcher; cookies member hiện chỉ reset vì cookies chưa nằm trong MVP.
- Luồng create → start → status → stop chạy ở sync/async; lỗi ứng dụng vẫn cleanup, 429 trên read-only search được retry, 503 trên start không retry, status timeout vẫn stop profile đã start.

Mocks local được viết từ body/response shapes của collection. CLI mock list trên workspace được cung cấp trả danh sách rỗng; không có owner mock để tái sử dụng. Responses mâu thuẫn HTTP/envelope được giữ như negative tests; successful simulation responses là fixtures chuẩn hóa, chưa phải bằng chứng live.

## Cách tái lập

```bash
python -m pip install -r requirements-dev.lock
python -m pip install -e .
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy src/multilogin_sdk
python scripts/check_coverage.py
python -m build
postman simulation run tests/fixtures/simulation/mvp.sim.yaml --port 4900 --output ndjson --no-history
# Terminal khác
MULTILOGIN_SIMULATION=1 python -m pytest tests/integration/test_simulated_workflow.py -q
```

## Giới hạn

Chưa dùng token Multilogin thật, chưa start browser/profile thật, chưa xác nhận TLS Launcher tại máy người dùng hoặc quota của tài khoản. GitHub CI run39822802822 đã pass Python3.11, Python3.14 và Postman simulation trên commit ac555ee. Không publish package. Bộ simulation không xác nhận toàn bộ125 requests.

MVP folder_update Cloud origin suy luận từ cùng biến baseUrl đã được thay bằng api.multilogin.com trong các saved request create/remove/revoke; global thực tế thiếu biến này. Xem discrepancies.md và spec cho các operation chưa đủ bằng chứng.

CI evidence: https://github.com/tmq9999/MultiloginSDK/actions/runs/39822802822

Sau independent review: sửa strict-remove validation bằng regression test RED→GREEN cho sync/async; local suite146 pass/1 live skip.
