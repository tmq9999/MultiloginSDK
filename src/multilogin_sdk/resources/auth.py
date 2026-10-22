"""Explicit sign-in, refresh and automation token creation."""

import hashlib
import re
from typing import get_args

from .._operations import Operation, RequestSpec
from .._transport import AsyncTransport, SyncTransport
from ..models.auth import AutomationToken, ExpirationPeriod, Tokens
from ..models.common import ApiResponse


def build_sign_in(email: str, password_md5: str) -> RequestSpec:
    if not email or not re.fullmatch(r"[a-fA-F0-9]{32}", password_md5):
        raise ValueError(
            "Email and a 32-character hexadecimal password hash are required"
        )
    return RequestSpec(
        Operation("user_sign_in", "cloud", "POST", "/user/signin", auth_required=False),
        json_body={"email": email, "password": password_md5},
    )


def build_refresh(email: str, refresh_token: str, workspace_id: str) -> RequestSpec:
    if not all([email, refresh_token, workspace_id]):
        raise ValueError("Email, refresh token and workspace ID are required")
    return RequestSpec(
        Operation(
            "user_refresh_token_switch_workspace",
            "cloud",
            "POST",
            "/user/refresh_token",
            auth_required=False,
        ),
        json_body={
            "email": email,
            "refresh_token": refresh_token,
            "workspace_id": workspace_id,
        },
    )


def build_automation_token(expiration_period: ExpirationPeriod) -> RequestSpec:
    if expiration_period not in get_args(ExpirationPeriod):
        raise ValueError("Unsupported expiration period")
    return RequestSpec(
        Operation(
            "workspace_automation_token", "cloud", "GET", "/workspace/automation_token"
        ),
        query={"expiration_period": expiration_period},
    )


class AuthResource:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def sign_in(self, email: str, password: str) -> ApiResponse[Tokens]:
        return self.sign_in_with_hash(
            email, hashlib.md5(password.encode(), usedforsecurity=False).hexdigest()
        )

    def sign_in_with_hash(self, email: str, password_md5: str) -> ApiResponse[Tokens]:
        return self._transport.send(build_sign_in(email, password_md5), Tokens)

    def refresh(
        self, email: str, refresh_token: str, workspace_id: str
    ) -> ApiResponse[Tokens]:
        return self._transport.send(
            build_refresh(email, refresh_token, workspace_id), Tokens
        )

    def automation_token(
        self, expiration_period: ExpirationPeriod
    ) -> ApiResponse[AutomationToken]:
        return self._transport.send(
            build_automation_token(expiration_period), AutomationToken
        )


class AsyncAuthResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def sign_in(self, email: str, password: str) -> ApiResponse[Tokens]:
        return await self.sign_in_with_hash(
            email, hashlib.md5(password.encode(), usedforsecurity=False).hexdigest()
        )

    async def sign_in_with_hash(
        self, email: str, password_md5: str
    ) -> ApiResponse[Tokens]:
        return await self._transport.send(build_sign_in(email, password_md5), Tokens)

    async def refresh(
        self, email: str, refresh_token: str, workspace_id: str
    ) -> ApiResponse[Tokens]:
        return await self._transport.send(
            build_refresh(email, refresh_token, workspace_id), Tokens
        )

    async def automation_token(
        self, expiration_period: ExpirationPeriod
    ) -> ApiResponse[AutomationToken]:
        return await self._transport.send(
            build_automation_token(expiration_period), AutomationToken
        )
