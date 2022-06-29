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
    res = (
        _nested_get(source, key, default)
        if "." in key
        else _single_get(source, key, default)
    )
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
    res = source
    idx = re.search(r"\[\d+\]", key)
    if idx:
        # TODO: consolidate str logic into shared functions
        #       E.g. have `_clean_idx` handle this case
        idx_str = idx.group(0)
        i = int(idx_str[1:-1])  # Casts str->int, e.g. "[0]" -> 0
        key = key.replace(idx_str, "")
        res = res.get(key, [])
        res = res[i] if i in range(len(res)) else None
    elif key.endswith("[*]"):
        res = res.get(key[:-3])
        res = __handle_ending_star_unwrap(res, key)
    else:
        res = res.get(key, default)
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
    if "." not in key:
        return _single_get(source, key, default)
    stack = key.split(".")
    res = deepcopy(source)
    while len(stack) > 0:
        k = stack.pop(0)
        # If need to unwrap, then empty stack
        if k.endswith("[*]"):
            k = k[:-3]
            remaining_key = ".".join(stack)
            stack = []  # wipe stack for current run
            res = res.get(k)
            if remaining_key != "":
                res = [_nested_get(v, remaining_key, None) for v in res]
        else:
            res = _single_get(res, k)
        if res == None:
            break
    res = __handle_ending_star_unwrap(res, key)
    return res if res != None else default


def _nested_delete(source: dict, key: str) -> dict:
    """
    Has same syntax as _nested_get, except returns the original source
    with the requested key set to `None`
    """
    res = deepcopy(benedict(source))
    keypaths = [keypath_util.parse_keys(k, ".") for k in key.split("[*].")]
    # Case: value has an ROL object
    v = get(res, key)
    if type(v) == ROL:
        assert v.value < 0
        keypaths[-1] = keypaths[-1][: v.value]
    # Get up to the last key in keypath, then set that key to None
    #  We set to None instead of popping to preserve indices
    try:
        curr_keypath = keypaths[0]
        if len(keypaths) > 1:
            remaining_key = ".".join(key.split("[*].", 1)[1:])
            assert issubclass(type(res[curr_keypath][0]), dict)
            res[curr_keypath] = [
                _nested_delete(r, remaining_key) if issubclass(type(r), dict) else None
                for r in res[curr_keypath]
            ]
        else:
            res[curr_keypath] = None
    except Exception as e:
        raise IndexError(
            f"Failed to perform _nested_delete on key: {key}, Error: {e}, Input: {source}"
        )
    return res


def __handle_ending_star_unwrap(res: list, key: str) -> list:
    # HACK: Handle unwrapping if specified at the end
    # TODO: Find a nicer way to do this. Works for now...
    if key.endswith("[*]") and isinstance(res, list) and isinstance(res[0], list):
        res = [l for l in res if l != None]
        res = list(chain(*res))
    return res
