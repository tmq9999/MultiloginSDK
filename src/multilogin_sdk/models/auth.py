"""Authentication models: credential values are hidden in repr and JSON dumps."""
from typing import Literal

from pydantic import SecretStr

from .common import ResponseModel

ExpirationPeriod = Literal['1h','3h','5h','16h','24h','48h','1w','2w','3w','1mo','no_exp']


class Tokens(ResponseModel):
    token: SecretStr
    refresh_token: SecretStr


class AutomationToken(ResponseModel):
    token: SecretStr
