"""Read workspace membership without changing the client's token."""
from .._operations import Operation, RequestSpec
from .._transport import SyncTransport, AsyncTransport
from ..models.common import ApiResponse
from ..models.workspaces import WorkspacesData


def build_list() -> RequestSpec:
    return RequestSpec(Operation('user_workspaces','cloud','GET','/user/workspaces',read_only=True))


class WorkspacesResource:
    def __init__(self,transport: SyncTransport) -> None:
        self._transport=transport

    def list(self) -> ApiResponse[WorkspacesData]:
        return self._transport.send(build_list(),WorkspacesData)


class AsyncWorkspacesResource:
    def __init__(self,transport: AsyncTransport) -> None:
        self._transport=transport

    async def list(self) -> ApiResponse[WorkspacesData]:
        return await self._transport.send(build_list(),WorkspacesData)
