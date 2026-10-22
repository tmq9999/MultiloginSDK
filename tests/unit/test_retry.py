import httpx
import pytest
from conftest import resolve, session_for, envelope
from multilogin_sdk._operations import Operation, RequestSpec
from multilogin_sdk._transport import SyncTransport, AsyncTransport
from multilogin_sdk._retry import retry_delay
from multilogin_sdk.config import ClientConfig
from multilogin_sdk.errors import HttpError


@pytest.mark.parametrize('safe,retries,status,expected',[(True,0,429,1),(True,2,429,3),(True,2,502,3),(True,2,503,3),(True,2,504,3),(False,2,503,1),(True,2,401,1),(True,2,403,1)])
async def test_retry_operation_policy(mode,safe,retries,status,expected):
    calls=[]; sleeps=[]
    def handler(req):
        calls.append(req)
        return httpx.Response(status,json=envelope({},code=status),headers={'Retry-After':'0'})
    s=session_for(mode,handler)
    cls=SyncTransport if mode=='sync' else AsyncTransport
    async def async_sleep(delay): sleeps.append(delay)
    t=cls(ClientConfig(max_retries=retries),tokens={'cloud':'s'},sessions={'cloud':s},sleeper=sleeps.append if mode=='sync' else async_sleep)
    with pytest.raises(HttpError):
        await resolve(t.send(RequestSpec(Operation('start','cloud','GET','/x',read_only=safe)),dict))
    assert len(calls)==expected
    await resolve(t.close() if mode=='sync' else t.aclose())
    await resolve(s.close() if mode=='sync' else s.aclose())


def test_retry_after_values_and_budget():
    assert retry_delay('4',0,10,now=0,jitter=0)==4
    assert retry_delay('Thu, 01 Jan 1970 00:00:05 GMT',0,10,now=0,jitter=0)==5
    assert retry_delay('invalid',0,10,now=0,jitter=0)==0.5
    assert retry_delay('40',0,10,now=0,jitter=0) is None
