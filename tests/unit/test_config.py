import pytest
from multilogin_sdk.config import ClientConfig


@pytest.mark.parametrize('kwargs', [dict(max_retries=-1), dict(retry_budget=-1), dict(cloud_url='https://user:secret@api.test'), dict(cloud_url='https://api.test/?token=s'), dict(cloud_url='file:///tmp/x'), dict(launcher_url='https://api.test/#x')])
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        ClientConfig(**kwargs)
