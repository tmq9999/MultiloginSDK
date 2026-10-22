import httpx
import pytest
from pydantic import ValidationError
from conftest import envelope
from multilogin_sdk._operations import Operation
from multilogin_sdk._response import parse_response
from multilogin_sdk.models.launcher import BrowserConnection,QuickProfileV3Request
from multilogin_sdk.errors import ProtocolError


@pytest.mark.parametrize('port',['bad','0','65536',True,None])
def test_invalid_connection_port(port):
    with pytest.raises(ProtocolError):
        parse_response(httpx.Response(200,json=envelope({'id':'p','port':port,'browser_type':'mimic','is_quick':False})),Operation('start','launcher','GET','/x'),BrowserConnection)


def test_normalized_connection():
    c=BrowserConnection.model_validate({'id':'p','port':'55513','browser_type':'mimic','is_quick':False,'future':42})
    assert c.port==55513 and c.model_dump()['future']==42


def test_stealthfox_playwright_rejected():
    with pytest.raises(ValidationError):
        QuickProfileV3Request(browser_type='stealthfox',automation='playwright')
    with pytest.raises(ValidationError):
        QuickProfileV3Request(parameters={'flags':{'canvas_noise:':'mask'}})
