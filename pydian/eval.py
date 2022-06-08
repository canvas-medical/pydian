"""
Transform functions

All functions in this module have at least 1 required parameter which represents
the incoming message. Thus, all functions in this module are curry-able
and compatible to be evaluated in mapping rules.
"""

from typing import Any, Optional, Union
from collections.abc import Callable
from pydian.lib.util import has_content, remove_empty_values, update_dict
from itertools import chain
from copy import deepcopy
import re

def evaluate_mapping_statement(msg: dict, statement: Any, remove_empty: bool) -> Any:
    """
    Evalutes the statement on the msg dict.

    Program-specific things:
    - If function is passed, it needs to take exactly 1 argument (the msg message)
    - Else, it should be a primitive
    """
    res = None
    if callable(statement):
        try:
            res = statement(deepcopy(msg))
        # TODO: make sure exceptions here are nice
        except Exception as e:
            raise ValueError(f'Function evaluation failed at statement {statement}, error: {e}')
    elif type(statement) == list:
        res = [evaluate_mapping_statement(msg, s, remove_empty) for s in statement]
    elif type(statement) == dict:
        res = {
            k: evaluate_mapping_statement(msg, statement[k], remove_empty) for k in statement
        }
    else:
        res = statement
        if type(res) not in {str, bool, int, float}:
            raise ValueError(f"Error when evaluating {statement}: result cannot be non-primitive value")
    if remove_empty:
        res = remove_empty_values(res)
    return res


def apply_mapping(msg: dict, mapping: dict, start_at_key: Optional[str] = None, remove_empty: bool = False) -> dict:
    """
    The main mapping function. Recursively evaluates and creates transformed JSON from input mapping

    Python's native recursion limit is ~1000 calls which functionally should not be an issue
    """
    local_msg = deepcopy(msg)
    if start_at_key:
        local_msg = nested_get(local_msg, start_at_key)
    res = dict()
    # Only use fields specified in mapping
    for k in mapping:
        # Dict (JSON Object)
        if type(mapping[k]) == dict:
            v = apply_mapping(local_msg, mapping[k], remove_empty=remove_empty)
            res = update_dict(res, k, v, remove_empty=remove_empty)
        # List (JSON Array)
        elif type(mapping[k]) == list:
            vals = []
            for m in mapping[k]:
                if type(m) == dict:
                    v = apply_mapping(local_msg, m, remove_empty=remove_empty)
                    if not remove_empty or has_content(v):
                        vals.append(v)
                else:
                    v = evaluate_mapping_statement(local_msg, m, remove_empty=remove_empty)
                    if not remove_empty or has_content(v):
                        vals.append(v)
            res = update_dict(res, k, vals, remove_empty)
        # Primitive, or Function output
        else:
            v = evaluate_mapping_statement(local_msg, mapping[k], remove_empty=remove_empty)
            res = update_dict(res, k, v, remove_empty=remove_empty)
    return res


def eval_then_apply(msg: dict, eval: Callable, apply: Callable) -> Any:
    """
    Evaluates the function, then appliies the second function
    """
    # TODO: add nicer error handling
    res = None
    if not (callable(eval) and callable(apply)):
        raise ValueError(f'One or both of the following is not callable:\n\t{eval}\n\t{apply}')
    l = eval(msg)
    res = apply(l)
    return res

def single_get(msg: dict, key: str, default: Any = None) -> Any:
    """
    Gets single item, supports int indexing, e.g. `someKey[0]`

    If indexing a dict, use `nested_get` instead
    """
    res = msg
    idx = re.search(r'\[\d+\]', key)
    if idx:
        idx_str = idx.group(0)
        # Cast the index (e.g. "[0]") to an int (e.g. 0)
        i = int(idx_str[1:-1])
        key = key.replace(idx_str, '')
        res = res.get(key)
        res = res[i] if i in range(len(res)) else None
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
    stack = key.split('.')[::-1]
    res = deepcopy(msg)
    while len(stack) > 0:
        k = stack.pop()
        # If need to unwrap, then empty stack 
        if '[*]' in k:
            k = k.replace('[*]', '')
            remaining_key = '.'.join(stack[::-1])
            stack = []
            res = res.get(k)
            if remaining_key != '':
                res = [nested_get(v, remaining_key, None) for v in res]
        else:
            res = single_get(res, k)
        if res == None:
            break
    # HACK: Handle unwrapping if specified at the end
    # TODO: Find a nicer way to do this. Works for now...
    if key[-3:] == '[*]' and type(res) == list and type(res[0]) == list:
        res = [l for l in res if l != None]
        res = list(chain(*res))
    return res if res != None else default

def map_list(msg: dict, iter_over: Union[list, Callable], apply_fn: Callable, remove_empty: bool = False) -> list:
    """
    Takes function in and applies it over each item from `iter_over`. 
    
    Returns as list
    """
    if callable(iter_over):
        iter_over = evaluate_mapping_statement(msg, iter_over, remove_empty)

    if not hasattr(iter_over, '__iter__'):
        raise TypeError(f'iter_over was not a valid tuple or iterable, got: {iter_over}') 
    
    # Do the iterating
    res = map(apply_fn, iter_over)
    
    return list(res)

def concat(msg: dict, items: tuple, remove_empty: bool) -> Any:
    """
    Takes all items in the list and adds them together (Python's + operator)
    """
    res = None
    for item in items:
        val = evaluate_mapping_statement(msg, item, remove_empty)
        if res == None:
            res = val
        elif val == None:
            continue
        else:
            res += val
    return res

def filter_list(msg: dict, items: tuple, filter_expr: Callable, remove_empty: bool) -> list:
    """
    Takes all items in the list, and returns a list with only items passing the filter_expr
    """
    res = []
    for item in items:
        ev = evaluate_mapping_statement(msg, item, remove_empty)
        if type(ev) != list:
            ev = list(ev)
        res += ev
    return list(filter(filter_expr, res))

def lookup(msg: dict, val: Any, lookup_dict: dict, default: Any) -> Optional[Any]:
    """
    Looks up a value in a dictionary. Assume val should be evaluated if it's callable. Take defaults
    """
    if callable(val):
        val = evaluate_mapping_statement(msg, val, remove_empty=False)
    return lookup_dict.get(val, default)