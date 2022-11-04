import re
from collections.abc import Collection
from itertools import chain
from typing import Any, TypeVar

DL = TypeVar("DL", dict[str, Any], list[Any])


def remove_empty_values(input: DL) -> DL:
    """
    Recursively removes "empty" objects (`None` and/or objects only containing `None` values).
    """
    if isinstance(input, list):
        return [remove_empty_values(v) for v in input if has_content(v)]
    elif isinstance(input, dict):
        return {k: remove_empty_values(v) for k, v in input.items() if has_content(v)}
    return input


def has_content(obj: Any) -> bool:
    """
    Checks if the object has "content" (a non-`None` value), and/or contains at least one item with "content".
    """
    res = obj is not None
    if res and isinstance(obj, Collection):
        res = len(obj) > 0
        # If has items, recursively check if those items have content.
        #   A case has content if at least one inner item has content.
        if isinstance(obj, list):
            res = any(has_content(item) for item in obj)
        elif isinstance(obj, dict):
            res = any(has_content(item) for item in obj.values())
    return res


def get_keys_containing_class(source: dict[str, Any], cls: type, key_prefix: str = "") -> set[str]:
    """
    Recursively finds all keys where a DROP object is found.
    """
    res = set()
    for k, v in source.items():
        curr_key = f"{key_prefix}.{k}" if key_prefix != "" else k
        match v:
            case cls():  # type: ignore
                res.add(curr_key)
            case dict():
                res |= get_keys_containing_class(v, cls, curr_key)
            case list():
                for i, item in enumerate(v):
                    indexed_keypath = f"{curr_key}[{i}]"
                    if isinstance(item, cls):
                        res.add(indexed_keypath)
                    elif isinstance(item, dict):
                        res |= get_keys_containing_class(item, cls, indexed_keypath)
    return res


REGEX_TUPLE_CASE_DELIM = re.compile(r"\.?\(|\)\.?")


def split_key(key: str) -> list[str]:
    """
    Splits keys into individual components. Removes spaces.

    Handles the tuple case, e.g.:
        "a.b.(c,d)" -> ["a", "b", "c,d"]
    """
    if "(" in key:
        split_parts = re.split(REGEX_TUPLE_CASE_DELIM, key)
        # Remove beginning and trailing empty strings
        if split_parts:
            if split_parts[0] == "":
                split_parts = split_parts[1:]
            if split_parts[-1] == "":
                split_parts = split_parts[:-1]
        # Remove spaces
        split_parts = [p.replace(" ", "") for p in split_parts]
        # Split into sublists
        split_subparts = [p.split(".") if "," not in p else [p] for p in split_parts]
        return list(chain.from_iterable(split_subparts))
    else:
        return key.split(".")
