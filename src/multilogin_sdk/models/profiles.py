"""Operation-specific browser profile payloads."""
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from .common import RequestModel, ResponseModel

BrowserType = Literal['mimic', 'stealthfox']
OSType = Literal['linux','macos','windows','android']


class Proxy(RequestModel):
    host: str
    type: str = ''
    port: int = Field(default=1, ge=1, le=65535)
    username: str = Field(default='', repr=False)
    password: str = Field(default='', repr=False)
    isp_ip_id: str = ''
    save_traffic: bool = False


class Flags(RequestModel):
    audio_masking: str = 'natural'
    fonts_masking: str = 'mask'
    geolocation_masking: str = 'mask'
    geolocation_popup: str = 'prompt'
    graphics_masking: str = 'mask'
    graphics_noise: str = 'mask'
    localization_masking: str = 'mask'
    media_devices_masking: str = 'mask'
    navigator_masking: str = 'mask'
    ports_masking: str = 'mask'
    proxy_masking: str = 'disabled'
    screen_masking: str = 'mask'
    timezone_masking: str = 'mask'
    webrtc_masking: str = 'mask'
    canvas_noise: str = 'mask'
    startup_behavior: str = 'recover'
    quic_mode: str = 'disabled'


class Storage(RequestModel):
    is_local: bool = False
    save_service_worker: bool = False


class PartialParameters(RequestModel):
    flags: Flags = Field(default_factory=Flags)
    storage: Storage = Field(default_factory=Storage)
    fingerprint: dict[str, Any] = Field(default_factory=dict)


class ProfileParameters(PartialParameters):
    proxy: Proxy | None = None
    custom_start_urls: list[str] = Field(default_factory=list, max_length=5)

    @model_validator(mode='before')
    @classmethod
    def reject_null_proxy(cls, values: Any) -> Any:
        if isinstance(values, dict) and 'proxy' in values and values['proxy'] is None:
            raise ValueError('Omit proxy instead of sending null')
        return values


class ProfileCreateRequest(RequestModel):
    name: str = Field(min_length=1)
    folder_id: str = Field(min_length=1)
    browser_type: BrowserType = 'mimic'
    os_type: OSType = 'windows'
    auto_update_core: bool = True
    core_version: int = Field(default=1, ge=1)
    core_minor_version: int = Field(default=0, ge=0)
    times: int = Field(default=1, ge=1, le=10)
    notes: str = Field(default='', max_length=400)
    tags: list[str] = Field(default_factory=list, max_length=10)
    parameters: ProfileParameters = Field(default_factory=ProfileParameters)

    @model_validator(mode='after')
    def constraints(self) -> Self:
        if self.parameters.proxy and self.parameters.proxy.isp_ip_id and self.times != 1:
            raise ValueError('ISP proxy requires times=1')
        if self.os_type == 'android' and self.browser_type != 'mimic':
            raise ValueError('Android browser profiles require mimic')
        return self


class ProfileUpdateRequest(RequestModel):
    profile_id: str = Field(min_length=1)
    name: str = Field(default='', min_length=1)
    auto_update_core: bool = True
    core_version: int = Field(default=1, ge=1)
    core_minor_version: int = Field(default=0, ge=0)
    notes: str = Field(default='', max_length=400)
    tags: list[str] = Field(default_factory=list, max_length=10)
    parameters: ProfileParameters = Field(default_factory=ProfileParameters)


class ProfilePartialUpdateRequest(RequestModel):
    profile_id: str = Field(min_length=1)
    name: str = Field(default='', min_length=1)
    auto_update_core: bool = True
    core_version: int = Field(default=1, ge=1)
    core_minor_version: int = Field(default=0, ge=0)
    notes: str = Field(default='', max_length=400)
    tags: list[str] = Field(default_factory=list, max_length=10)
    parameters: PartialParameters = Field(default_factory=PartialParameters)
    proxy: Proxy | None = None
    custom_start_urls: list[str] = Field(default_factory=list, max_length=5)

    @model_validator(mode='before')
    @classmethod
    def reject_null_proxy(cls, values: Any) -> Any:
        if isinstance(values, dict) and 'proxy' in values and values['proxy'] is None:
            raise ValueError('Omit proxy instead of sending null')
        return values


class ProfileSearchRequest(RequestModel):
    is_removed: bool = False
    core_version: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0, le=10000)
    search_text: str = Field(default='', max_length=50)
    folder_id: str = ''
    storage_type: Literal['all','cloud','local'] = 'all'
    order_by: Literal['name','created_at','updated_at','started_at','removed_at'] = 'created_at'
    sort: Literal['asc','desc'] = 'asc'
    created_from: str = ''
    created_to: str = ''
    updated_from: str = ''
    updated_to: str = ''
    last_launched_from: str = ''
    last_launched_to: str = ''
    last_launched_by: str = ''
    last_launched_on: str = ''
    last_updated_by: str = ''
    in_use_by: str = ''
    created_by: str = ''
    tags: list[str] = Field(default_factory=list)
    password_protected: bool = False
    password_restricted: list[str] = Field(default_factory=list)
    notes: str = ''


class ProfileRemoveRequest(RequestModel):
    ids: list[str] = Field(min_length=1)
    permanently: bool = False


class ProfileRestoreRequest(RequestModel):
    ids: list[str] = Field(min_length=1)


class ProfileMetasRequest(RequestModel):
    ids: list[str] = Field(min_length=1)


class ProfileSummary(ResponseModel):
    id: str
    name: str
    browser_type: str


class ProfileSearchData(ResponseModel):
    profiles: list[ProfileSummary]
