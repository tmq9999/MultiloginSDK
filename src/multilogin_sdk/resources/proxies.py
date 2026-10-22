"""Read workspace proxy account and ISP inventory."""

from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.common import ApiResponse


def build_user() -> RequestSpec:
    return RequestSpec(
        Operation("fetch_proxy_data", "cloud", "GET", "/proxynm/user", read_only=True)
    )


def build_isp_proxies() -> RequestSpec:
    return RequestSpec(
        Operation(
            "list_isp_proxies", "cloud", "GET", "/proxynm/isp/proxies", read_only=True
        )
    )


class ProxiesResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def user(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_user(), dict[str, object])

    def isp_proxies(self) -> ApiResponse[list[dict[str, object]]]:
        return self._transport.send(build_isp_proxies(), list[dict[str, object]])


class AsyncProxiesResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def user(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_user(), dict[str, object])

    async def isp_proxies(self) -> ApiResponse[list[dict[str, object]]]:
        return await self._transport.send(build_isp_proxies(), list[dict[str, object]])
