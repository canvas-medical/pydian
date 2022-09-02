from functools import partial
from typing import Any, Callable, Container, Iterable, Sequence

import pydian
from pydian.types import DROP, ApplyFunc, ConditionalCheck

"""
`pydian` Wrappers
"""


def get(
    key: str,
    default: Any = None,
    apply: ApplyFunc | Iterable[ApplyFunc] | None = None,
    only_if: ConditionalCheck | None = None,
    drop_level: DROP | None = None,
):
    """
    Partial wrapper around the Pydian `get` function
    """
    kwargs = {
        "key": key,
        "default": default,
        "apply": apply,
        "only_if": only_if,
        "drop_level": drop_level,
    }
    return partial(pydian.get, **kwargs)


"""
Generic Wrappers
"""


def do(func: Callable, *args: Any, **kwargs: Any) -> Callable[[Any], Any]:
    """
    Generic partial wrapper for functions
    """
    return partial(func, *args, **kwargs)


def equals(value: Any) -> Callable[[Any], bool]:
    return lambda v: v == value


def equivalent(value: Any) -> Callable[[Any], bool]:
    return lambda v: v is value


def contained_in(container: Container) -> Callable[[Any], bool]:
    return lambda v: v in container


def not_equal(value: Any) -> Callable[[Any], bool]:
    return lambda v: v != value


def not_equivalent(value: Any) -> Callable[[Any], bool]:
    return lambda v: v is not value


def not_contained_in(container: Container) -> Callable[[Any], bool]:
    return lambda v: v not in container


def keep(n: int) -> Callable[[Iterable], list[Any]]:
    return lambda it: list(iter(it))[:n]


def index(i: int) -> Callable[[Iterable], Any]:
    return lambda it: list(iter(it))[i] if len(list(iter(it))) > 0 else None


"""
stdlib Wrappers
"""


def map_then_list(apply: Callable) -> Callable[[Iterable], Any]:
    """
    Partial wrapper for `map`, then casts to a list
    """
    _map_to_list: Callable = lambda func, it: list(map(func, it))
    return partial(_map_to_list, apply)


def filter_then_list(keep_filter: Callable) -> Callable[[Iterable], Any]:
    """
    Partial wrapper for `filter`, then casts to a list
    """
    _filter_to_list: Callable = lambda func, it: list(filter(func, it))
    return partial(_filter_to_list, keep_filter)


def replace_str(old: str, new: str) -> Callable[[str], str]:
    """
    Partial wrapper for `str.replace`
    """
    _str_replace: Callable = lambda old, new, s: str.replace(s, old, new)
    return partial(_str_replace, old, new)


def str_startswith(prefix: str) -> Callable[[str], bool]:
    """
    Partial wrapper for `str.startswith`
    """
    _str_startswith: Callable = lambda s, pre: str.startswith(s, pre)
    return partial(_str_startswith, pre=prefix)


def str_endswith(suffix: str) -> Callable[[str], bool]:
    """
    Partial wrapper for `str.endswith`
    """
    _str_endswith: Callable = lambda s, suf: str.endswith(s, suf)
    return partial(_str_endswith, suf=suffix)
