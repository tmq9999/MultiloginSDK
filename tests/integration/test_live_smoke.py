"""Explicitly opt-in: uses only a profile created by this test."""

import os
import uuid

import pytest

from multilogin_sdk import MultiloginClient
from multilogin_sdk.models.launcher import LauncherStartRequest
from multilogin_sdk.models.profiles import ProfileCreateRequest, ProfileRemoveRequest

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("MULTILOGIN_LIVE_TEST") != "1",
        reason="Live smoke requires explicit opt-in",
    ),
]


def test_live_owned_profile_smoke():
    required = [
        "MULTILOGIN_TOKEN",
        "MULTILOGIN_TEST_WORKSPACE_ID",
        "MULTILOGIN_TEST_FOLDER_ID",
    ]
    if not all(os.environ.get(k) for k in required):
        pytest.fail(
            "Live smoke requires token, test workspace ID and test folder ID before network"
        )
    with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as c:
        workspaces = c.workspaces.list().data.workspaces
        assert any(
            w.workspace_id == os.environ["MULTILOGIN_TEST_WORKSPACE_ID"]
            for w in workspaces
        )
        created = c.profiles.create(
            ProfileCreateRequest(
                name="sdk-smoke-" + uuid.uuid4().hex,
                folder_id=os.environ["MULTILOGIN_TEST_FOLDER_ID"],
            )
        ).data
        profile_id = created["ids"][0]
        try:
            with c.launcher.session(
                LauncherStartRequest(
                    folder_id=os.environ["MULTILOGIN_TEST_FOLDER_ID"],
                    profile_id=profile_id,
                )
            ) as connection:
                assert 1 <= connection.port <= 65535
        finally:
            c.profiles.remove(ProfileRemoveRequest(ids=[profile_id], permanently=False))
