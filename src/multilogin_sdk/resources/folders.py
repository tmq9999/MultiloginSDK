"""Folder mutations use explicit JSON bodies, never documentation query fields."""

from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.common import ApiResponse
from ..models.workspaces import (
    FolderCreateRequest,
    FoldersData,
    FoldersRemoveRequest,
    FolderUpdateRequest,
)


def build_list() -> RequestSpec:
    return RequestSpec(
        Operation(
            "workspace_folders", "cloud", "GET", "/workspace/folders", read_only=True
        )
    )


def build_create(request: FolderCreateRequest) -> RequestSpec:
    return RequestSpec(
        Operation(
            "workspace_create_folder", "cloud", "POST", "/workspace/folder_create"
        ),
        json_body=request.to_wire(),
    )


def build_update(request: FolderUpdateRequest) -> RequestSpec:
    return RequestSpec(
        Operation(
            "workspace_update_folder", "cloud", "POST", "/workspace/folder_update"
        ),
        json_body=request.to_wire(),
    )


def build_remove(request: FoldersRemoveRequest) -> RequestSpec:
    return RequestSpec(
        Operation(
            "workspace_remove_folders", "cloud", "POST", "/workspace/folders_remove"
        ),
        json_body=request.to_wire(),
    )


class FoldersResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(self) -> ApiResponse[FoldersData]:
        return self._transport.send(build_list(), FoldersData)

    def create(self, request: FolderCreateRequest) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_create(request), dict[str, object])

    def update(self, request: FolderUpdateRequest) -> ApiResponse[None]:
        return self._transport.send(build_update(request), type(None))

    def remove(self, request: FoldersRemoveRequest) -> ApiResponse[None]:
        return self._transport.send(build_remove(request), type(None))


class AsyncFoldersResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(self) -> ApiResponse[FoldersData]:
        return await self._transport.send(build_list(), FoldersData)

    async def create(
        self, request: FolderCreateRequest
    ) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_create(request), dict[str, object])

    async def update(self, request: FolderUpdateRequest) -> ApiResponse[None]:
        return await self._transport.send(build_update(request), type(None))

    async def remove(self, request: FoldersRemoveRequest) -> ApiResponse[None]:
        return await self._transport.send(build_remove(request), type(None))
