"""Browser Launcher operations with no implicit API version fallback."""

from contextlib import AbstractAsyncContextManager, AbstractContextManager

from .. import _session
from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.common import ApiResponse
from ..models.launcher import (
    BrowserConnection,
    LauncherStartRequest,
    QuickProfileV3Request,
)


def build_start(
    request: LauncherStartRequest, *, read_timeout: float = 120
) -> RequestSpec:
    return RequestSpec(
        Operation(
            "start_browser_profile",
            "launcher",
            "GET",
            "/api/v2/profile/f/{folder_id}/p/{profile_id}/start",
            read_timeout=read_timeout,
        ),
        path_params={"folder_id": request.folder_id, "profile_id": request.profile_id},
        query={
            "automation_type": request.automation_type,
            "headless_mode": request.headless_mode,
        },
    )


def build_quick(
    request: QuickProfileV3Request, *, read_timeout: float = 120
) -> RequestSpec:
    return RequestSpec(
        Operation(
            "start_quick_profile_v3",
            "launcher",
            "POST",
            "/api/v3/profile/quick",
            read_timeout=read_timeout,
        ),
        json_body=request.to_wire(),
    )


def build_stop(profile_id: str) -> RequestSpec:
    return RequestSpec(
        Operation(
            "stop_browser_profile",
            "launcher",
            "GET",
            "/api/v1/profile/stop/p/{profile_id}",
        ),
        path_params={"profile_id": profile_id},
    )


def build_status(profile_id: str) -> RequestSpec:
    return RequestSpec(
        Operation(
            "get_profile_status",
            "launcher",
            "GET",
            "/api/v1/profile/status/p/{profile_id}",
            read_only=True,
        ),
        path_params={"profile_id": profile_id},
    )


def build_statuses() -> RequestSpec:
    return RequestSpec(
        Operation(
            "get_all_profiles_status",
            "launcher",
            "GET",
            "/api/v1/profile/statuses",
            read_only=True,
        )
    )


def build_version() -> RequestSpec:
    return RequestSpec(
        Operation("get_version", "launcher", "GET", "/api/v1/version", read_only=True)
    )


class LauncherResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def start(self, request: LauncherStartRequest) -> ApiResponse[BrowserConnection]:
        return self._transport.send(
            build_start(request, read_timeout=self._transport.config.start_timeout),
            BrowserConnection,
        )

    def quick(self, request: QuickProfileV3Request) -> ApiResponse[BrowserConnection]:
        return self._transport.send(
            build_quick(request, read_timeout=self._transport.config.start_timeout),
            BrowserConnection,
        )

    def stop(self, profile_id: str) -> ApiResponse[None]:
        return self._transport.send(build_stop(profile_id), type(None))

    def status(self, profile_id: str) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_status(profile_id), dict[str, object])

    def statuses(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_statuses(), dict[str, object])

    def version(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_version(), dict[str, object])

    def wait_ready(
        self, profile_id: str, *, timeout: float = 120, poll_interval: float = 1
    ) -> ApiResponse[dict[str, object]]:
        return _session.wait_ready(
            self, profile_id, timeout=timeout, poll_interval=poll_interval
        )

    def session(
        self,
        request: LauncherStartRequest,
        *,
        wait_timeout: float = 120,
        poll_interval: float = 1,
        cleanup_timeout: float = 10,
    ) -> AbstractContextManager[BrowserConnection]:
        return _session.session(
            self,
            request,
            wait_timeout=wait_timeout,
            poll_interval=poll_interval,
            cleanup_timeout=cleanup_timeout,
        )


class AsyncLauncherResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def start(
        self, request: LauncherStartRequest
    ) -> ApiResponse[BrowserConnection]:
        return await self._transport.send(
            build_start(request, read_timeout=self._transport.config.start_timeout),
            BrowserConnection,
        )

    async def quick(
        self, request: QuickProfileV3Request
    ) -> ApiResponse[BrowserConnection]:
        return await self._transport.send(
            build_quick(request, read_timeout=self._transport.config.start_timeout),
            BrowserConnection,
        )

    async def stop(self, profile_id: str) -> ApiResponse[None]:
        return await self._transport.send(build_stop(profile_id), type(None))

    async def status(self, profile_id: str) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_status(profile_id), dict[str, object])

    async def statuses(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_statuses(), dict[str, object])

    async def version(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_version(), dict[str, object])

    async def wait_ready(
        self, profile_id: str, *, timeout: float = 120, poll_interval: float = 1
    ) -> ApiResponse[dict[str, object]]:
        return await _session.async_wait_ready(
            self, profile_id, timeout=timeout, poll_interval=poll_interval
        )

    def session(
        self,
        request: LauncherStartRequest,
        *,
        wait_timeout: float = 120,
        poll_interval: float = 1,
        cleanup_timeout: float = 10,
    ) -> AbstractAsyncContextManager[BrowserConnection]:
        return _session.async_session(
            self,
            request,
            wait_timeout=wait_timeout,
            poll_interval=poll_interval,
            cleanup_timeout=cleanup_timeout,
        )
