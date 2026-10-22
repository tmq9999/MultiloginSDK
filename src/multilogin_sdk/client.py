"""Public clients: no login, token refresh or network I/O on construction."""
from types import TracebackType
from typing import Mapping, Self

import httpx

from ._operations import Service
from ._transport import SERVICES, AsyncTransport, SyncTransport
from .config import ClientConfig
from .resources.launcher import LauncherResource, AsyncLauncherResource
from .resources.profiles import ProfilesResource, AsyncProfilesResource
from .resources.auth import AuthResource, AsyncAuthResource
from .resources.workspaces import WorkspacesResource, AsyncWorkspacesResource
from .resources.folders import FoldersResource, AsyncFoldersResource


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
        self.auth = AuthResource(self._transport)
        self.workspaces = WorkspacesResource(self._transport)
        self.folders = FoldersResource(self._transport)
        self.profiles = ProfilesResource(self._transport)
        self.launcher = LauncherResource(self._transport)

    def with_token(self, token: str) -> Self:
        return type(self)(token, config=self.config)

    def switch_workspace(self, *, email: str, refresh_token: str, workspace_id: str) -> Self:
        tokens = self.auth.refresh(email, refresh_token, workspace_id).data
        return self.with_token(tokens.token.get_secret_value())

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
        self.auth = AsyncAuthResource(self._transport)
        self.workspaces = AsyncWorkspacesResource(self._transport)
        self.folders = AsyncFoldersResource(self._transport)
        self.profiles = AsyncProfilesResource(self._transport)
        self.launcher = AsyncLauncherResource(self._transport)

    def with_token(self, token: str) -> Self:
        return type(self)(token, config=self.config)

    async def switch_workspace(self, *, email: str, refresh_token: str, workspace_id: str) -> Self:
        tokens = (await self.auth.refresh(email, refresh_token, workspace_id)).data
        return self.with_token(tokens.token.get_secret_value())

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> Self:
        if self._transport._closed:
            raise RuntimeError('Client is closed')
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
        await self.aclose()
