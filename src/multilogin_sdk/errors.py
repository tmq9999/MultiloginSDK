"""Errors expose safe metadata and never retain raw responses or request bodies."""


class MultiloginError(Exception):
    def __init__(self, message: str, *, operation: str = '', status_code: int | None = None,
                 api_error_code: str | None = None, request_id: str | None = None) -> None:
        super().__init__(message)
        self.operation = operation
        self.status_code = status_code
        self.api_error_code = api_error_code
        self.request_id = request_id


class HttpError(MultiloginError):
    pass


class ApiError(MultiloginError):
    pass


class ProtocolError(MultiloginError):
    pass


class TransportError(MultiloginError):
    pass


class LauncherUnavailable(TransportError):
    pass


class PaginationLimitError(MultiloginError):
    pass


class PollingTimeout(MultiloginError):
    pass
