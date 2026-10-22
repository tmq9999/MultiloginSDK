import json

import httpx
import pytest
from conftest import envelope, resolve, session_for

from multilogin_sdk import AsyncMultiloginClient, MultiloginClient
from multilogin_sdk.models.profiles import (
    ProfileCreateRequest,
    ProfileMetasRequest,
    ProfilePartialUpdateRequest,
    ProfileRemoveRequest,
    ProfileRestoreRequest,
    ProfileSearchRequest,
    ProfileUpdateRequest,
)

CASES = [
    (
        "create",
        ProfileCreateRequest(name="x", folder_id="f"),
        "/profile/create",
        {"name": "x", "folder_id": "f"},
        {"ids": ["p"]},
    ),
    (
        "search",
        ProfileSearchRequest(limit=10, offset=0, search_text=""),
        "/profile/search",
        {
            "is_removed": False,
            "core_version": 1,
            "limit": 10,
            "offset": 0,
            "search_text": "",
            "folder_id": "",
            "storage_type": "all",
            "order_by": "created_at",
            "sort": "asc",
        },
        {"profiles": []},
    ),
    (
        "update",
        ProfileUpdateRequest(profile_id="p", name="x"),
        "/profile/update",
        {"profile_id": "p", "name": "x"},
        None,
    ),
    (
        "partial_update",
        ProfilePartialUpdateRequest(profile_id="p", auto_update_core=False),
        "/profile/partial_update",
        {"profile_id": "p", "auto_update_core": False},
        None,
    ),
    (
        "remove",
        ProfileRemoveRequest(ids=["p"], permanently=False),
        "/profile/remove",
        {"ids": ["p"], "permanently": False},
        None,
    ),
    (
        "restore",
        ProfileRestoreRequest(ids=["p"]),
        "/profile/restore",
        {"ids": ["p"]},
        None,
    ),
    (
        "metas",
        ProfileMetasRequest(ids=["p"]),
        "/profile/metas",
        {"ids": ["p"]},
        {"profiles": []},
    ),
]


@pytest.mark.parametrize("method,payload,path,body,data", CASES)
async def test_profile_wire_contract(mode, method, payload, path, body, data):
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=envelope(data))

    s = session_for(mode, handler)
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        "T", sessions={"cloud": s}
    )
    await resolve(getattr(c.profiles, method)(payload))
    assert seen[0].method == "POST" and seen[0].url.path == path
    assert json.loads(seen[0].content) == body
    assert not seen[0].url.query
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())


async def test_strict_remove_requires_explicit_permanently(mode):
    from multilogin_sdk import ClientConfig

    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=envelope())

    s = session_for(mode, handler)
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        "T", config=ClientConfig(strict_mode=True), sessions={"cloud": s}
    )
    with pytest.raises(ValueError):
        await resolve(c.profiles.remove(ProfileRemoveRequest(ids=["p"])))
    assert seen == []
    await resolve(c.profiles.remove(ProfileRemoveRequest(ids=["p"], permanently=False)))
    assert json.loads(seen[0].content) == {"ids": ["p"], "permanently": False}
    assert seen[0].headers["X-Strict-Mode"] == "true"
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())
