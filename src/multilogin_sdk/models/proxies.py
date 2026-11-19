"""Generate Proxy wire fields; connection strings carry credentials."""

from typing import Any, Literal

from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import core_schema

from .common import RequestModel, ResponseModel

ProxyProtocol = Literal["http", "socks5"]
ProxySessionType = Literal["sticky", "rotating"]
ProxyConnectionType = Literal["residential", "mobile"]


class ConnectionUrl(str):
    """`host:port:user:pass` string whose repr never exposes the credentials."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "ConnectionUrl('[REDACTED]')"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls, core_schema.str_schema(strict=True)
        )


class ProxyGenerateRequest(RequestModel):
    country: str = Field(min_length=1)
    protocol: ProxyProtocol
    session_type: ProxySessionType
    region: str | None = Field(default=None, min_length=1)
    city: str | None = Field(default=None, min_length=1)
    ip_ttl: int | None = Field(default=None, ge=1)
    count: int | None = Field(default=None, ge=1, le=100)
    connection_type: ProxyConnectionType | None = None
    isp: str | None = Field(default=None, min_length=1)


class ProxyGenerateResponse(ResponseModel):
    connection_urls: list[ConnectionUrl]
