from typing import Any, Callable
import re
from copy import deepcopy
from itertools import chain
from .enums import RelativeObjectLevel as ROL
from benedict import benedict
from benedict.dicts.keypath import keypath_util


def get(
    source: dict,
    key: str,
    default: Any = None,
    apply: Callable | None = None,
    drop_level: ROL | None = None,
):
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


def _nested_get(source: dict, key: str, default: Any = None) -> Any:
    """
    Expects `.`-delimited string and tries to get the item in the dict.

    If the dict contains an array, the correct index is expected, e.g. for a dict d:
        d.a.b[0]
    will try d['a']['b'][0], where a should be a dict containing b which should be an array with at least 1 item

    If d[*] is passed, then that means return a list of all elements. E.g. for a dict d:
    d[*].a.b
    will try to get e['a']['b'] for e in d

    TODO: Add support for querying, maybe e.g. [?: thing.val==1]
    """
    res = deepcopy(benedict(source))
    keypaths = key.split("[*].", 1)
    if "[*]" in keypaths[0]:
        res = res.get(keypaths[0][:-3])
    else:
        res = res.get(keypaths[0])
    if len(keypaths) > 1:
        res = [_nested_get(v, keypaths[1]) for v in res]
    res = __handle_ending_star_unwrap(res, key)
    return res if res is not None else default


def _nested_delete(source: dict, key: str) -> dict:
    """
    Has same syntax as _nested_get, except returns the original source
    with the requested key set to `None`
    """
    res = deepcopy(benedict(source))
    keypaths = key.split("[*].", 1)
    # Get up to the last key in keypath, then set that key to None
    #  We set to None instead of popping to preserve indices
    curr_keypath = keypath_util.parse_keys(keypaths[0], ".")
    if len(keypaths) > 1:
        res[curr_keypath] = [
            _nested_delete(r, keypaths[1]) if isinstance(r, dict) else None
            for r in res[curr_keypath]
        ]
    else:
        # Case: value has an ROL object
        v = res[curr_keypath]
        if isinstance(v, ROL):
            assert v.value < 0
            curr_keypath = curr_keypath[: v.value]
        res[curr_keypath] = None
    return res


def __handle_ending_star_unwrap(res: list, key: str) -> list:
    # HACK: Handle unwrapping if specified at the end
    # TODO: Find a nicer way to do this. Works for now...
    if key.endswith("[*]") and isinstance(res, list) and isinstance(res[0], list):
        res = [l for l in res if l != None]
        res = list(chain(*res))
    return res
