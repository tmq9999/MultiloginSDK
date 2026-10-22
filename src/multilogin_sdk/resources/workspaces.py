"""Read workspace membership without changing the client's token."""

from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.common import ApiResponse
from ..models.workspaces import WorkspacesData


def build_list() -> RequestSpec:
    return RequestSpec(
        Operation("user_workspaces", "cloud", "GET", "/user/workspaces", read_only=True)
    )


def build_statistics() -> RequestSpec:
    return RequestSpec(
        Operation(
            "workspace_statistics",
            "cloud",
            "GET",
            "/workspace/statistics",
            read_only=True,
        )
    )


class WorkspacesResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(self) -> ApiResponse[WorkspacesData]:
        return self._transport.send(build_list(), WorkspacesData)

    def statistics(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_statistics(), dict[str, object])


class AsyncWorkspacesResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(self) -> ApiResponse[WorkspacesData]:
        return await self._transport.send(build_list(), WorkspacesData)

    async def statistics(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_statistics(), dict[str, object])
