"""Launcher v2 regular and v3 quick profiles."""
from typing import Any, Literal, Self

from pydantic import Field, field_validator, model_validator

from .common import RequestModel, ResponseModel
from .profiles import BrowserType, OSType, ProfileParameters

AutomationType=Literal['selenium','puppeteer','playwright']


class LauncherStartRequest(RequestModel):
    folder_id: str = Field(min_length=1)
    profile_id: str = Field(min_length=1)
    automation_type: AutomationType = 'selenium'
    headless_mode: bool = False


class QuickProfileV3Request(RequestModel):
    browser_type: BrowserType = 'mimic'
    os_type: OSType = 'windows'
    script_file: str = ''
    automation: AutomationType = 'selenium'
    auto_update_core: bool = True
    core_version: int = Field(default=1, ge=1)
    core_minor_version: int = Field(default=0, ge=0)
    is_headless: bool = False
    parameters: ProfileParameters = Field(default_factory=ProfileParameters)

    @model_validator(mode='after')
    def compatibility(self) -> Self:
        if self.browser_type=='stealthfox' and self.automation!='selenium':
            raise ValueError('Stealthfox supports only selenium automation')
        if self.os_type=='android' and self.browser_type!='mimic':
            raise ValueError('Android browser profiles require mimic')
        return self


class BrowserConnection(ResponseModel):
    id: str = Field(min_length=1)
    port: int = Field(ge=1,le=65535)
    browser_type: str
    core_version: int | None = None
    is_quick: bool

    @field_validator('port',mode='before')
    @classmethod
    def port_number(cls,value: Any) -> int:
        if type(value) is int:
            return value
        if isinstance(value,str) and value.isascii() and value.isdigit():
            return int(value)
        raise ValueError('Connection port must be an integer or decimal string')
