import httpx
import pytest
from conftest import envelope, resolve, session_for
from multilogin_sdk._transport import SyncTransport, AsyncTransport
from multilogin_sdk._operations import Operation, RequestSpec
from multilogin_sdk.config import ClientConfig
from multilogin_sdk.errors import HttpError, LauncherUnavailable


async def test_service_routing_and_url_encoding(mode):
    seen = []
    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=envelope({}))
    sessions = {s: session_for(mode, handler) for s in ['cloud', 'launcher', 'cookies']}
    cls = SyncTransport if mode == 'sync' else AsyncTransport
    transport = cls(ClientConfig(), tokens={'cloud': 'cloud-secret', 'launcher': 'launch-secret', 'cookies': 'cookie-secret'}, sessions=sessions)
    for service in sessions:
        spec = RequestSpec(Operation('read', service, 'GET', '/items/{id}', read_only=True), path_params={'id': 'abc/def?x=#'})
        await resolve(transport.send(spec, dict))
    assert [r.url.host for r in seen] == ['api.multilogin.com', 'launcher.mlx.yt', 'cookies.multilogin.com']
    assert [r.headers['authorization'] for r in seen] == ['Bearer cloud-secret', 'Bearer launch-secret', 'Bearer cookie-secret']
    assert b'abc%2Fdef%3Fx%3D%23' in seen[0].url.raw_path
    assert seen[0].extensions['timeout'] == {'connect':10, 'read':30, 'write':30, 'pool':30}
    await resolve(transport.close() if mode == 'sync' else transport.aclose())
    assert not any(s.is_closed for s in sessions.values())
    for s in sessions.values():
        await resolve(s.close() if mode == 'sync' else s.aclose())


async def test_no_cross_origin_redirect(mode):
    seen = []
    def handler(req):
        seen.append(req)
        return httpx.Response(302, headers={'Location': 'https://untrusted.test'})
    s = session_for(mode, handler)
    cls = SyncTransport if mode == 'sync' else AsyncTransport
    t = cls(ClientConfig(), tokens={'cloud':'secret'}, sessions={'cloud':s})
    with pytest.raises(HttpError):
        await resolve(t.send(RequestSpec(Operation('read','cloud','GET','/x')), dict))
    assert len(seen) == 1
    await resolve(t.close() if mode == 'sync' else t.aclose())
    await resolve(s.close() if mode == 'sync' else s.aclose())


async def test_noauth_ignores_injected_default_auth(mode):
    seen = []
    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=envelope({}))
    s = session_for(mode, handler)
    s.headers['Authorization'] = 'Bearer accidental'
    cls = SyncTransport if mode == 'sync' else AsyncTransport
    t = cls(ClientConfig(), tokens={}, sessions={'cloud':s})
    await resolve(t.send(RequestSpec(Operation('signin','cloud','POST','/signin',auth_required=False)), dict))
    assert 'authorization' not in seen[0].headers
    await resolve(t.close() if mode == 'sync' else t.aclose())
    await resolve(s.close() if mode == 'sync' else s.aclose())


async def test_launcher_unavailable(mode):
    def handler(req):
        raise httpx.ConnectError('secret', request=req)
    s = session_for(mode,handler)
    cls = SyncTransport if mode=='sync' else AsyncTransport
    t=cls(ClientConfig(),tokens={'launcher':'secret'},sessions={'launcher':s})
    with pytest.raises(LauncherUnavailable) as e:
        await resolve(t.send(RequestSpec(Operation('version','launcher','GET','/version')),dict))
    assert 'desktop' in str(e.value) and 'secret' not in str(e.value)
    await resolve(t.close() if mode=='sync' else t.aclose())
    await resolve(s.close() if mode=='sync' else s.aclose())
