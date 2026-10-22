import json

import httpx
import pytest
from conftest import envelope, resolve, session_for

from multilogin_sdk import AsyncMultiloginClient, MultiloginClient


async def test_password_hash_once(mode):
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(
            200, json=envelope({"token": "TOKEN", "refresh_token": "REFRESH"})
        )

    s = session_for(mode, handler)
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        sessions={"cloud": s}
    )
    result = await resolve(c.auth.sign_in("a@example.test", "password"))
    assert json.loads(seen[0].content)["password"] == "5f4dcc3b5aa765d61d8327deb882cf99"
    assert "authorization" not in seen[0].headers
    assert "TOKEN" not in repr(result) and "REFRESH" not in repr(result)
    await resolve(c.auth.sign_in_with_hash("a@example.test", "0" * 32))
    assert json.loads(seen[-1].content)["password"] == "0" * 32
    with pytest.raises(ValueError):
        await resolve(c.auth.sign_in_with_hash("a", "bad"))
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())


async def test_workspace_switch_isolation(mode):
    s = session_for(
        mode,
        lambda r: httpx.Response(
            200, json=envelope({"token": "NEW", "refresh_token": "NEXT"})
        ),
    )
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        "OLD", sessions={"cloud": s}
    )
    d = await resolve(
        c.switch_workspace(email="a", refresh_token="refresh", workspace_id="w")
    )
    assert d is not c
    from multilogin_sdk._operations import Operation, RequestSpec

    spec = RequestSpec(Operation("read", "cloud", "GET", "/read"))
    assert c._transport._request(spec).headers["Authorization"] == "Bearer OLD"
    assert d._transport._request(spec).headers["Authorization"] == "Bearer NEW"
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(d.close() if mode == "sync" else d.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())
