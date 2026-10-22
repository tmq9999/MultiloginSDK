"""Read object-storage metadata without mutating stored objects."""

from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.common import ApiResponse


def build_types() -> RequestSpec:
    return RequestSpec(
        Operation(
            "get_list_of_object_types",
            "cloud",
            "GET",
            "/api/v1/resources/types",
            read_only=True,
        )
    )


def build_statistics() -> RequestSpec:
    return RequestSpec(
        Operation(
            "get_statistics_for_objects",
            "cloud",
            "GET",
            "/api/v1/resources/statistics",
            read_only=True,
        )
    )


class ObjectsResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def types(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_types(), dict[str, object])

    def statistics(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_statistics(), dict[str, object])


class AsyncObjectsResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def types(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_types(), dict[str, object])

    async def statistics(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_statistics(), dict[str, object])
