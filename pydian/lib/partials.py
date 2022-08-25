from functools import partial
from typing import Any, Callable, Iterable, Sequence, TypeVar

import funcy


def take(n: int) -> Callable[[Sequence[Any]], list[Any]]:
    """
    Takes first n items from Sequence, returns as a list
    """
    return partial(funcy.take, n)


def map_list(fn: Callable) -> Callable[[Iterable], Any]:
    """
    Partial wrapper for `map`, then casts to a list
    """
    _map_to_list = lambda func, it: list(map(func, it))
    return partial(_map_to_list, fn)


def str_replace(old: str, new: str) -> Callable[[str], str]:
    """
    Partial wrapper for `str.replace`
    """
    _str_replace = lambda s: s.replace(old, new)
    return partial(_str_replace, old=old, new=new)
