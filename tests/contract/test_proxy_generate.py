import httpx
import pytest
from conftest import envelope, resolve, session_for
from pydantic import ValidationError

from multilogin_sdk import AsyncMultiloginClient, MultiloginClient
from multilogin_sdk.config import ClientConfig
from multilogin_sdk.errors import ApiError, HttpError
from multilogin_sdk.models.proxies import ProxyGenerateRequest

SECRET = "h.example:1:proxyuser:s3cretpw"
BASE = {"country": "US", "protocol": "http", "session_type": "sticky"}


def make_client(mode, handler, **config):
    s = session_for(mode, handler)
    cls = MultiloginClient if mode == "sync" else AsyncMultiloginClient
    c = cls("T", config=ClientConfig(**config), sessions={"cloud": s})
    return c, s


async def close(mode, c, s):
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())


async def test_generate_wire_contract(mode):
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=envelope({"connection_urls": [SECRET]}))

    c, s = make_client(mode, handler)
    req = ProxyGenerateRequest(
        **BASE,
        region="CA",
        city="LA",
        ip_ttl=30,
        count=100,
        connection_type="mobile",
        isp="att",
    )
    resp = await resolve(c.proxies.generate(req))
    r = seen[0]
    assert r.method == "GET" and r.url.path == "/proxynm/connection_url"
    assert r.content == b""
    assert r.headers["Authorization"] == "Bearer T"
    assert dict(r.url.params) == {
        "country": "US",
        "protocol": "http",
        "session_type": "sticky",
        "region": "CA",
        "city": "LA",
        "ip_ttl": "30",
        "count": "100",
        "connection_type": "mobile",
        "isp": "att",
    }
    assert resp.data.connection_urls == [SECRET]
    await close(mode, c, s)


async def test_generate_omits_unset_optional_params(mode):
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=envelope({"connection_urls": []}))

    c, s = make_client(mode, handler)
    await resolve(c.proxies.generate(ProxyGenerateRequest(**BASE, count=1)))
    await resolve(c.proxies.generate(ProxyGenerateRequest(**BASE)))
    assert dict(seen[0].url.params) == {**BASE, "count": "1"}
    assert dict(seen[1].url.params) == BASE
    await close(mode, c, s)


@pytest.mark.parametrize(
    "override",
    [
        {"count": 0},
        {"count": 101},
        {"count": True},
        {"count": "5"},
        {"protocol": "https"},
        {"session_type": "static"},
        {"connection_type": "datacenter"},
        {"country": ""},
        {"ip_ttl": 0},
        {"unknown": 1},
    ],
)
def test_generate_request_validation(override):
    with pytest.raises(ValidationError):
        ProxyGenerateRequest(**{**BASE, **override})
    with pytest.raises(ValidationError):
        ProxyGenerateRequest(country="US", protocol="http")


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
async def test_generate_never_auto_retries(mode, status):
    calls = []

    def handler(req):
        calls.append(req)
        return httpx.Response(
            status, json=envelope(None, code=status), headers={"Retry-After": "0"}
        )

    c, s = make_client(mode, handler, max_retries=2)
    with pytest.raises(HttpError) as exc:
        await resolve(c.proxies.generate(ProxyGenerateRequest(**BASE)))
    assert len(calls) == 1
    assert exc.value.status_code == status
    await close(mode, c, s)


async def test_generate_redacts_credentials(mode):
    def ok(req):
        return httpx.Response(200, json=envelope({"connection_urls": [SECRET]}))

    c, s = make_client(mode, ok)
    resp = await resolve(c.proxies.generate(ProxyGenerateRequest(**BASE)))
    for text in (repr(resp), repr(resp.data), str(resp.data.model_dump())):
        assert "s3cretpw" not in text and "proxyuser" not in text
    assert resp.data.connection_urls[0] == SECRET
    await close(mode, c, s)

    def api_error(req):
        return httpx.Response(
            200,
            json=envelope(
                {"connection_urls": [SECRET]},
                code=400,
                error="PROXY_ERR",
                message=f"bad {SECRET}",
            ),
        )

    c, s = make_client(mode, api_error)
    with pytest.raises(ApiError) as exc:
        await resolve(c.proxies.generate(ProxyGenerateRequest(**BASE)))
    assert "s3cretpw" not in str(exc.value) + repr(exc.value)
    assert "proxyuser" not in str(exc.value) + repr(exc.value)
    assert exc.value.api_error_code == "PROXY_ERR"
    await close(mode, c, s)

    def http_error(req):
        return httpx.Response(500, text=f"boom {SECRET}")

    c, s = make_client(mode, http_error)
    with pytest.raises(HttpError) as exc:
        await resolve(c.proxies.generate(ProxyGenerateRequest(**BASE)))
    assert "s3cretpw" not in str(exc.value) + repr(exc.value)
    await close(mode, c, s)
