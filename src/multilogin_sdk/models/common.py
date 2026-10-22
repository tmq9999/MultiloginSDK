"""Shared wire models; omission is distinct from false, empty and null."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, model_validator

T = TypeVar("T")


class _Unset:
    def __repr__(self) -> str:
        return "UNSET"


UNSET = _Unset()


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @model_validator(mode="before")
    @classmethod
    def omit_unset(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {k: v for k, v in value.items() if v is not UNSET}
        return value

    def to_wire(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_unset=True)


class ResponseModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class ApiStatus(ResponseModel):
    http_code: int
    error_code: str
    message: str


class ApiResponse(ResponseModel, Generic[T]):
    data: T
    status: ApiStatus
    http_status: int
    request_id: str | None = None
