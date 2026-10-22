"""Read profiles; run an owned browser session only for a supplied profile."""

import os

from multilogin_sdk import MultiloginClient
from multilogin_sdk.models.launcher import LauncherStartRequest
from multilogin_sdk.models.profiles import ProfileSearchRequest


def main() -> None:
    with MultiloginClient(os.environ["MULTILOGIN_TOKEN"]) as client:
        for profile in client.profiles.iter_profiles(ProfileSearchRequest(limit=10)):
            print(profile.id, profile.name)
        profile_id = os.environ.get("MULTILOGIN_PROFILE_ID")
        if profile_id:
            with client.launcher.session(
                LauncherStartRequest(
                    folder_id=os.environ["MULTILOGIN_FOLDER_ID"], profile_id=profile_id
                )
            ) as connection:
                print("Automation port:", connection.port)


if __name__ == "__main__":
    main()
