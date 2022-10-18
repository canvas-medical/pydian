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
    return lambda x: func(x, *args, **kwargs)


def add(value: Any, before: bool = False) -> ApplyFunc:
    if before:
        return lambda v: value + v
    return lambda v: v + value


def subtract(value: Any, before: bool = False) -> ApplyFunc:
    if before:
        return lambda v: value - v
    return lambda v: v - value


def multiply(value: Any, before: bool = False) -> ApplyFunc:
    if before:
        return lambda v: value * v
    return lambda v: v * value


def divide(value: Any, before: bool = False) -> ApplyFunc:
    if before:
        return lambda v: value / v
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


def map_to_list(func: Callable) -> ApplyFunc | Callable[[Iterable], list[Any]]:
    """
    Partial wrapper for `map`, then casts to a list
    """
    _map_to_list: Callable = lambda fn, it: list(map(fn, it))
    return partial(_map_to_list, func)


def filter_to_list(func: Callable) -> ApplyFunc | Callable[[Iterable], list[Any]]:
    """
    Partial wrapper for `filter`, then casts to a list
    """
    _filter_to_list: Callable = lambda fn, it: list(filter(fn, it))
    return partial(_filter_to_list, func)
