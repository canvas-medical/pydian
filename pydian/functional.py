from collections.abc import Sequence
from typing import Any


def first_of(
    seq: Sequence, default: Any | None = None, keep_n: int | None = None
) -> Any | Sequence[Any]:
    """
    Returns first non-None value in a Sequence (if any)
    """
    res = [item for item in seq if item is not None]
    if len(res) == 0:
        return default
    if keep_n:
        return res[:keep_n]
    return res[0]
