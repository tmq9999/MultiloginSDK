"""Sync and async HTTP execution with explicit origin and session ownership."""
import asyncio
import time
from typing import Any, Awaitable, Callable, Mapping, TypeVar
from urllib.parse import quote

import httpx

from ._operations import RequestSpec, Service
from ._response import parse_response
from ._retry import retry_delay
from ._strict import validate_strict
from .config import ClientConfig
from .errors import LauncherUnavailable, TransportError
from .models.common import ApiResponse

T = TypeVar('T')
SERVICES: tuple[Service, ...] = ('cloud', 'launcher', 'cookies')


class _Common:
    def __init__(self, config: ClientConfig, tokens: Mapping[Service, str]) -> None:
        self.config = config
        self._tokens = dict(tokens)
        self._closed = False
        self._origins = {'cloud': config.cloud_url.rstrip('/'), 'launcher': config.launcher_url.rstrip('/'), 'cookies': config.cookies_url.rstrip('/')}

    def _request(self, spec: RequestSpec) -> httpx.Request:
        if self._closed:
            raise RuntimeError('Client is closed')
        op = spec.operation
        if op.auth_required and not self._tokens.get(op.service):
            raise ValueError('A token is required for this operation')
        path = op.path
        for key, value in spec.path_params.items():
            if not value or value in {'.', '..'}:
                raise ValueError('Path identifiers must be non-empty and cannot be dot segments')
            path = path.replace('{' + key + '}', quote(value, safe=''))
        if not path.startswith('/') or path.startswith('//') or '{' in path or '?' in path or '#' in path:
            raise ValueError('Operation path must be a resolved relative path')
        headers = {'Accept': 'application/json'}
        if op.auth_required:
            headers['Authorization'] = 'Bearer ' + self._tokens[op.service]
        strict = spec.strict_mode if spec.strict_mode is not None else self.config.strict_mode
        if strict is True:
            validate_strict(spec)
        if strict is not None:
            headers['X-Strict-Mode'] = str(strict).lower()
        query = {k: str(v).lower() if isinstance(v, bool) else v for k, v in spec.query.items()}
        timeout = self.config.timeout.as_dict()
        if op.read_timeout is not None:
            timeout['read'] = op.read_timeout
        # Do not use Client.build_request: injected session defaults could leak
        # its Authorization/cookies into noauth or other service requests.
        return httpx.Request(op.method, self._origins[op.service] + path, params=query,
                             json=dict(spec.json_body) if spec.json_body is not None else None,
                             headers=headers, extensions={'timeout': timeout})

    def _delay(self, spec: RequestSpec, response: httpx.Response, attempt: int, waited: float) -> float | None:
        if not spec.operation.read_only or attempt >= self.config.max_retries or response.status_code not in {429, 502, 503, 504}:
            return None
        return retry_delay(response.headers.get('Retry-After'), attempt, self.config.retry_budget - waited)

    def _network_error(self, spec: RequestSpec, exc: httpx.RequestError) -> TransportError:
        if spec.operation.service == 'launcher' and isinstance(exc, httpx.ConnectError):
            return LauncherUnavailable(f'Launcher unavailable at {self.config.launcher_url}; check the Multilogin desktop app/agent', operation=spec.operation.name)
        return TransportError(f'{spec.operation.name}: {type(exc).__name__}', operation=spec.operation.name)


class SyncTransport(_Common):
    def __init__(self, config: ClientConfig, *, tokens: Mapping[Service, str], sessions: Mapping[Service, httpx.Client] | None = None, sleeper: Callable[[float], Any] = time.sleep) -> None:
        super().__init__(config, tokens)
        supplied = dict(sessions or {})
        self._owned = [s for s in SERVICES if s not in supplied]
        self._sessions = supplied
        self._sleep = sleeper

    def _session(self, service: Service) -> httpx.Client:
        if service not in self._sessions:
            verify = self.config.launcher_ca if service == 'launcher' and self.config.launcher_ca is not None else True
            self._sessions[service] = httpx.Client(verify=verify, trust_env=False)
        return self._sessions[service]

    def send(self, spec: RequestSpec, data_type: type[T]) -> ApiResponse[T]:
        waited = 0.0
        for attempt in range(self.config.max_retries + 1):
            request = self._request(spec)
            try:
                response = self._session(spec.operation.service).send(request, auth=None, follow_redirects=False)
            except httpx.RequestError as exc:
                raise self._network_error(spec, exc) from None
            delay = self._delay(spec, response, attempt, waited)
            if delay is None:
                return parse_response(response, spec.operation, data_type)
            response.close()
            self._sleep(delay)
            waited += delay
        raise AssertionError('Retry loop exhausted')

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            for service in self._owned:
                if service in self._sessions:
                    self._sessions[service].close()


class AsyncTransport(_Common):
    def __init__(self, config: ClientConfig, *, tokens: Mapping[Service, str], sessions: Mapping[Service, httpx.AsyncClient] | None = None, sleeper: Callable[[float], Awaitable[Any]] = asyncio.sleep) -> None:
        super().__init__(config, tokens)
        supplied = dict(sessions or {})
        self._owned = [s for s in SERVICES if s not in supplied]
        self._sessions = supplied
        self._sleep = sleeper

    def _session(self, service: Service) -> httpx.AsyncClient:
        if service not in self._sessions:
            verify = self.config.launcher_ca if service == 'launcher' and self.config.launcher_ca is not None else True
            self._sessions[service] = httpx.AsyncClient(verify=verify, trust_env=False)
        return self._sessions[service]

    async def send(self, spec: RequestSpec, data_type: type[T]) -> ApiResponse[T]:
        waited = 0.0
        for attempt in range(self.config.max_retries + 1):
            request = self._request(spec)
            try:
                response = await self._session(spec.operation.service).send(request, auth=None, follow_redirects=False)
            except httpx.RequestError as exc:
                raise self._network_error(spec, exc) from None
            delay = self._delay(spec, response, attempt, waited)
            if delay is None:
                return parse_response(response, spec.operation, data_type)
            await response.aclose()
            await self._sleep(delay)
            waited += delay
        raise AssertionError('Retry loop exhausted')

    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True
            for service in self._owned:
                if service in self._sessions:
                    await self._sessions[service].aclose()
