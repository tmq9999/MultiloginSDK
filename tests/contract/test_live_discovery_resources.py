import httpx
import pytest
from conftest import envelope, resolve, session_for

from multilogin_sdk import AsyncMultiloginClient, MultiloginClient

CASES = [
    ("proxies", "user", "cloud", "/proxynm/user", {"workspace_id": "w"}),
    ("proxies", "isp_proxies", "cloud", "/proxynm/isp/proxies", []),
    ("objects", "types", "cloud", "/api/v1/resources/types", {"types": []}),
    (
        "objects",
        "statistics",
        "cloud",
        "/api/v1/resources/statistics",
        {"global_count": 0},
    ),
    ("mobile", "limit", "cloud", "/mobile_profiles/limit", {"remaining_limit": 0}),
    (
        "mobile",
        "list",
        "cloud",
        "/mobile_profiles/phone/list",
        {"items": [], "page": 1, "page_size": 20, "total": 0},
    ),
    ("fingerprints", "resolutions", "cloud", "/fpb/resolutions", {"resolutions": []}),
    (
        "workspaces",
        "statistics",
        "cloud",
        "/workspace/statistics",
        {"active_profiles_count": 0},
    ),
    (
        "cookies",
        "websites",
        "cookies",
        "/api/v1/cookies/metadata/websites",
        [{"key": "example", "value": "Example"}],
    ),
]


@pytest.mark.parametrize("resource,method,service,path,data", CASES)
async def test_live_discovery_resource_wire_contract(
    mode, resource, method, service, path, data
):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json=envelope(data))

    session = session_for(mode, handler)
    client_type = MultiloginClient if mode == "sync" else AsyncMultiloginClient
    client = client_type("T", sessions={service: session})

    response = await resolve(getattr(getattr(client, resource), method)())

    assert response.data == data
    assert seen[0].method == "GET"
    assert seen[0].url.path == path
    assert not seen[0].content
    await resolve(client.close() if mode == "sync" else client.aclose())
    await resolve(session.close() if mode == "sync" else session.aclose())
