from functools import partial
from typing import Any, Callable, Collection, Iterable, Mapping, Sequence

import funcy

"""
stdlib Wrappers
"""


def map_list(apply: Callable) -> Callable[[Iterable], Any]:
    """
    Partial wrapper for `map`, then casts to a list
    """
    _map_to_list = lambda func, it: list(map(func, it))
    return partial(_map_to_list, apply)


def filter_list(apply: Callable) -> Callable[[Iterable], Any]:
    """
    Partial wrapper for `map`, then casts to a list
    """
    _filter_to_list: Callable = lambda func, it: list(filter(func, it))
    return partial(_filter_to_list, apply)


def str_replace(old: str, new: str) -> Callable[[str], str]:
    """
    Partial wrapper for `str.replace`
    """
    _str_replace = lambda old, new, s: s.replace(old, new)
    return partial(_str_replace, old, new)


"""
`funcy` Wrappers
"""
# TODO: These are technically not partials, split-out into separate helper module?
first = funcy.first
join = funcy.join


def take(n: int) -> Callable[[Sequence[Any]], list[Any]]:
    """
    Takes first n items from Sequence, returns as a list
    """
    return partial(funcy.take, n)


def nth(n: int) -> Callable[[Sequence[Any]], list[Any]]:
    """
    Takes first n items from Sequence, returns as a list
    """
    return partial(funcy.nth, n)


def walk(apply: Callable) -> Callable[[Collection], Collection]:
    return partial(funcy.walk, apply)


def walk_keys(apply: Callable) -> Callable[[Mapping[Any, Any]], Mapping[Any, Any]]:
    return partial(funcy.walk_keys, apply)


def walk_values(apply: Callable) -> Callable[[Mapping[Any, Any]], Mapping[Any, Any]]:
    return partial(funcy.walk_values, apply)


def select(filter_by: Callable) -> Callable[[Collection], Collection]:
    return partial(funcy.select, filter_by)


def select_keys(filter_by: Callable) -> Callable[[Mapping[Any, Any]], Mapping[Any, Any]]:
    return partial(funcy.select_keys, filter_by)
