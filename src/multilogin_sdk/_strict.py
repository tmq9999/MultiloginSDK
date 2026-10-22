"""Validate confirmed strict-mode fields before sending a request."""

from collections.abc import Mapping
from typing import Any

from ._operations import RequestSpec

_FLAGS = (
    "audio_masking",
    "fonts_masking",
    "geolocation_masking",
    "geolocation_popup",
    "graphics_masking",
    "graphics_noise",
    "localization_masking",
    "media_devices_masking",
    "navigator_masking",
    "ports_masking",
    "proxy_masking",
    "screen_masking",
    "timezone_masking",
    "webrtc_masking",
    "canvas_noise",
    "startup_behavior",
)
STRICT_FIELDS: dict[str, tuple[str, ...]] = {
    "profile_create": (
        "name",
        "browser_type",
        "folder_id",
        "os_type",
        "auto_update_core",
        "core_version",
        "parameters.storage.is_local",
        "parameters.storage.save_service_worker",
        *[f"parameters.flags.{f}" for f in _FLAGS],
    ),
    "profile_search": (
        "is_removed",
        "core_version",
        "limit",
        "offset",
        "search_text",
        "folder_id",
        "storage_type",
        "order_by",
        "sort",
    ),
    "start_quick_profile_v3": (
        "browser_type",
        "os_type",
        "automation",
        "auto_update_core",
        "core_version",
        "is_headless",
        "parameters.fingerprint",
        *[f"parameters.flags.{f}" for f in _FLAGS],
    ),
}


def validate_strict(spec: RequestSpec) -> None:
    body = spec.json_body or {}
    missing = []
    for path in STRICT_FIELDS.get(spec.operation.name, ()):
        value: Any = body
        for part in path.split("."):
            if not isinstance(value, Mapping) or part not in value:
                missing.append(path)
                break
            value = value[part]
    if missing:
        raise ValueError(
            "Strict mode requires explicitly supplied fields: " + ", ".join(missing)
        )
