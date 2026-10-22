"""Immutable service configuration."""

import math
import ssl
from dataclasses import dataclass, field
from urllib.parse import urlsplit

import httpx


@dataclass(frozen=True)
class ClientConfig:
    cloud_url: str = "https://api.multilogin.com"
    launcher_url: str = "https://launcher.mlx.yt:45001"
    cookies_url: str = "https://cookies.multilogin.com"
    strict_mode: bool | None = None
    timeout: httpx.Timeout = field(
        default_factory=lambda: httpx.Timeout(30, connect=10)
    )
    start_timeout: float = 120
    max_retries: int = 0
    retry_budget: float = 30
    launcher_ca: ssl.SSLContext | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        for url in [self.cloud_url, self.launcher_url, self.cookies_url]:
            p = urlsplit(url)
            if (
                p.scheme not in {"http", "https"}
                or not p.hostname
                or p.username is not None
                or p.password is not None
                or p.query
                or p.fragment
                or any(part in {".", ".."} for part in p.path.split("/"))
                or "%" in p.path
                or "\\" in p.path
            ):
                raise ValueError(
                    "Service URL must be HTTP(S) with a safe prefix and no credentials, query or fragment"
                )
            _ = p.port
        if not math.isfinite(self.start_timeout) or self.start_timeout <= 0:
            raise ValueError("start_timeout must be finite and positive")
        if (
            isinstance(self.max_retries, bool)
            or not isinstance(self.max_retries, int)
            or self.max_retries < 0
        ):
            raise ValueError("max_retries must be a non-negative integer")
        if not math.isfinite(self.retry_budget) or self.retry_budget < 0:
            raise ValueError("retry_budget must be finite and non-negative")
        for value in self.timeout.as_dict().values():
            if value is None or not math.isfinite(value) or value <= 0:
                raise ValueError("All timeouts must be finite and positive")
        if self.strict_mode is not None and not isinstance(self.strict_mode, bool):
            raise ValueError("strict_mode must be bool or None")
        if self.launcher_ca is not None and (
            self.launcher_ca.verify_mode != ssl.CERT_REQUIRED
            or not self.launcher_ca.check_hostname
        ):
            raise ValueError(
                "Launcher CA context must verify certificates and hostnames"
            )
