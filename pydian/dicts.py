import re
from collections import deque
from itertools import chain
from typing import Any, Callable, Iterable, TypeVar, cast

from benedict import benedict
from benedict.dicts.keypath import keypath_util

from .lib.enums import DeleteRelativeObjectPlaceholder as DROP


def get(
    source: dict[str, Any],
    key: str,
    default: Any = None,
    apply: Callable[[Any], Any] | None = None,
    drop_level: DROP | None = None,
) -> Any:
    """
    Gets a value from the source dictionary using a `.` syntax.
    Handles None-checking (instead of raising error, returns default).

    `key` notes:
     - Use `.` to chain gets
     - Index into lists, e.g. `[0]`, `[-1]`
     - Iterate through and "unwrap" a list using `[*]`

    Use `apply` to safely chain an operation on a successful get.

    Use `drop_level` to specify conditional dropping if get results in None.
    """
    res = _nested_get(source, key.split("."), default)
    if res and apply:
        try:
            res = apply(res)
        except Exception as e:
            raise RuntimeError(
                f"`apply` callable failed when getting key: {key}, error: {e}"
            )
    if drop_level and res is None:
        res = drop_level
    return res


def _single_get(source: dict, key: str, default: Any = None) -> Any:
    """
    Gets single item, supports int indexing, e.g. `someKey[0]`
    """
    if match := re.fullmatch(r"(.*)\[(-?\d+|\*)\]$", key):
        key_part = match.group(1)
        index_part = match.group(2)
        if index_part == "*":
            return _handle_ending_star_unwrap(source.get(key_part))
        values = source.get(key_part, [])
        try:
            return values[int(index_part)]
        except IndexError:
            return None
    return source.get(key, default)


def _nested_get(
    source: dict[str, Any], key_list: list[str], default: Any = None
) -> Any:
    """
    Expects `.`-delimited string and tries to get the item in the dict.

    If the dict contains an array, the correct index is expected, e.g. for a dict d:
        d.a.b[0]
      will try d['a']['b'][0], where b should be an array with at least 1 item.


    If [*] is passed, then that means get into each object in the list. E.g. for a list l:
        l[*].a.b
      will return the following: [d['a']['b'] for d in l]
    """
    # Handle base cases
    match len(key_list):
        case 0:
            return None
        case 1:
            return _single_get(source, key_list[0], default)

    queue = deque(key_list)
    res = source
    while len(queue) > 0:
        key_part = queue.popleft()
        # If need to unwrap, then empty queue
        if key_part.endswith("[*]"):
            res = res.get(key_part[:-3], [])
            # Handle remaining queue items in the recursive call(s)
            if len(queue) > 0:
                res = [_nested_get(v, list(queue), []) for v in res]
                queue.clear()
        else:
            res = _single_get(res, key_part)
            if res is None:
                break
    if key_list[-1].endswith("[*]"):
        res = _handle_ending_star_unwrap(res)
    return res if res is not None else default


def _nested_delete(
    source: dict[str, Any], keys_to_drop: Iterable[str]
) -> dict[str, Any]:
    """
    Returns the dictionary with the requested keys set to `None`.

    DROP values are checked and handled here.
    """
    res = benedict(source)
    for key in keys_to_drop:
        curr_keypath = keypath_util.parse_keys(key, ".")
        # Check if value has a DROP object
        v = res[curr_keypath]
        if isinstance(v, DROP):
            # If "out of bounds", raise an error
            if -1 * v.value > len(curr_keypath):
                raise RuntimeError(f"Error: DROP level {v} at {key} is out-of-bounds")
            curr_keypath = curr_keypath[: v.value]
            # Handle case for dropping entire object
            if len(curr_keypath) == 0:
                return dict()
        res[curr_keypath] = None
    return cast(dict[str, Any], res.dict())


T = TypeVar("T")


def _handle_ending_star_unwrap(res: T) -> T | list[Any]:
    """
    Handles case of [*] unwrap specified at the end

    E.g. given: `a[*].b.c`    -> [[1, 2, 3], [4, 5, 6]]
          then: `a[*].b.c[*]` -> [1, 2, 3, 4, 5, 6]

    # TODO: Find a nicer way to do this. Works for now...
    """
    if isinstance(res, list) and len(res) > 0 and isinstance(res[0], list):
        new_res = [l for l in res if l is not None]
        return list(chain.from_iterable(new_res))
    return res
