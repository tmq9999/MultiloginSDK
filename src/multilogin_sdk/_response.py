"""Parse wire envelopes without embedding server bodies in errors."""

import re
from collections.abc import Collection
from typing import Any, TypeVar

import httpx
from pydantic import TypeAdapter, ValidationError

from ._operations import Operation
from ._redaction import redact
from .errors import ApiError, HttpError, ProtocolError
from .models.common import ApiResponse, ApiStatus

T = TypeVar("T")


def _identifier(value: str | None, secrets: Collection[str]) -> str | None:
    if not value or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value):
        return None
    if any(secret and secret in value for secret in secrets):
        return None
    return value


def parse_response(
    response: httpx.Response,
    operation: Operation,
    data_type: type[T],
    *,
    secrets: Collection[str] = (),
) -> ApiResponse[T]:
    # Server-controlled messages/codes/IDs can echo credentials: errors deliberately
    # expose fixed messages and bounded HTTP metadata, never the raw body.
    metadata: dict[str, Any] = {
        "operation": operation.name,
        "status_code": response.status_code,
        "request_id": _identifier(response.headers.get("x-request-id"), secrets),
    }
    if not 200 <= response.status_code < 300:
        raise HttpError(f"{operation.name}: HTTP {response.status_code}", **metadata)
    if operation.response_kind in {"empty", "binary"}:
        value = None if operation.response_kind == "empty" else response.content
        return ApiResponse[T](
            data=TypeAdapter(data_type).validate_python(value),
            status=ApiStatus(http_code=response.status_code, error_code="", message=""),
            http_status=response.status_code,
            request_id=metadata["request_id"],
        )
    try:
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("status"), dict):
            raise TypeError("Missing status")
        status = ApiStatus.model_validate(payload["status"], strict=True)
    except (ValueError, ValidationError, TypeError):
        raise ProtocolError(
            f"{operation.name}: invalid JSON status envelope", **metadata
        ) from None
    metadata["api_error_code"] = _identifier(status.error_code, secrets)
    status.message = redact(status.message, secrets)
    if status.http_code >= 400 or status.error_code:
        raise ApiError(f"{operation.name}: API reported an error", **metadata)
    if not 200 <= status.http_code < 300:
        raise ProtocolError(
            f"{operation.name}: invalid envelope success code", **metadata
        )
    try:
        data = TypeAdapter(data_type).validate_python(payload.get("data"))
    except (ValidationError, ValueError, TypeError):
        raise ProtocolError(
            f"{operation.name}: invalid response data", **metadata
        ) from None
    return ApiResponse[T](
        data=data,
        status=status,
        http_status=response.status_code,
        request_id=metadata["request_id"],
    )
