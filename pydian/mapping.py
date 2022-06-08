from typing import Union, Any, Callable, Optional, List
import pydian.eval as E
from pydian.lib.util import assign_name
from functools import partial

# TODO: Add Tests
def get(key: str, then: Optional[Callable] = None) -> Callable:
    partial_fn = partial(E.single_get, key=key)
    if '.' in key:
        partial_fn = partial(E.nested_get, key=key)
    if then:
        partial_fn = eval_then_apply(partial_fn, then)
    return assign_name(partial_fn, 'get')

def eval_then_apply(eval: Callable, apply: Callable):
    partial_fn = partial(E.eval_then_apply, eval=eval, apply=apply)
    return assign_name(partial_fn, 'eval_then_apply')

def map_list(iter_over: Union[list, Callable], apply_fn: Callable) -> Callable:
    partial_fn = partial(E.map_list, iter_over=iter_over, apply_fn=apply_fn)
    return assign_name(partial_fn, 'map_list')

def concat(*items, remove_empty: Optional[bool] = False) -> Callable:
    partial_fn = partial(E.concat, items=items, remove_empty=remove_empty)
    return assign_name(partial_fn, 'concat')

def filter_list(items: List[Any], filter_expr: Callable, remove_empty: Optional[bool] = False) -> Callable:
    partial_fn = partial(E.filter_list, items=items, filter_expr=filter_expr, remove_empty=remove_empty)
    return assign_name(partial_fn, 'filter_list')

def lookup(val: Any, lookup_dict: dict, default: Optional[Any] = None) -> Callable:
    partial_fn = partial(E.lookup, val=val, lookup_dict=lookup_dict, default=default)
    return assign_name(partial_fn, 'lookup')

def apply_mapping(mapping: dict, start_at_key: Optional[str] = None) -> Callable:
    partial_fn = partial(E.apply_mapping, mapping=mapping, start_at_key=start_at_key)
    return assign_name(partial_fn, 'apply_mapping')

# def evaluate_list_then_add(eval_list: List[Callable]) -> Callable:
#     partial_fn = partial(eval.evaluate_list_then_add, eval_list=eval_list)
#     return assign_name(partial_fn, 'evaluate_list_then_add')

# def map_list_then_add(iter_over: Union[list, Callable], apply_fn: Callable) -> Callable:
#     partial_fn = partial(eval.map_list_then_add, iter_over=iter_over, apply_fn=apply_fn)
#     return assign_name(partial_fn, 'map_list_then_add')