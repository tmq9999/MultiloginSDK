"""Read workspace proxy inventory and generate proxy connection strings."""

from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.common import ApiResponse
from ..models.proxies import ProxyGenerateRequest, ProxyGenerateResponse


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


def build_generate(request: ProxyGenerateRequest) -> RequestSpec:
    # Not read_only: each call may allocate new proxy sessions, so never auto-retry.
    return RequestSpec(
        Operation("generate_proxy", "cloud", "GET", "/proxynm/connection_url"),
        query={k: v for k, v in request.to_wire().items() if v is not None},
    )


class ProxiesResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def user(self) -> ApiResponse[dict[str, object]]:
        return self._transport.send(build_user(), dict[str, object])

    def isp_proxies(self) -> ApiResponse[list[dict[str, object]]]:
        return self._transport.send(build_isp_proxies(), list[dict[str, object]])

    def generate(
        self, request: ProxyGenerateRequest
    ) -> ApiResponse[ProxyGenerateResponse]:
        return self._transport.send(build_generate(request), ProxyGenerateResponse)


class AsyncProxiesResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def user(self) -> ApiResponse[dict[str, object]]:
        return await self._transport.send(build_user(), dict[str, object])

    async def isp_proxies(self) -> ApiResponse[list[dict[str, object]]]:
        return await self._transport.send(build_isp_proxies(), list[dict[str, object]])

    async def generate(
        self, request: ProxyGenerateRequest
    ) -> ApiResponse[ProxyGenerateResponse]:
        return await self._transport.send(
            build_generate(request), ProxyGenerateResponse
        )
