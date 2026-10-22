import httpx
import pytest
from conftest import envelope, resolve, session_for
from multilogin_sdk import MultiloginClient, AsyncMultiloginClient
from multilogin_sdk._operations import Operation, RequestSpec


async def test_client_lifecycle(mode):
    cls=MultiloginClient if mode=='sync' else AsyncMultiloginClient
    s=session_for(mode,lambda r: httpx.Response(200,json=envelope({})))
    c=cls('secret',sessions={'cloud':s})
    spec=RequestSpec(Operation('read','cloud','GET','/read'))
    assert (await resolve(c._transport.send(spec,dict))).data == {}
    await resolve(c.close() if mode=='sync' else c.aclose())
    await resolve(c.close() if mode=='sync' else c.aclose())
    assert not s.is_closed
    with pytest.raises(RuntimeError):
        await resolve(c._transport.send(spec,dict))
    await resolve(s.close() if mode=='sync' else s.aclose())


async def test_with_token_isolation(mode):
    cls=MultiloginClient if mode=='sync' else AsyncMultiloginClient
    c=cls('first-secret')
    d=c.with_token('second-secret')
    assert d is not c
    assert 'secret' not in repr(c) and 'secret' not in repr(d)
    spec=RequestSpec(Operation('read','cloud','GET','/read'))
    assert c._transport._request(spec).headers['Authorization']=='Bearer first-secret'
    assert d._transport._request(spec).headers['Authorization']=='Bearer second-secret'
    await resolve(d.close() if mode=='sync' else d.aclose())
    assert c._transport._request(spec).headers['Authorization']=='Bearer first-secret'
    await resolve(c.close() if mode=='sync' else c.aclose())


async def test_unauthenticated_operation_rejected(mode):
    cls=MultiloginClient if mode=='sync' else AsyncMultiloginClient
    c=cls()
    with pytest.raises(ValueError):
        await resolve(c._transport.send(RequestSpec(Operation('read','cloud','GET','/read')),dict))
    await resolve(c.close() if mode=='sync' else c.aclose())
