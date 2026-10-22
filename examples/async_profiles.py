"""Async equivalent; no network occurs when importing this example."""

import asyncio
import os

from multilogin_sdk import AsyncMultiloginClient
from multilogin_sdk.models.launcher import LauncherStartRequest
from multilogin_sdk.models.profiles import ProfileSearchRequest


async def main() -> None:
    async with AsyncMultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
        async for profile in client.profiles.iter_profiles(
            ProfileSearchRequest(limit=10)
        ):
            print(profile.id, profile.name)
        profile_id = os.environ.get("MULTILOGIN_PROFILE_ID")
        if profile_id:
            async with client.launcher.session(
                LauncherStartRequest(
                    folder_id=os.environ["MULTILOGIN_FOLDER_ID"], profile_id=profile_id
                )
            ) as connection:
                print("Automation port:", connection.port)


if __name__ == "__main__":
    asyncio.run(main())
