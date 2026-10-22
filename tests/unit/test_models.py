import pytest
from pydantic import Field, ValidationError

from multilogin_sdk.models.common import UNSET, RequestModel, ResponseModel


class Payload(RequestModel):
    enabled: bool = True
    count: int = 1
    name: str = "default"
    ids: list[str] = Field(default_factory=list)
    nullable: str | None = None


def test_omitted_vs_falsy():
    assert Payload(enabled=False, count=0, name="", ids=[]).to_wire() == {
        "enabled": False,
        "count": 0,
        "name": "",
        "ids": [],
    }
    assert Payload(enabled=UNSET).to_wire() == {}
    assert Payload(nullable=None).to_wire() == {"nullable": None}
    with pytest.raises(ValidationError):
        Payload(enabled=None)
    with pytest.raises(ValidationError):
        Payload(typo=True)


def test_extra_response_preserved():
    assert ResponseModel.model_validate({"future": False}).model_dump() == {
        "future": False
    }
