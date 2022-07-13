from copy import deepcopy
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
    res = _nested_get(source, key, default)
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


def _nested_get(source: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Expects `.`-delimited string and tries to get the item in the dict.

    If the dict contains an array, the correct index is expected, e.g. for a dict d:
        d.a.b[0]
      will try d['a']['b'][0], where b should be an array with at least 1 item.


    If [*] is passed, then that means get into each object in the list. E.g. for a list l:
        l[*].a.b
      will return the following: [d['a']['b'] for d in l]

    TODO: Add support for list slicing, e.g. [:1], [1:], [:-1], etc.
    TODO: Add support for querying, maybe e.g. [?:key=1]
    """
    res = benedict(source)
    keypaths = key.split("[*].", 1)
    if "[*]" in keypaths[0]:
        res = res.get(keypaths[0][:-3])
    else:
        res = res.get(keypaths[0])
    if len(keypaths) > 1 and res is not None:
        res = [_nested_get(v, keypaths[1]) for v in res]
    res = _handle_ending_star_unwrap(res, key)
    return res if res is not None else default


def _nested_delete(
    source: dict[str, Any], keys_to_drop: Iterable[str]
) -> dict[str, Any]:
    """
    Returns the dictionary with the requested keys set to `None`
    """
    res = deepcopy(benedict(source))
    for key in keys_to_drop:
        curr_keypath = keypath_util.parse_keys(key, ".")
        # Check if value has a DROP object
        v = res[curr_keypath]
        if isinstance(v, DROP):
            # If "out of bounds", return an empty dict
            if -1 * v.value >= len(curr_keypath):
                return dict()
            curr_keypath = curr_keypath[: v.value]
        res[curr_keypath] = None
    return cast(dict[str, Any], res.dict())


T = TypeVar("T")


def _handle_ending_star_unwrap(res: T, key: str) -> T | list[Any]:
    # HACK: Handle unwrapping if specified at the end
    # TODO: Find a nicer way to do this. Works for now...
    if (
        key.endswith("[*]")
        and isinstance(res, list)
        and len(res) > 0
        and isinstance(res[0], list)
    ):
        new_res = [l for l in res if l is not None]
        return list(chain.from_iterable(new_res))
    return res
