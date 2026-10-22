import pytest
from pydantic import ValidationError

from multilogin_sdk.models.profiles import (
    ProfileCreateRequest,
    ProfilePartialUpdateRequest,
    ProfileSearchData,
    ProfileSearchRequest,
)


def test_isp_payload():
    req = ProfileCreateRequest(
        name="x",
        folder_id="f",
        parameters={"proxy": {"host": "", "isp_ip_id": "isp"}},
        times=1,
    )
    assert req.to_wire()["parameters"]["proxy"] == {"host": "", "isp_ip_id": "isp"}
    with pytest.raises(ValidationError):
        ProfileCreateRequest(
            name="x",
            folder_id="f",
            parameters={"proxy": {"host": "", "isp_ip_id": "isp"}},
            times=2,
        )
    partial = ProfilePartialUpdateRequest(
        profile_id="p",
        proxy={"host": "", "isp_ip_id": "isp"},
        parameters={"flags": {"proxy_masking": "custom"}},
    )
    assert partial.to_wire()["proxy"]["host"] == ""
    assert "proxy" not in partial.to_wire()["parameters"]


def test_partial_preserves_explicit_false():
    assert ProfilePartialUpdateRequest(
        profile_id="p", auto_update_core=False
    ).to_wire() == {"profile_id": "p", "auto_update_core": False}
    assert ProfilePartialUpdateRequest(profile_id="p").to_wire() == {"profile_id": "p"}
    with pytest.raises(ValidationError):
        ProfilePartialUpdateRequest(profile_id="p", auto_update_core=None)


@pytest.mark.parametrize(
    "kwargs", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"offset": 10001}]
)
def test_search_boundaries(kwargs):
    with pytest.raises(ValidationError):
        ProfileSearchRequest(**kwargs)


def test_search_serializes_its_server_required_defaults():
    payload = ProfileSearchRequest(limit=1, offset=0).to_wire()

    assert {
        "is_removed": False,
        "core_version": 1,
        "limit": 1,
        "offset": 0,
        "search_text": "",
        "folder_id": "",
        "storage_type": "all",
        "order_by": "created_at",
        "sort": "asc",
    }.items() <= payload.items()


def test_search_response_normalizes_null_profiles_from_live_api():
    assert (
        ProfileSearchData.model_validate({"profiles": None, "total_count": 0}).profiles
        == []
    )
