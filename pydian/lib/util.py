from typing import Any, Callable, Union
from copy import deepcopy
from pydian.lib.enums import TO_DELETE_KEY, ToDeleteInfo

def remove_empty_values(input: Union[list, dict]):
    """
    Removes empty inner lists/dicts.
    """
    if type(input) == list:
        return [remove_empty_values(v) for v in input if has_content(v)]
    elif type(input) == dict:
        return {k:remove_empty_values(v) for k, v in input.items() if has_content(v)}
    return input

def merge_dicts(*args) -> dict:
    """
    Merges multiple dicts. For duplicate keys:
        - First key appearance is final key location (order) in resulting dict
        - Second value appearance is final value associated to the key
    """
    appended_list = []
    for d in args:
        appended_list += list(d.items())
    return dict(appended_list)

def has_content(obj: Any) -> bool:
    """
    False if object is empty, and/or contains only empty items, otherwise True
    """
    res = obj != None
    if hasattr(obj, '__len__'):
        res = len(obj) > 0
        # If has items, recursively check if those items have content.
        # A case has content if at least one inner item has content.
        if type(obj) == list:
            inner_res = False
            for item in obj:
                inner_res = inner_res or has_content(item)
            res = res and inner_res
        elif type(obj) == dict:
            inner_res = False
            for _, v in obj.items():
                inner_res = inner_res or has_content(v)
            res = res and inner_res
    return res

def assign_name(fn: Callable, name: str) -> Callable:
    """
    Assigns name to object (intended for functions)
    """
    # TODO: Make sure this actually does what we want
    #       The end goal is make the stack trace nicer on errors
    fn.__name__ = name
    return fn