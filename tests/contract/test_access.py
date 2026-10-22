import json

import httpx
import pytest
from conftest import envelope, resolve, session_for

from multilogin_sdk import AsyncMultiloginClient, MultiloginClient
from multilogin_sdk.models.workspaces import (
    FolderCreateRequest,
    FoldersRemoveRequest,
    FolderUpdateRequest,
)

CASES = [
    (
        "auth",
        "sign_in",
        ("a", "password"),
        "POST",
        "/user/signin",
        {"email": "a", "password": "5f4dcc3b5aa765d61d8327deb882cf99"},
        {"token": "T", "refresh_token": "R"},
    ),
    (
        "auth",
        "refresh",
        ("a", "r", "w"),
        "POST",
        "/user/refresh_token",
        {"email": "a", "refresh_token": "r", "workspace_id": "w"},
        {"token": "T", "refresh_token": "R"},
    ),
    (
        "auth",
        "automation_token",
        ("1h",),
        "GET",
        "/workspace/automation_token",
        None,
        {"token": "T"},
    ),
    (
        "workspaces",
        "list",
        (),
        "GET",
        "/user/workspaces",
        None,
        {"workspaces": [], "total_count": 0},
    ),
    ("folders", "list", (), "GET", "/workspace/folders", None, {"folders": []}),
    (
        "folders",
        "create",
        (FolderCreateRequest(name="x", comment=""),),
        "POST",
        "/workspace/folder_create",
        {"name": "x", "comment": ""},
        {"id": "f"},
    ),
    (
        "folders",
        "update",
        (FolderUpdateRequest(folder_id="f", name="y", comment=""),),
        "POST",
        "/workspace/folder_update",
        {"folder_id": "f", "name": "y", "comment": ""},
        None,
    ),
    (
        "folders",
        "remove",
        (FoldersRemoveRequest(ids=["f"]),),
        "POST",
        "/workspace/folders_remove",
        {"ids": ["f"]},
        None,
    ),
]


@pytest.mark.parametrize("resource,method,args,http_method,path,body,data", CASES)
async def test_access_wire_contract(
    mode, resource, method, args, http_method, path, body, data
):
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=envelope(data))

    s = session_for(mode, handler)
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        "T", sessions={"cloud": s}
    )
    await resolve(getattr(getattr(c, resource), method)(*args))
    req = seen[0]
    assert req.method == http_method and req.url.path == path
    assert (json.loads(req.content) if req.content else None) == body
    assert dict(req.url.params) == (
        {"expiration_period": "1h"} if method == "automation_token" else {}
    )
    assert "X-Strict-Mode" not in req.headers
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())
