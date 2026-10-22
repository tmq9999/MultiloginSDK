"""Browser CRUD and search; update and partial update use distinct models."""
from collections.abc import Iterator, AsyncIterator
from .._operations import Operation, RequestSpec
from .._pagination import next_offset
from .._transport import SyncTransport, AsyncTransport
from ..models.common import ApiResponse
from ..models.profiles import (ProfileCreateRequest, ProfileUpdateRequest, ProfilePartialUpdateRequest,
    ProfileSearchRequest, ProfileRemoveRequest, ProfileRestoreRequest, ProfileMetasRequest,
    ProfileSearchData, ProfileSummary)

def build_create(request: ProfileCreateRequest) -> RequestSpec:
    return RequestSpec(Operation('profile_create','cloud','POST','/profile/create',read_only=False),json_body=request.to_wire())


def build_search(request: ProfileSearchRequest) -> RequestSpec:
    return RequestSpec(Operation('profile_search','cloud','POST','/profile/search',read_only=True),json_body=request.to_wire())


def build_update(request: ProfileUpdateRequest) -> RequestSpec:
    return RequestSpec(Operation('profile_update','cloud','POST','/profile/update',read_only=False),json_body=request.to_wire())


def build_partial_update(request: ProfilePartialUpdateRequest) -> RequestSpec:
    return RequestSpec(Operation('profile_partial_update','cloud','POST','/profile/partial_update',read_only=False),json_body=request.to_wire())


def build_remove(request: ProfileRemoveRequest) -> RequestSpec:
    return RequestSpec(Operation('profile_remove','cloud','POST','/profile/remove',read_only=False),json_body=request.to_wire())


def build_restore(request: ProfileRestoreRequest) -> RequestSpec:
    return RequestSpec(Operation('profile_restore','cloud','POST','/profile/restore',read_only=False),json_body=request.to_wire())


def build_metas(request: ProfileMetasRequest) -> RequestSpec:
    return RequestSpec(Operation('profile_metas','cloud','POST','/profile/metas',read_only=False),json_body=request.to_wire())


class ProfilesResource:
    def __init__(self,transport: SyncTransport) -> None:
        self._transport=transport

    def create(self,request: ProfileCreateRequest) -> ApiResponse[dict[str,object]]:
        return self._transport.send(build_create(request),dict[str,object])

    def search(self,request: ProfileSearchRequest) -> ApiResponse[ProfileSearchData]:
        return self._transport.send(build_search(request),ProfileSearchData)

    def update(self,request: ProfileUpdateRequest) -> ApiResponse[None]:
        return self._transport.send(build_update(request),type(None))

    def partial_update(self,request: ProfilePartialUpdateRequest) -> ApiResponse[None]:
        return self._transport.send(build_partial_update(request),type(None))

    def remove(self,request: ProfileRemoveRequest) -> ApiResponse[None]:
        return self._transport.send(build_remove(request),type(None))

    def restore(self,request: ProfileRestoreRequest) -> ApiResponse[None]:
        return self._transport.send(build_restore(request),type(None))

    def metas(self,request: ProfileMetasRequest) -> ApiResponse[dict[str,object]]:
        return self._transport.send(build_metas(request),dict[str,object])

    def iter_profiles(self,request: ProfileSearchRequest) -> Iterator[ProfileSummary]:
        offset=request.offset
        while True:
            page=ProfileSearchRequest.model_validate({**request.to_wire(),'offset':offset,'limit':request.limit})
            items=(self.search(page)).data.profiles
            for item in items:
                yield item
            next_page=next_offset(offset,request.limit,len(items))
            if next_page is None:
                return
            offset=next_page


class AsyncProfilesResource:
    def __init__(self,transport: AsyncTransport) -> None:
        self._transport=transport

    async def create(self,request: ProfileCreateRequest) -> ApiResponse[dict[str,object]]:
        return await self._transport.send(build_create(request),dict[str,object])

    async def search(self,request: ProfileSearchRequest) -> ApiResponse[ProfileSearchData]:
        return await self._transport.send(build_search(request),ProfileSearchData)

    async def update(self,request: ProfileUpdateRequest) -> ApiResponse[None]:
        return await self._transport.send(build_update(request),type(None))

    async def partial_update(self,request: ProfilePartialUpdateRequest) -> ApiResponse[None]:
        return await self._transport.send(build_partial_update(request),type(None))

    async def remove(self,request: ProfileRemoveRequest) -> ApiResponse[None]:
        return await self._transport.send(build_remove(request),type(None))

    async def restore(self,request: ProfileRestoreRequest) -> ApiResponse[None]:
        return await self._transport.send(build_restore(request),type(None))

    async def metas(self,request: ProfileMetasRequest) -> ApiResponse[dict[str,object]]:
        return await self._transport.send(build_metas(request),dict[str,object])

    async def iter_profiles(self,request: ProfileSearchRequest) -> AsyncIterator[ProfileSummary]:
        offset=request.offset
        while True:
            page=ProfileSearchRequest.model_validate({**request.to_wire(),'offset':offset,'limit':request.limit})
            items=(await self.search(page)).data.profiles
            for item in items:
                yield item
            next_page=next_offset(offset,request.limit,len(items))
            if next_page is None:
                return
            offset=next_page


