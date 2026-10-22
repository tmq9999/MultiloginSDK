import pytest

from multilogin_sdk.config import ClientConfig


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_retries": -1},
        {"retry_budget": -1},
        {"cloud_url": "https://user:secret@api.test"},
        {"cloud_url": "https://api.test/?token=s"},
        {"cloud_url": "file:///tmp/x"},
        {"launcher_url": "https://api.test/#x"},
    ],
)
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        ClientConfig(**kwargs)
