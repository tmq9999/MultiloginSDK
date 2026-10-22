import inspect

import httpx
import pytest


def envelope(data=None, *, code=200, error="", message=""):
    return {
        "status": {"http_code": code, "error_code": error, "message": message},
        "data": data,
    }


async def resolve(value):
    return await value if inspect.isawaitable(value) else value


@pytest.fixture(params=["sync", "async"])
def mode(request):
    return request.param


def session_for(mode, handler):
    cls = httpx.Client if mode == "sync" else httpx.AsyncClient
    return cls(transport=httpx.MockTransport(handler))
