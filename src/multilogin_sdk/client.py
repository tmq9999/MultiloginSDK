"""Public clients: no login, token refresh or network I/O on construction."""
from types import TracebackType
from typing import Mapping, Self

import httpx

from ._operations import Service
from ._transport import SERVICES, AsyncTransport, SyncTransport
from .config import ClientConfig


def _tokens(token: str | None, service_tokens: Mapping[Service, str] | None) -> dict[Service, str]:
    tokens: dict[Service, str] = {s: token for s in SERVICES} if token else {}
    tokens.update(service_tokens or {})
    return tokens


class MultiloginClient:
    def __init__(self, token: str | None = None, *, config: ClientConfig | None = None,
                 service_tokens: Mapping[Service, str] | None = None,
                 sessions: Mapping[Service, httpx.Client] | None = None) -> None:
        self.config = config or ClientConfig()
        self._transport = SyncTransport(self.config, tokens=_tokens(token, service_tokens), sessions=sessions)

    def with_token(self, token: str) -> Self:
        return type(self)(token, config=self.config)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Self:
        if self._transport._closed:
            raise RuntimeError('Client is closed')
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
        self.close()


class AsyncMultiloginClient:
    def __init__(self, token: str | None = None, *, config: ClientConfig | None = None,
                 service_tokens: Mapping[Service, str] | None = None,
                 sessions: Mapping[Service, httpx.AsyncClient] | None = None) -> None:
        self.config = config or ClientConfig()
        self._transport = AsyncTransport(self.config, tokens=_tokens(token, service_tokens), sessions=sessions)

    def with_token(self, token: str) -> Self:
        return type(self)(token, config=self.config)

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> Self:
        if self._transport._closed:
            raise RuntimeError('Client is closed')
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
        await self.aclose()
