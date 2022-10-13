from functools import partial
from itertools import islice
from typing import Any, Callable, Container, Iterable, Reversible

import pydian
from pydian.lib.types import DROP, ApplyFunc, ConditionalCheck

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


def do(func: Callable, *args: Any, **kwargs: Any) -> ApplyFunc:
    """
    Generic partial wrapper for functions.

    Starts at the second parameter when using *args (as opposed to the first).
    """
    # To start partial application at second param, convert args -> kwargs based on index.
    if not kwargs:
        kwargs = {}
    if args:
        varnames = func.__code__.co_varnames
        if len(args) >= len(varnames):
            raise ValueError(
                f"Received too many parameters to partial (expected at most {len(varnames) - 1}, got {len(args)})"
            )
        varnames_to_map = varnames[1:]
        kwargs.update({varnames_to_map[i]: args[i] for i in range(len(args))})
    return partial(func, **kwargs)


def add(value: Any) -> ApplyFunc:
    return lambda v: v + value


def subtract(value: Any) -> ApplyFunc:
    return lambda v: v - value


def multiply(value: Any) -> ApplyFunc:
    return lambda v: v * value


def divide(value: Any) -> ApplyFunc:
    return lambda v: v / value


def keep(n: int) -> ApplyFunc | Callable[[Iterable], list[Any]]:
    return lambda it: list(islice(it, n))


def index(idx: int) -> ApplyFunc | Callable[[Reversible], Any]:
    def get_index(obj: Reversible, i: int) -> Any:
        if i >= 0:
            it = iter(obj)
        else:
            i = (i + 1) * -1
            it = reversed(obj)
        return next(islice(it, i, i + 1), None)

    return partial(get_index, i=idx)


def equals(value: Any) -> ConditionalCheck:
    return lambda v: v == value


def gt(value: Any) -> ConditionalCheck:
    return lambda v: v > value


def lt(value: Any) -> ConditionalCheck:
    return lambda v: v < value


def gte(value: Any) -> ConditionalCheck:
    return lambda v: v >= value


def lte(value: Any) -> ConditionalCheck:
    return lambda v: v <= value


def equivalent(value: Any) -> ConditionalCheck:
    return lambda v: v is value


def contains(value: Any) -> ConditionalCheck:
    return lambda container: value in container


def contained_in(container: Container) -> ConditionalCheck:
    return lambda v: v in container


def not_equal(value: Any) -> ConditionalCheck:
    return lambda v: v != value


def not_equivalent(value: Any) -> ConditionalCheck:
    return lambda v: v is not value


def not_contains(value: Any) -> ConditionalCheck:
    return lambda container: value not in container


def not_contained_in(container: Container) -> ConditionalCheck:
    return lambda v: v not in container


"""
stdlib Wrappers
"""


def map_to_list(apply: Callable) -> ApplyFunc | Callable[[Iterable], list[Any]]:
    """
    Partial wrapper for `map`, then casts to a list
    """
    _map_to_list: Callable = lambda func, it: list(map(func, it))
    return partial(_map_to_list, apply)


def filter_to_list(keep_filter: Callable) -> ApplyFunc | Callable[[Iterable], list[Any]]:
    """
    Partial wrapper for `filter`, then casts to a list
    """
    _filter_to_list: Callable = lambda func, it: list(filter(func, it))
    return partial(_filter_to_list, keep_filter)


def str_replace(old: str, new: str) -> ApplyFunc | Callable[[str], str]:
    """
    Partial wrapper for `str.replace`
    """
    _str_replace: Callable = lambda old, new, s: str.replace(s, old, new)
    return partial(_str_replace, old, new)


def str_startswith(prefix: str) -> ApplyFunc | Callable[[str], bool]:
    """
    Partial wrapper for `str.startswith`
    """
    _str_startswith: Callable = lambda s, pre: str.startswith(s, pre)
    return partial(_str_startswith, pre=prefix)


def str_endswith(suffix: str) -> ApplyFunc | Callable[[str], bool]:
    """
    Partial wrapper for `str.endswith`
    """
    _str_endswith: Callable = lambda s, suf: str.endswith(s, suf)
    return partial(_str_endswith, suf=suffix)
