import httpx
from conftest import envelope

from multilogin_sdk._operations import Operation
from multilogin_sdk._redaction import redact
from multilogin_sdk._response import parse_response
from multilogin_sdk.errors import HttpError


def test_recursive_redaction():
    value = {
        "message": "oops TOKEN",
        "cookies": [{"value": "COOKIE"}],
        "proxy": {"password": "PWD"},
        "nested": {"pwd": "ADB"},
    }
    safe = redact(value, ["TOKEN"])
    assert all(x not in str(safe) for x in ["TOKEN", "COOKIE", "PWD", "ADB"])


def test_error_message_secret_redaction():
    try:
        parse_response(
            httpx.Response(
                500, json=envelope({"password": "PWD"}, message="TOKEN PWD COOKIE ADB")
            ),
            Operation("read", "cloud", "GET", "/x"),
            dict,
        )
    except HttpError as e:
        assert all(s not in repr(e) for s in ["TOKEN", "PWD", "COOKIE", "ADB"])
    else:
        raise AssertionError("HTTP error not raised")
