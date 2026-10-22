"""Read mobile-profile capacity and inventory."""

from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.common import ApiResponse


def build_limit() -> RequestSpec:
    return RequestSpec(
        Operation(
            "mobile_profile_limit",
            "cloud",
            "GET",
            "/mobile_profiles/limit",
            read_only=True,
        )
    )


def build_list() -> RequestSpec:
    return RequestSpec(
        Operation(
            "mobile_profile_list",
            "cloud",
            "GET",
            "/mobile_profiles/phone/list",
            read_only=True,
        )
    )


class MobileResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def limit(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_limit(), dict[str, object])

    def list(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_list(), dict[str, object])


class AsyncMobileResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def limit(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_limit(), dict[str, object])

    async def list(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_list(), dict[str, object])
