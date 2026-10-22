import httpx
import pytest
from conftest import envelope

from multilogin_sdk._operations import Operation
from multilogin_sdk._response import parse_response
from multilogin_sdk.errors import ApiError, HttpError, ProtocolError


@pytest.mark.parametrize(
    "http_status,body,error",
    [
        (500, envelope({}, code=200), HttpError),
        (200, envelope({}, error="BAD"), ApiError),
        (200, envelope({}, code=403), ApiError),
        (200, {}, ProtocolError),
        (200, envelope({}, code=0), ProtocolError),
        (
            200,
            {"status": {"http_code": True, "error_code": "", "message": ""}},
            ProtocolError,
        ),
    ],
)
def test_response_failure_classification(http_status, body, error):
    with pytest.raises(error):
        parse_response(
            httpx.Response(http_status, json=body),
            Operation("read", "cloud", "GET", "/x"),
            dict,
        )


def test_bad_json():
    with pytest.raises(ProtocolError):
        parse_response(
            httpx.Response(200, content="broken"),
            Operation("read", "cloud", "GET", "/x"),
            dict,
        )


def test_explicit_binary_and_empty():
    op = Operation("download", "cloud", "GET", "/x", response_kind="binary")
    assert parse_response(httpx.Response(200, content=b"abc"), op, bytes).data == b"abc"
    op = Operation("empty", "cloud", "POST", "/x", response_kind="empty")
    assert parse_response(httpx.Response(204), op, type(None)).data is None


def test_response_metadata():
    response = httpx.Response(
        200, json=envelope({}), headers={"X-Request-ID": "req-123"}
    )
    result = parse_response(response, Operation("read", "cloud", "GET", "/x"), dict)
    assert result.request_id == "req-123"
    with pytest.raises(ApiError) as exc:
        parse_response(
            httpx.Response(
                200,
                json=envelope({}, error="LIMIT"),
                headers={"X-Request-ID": "req-456"},
            ),
            Operation("read", "cloud", "GET", "/x"),
            dict,
        )
    assert exc.value.api_error_code == "LIMIT" and exc.value.request_id == "req-456"
