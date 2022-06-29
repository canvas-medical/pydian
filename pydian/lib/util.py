from collections.abc import Collection
from typing import Any


def remove_empty_values(input: list | dict):
    """
    Removes empty inner lists/dicts.
    """
    if isinstance(input, list):
        return [remove_empty_values(v) for v in input if has_content(v)]
    elif isinstance(input, dict):
        return {k: remove_empty_values(v) for k, v in input.items() if has_content(v)}
    return input


def has_content(obj: Any) -> bool:
    """
    False if object is empty, and/or contains only empty items, otherwise True
    """
    res = obj is not None
    if res and isinstance(obj, Collection):
        res = len(obj) > 0
        # If has items, recursively check if those items have content.
        # A case has content if at least one inner item has content.
        if isinstance(obj, list):
            res = any(has_content(item) for item in obj)
        elif isinstance(obj, dict):
            res = any(has_content(item) for item in obj.values())
    return res
