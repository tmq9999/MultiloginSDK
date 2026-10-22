"""Offset arithmetic is bounded by the API's documented maximum."""
from .errors import PaginationLimitError


def next_offset(offset: int, limit: int, count: int) -> int | None:
    if count < limit:
        return None
    if offset + limit > 10000:
        raise PaginationLimitError('Search offset limit 10000 reached; narrow the search to continue')
    return offset + limit
