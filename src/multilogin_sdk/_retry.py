"""Retry delay calculation; safety is supplied by the operation registry."""
import math
import random
import time
from email.utils import parsedate_to_datetime


def retry_delay(header: str | None, attempt: int, remaining: float, *, now: float | None = None, jitter: float | None = None) -> float | None:
    delay: float | None = None
    if header:
        try:
            delay = max(0.0, float(header))
        except ValueError:
            try:
                delay = max(0.0, parsedate_to_datetime(header).timestamp() - (time.time() if now is None else now))
            except (ValueError, TypeError, OverflowError):
                pass
    if delay is None or not math.isfinite(delay):
        delay = min(8.0, 0.5 * 2 ** min(attempt, 5)) + (random.random() * 0.25 if jitter is None else jitter)
    return delay if delay <= remaining else None
