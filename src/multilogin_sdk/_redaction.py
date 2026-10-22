"""Small recursive sanitizer for opt-in diagnostics."""

import re
from collections.abc import Collection
from typing import Any

SENSITIVE = {
    "authorization",
    "token",
    "refresh_token",
    "password",
    "password_md5",
    "pwd",
    "cookies",
    "cookie",
    "set-cookie",
    "username",
    "otp",
    "backup_codes",
    "otp_url_bytes",
}


def redact(value: Any, secrets: Collection[str] = ()) -> Any:
    if isinstance(value, dict):
        return {
            k: "[REDACTED]" if str(k).lower() in SENSITIVE else redact(v, secrets)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(v, secrets) for v in value]
    if isinstance(value, str):
        for secret in sorted(filter(None, secrets), key=len, reverse=True):
            value = value.replace(secret, "[REDACTED]")
        return re.sub(r"eyJ[\w-]+\.[\w-]+\.[\w-]+", "[REDACTED]", value)
    return value


def sensitive_values(value: Any) -> list[str]:
    result: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in SENSITIVE and isinstance(item, str):
                result.append(item)
            result.extend(sensitive_values(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            result.extend(sensitive_values(item))
    return result
