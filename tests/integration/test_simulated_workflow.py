"""Real HTTP tests against the checked-in Postman simulation."""

import asyncio
import os

import httpx
import pytest

from multilogin_sdk import AsyncMultiloginClient, ClientConfig, MultiloginClient
from multilogin_sdk.errors import HttpError, TransportError
from multilogin_sdk.models.launcher import LauncherStartRequest
from multilogin_sdk.models.profiles import ProfileCreateRequest, ProfileSearchRequest

BASE = os.environ.get("MULTILOGIN_SIM_URL", "http://127.0.0.1:4900")
pytestmark = [
    pytest.mark.simulation,
    pytest.mark.skipif(
        os.environ.get("MULTILOGIN_SIMULATION") != "1",
        reason="Start checked-in Postman simulation and set MULTILOGIN_SIMULATION=1",
    ),
]


def config(**kwargs):
    return ClientConfig(
        cloud_url=BASE + "/cloud",
        launcher_url=BASE + "/launcher",
        cookies_url=BASE + "/cookies",
        **kwargs,
    )


def reset():
    for member in ["cloud", "launcher", "cookies"]:
        r = httpx.post(BASE + "/" + member + "/__reset", timeout=2)
        r.raise_for_status()


async def test_create_start_status_stop_workflow(mode):
    await asyncio.to_thread(reset)
    if mode == "sync":
        with MultiloginClient("sim", config=config()) as c:
            profile = c.profiles.create(
                ProfileCreateRequest(name="simulation", folder_id="f")
            ).data["ids"][0]
            with (
                pytest.raises(LookupError),
                c.launcher.session(
                    LauncherStartRequest(folder_id="f", profile_id=profile)
                ),
            ):
                raise LookupError("application error")
            assert c.launcher.status(profile).data["status"] == "stopped"
    else:
        async with AsyncMultiloginClient("sim", config=config()) as c:
            profile = (
                await c.profiles.create(
                    ProfileCreateRequest(name="simulation", folder_id="f")
                )
            ).data["ids"][0]
            with pytest.raises(LookupError):
                async with c.launcher.session(
                    LauncherStartRequest(folder_id="f", profile_id=profile)
                ):
                    raise LookupError("application error")
            assert (await c.launcher.status(profile)).data["status"] == "stopped"
    async with httpx.AsyncClient() as observer:
        stats = (await observer.get(BASE + "/launcher/__stats")).json()
    assert stats["starts"] == 1 and stats["stops"] == 1


def test_rate_limit_safe_search_and_unsafe_start():
    reset()
    with MultiloginClient("sim", config=config(max_retries=2)) as c:
        assert (
            c.profiles.search(
                ProfileSearchRequest(search_text="rate-limit")
            ).data.profiles
            == []
        )
        with pytest.raises(HttpError):
            c.launcher.start(
                LauncherStartRequest(folder_id="f", profile_id="start-503")
            )
    assert httpx.get(BASE + "/cloud/__stats").json()["searches"] == 2
    assert httpx.get(BASE + "/launcher/__stats").json()["starts"] == 1


async def test_status_timeout_cleans_up(mode):
    await asyncio.to_thread(reset)
    cfg = config(timeout=httpx.Timeout(0.05))
    if mode == "sync":
        with MultiloginClient("sim", config=cfg) as c, pytest.raises(TransportError):
            with c.launcher.session(
                LauncherStartRequest(folder_id="f", profile_id="status-hang"),
                wait_timeout=0.03,
            ):
                pass
    else:
        from multilogin_sdk.errors import PollingTimeout

        async with AsyncMultiloginClient("sim", config=cfg) as c:
            with pytest.raises((TransportError, PollingTimeout)):
                async with c.launcher.session(
                    LauncherStartRequest(folder_id="f", profile_id="status-hang"),
                    wait_timeout=0.03,
                ):
                    pass
    async with httpx.AsyncClient() as observer:
        assert (await observer.get(BASE + "/launcher/__stats")).json()["stops"] == 1
