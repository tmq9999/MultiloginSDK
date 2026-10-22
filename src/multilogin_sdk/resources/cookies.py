"""Read the pre-made-cookie website catalogue."""

from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.common import ApiResponse


def build_websites() -> RequestSpec:
    return RequestSpec(
        Operation(
            "target_website_list",
            "cookies",
            "GET",
            "/api/v1/cookies/metadata/websites",
            read_only=True,
        )
    )


class CookiesResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def websites(self) -> ApiResponse[list[dict[str, object]]]:
        return self._transport.send(build_websites(), list[dict[str, object]])


class AsyncCookiesResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def websites(self) -> ApiResponse[list[dict[str, object]]]:
        return await self._transport.send(build_websites(), list[dict[str, object]])
