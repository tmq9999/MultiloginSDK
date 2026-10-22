"""Public clients: no login, token refresh or network I/O on construction."""

from collections.abc import Mapping
from types import TracebackType
from typing import Self

import httpx

from ._operations import Service
from ._transport import SERVICES, AsyncTransport, SyncTransport
from .config import ClientConfig
from .resources.auth import AsyncAuthResource, AuthResource
from .resources.cookies import AsyncCookiesResource, CookiesResource
from .resources.fingerprints import AsyncFingerprintsResource, FingerprintsResource
from .resources.folders import AsyncFoldersResource, FoldersResource
from .resources.launcher import AsyncLauncherResource, LauncherResource
from .resources.mobile import AsyncMobileResource, MobileResource
from .resources.objects import AsyncObjectsResource, ObjectsResource
from .resources.profiles import AsyncProfilesResource, ProfilesResource
from .resources.proxies import AsyncProxiesResource, ProxiesResource
from .resources.workspaces import AsyncWorkspacesResource, WorkspacesResource


def _tokens(
    token: str | None, service_tokens: Mapping[Service, str] | None
) -> dict[Service, str]:
    tokens: dict[Service, str] = dict.fromkeys(SERVICES, token) if token else {}
    tokens.update(service_tokens or {})
    return tokens


class MultiloginClient:
    def __init__(
        self,
        token: str | None = None,
        *,
        config: ClientConfig | None = None,
        service_tokens: Mapping[Service, str] | None = None,
        sessions: Mapping[Service, httpx.Client] | None = None,
    ) -> None:
        self.config = config or ClientConfig()
        self._transport = SyncTransport(
            self.config, tokens=_tokens(token, service_tokens), sessions=sessions
        )
        self.auth = AuthResource(self._transport)
        self.workspaces = WorkspacesResource(self._transport)
        self.folders = FoldersResource(self._transport)
        self.profiles = ProfilesResource(self._transport)
        self.launcher = LauncherResource(self._transport)
        self.proxies = ProxiesResource(self._transport)
        self.objects = ObjectsResource(self._transport)
        self.mobile = MobileResource(self._transport)
        self.fingerprints = FingerprintsResource(self._transport)
        self.cookies = CookiesResource(self._transport)

    def with_token(self, token: str) -> Self:
        return type(self)(token, config=self.config)

    def switch_workspace(
        self, *, email: str, refresh_token: str, workspace_id: str
    ) -> Self:
        tokens = self.auth.refresh(email, refresh_token, workspace_id).data
        return self.with_token(tokens.token.get_secret_value())

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Self:
        if self._transport._closed:
            raise RuntimeError("Client is closed")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


class AsyncMultiloginClient:
    def __init__(
        self,
        token: str | None = None,
        *,
        config: ClientConfig | None = None,
        service_tokens: Mapping[Service, str] | None = None,
        sessions: Mapping[Service, httpx.AsyncClient] | None = None,
    ) -> None:
        self.config = config or ClientConfig()
        self._transport = AsyncTransport(
            self.config, tokens=_tokens(token, service_tokens), sessions=sessions
        )
        self.auth = AsyncAuthResource(self._transport)
        self.workspaces = AsyncWorkspacesResource(self._transport)
        self.folders = AsyncFoldersResource(self._transport)
        self.profiles = AsyncProfilesResource(self._transport)
        self.launcher = AsyncLauncherResource(self._transport)
        self.proxies = AsyncProxiesResource(self._transport)
        self.objects = AsyncObjectsResource(self._transport)
        self.mobile = AsyncMobileResource(self._transport)
        self.fingerprints = AsyncFingerprintsResource(self._transport)
        self.cookies = AsyncCookiesResource(self._transport)

    def with_token(self, token: str) -> Self:
        return type(self)(token, config=self.config)

    async def switch_workspace(
        self, *, email: str, refresh_token: str, workspace_id: str
    ) -> Self:
        tokens = (await self.auth.refresh(email, refresh_token, workspace_id)).data
        return self.with_token(tokens.token.get_secret_value())

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> Self:
        if self._transport._closed:
            raise RuntimeError("Client is closed")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()
