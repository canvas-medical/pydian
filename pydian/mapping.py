from typing import Union, Any, Callable, Optional, List
import pydian.eval as E
from pydian.lib.util import assign_name
from pydian.lib.enums import RelativeObjectLevel as ROL
from functools import partial

""" Value-level Functions """
def get(key: str, then: Optional[Callable] = None, default: Optional[Any] = None) -> Callable:
    partial_fn = partial(E.single_get, key=key, default=default)
    if '.' in key:
        partial_fn = partial(E.nested_get, key=key, default=default)
    if then:
        partial_fn = eval_then_apply(partial_fn, then)
    return assign_name(partial_fn, 'get')

def eval_then_apply(eval: Callable, apply: Callable):
    partial_fn = partial(E.eval_then_apply, eval=eval, apply=apply)
    return assign_name(partial_fn, 'eval_then_apply')

def map_list(iter_over: Union[list, Callable], apply_fn: Callable, remove_empty: bool = False) -> Callable:
    partial_fn = partial(E.map_list, iter_over=iter_over, apply_fn=apply_fn, remove_empty=remove_empty)
    return assign_name(partial_fn, 'map_list')

def concat(*items, remove_empty: Optional[bool] = False) -> Callable:
    partial_fn = partial(E.concat, items=items, remove_empty=remove_empty)
    return assign_name(partial_fn, 'concat')

def filter_list(*items, filter_expr: Callable, remove_empty: bool = False) -> Callable:
    partial_fn = partial(E.filter_list, items=items, filter_expr=filter_expr, remove_empty=remove_empty)
    return assign_name(partial_fn, 'filter_list')

def lookup(val: Any, lookup_dict: dict, default: Optional[Any] = None) -> Callable:
    partial_fn = partial(E.lookup, val=val, lookup_dict=lookup_dict, default=default)
    return assign_name(partial_fn, 'lookup')

def apply_mapping(mapping: dict, start_at_key: Optional[str] = None, remove_empty: bool = False) -> Callable:
    partial_fn = partial(E.apply_mapping, mapping=mapping, start_at_key=start_at_key, remove_empty=remove_empty)
    return assign_name(partial_fn, 'apply_mapping')

""" Key-level Functions """
def drop_object_if(cond: Callable, res: ROL = ROL.CURRENT) -> Optional[ROL]:
    partial_fn = partial(E.drop_object_if, cond=cond, res=res)
    return assign_name(partial_fn, 'drop_object_if')