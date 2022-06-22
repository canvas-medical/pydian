from typing import Any, Callable
import re
from copy import deepcopy
from itertools import chain
from .enums import RelativeObjectLevel as ROL

def get(msg: dict, key: str, default: Any = None, then: Callable | None = None, drop_rol: ROL | None = None):
    res = nested_get(msg, key, default) \
        if '.' in key else single_get(msg, key, default)
    if res and callable(then):
        try:
            res = then(res)
        except Exception as e:
            raise RuntimeError(f'`then` callable failed when getting key: {key}, error: {e}')
    if drop_rol and res is None:
        res = drop_rol
    return res

def single_get(msg: dict, key: str, default: Any = None) -> Any:
    """
    Gets single item, supports int indexing, e.g. `someKey[0]`
    """
    res = msg
    idx = re.search(r'\[\d+\]', key)
    if idx:
        # TODO: consolidate str logic into shared functions
        #       E.g. have `_clean_idx` handle this case 
        idx_str = idx.group(0)
        i = int(idx_str[1:-1]) # Casts str->int, e.g. "[0]" -> 0
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

# TODO: Add test for this
def nested_delete(msg: dict, key: str) -> dict:
    """
    Has same syntax as nested_get, except returns the original msg
    with the requested key deleted
    """
    res = deepcopy(msg)
    # Case: value has an ROL object
    v = get(res, key)
    nidx = -1
    if type(v) == ROL:
        assert v.value < 0
        nidx += v.value
    # For nesting, an array index counts as a level
    #  e.g. 'a.b[0].c' -> ['a', 'b', 0, 'c']
    # TODO: see if can leverage benedict library (update DictWrapper)
    nesting = []
    for item in key.split('.'):
        if '[' in item:
            parts = item.split('[')
            parts[1] = f'[{parts[1]}'
            nesting += parts
        else:
            nesting.append(item)
    nesting = list(map(_clean_idx, nesting))
    # Get up to the last key in nesting, then try to pop that key
    curr = res
    for i in nesting[:nidx]:
        # TODO: Handle [*] case
        try:
            curr = curr[i]
        except Exception as e:
            raise IndexError(f'Failed to perform nested_delete on key: {key}, Error: {e}, Input: {msg}')
    try:
        # TODO: Handle [*] case
        del curr[nesting[nidx]]
    except Exception as e:
        raise IndexError(f'Failed to perform nested_delete on key: {key}, Error: {e}, Input: {msg}')
    return res

def _handle_ending_star_unwrap(res: dict, key: str) -> dict:
    # HACK: Handle unwrapping if specified at the end
    # TODO: Find a nicer way to do this. Works for now...
    if key[-3:] == '[*]' and type(res) == list and type(res[0]) == list:
        res = [l for l in res if l != None]
        res = list(chain(*res))
    return res

def _clean_idx(s: str) -> int | str:
    """
    Cleans "[0]" -> 0, otherwise returns original str
    """
    KEY_INDEX_RE = r"(?:\[[\'\"]*(\-?[\d]+)[\'\"]*\]){1}$"
    matches = re.findall(KEY_INDEX_RE, s)
    if matches:
        s = re.sub(KEY_INDEX_RE, "", s)
        index = int(matches[0])
        return index
    return s