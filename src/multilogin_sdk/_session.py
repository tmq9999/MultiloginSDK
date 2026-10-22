"""Own only successfully started profiles; bound polling and cancellation cleanup."""
from __future__ import annotations

import asyncio
import math
from contextlib import asynccontextmanager, contextmanager, suppress
from dataclasses import replace
from time import monotonic, sleep
from typing import AsyncIterator, Iterator, TYPE_CHECKING

import httpx

from .errors import ApiError, PollingTimeout
from .models.common import ApiResponse
from .models.launcher import BrowserConnection, LauncherStartRequest

if TYPE_CHECKING:
    from .resources.launcher import LauncherResource, AsyncLauncherResource

async_sleep = asyncio.sleep


def _validate(*values: float) -> None:
    if any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError('Timeouts and polling intervals must be finite and positive')


def _state(result: ApiResponse[dict[str, object]]) -> bool:
    status = result.data.get('status')
    if not isinstance(status, str):
        from .errors import ProtocolError
        raise ProtocolError('Profile status response must contain a status string')
    if status == 'browser_running':
        return True
    if status.endswith('_error') or status in {'error', 'stopped'}:
        raise ApiError('Profile stopped or failed before becoming ready', operation='get_profile_status')
    return False


def wait_ready(resource: LauncherResource, profile_id: str, *, timeout: float, poll_interval: float) -> ApiResponse[dict[str, object]]:
    from .resources.launcher import build_status
    _validate(timeout, poll_interval)
    deadline = monotonic() + timeout
    while True:
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise PollingTimeout('Profile readiness deadline exceeded')
        spec = build_status(profile_id)
        spec = replace(spec, operation=replace(spec.operation, read_only=False), timeout=httpx.Timeout(remaining))
        result = resource._transport.send(spec, dict[str, object])
        if monotonic() >= deadline:
            raise PollingTimeout('Profile readiness deadline exceeded')
        if _state(result):
            return result
        sleep(min(poll_interval, max(0, deadline - monotonic())))


async def async_wait_ready(resource: AsyncLauncherResource, profile_id: str, *, timeout: float, poll_interval: float) -> ApiResponse[dict[str, object]]:
    from .resources.launcher import build_status
    _validate(timeout, poll_interval)
    deadline = monotonic() + timeout
    while True:
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise PollingTimeout('Profile readiness deadline exceeded')
        spec = build_status(profile_id)
        spec = replace(spec, operation=replace(spec.operation, read_only=False), timeout=httpx.Timeout(remaining))
        try:
            async with asyncio.timeout(remaining):
                result = await resource._transport.send(spec, dict[str, object])
        except TimeoutError:
            raise PollingTimeout('Profile readiness deadline exceeded') from None
        if _state(result):
            return result
        await async_sleep(min(poll_interval, max(0, deadline - monotonic())))


def _cleanup(resource: LauncherResource, profile_id: str, timeout: float) -> None:
    from .resources.launcher import build_stop
    resource._transport.send(replace(build_stop(profile_id), timeout=httpx.Timeout(timeout)), type(None))


async def _async_cleanup(resource: AsyncLauncherResource, profile_id: str, timeout: float) -> None:
    from .resources.launcher import build_stop
    async def stop() -> None:
        async with asyncio.timeout(timeout):
            await resource._transport.send(replace(build_stop(profile_id), timeout=httpx.Timeout(timeout)), type(None))
    task = asyncio.create_task(stop())
    try:
        await asyncio.shield(task)
    except BaseException:
        if not task.done():
            task.cancel()
            with suppress(BaseException):
                await task
        raise


@contextmanager
def session(resource: LauncherResource, request: LauncherStartRequest, *, wait_timeout: float, poll_interval: float, cleanup_timeout: float) -> Iterator[BrowserConnection]:
    _validate(wait_timeout, poll_interval, cleanup_timeout)
    connection = resource.start(request).data
    try:
        resource.wait_ready(connection.id, timeout=wait_timeout, poll_interval=poll_interval)
        yield connection
    except BaseException as original:
        try:
            _cleanup(resource, connection.id, cleanup_timeout)
        except BaseException:
            original.add_note('Profile cleanup also failed; check the owned profile status')
        raise
    else:
        _cleanup(resource, connection.id, cleanup_timeout)


@asynccontextmanager
async def async_session(resource: AsyncLauncherResource, request: LauncherStartRequest, *, wait_timeout: float, poll_interval: float, cleanup_timeout: float) -> AsyncIterator[BrowserConnection]:
    _validate(wait_timeout, poll_interval, cleanup_timeout)
    connection = (await resource.start(request)).data
    try:
        await resource.wait_ready(connection.id, timeout=wait_timeout, poll_interval=poll_interval)
        yield connection
    except BaseException as original:
        try:
            await _async_cleanup(resource, connection.id, cleanup_timeout)
        except BaseException:
            original.add_note('Profile cleanup also failed; check the owned profile status')
        raise
    else:
        await _async_cleanup(resource, connection.id, cleanup_timeout)
