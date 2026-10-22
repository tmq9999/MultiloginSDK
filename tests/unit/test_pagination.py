import json

import httpx
import pytest
from conftest import envelope, resolve, session_for

from multilogin_sdk import AsyncMultiloginClient, MultiloginClient
from multilogin_sdk.errors import PaginationLimitError
from multilogin_sdk.models.profiles import ProfileSearchRequest


@pytest.mark.parametrize(
    "offset,lengths,expected,error",
    [
        (0, [2, 1], [0, 2], False),
        (10000, [2], [10000], True),
        (10000, [1], [10000], False),
        (0, [0], [0], False),
    ],
)
async def test_pagination_boundary(mode, offset, lengths, expected, error):
    offsets = []

    def handler(req):
        offsets.append(json.loads(req.content)["offset"])
        n = lengths[len(offsets) - 1]
        return httpx.Response(
            200,
            json=envelope(
                {
                    "profiles": [
                        {"id": str(i), "name": "x", "browser_type": "mimic"}
                        for i in range(n)
                    ]
                }
            ),
        )

    s = session_for(mode, handler)
    c = (MultiloginClient if mode == "sync" else AsyncMultiloginClient)(
        "T", sessions={"cloud": s}
    )

    async def collect():
        iterator = c.profiles.iter_profiles(
            ProfileSearchRequest(limit=2, offset=offset)
        )
        if mode == "sync":
            return list(iterator)
        return [x async for x in iterator]

    if error:
        with pytest.raises(PaginationLimitError):
            await collect()
    else:
        result = await collect()
        assert len(result) == sum(lengths)
    assert offsets == expected
    await resolve(c.close() if mode == "sync" else c.aclose())
    await resolve(s.close() if mode == "sync" else s.aclose())
