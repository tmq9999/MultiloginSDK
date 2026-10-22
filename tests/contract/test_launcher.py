import json

import httpx
import pytest
from conftest import envelope, resolve, session_for

from multilogin_sdk import AsyncMultiloginClient, ClientConfig, MultiloginClient
from multilogin_sdk.models.launcher import LauncherStartRequest, QuickProfileV3Request

CONNECTION = {
    "id": "p",
    "port": "55513",
    "browser_type": "mimic",
    "core_version": 132,
    "is_quick": False,
}
CASES = [
    (
        "start",
        (LauncherStartRequest(folder_id="f", profile_id="p", headless_mode=False),),
        "GET",
        "/api/v2/profile/f/f/p/p/start",
        None,
        CONNECTION,
    ),
    (
        "quick",
        (
            QuickProfileV3Request(
                browser_type="mimic",
                parameters={"proxy": {"host": "proxy", "port": 8080}},
            ),
        ),
        "POST",
        "/api/v3/profile/quick",
        {
            "browser_type": "mimic",
            "parameters": {"proxy": {"host": "proxy", "port": 8080}},
        },
        CONNECTION,
    ),
    ("stop", ("p",), "GET", "/api/v1/profile/stop/p/p", None, None),
    (
        "status",
        ("p",),
        "GET",
        "/api/v1/profile/status/p/p",
        None,
        {"status": "browser_running"},
    ),
    ("statuses", (), "GET", "/api/v1/profile/statuses", None, {"states": {}}),
    ("version", (), "GET", "/api/v1/version", None, {"version": "1"}),
]


@pytest.mark.parametrize("method,args,http_method,path,body,data", CASES)
async def test_launcher_wire_contract(
    mode, method, args, http_method, path, body, data
):
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=envelope(data))

    s = session_for(mode, handler)
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        "T", sessions={"launcher": s}
    )
    await resolve(getattr(c.launcher, method)(*args))
    req = seen[0]
    assert req.method == http_method and req.url.path == path
    assert (json.loads(req.content) if req.content else None) == body
    assert dict(req.url.params) == (
        {"automation_type": "selenium", "headless_mode": "false"}
        if method == "start"
        else {}
    )
    assert "X-Strict-Mode" not in req.headers
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())


async def test_strict_mode_rejects_missing_confirmed_fields(mode):
    s = session_for(mode, lambda r: httpx.Response(200, json=envelope(CONNECTION)))
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        "T", config=ClientConfig(strict_mode=True), sessions={"launcher": s}
    )
    with pytest.raises(ValueError):
        await resolve(c.launcher.quick(QuickProfileV3Request()))
    result = await resolve(
        c.launcher.start(LauncherStartRequest(folder_id="f", profile_id="p"))
    )
    assert result.data.port == 55513
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())
