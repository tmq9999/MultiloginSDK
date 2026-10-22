import asyncio

import httpx
import pytest
from conftest import envelope, resolve, session_for

from multilogin_sdk import AsyncMultiloginClient, MultiloginClient
from multilogin_sdk.errors import HttpError, PollingTimeout
from multilogin_sdk.models.launcher import LauncherStartRequest

REQ = LauncherStartRequest(folder_id="f", profile_id="p")
CONN = {"id": "owned", "port": "55513", "browser_type": "mimic", "is_quick": False}


@pytest.mark.parametrize(
    "failure", ["none", "start", "wait", "body", "body_cleanup", "cleanup"]
)
async def test_session_owned_lifecycle(mode, failure):
    paths = []

    def handler(req):
        paths.append(req.url.path)
        if req.url.path.endswith("/start"):
            return httpx.Response(
                500 if failure == "start" else 200, json=envelope(CONN)
            )
        if "/status/" in req.url.path:
            return httpx.Response(
                500 if failure == "wait" else 200,
                json=envelope({"status": "browser_running"}),
            )
        if "/stop/" in req.url.path:
            return httpx.Response(
                500 if failure in {"body_cleanup", "cleanup"} else 200, json=envelope()
            )
        return httpx.Response(501)

    s = session_for(mode, handler)
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        "T", sessions={"launcher": s}
    )

    async def run():
        if mode == "sync":
            with c.launcher.session(REQ) as result:
                assert result.id == "owned"
                if failure.startswith("body"):
                    raise LookupError("application error")
        else:
            async with c.launcher.session(REQ) as result:
                assert result.id == "owned"
                if failure.startswith("body"):
                    raise LookupError("application error")

    if failure in {"start", "wait", "cleanup"}:
        with pytest.raises(HttpError):
            await run()
    elif failure.startswith("body"):
        with pytest.raises(LookupError) as exc:
            await run()
        if failure == "body_cleanup":
            assert "cleanup" in exc.value.__notes__[0]
    else:
        await run()
    assert sum(p.endswith("/start") for p in paths) == 1
    assert sum("/stop/" in p for p in paths) == (0 if failure == "start" else 1)
    assert all(p.endswith("/owned") for p in paths if "/stop/" in p)
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())


async def test_async_cancellation_cleanup_bounded():
    calls = []
    stop_begun = asyncio.Event()
    cancelled_stop = asyncio.Event()

    async def handler(req):
        calls.append(req.url.path)
        if req.url.path.endswith("/start"):
            return httpx.Response(200, json=envelope(CONN))
        if "/status/" in req.url.path:
            return httpx.Response(200, json=envelope({"status": "browser_running"}))
        stop_begun.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled_stop.set()

    s = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    async with AsyncMultiloginClient("T", sessions={"launcher": s}) as c:
        ready = asyncio.Event()

        async def body():
            async with c.launcher.session(REQ, cleanup_timeout=0.01):
                ready.set()
                await asyncio.Event().wait()

        task = asyncio.create_task(body())
        await asyncio.wait_for(ready.wait(), 0.2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, 1)
        assert stop_begun.is_set() and cancelled_stop.is_set()
        assert sum("/stop/" in p for p in calls) == 1
    await s.aclose()


async def test_polling_deadline(mode, monkeypatch):
    from multilogin_sdk import _session

    clock = [0.0]
    calls = []
    monkeypatch.setattr(_session, "monotonic", lambda: clock[0])

    def sleep(dt):
        clock[0] += dt

    async def asleep(dt):
        clock[0] += dt

    monkeypatch.setattr(_session, "sleep", sleep)
    monkeypatch.setattr(_session, "async_sleep", asleep)

    def handler(req):
        calls.append(req)
        return httpx.Response(200, json=envelope({"status": "future_state"}))

    s = session_for(mode, handler)
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        "T", sessions={"launcher": s}
    )
    with pytest.raises(PollingTimeout):
        await resolve(c.launcher.wait_ready("p", timeout=2, poll_interval=1))
    assert len(calls) == 2 and clock[0] == 2
    assert all(r.extensions["timeout"]["read"] <= 2 for r in calls)
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())
