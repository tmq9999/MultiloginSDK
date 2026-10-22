"""Read fingerprint catalogues exposed by the cloud API."""

from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.common import ApiResponse


def build_resolutions() -> RequestSpec:
    return RequestSpec(
        Operation(
            "screen_resolution",
            "cloud",
            "GET",
            "/fpb/resolutions",
            read_only=True,
        )
    )


class FingerprintsResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def resolutions(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_resolutions(), dict[str, object])


class AsyncFingerprintsResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def resolutions(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_resolutions(), dict[str, object])
