"""Declarative requests shared by sync and async execution."""
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Literal, Mapping

Service = Literal['cloud', 'launcher', 'cookies']


@dataclass(frozen=True)
class Operation:
    name: str
    service: Service
    method: str
    path: str
    read_only: bool = False
    auth_required: bool = True
    response_kind: Literal['envelope', 'empty', 'binary'] = 'envelope'
    read_timeout: float | None = None


@dataclass(frozen=True)
class RequestSpec:
    operation: Operation
    path_params: Mapping[str, str] = field(default_factory=dict)
    query: Mapping[str, Any] = field(default_factory=dict)
    json_body: Mapping[str, Any] | None = None
    strict_mode: bool | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'path_params', deepcopy(dict(self.path_params)))
        object.__setattr__(self, 'query', deepcopy(dict(self.query)))
        object.__setattr__(self, 'json_body', deepcopy(dict(self.json_body)) if self.json_body is not None else None)
