from typing import Any, Callable
import re
from copy import deepcopy
from itertools import chain

def get(msg: dict, key: str, default: Any = None, then: Callable | None = None):
    res = nested_get(msg, key, default) \
        if '.' in key else single_get(msg, key, default)
    if res and callable(then):
        try:
            res = then(res)
        except Exception as e:
            raise RuntimeError(f'`then` callable failed when getting key: {key}, error: {e}')
    return res

def single_get(msg: dict, key: str, default: Any = None) -> Any:
    """
    Gets single item, supports int indexing, e.g. `someKey[0]`
    """
    res = msg
    idx = re.search(r'\[\d+\]', key)
    if idx:
        idx_str = idx.group(0)
        # Cast the index (e.g. "[0]") to an int (e.g. 0)
        i = int(idx_str[1:-1])
        key = key.replace(idx_str, '')
        res = res.get(key, [])
        res = res[i] if i in range(len(res)) else None
    elif key[-3:] == '[*]':
        res = res.get(key[:-3])
        res = _handle_ending_star_unwrap(res, key)
    else:
        res = res.get(key, default)
    return res


def nested_get(msg: dict, key: str, default: Any = None) -> Any:
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
    if '.' not in key:
        return single_get(msg, key, default)
    stack = key.split('.')
    res = deepcopy(msg)
    while len(stack) > 0:
        k = stack.pop(0)
        # If need to unwrap, then empty stack 
        if k[-3:] == '[*]':
            k = k[:-3]
            remaining_key = '.'.join(stack)
            stack = [] # wipe stack for current run
            res = res.get(k)
            if remaining_key != '':
                res = [nested_get(v, remaining_key, None) for v in res]
        else:
            res = single_get(res, k)
        if res == None:
            break
    res = _handle_ending_star_unwrap(res, key)
    return res if res != None else default

def nested_delete(msg: dict, key: str) -> dict:
    """
    Has same syntax as nested_get, except returns the original msg
    with the requested key deleted
    """
    res = deepcopy(msg)
    curr = res
    keys = key.split('.')
    # TODO: Handle [*] case
    for k in keys[:-1]:
        curr = curr.get(k)
    try:
        curr.pop(keys[-1])
    except Exception as e:
        raise IndexError(f'Failed to perform nested_delete on key: {key}')
    return res

def _handle_ending_star_unwrap(res: dict, key: str) -> dict:
    # HACK: Handle unwrapping if specified at the end
    # TODO: Find a nicer way to do this. Works for now...
    if key[-3:] == '[*]' and type(res) == list and type(res[0]) == list:
        res = [l for l in res if l != None]
        res = list(chain(*res))
    return res